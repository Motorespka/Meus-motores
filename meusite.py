import streamlit as st
import pandas as pd
import os
import re
import hashlib
from datetime import datetime, timedelta
from PIL import Image

# --- 1. CONFIGURAÇÕES E BANCO TÉCNICO ---
ARQUIVO_USUARIOS = 'usuarios.csv'
ARQUIVO_CSV = 'meubancodedados.csv'
PASTA_ESQUEMAS = 'esquemas_fotos'
CHAVE_MESTRA_CHEFIA = "PABLO2026"

# Tabela AWG Oficial (Área em mm²)
TABELA_AWG = {
    '14': 2.08, '15': 1.65, '16': 1.31, '17': 1.04, '18': 0.823, '19': 0.653,
    '20': 0.518, '21': 0.410, '22': 0.326, '23': 0.258, '24': 0.205, '25': 0.162
}

if not os.path.exists(PASTA_ESQUEMAS): os.makedirs(PASTA_ESQUEMAS)

# --- 2. FUNÇÕES DE ENGENHARIA AUTOMÁTICA ---
def calcular_mm2(texto_fio):
    try:
        texto = str(texto_fio).lower().replace('awg', '').strip()
        if 'x' in texto:
            partes = texto.split('x')
            qtd = int(re.findall(r'\d+', partes[0])[0])
            bitola = partes[1].strip()
            return qtd * TABELA_AWG.get(bitola, 0)
        bitolas = re.findall(r'\d+', texto)
        return TABELA_AWG.get(bitolas[0], 0) if bitolas else 0
    except: return 0

def buscar_equivalentes(area_alvo):
    if area_alvo <= 0: return []
    opcoes = []
    for bitola, area_u in TABELA_AWG.items():
        for qtd in range(1, 5):
            area_t = area_u * qtd
            diff = ((area_t - area_alvo) / area_alvo) * 100
            if -3.0 <= diff <= 5.0: # Margem de segurança técnica
                opcoes.append({'label': f"{qtd}x {bitola} AWG", 'diff': diff})
    return sorted(opcoes, key=lambda x: abs(x['diff']))

# --- 3. FUNÇÕES DE DADOS ---
def carregar_dados():
    if not os.path.exists(ARQUIVO_CSV): return pd.DataFrame()
    df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig', dtype=str)
    df.columns = df.columns.str.strip()
    return df

def salvar_dados(df):
    df.to_csv(ARQUIVO_CSV, index=False, sep=';', encoding='utf-8-sig')
    st.cache_data.clear()

# --- 4. INTERFACE ---
st.set_page_config(page_title="Pablo Motores | Gestão", layout="wide")

if 'user_data' not in st.session_state: st.session_state['user_data'] = None

# (Lógica de Login e Sidebar mantida conforme sua base original)
if st.session_state['user_data']:
    user = st.session_state['user_data']
    e_admin = (user.get('perfil') == 'admin')
    
    menu = ["🔍 CONSULTA"]
    if e_admin: menu += ["➕ NOVO CADASTRO", "🖼️ ADICIONAR FOTO", "🗑️ LIXEIRA"]
    escolha = st.sidebar.radio("Menu", menu)

    # --- ABA: CONSULTA (EDITAR E ALTERAR/CÓPIA) ---
    if escolha == "🔍 CONSULTA":
        st.title("⚙️ SISTEMA DE CONSULTA TÉCNICA")
        df = carregar_dados()
        busca = st.text_input("🔍 Pesquisar motor...")

        if not df.empty:
            # Filtro para usuários comuns não verem deletados
            if not e_admin:
                df = df[df.get('status', 'ativo') != 'deletado']
            
            df_f = df[df.apply(lambda row: row.astype(str).str.contains(busca, case=False).any(), axis=1)] if busca else df
            
            for idx, row in df_f.iterrows():
                area_orig = calcular_mm2(row.get('Fio_Principal', ''))
                label = f"📦 {row.get('Marca', 'S/M')} | {row.get('Potencia_CV', 'S/P')} CV"
                
                with st.expander(label):
                    c1, c2 = st.columns([2, 1])
                    with c1:
                        st.write(f"**Fio Original:** {row.get('Fio_Principal')} ({area_orig:.3f} mm²)")
                        st.write(f"**Amperagem:** {row.get('Amperagem')} | **RPM:** {row.get('RPM')}")
                        st.write(f"**Mecânica:** Rol: {row.get('Rolamentos')} | Eixo: {row.get('Eixo_X')}/{row.get('Eixo_Y')}")

                    with c2:
                        # BOTÃO ALTERAR (CÓPIA AUTOMÁTICA)
                        if st.button("🔄 Alterar (Ver Opções)", key=f"alt_{idx}"):
                            st.session_state[f"view_{idx}"] = True
                        
                        # BOTÃO EDITAR (SOMENTE ADMIN)
                        if e_admin:
                            if st.button("📝 Editar Cadastro", key=f"ed_{idx}"):
                                st.session_state[f"edit_{idx}"] = True
                            if st.button("🗑️ Excluir", key=f"del_{idx}"):
                                df.at[idx, 'status'] = 'deletado'
                                df.at[idx, 'data_delete'] = datetime.now().strftime('%Y-%m-%d')
                                salvar_dados(df)
                                st.rerun()

                    # --- LÓGICA ALTERAR (SUGESTÕES AUTOMÁTICAS) ---
                    if st.session_state.get(f"view_{idx}"):
                        st.markdown("---")
                        st.info("💡 **SUGESTÕES DE SUBSTITUIÇÃO SEGURA**")
                        sugestoes = buscar_equivalentes(area_orig)
                        if sugestoes:
                            for s in sugestoes:
                                cor = "green" if abs(s['diff']) < 1.5 else "orange"
                                st.markdown(f"✅ **{s['label']}** (Diferença: {s['diff']:.1f}%)")
                        else: st.warning("Nenhuma combinação AWG simples encontrada.")
                        if st.button("Fechar Opções", key=f"cls_{idx}"):
                            del st.session_state[f"view_{idx}"]; st.rerun()

                    # --- LÓGICA EDITAR (ADMIN - ALTERA O BANCO) ---
                    if e_admin and st.session_state.get(f"edit_{idx}"):
                        with st.form(f"form_ed_{idx}"):
                            st.warning("✍️ VOCÊ ESTÁ ALTERANDO O ORIGINAL")
                            n_fio = st.text_input("Fio Principal", value=row.get('Fio_Principal'))
                            n_amp = st.text_input("Amperagem", value=row.get('Amperagem'))
                            if st.form_submit_button("SALVAR"):
                                df.at[idx, 'Fio_Principal'] = n_fio
                                df.at[idx, 'Amperagem'] = n_amp
                                salvar_dados(df)
                                del st.session_state[f"edit_{idx}"]; st.rerun()

    # --- ABA: NOVO CADASTRO (TODOS OS CAMPOS) ---
    elif escolha == "➕ NOVO CADASTRO" and e_admin:
        st.title("➕ Novo Motor")
        with st.form("cad_completo"):
            c1, c2, c3 = st.columns(3)
            with c1:
                marca = st.text_input("Marca"); cv = st.text_input("Potencia_CV"); rpm = st.text_input("RPM")
                pol = st.text_input("Polaridade"); volt = st.text_input("Voltagem"); amp = st.text_input("Amperagem")
            with c2:
                g_p = st.text_input("Grupo Principal"); f_p = st.text_input("Fio Principal")
                rol = st.text_input("Rolamentos"); ex_x = st.text_input("Eixo X")
            with c3:
                g_a = st.text_input("Grupo Auxiliar"); f_a = st.text_input("Fio Auxiliar")
                cap = st.text_input("Capacitor"); ex_y = st.text_input("Eixo Y")
            
            if st.form_submit_button("CADASTRAR"):
                novo = {
                    'Marca': marca, 'Potencia_CV': cv, 'RPM': rpm, 'Polaridade': pol, 'Voltagem': volt,
                    'Amperagem': amp, 'Bobina_Principal': g_p, 'Fio_Principal': f_p, 'Rolamentos': rol,
                    'Eixo_X': ex_x, 'Bobina_Auxiliar': g_a, 'Fio_Auxiliar': f_a, 'Capacitor': cap,
                    'Eixo_Y': ex_y, 'status': 'ativo'
                }
                df_novo = pd.concat([carregar_dados(), pd.DataFrame([novo])], ignore_index=True)
                salvar_dados(df_novo)
                st.success("Salvo!")

    # --- ABA: LIXEIRA (LIMPEZA APÓS 5 DIAS) ---
    elif escolha == "🗑️ LIXEIRA" and e_admin:
        st.title("🗑️ Lixeira")
        df = carregar_dados()
        if not df.empty:
            hoje = datetime.now()
            # Remove permanente se passar de 5 dias
            for i, r in df[df['status'] == 'deletado'].iterrows():
                data_del = datetime.strptime(r['data_delete'], '%Y-%m-%d')
                if (hoje - data_del).days >= 5:
                    df.drop(i, inplace=True)
                    salvar_dados(df); st.rerun()
            
            excluidos = df[df['status'] == 'deletado']
            st.write(f"Itens na lixeira: {len(excluidos)}")
            for i, r in excluidos.iterrows():
                st.error(f"{r['Marca']} - {r['Potencia_CV']} CV")
                if st.button(f"Restaurar {i}"):
                    df.at[i, 'status'] = 'ativo'
                    salvar_dados(df); st.rerun()
                    
