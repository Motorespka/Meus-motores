import streamlit as st
import pandas as pd
import os
import re
import urllib.parse
from datetime import datetime

# --- 1. CONFIGURAÇÕES ---
TOKEN_PRO = "PABLO123"
TOKEN_MESTRE = "MESTRE99"
ARQUIVO_CSV = 'meubancodedados.csv'
ARQUIVO_FOTOS = 'biblioteca_fotos.csv'
PASTA_UPLOADS = 'uploads_ligacoes'

if not os.path.exists(PASTA_UPLOADS): os.makedirs(PASTA_UPLOADS)

# Colunas expandidas para suportar mais detalhes técnicos
COL_MOTORES = [
    'Marca', 'Potencia_CV', 'RPM', 'Voltagem', 'Amperagem', 'Polaridade', 
    'Bobina_Principal', 'Fio_Principal', 'Passo_Principal',
    'Bobina_Auxiliar', 'Fio_Auxiliar', 'Passo_Auxiliar',
    'Tipo_Ligacao', 'Ligacao_Interna', 'Rolamentos', 'Selo_Mecanico',
    'Eixo_X', 'Eixo_Y', 'Capacitor', 'status', 'Obs_Tecnica'
]

# --- 2. FUNÇÕES ---
def carregar_dados(arq, colunas):
    if not os.path.exists(arq) or os.stat(arq).st_size == 0:
        return pd.DataFrame(columns=colunas)
    df = pd.read_csv(arq, sep=';', encoding='utf-8-sig', dtype=str).fillna("")
    for col in colunas:
        if col not in df.columns: df[col] = ""
    return df

def salvar_dados(df, arq):
    df.fillna("").to_csv(arq, index=False, sep=';', encoding='utf-8-sig')

# --- 3. LOGIN ---
if 'autenticado' not in st.session_state: st.session_state['autenticado'] = False
if 'perfil' not in st.session_state: st.session_state['perfil'] = None

def tela_login():
    st.title("⚙️ Sistema Pablo Motores")
    aba1, aba2 = st.tabs(["🔐 Entrar", "📝 Novo Cliente"])
    with aba1:
        perfil = st.selectbox("Acesso", ["👤 Cliente", "🛠️ Profissional", "🧠 Mestre"])
        if perfil == "👤 Cliente":
            if st.button("Acessar como Visitante"):
                st.session_state['autenticado'] = True
                st.session_state['perfil'] = 'cliente'
                st.rerun()
        else:
            tk = st.text_input("Token de Acesso", type="password")
            if st.button("Validar"):
                if (perfil == "🛠️ Profissional" and tk == TOKEN_PRO) or (perfil == "🧠 Mestre" and tk == TOKEN_MESTRE):
                    st.session_state['autenticado'] = True
                    st.session_state['perfil'] = 'mestre' if perfil == "🧠 Mestre" else 'pro'
                    st.rerun()
                else: st.error("Token Inválido")

# --- 4. INTERFACE ---
if not st.session_state['autenticado']:
    tela_login()
else:
    st.set_page_config(page_title="Pablo Motores Pro", layout="wide")
    df_motores = carregar_dados(ARQUIVO_CSV, COL_MOTORES)
    df_fotos = carregar_dados(ARQUIVO_FOTOS, ['nome_ligacao', 'caminho_arquivo'])
    lista_ligacoes = [""] + df_fotos['nome_ligacao'].tolist()

    with st.sidebar:
        st.header(f"🔑 {st.session_state['perfil'].upper()}")
        if st.button("🚪 Sair"):
            st.session_state['autenticado'] = False
            st.rerun()
        st.divider()
        menu = st.radio("Navegação", ["🔍 CONSULTA", "➕ NOVO MOTOR", "🖼️ BIBLIOTECA", "🗑️ LIXEIRA"])

    if menu == "🔍 CONSULTA":
        busca = st.text_input("Filtrar motor (Marca, CV, RPM...)")
        df_f = df_motores[df_motores['status'] != 'deletado']
        if busca:
            df_f = df_f[df_f.apply(lambda r: r.astype(str).str.contains(busca, case=False).any(), axis=1)]

        for idx, row in df_f.iterrows():
            with st.expander(f"📦 {row['Marca']} | {row['Potencia_CV']} CV | {row['RPM']} RPM"):
                t_basico, t_pro, t_mestre = st.tabs(["🟢 BÁSICO", "🛠️ PROFISSIONAL", "🧠 MESTRE (EDITAR)"])
                
                with t_basico:
                    st.subheader("Informações Gerais")
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.write(f"**Voltagem:** {row['Voltagem']}")
                        st.write(f"**Amperagem:** {row['Amperagem']} A")
                        st.write(f"**Capacitor:** {row['Capacitor']}")
                    with c2:
                        st.write(f"**Rolamentos:** {row['Rolamentos']}")
                        st.write(f"**Selo Mecânico:** {row['Selo_Mecanico']}")
                        st.write(f"**Eixo:** {row['Eixo_X']} / {row['Eixo_Y']}")
                    with c3:
                        tipo = row['Tipo_Ligacao']
                        if tipo in df_fotos['nome_ligacao'].values:
                            st.image(df_fotos[df_fotos['nome_ligacao'] == tipo]['caminho_arquivo'].values[0])

                with t_pro:
                    if st.session_state['perfil'] in ['pro', 'mestre']:
                        st.subheader("Dados de Rebobinagem")
                        p1, p2 = st.columns(2)
                        with p1:
                            st.info(f"**Fio Principal:** {row['Fio_Principal']} (Passo: {row['Passo_Principal']})")
                            st.info(f"**Espiras P:** {row['Bobina_Principal']}")
                            st.write(f"**Ligação Interna:** {row['Ligacao_Interna']}")
                        with p2:
                            st.warning(f"**Fio Auxiliar:** {row['Fio_Auxiliar']} (Passo: {row['Passo_Auxiliar']})")
                            st.warning(f"**Espiras A:** {row['Bobina_Auxiliar']}")
                            st.write(f"**Obs:** {row['Obs_Tecnica']}")
                    else: st.warning("Acesso restrito.")

                with t_mestre:
                    if st.session_state['perfil'] == 'mestre':
                        st.subheader("📝 Painel de Edição Mestre")
                        with st.form(key=f"edit_{idx}"):
                            # Formulário de edição rápida
                            e1, e2, e3 = st.columns(3)
                            n_marca = e1.text_input("Marca", row['Marca'])
                            n_cv = e1.text_input("CV", row['Potencia_CV'])
                            n_fio = e2.text_input("Fio P", row['Fio_Principal'])
                            n_esp = e2.text_input("Espiras P", row['Bobina_Principal'])
                            n_rol = e3.text_input("Rolamentos", row['Rolamentos'])
                            n_obs = e3.text_area("Notas Técnicas", row['Obs_Tecnica'])
                            
                            if st.form_submit_button("💾 Salvar Alterações"):
                                df_motores.at[idx, 'Marca'] = n_marca
                                df_motores.at[idx, 'Potencia_CV'] = n_cv
                                df_motores.at[idx, 'Fio_Principal'] = n_fio
                                df_motores.at[idx, 'Bobina_Principal'] = n_esp
                                df_motores.at[idx, 'Rolamentos'] = n_rol
                                df_motores.at[idx, 'Obs_Tecnica'] = n_obs
                                salvar_dados(df_motores, ARQUIVO_CSV)
                                st.success("Dados atualizados!")
                                st.rerun()
                        
                        if st.button("🗑️ Excluir Motor", key=f"del_{idx}"):
                            df_motores.at[idx, 'status'] = 'deletado'
                            salvar_dados(df_motores, ARQUIVO_CSV); st.rerun()
                    else: st.warning("Acesso restrito ao Chefe.")

    elif menu == "➕ NOVO MOTOR":
        if st.session_state['perfil'] in ['pro', 'mestre']:
            st.header("Cadastrar Novo Motor")
            with st.form("add_motor", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                with c1:
                    m = st.text_input("Marca"); cv = st.text_input("CV"); rpm = st.text_input("RPM")
                    v = st.text_input("Voltagem"); amp = st.text_input("Amperagem")
                with c2:
                    fp = st.text_input("Fio Principal"); pp = st.text_input("Passo P"); bp = st.text_input("Espiras P")
                    fa = st.text_input("Fio Auxiliar"); pa = st.text_input("Passo A"); ba = st.text_input("Espiras A")
                with c3:
                    rol = st.text_input("Rolamentos"); selo = st.text_input("Selo Mecânico")
                    ex = st.text_input("Eixo X"); ey = st.text_input("Eixo Y"); cap = st.text_input("Capacitor")
                    lig_int = st.text_input("Ligação Interna (Série/Paralelo)")
                
                obs = st.text_area("Observações Técnicas")
                
                if st.form_submit_button("✅ SALVAR NO BANCO"):
                    novo = {
                        'Marca': m, 'Potencia_CV': cv, 'RPM': rpm, 'Voltagem': v, 'Amperagem': amp,
                        'Fio_Principal': fp, 'Passo_Principal': pp, 'Bobina_Principal': bp,
                        'Fio_Auxiliar': fa, 'Passo_Auxiliar': pa, 'Bobina_Auxiliar': ba,
                        'Rolamentos': rol, 'Selo_Mecanico': selo, 'Eixo_X': ex, 'Eixo_Y': ey,
                        'Capacitor': cap, 'Ligacao_Interna': lig_int, 'Obs_Tecnica': obs, 'status': 'ativo'
                    }
                    df_motores = pd.concat([df_motores, pd.DataFrame([novo])], ignore_index=True)
                    salvar_dados(df_motores, ARQUIVO_CSV); st.success("Motor cadastrado!")
        else: st.error("Apenas Profissionais ou Mestre podem cadastrar.")
