import streamlit as st
import pandas as pd
import os
import re
import hashlib
from datetime import datetime, timedelta
from PIL import Image

# --- 1. BANCO TÉCNICO DE ENGENHARIA (TABELA AWG COMPLETA) ---
TABELA_AWG_TECNICA = {
    '4/0': 107.0, '3/0': 85.0, '2/0': 67.4, '1/0': 53.5,
    '1': 42.41, '2': 33.63, '3': 26.67, '4': 21.147, '5': 16.764,
    '6': 13.299, '7': 10.55, '8': 8.367, '9': 6.633, '10': 5.26,
    '11': 4.169, '12': 3.307, '13': 2.627, '14': 2.082, '15': 1.651,
    '16': 1.307, '17': 1.04, '18': 0.8235, '19': 0.6533, '20': 0.5191,
    '21': 0.4117, '22': 0.3247, '23': 0.2588, '24': 0.2051, '25': 0.1626,
    '26': 0.1282, '27': 0.1024, '28': 0.0804, '29': 0.0647, '30': 0.0507,
    '31': 0.0401, '32': 0.0324, '33': 0.0254, '34': 0.0201
}

# --- 2. FUNÇÕES DE CÁLCULO E SEGURANÇA ---
def calcular_area_mm2(texto_fio):
    try:
        if not texto_fio or str(texto_fio) == "None": return 0.0
        texto = str(texto_fio).lower().replace('awg', '').strip()
        if 'x' in texto:
            qtd, bitola = texto.split('x')
            return int(re.findall(r'\d+', qtd)[0]) * TABELA_AWG_TECNICA.get(bitola.strip(), 0.0)
        bitolas = re.findall(r'\d+', texto)
        return TABELA_AWG_TECNICA.get(bitolas[0], 0.0) if bitolas else 0.0
    except: return 0.0

def gerar_sugestoes_com_risco(area_alvo):
    sugestoes = []
    if area_alvo <= 0: return []
    for bitola, area_u in TABELA_AWG_TECNICA.items():
        for qtd in range(1, 5):
            area_sim = area_u * qtd
            diff = ((area_sim - area_alvo) / area_alvo) * 100
            if -15.0 <= diff <= 15.0:
                if abs(diff) <= 2.5: cor, status = "#2ecc71", "SEGURA (Verde)"
                elif 2.5 < diff <= 8.0 or -8.0 <= diff < -2.5: cor, status = "#f1c40f", "ALERTA (Amarelo)"
                else: cor, status = "#e74c3c", "ARRISCADA (Vermelho)"
                sugestoes.append({'fio': f"{qtd}x{bitola} AWG", 'diff': diff, 'cor': cor, 'status': status})
    return sorted(sugestoes, key=lambda x: abs(x['diff']))

# --- 3. CONFIGURAÇÕES, LOGIN E ARQUIVOS ---
ARQUIVO_USUARIOS = 'usuarios.csv'
ARQUIVO_CSV = 'meubancodedados.csv'

def carregar_dados():
    if not os.path.exists(ARQUIVO_CSV): return pd.DataFrame()
    df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig', dtype=str)
    df.columns = df.columns.str.strip()
    return df

def salvar_dados(df):
    df.to_csv(ARQUIVO_CSV, index=False, sep=';', encoding='utf-8-sig')

st.set_page_config(page_title="Pablo Motores", layout="wide")

# --- LÓGICA DE LOGIN ---
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = None

if not st.session_state['user_data']:
    st.title("🔐 Acesso Pablo Motores")
    with st.form("login"):
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.form_submit_button("Entrar"):
            # Exemplo de validação simples (substitua pela sua lógica de CSV se necessário)
            if u == "admin" and p == "pablo2026":
                st.session_state['user_data'] = {'usuario': u, 'perfil': 'admin'}
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos")
else:
    # --- SITE LOGADO ---
    user = st.session_state['user_data']
    e_admin = (user['perfil'] == 'admin')

    with st.sidebar:
        st.write(f"👤 **{user['usuario'].upper()}**")
        menu = ["🔍 CONSULTA"]
        if e_admin: menu += ["➕ NOVO CADASTRO", "🗑️ LIXEIRA"]
        escolha = st.radio("Menu", menu)
        if st.button("Sair"):
            st.session_state['user_data'] = None
            st.rerun()

    # --- ABA: CONSULTA (INCLUI EDITAR E ALTERAR COM OPÇÕES DE RISCO) ---
    if escolha == "🔍 CONSULTA":
        st.title("🔍 Sistema de Consulta e Engenharia")
        df = carregar_dados()
        busca = st.text_input("Pesquisar por Marca, CV, RPM...")

        if not df.empty:
            if not e_admin: df = df[df.get('status', 'ativo') != 'deletado']
            df_f = df[df.apply(lambda row: row.astype(str).str.contains(busca, case=False).any(), axis=1)] if busca else df

            for idx, row in df_f.iterrows():
                area_orig = calcular_area_mm2(row.get('Fio_Principal'))
                
                with st.expander(f"📦 {row.get('Marca')} | {row.get('Potencia_CV')} CV"):
                    c_info, c_btns = st.columns([2, 1])
                    with c_info:
                        st.write(f"**Fio de Fábrica:** {row.get('Fio_Principal')} ({area_orig:.3f} mm²)")
                        st.write(f"**Amperagem:** {row.get('Amperagem')} | **Esquema:** {row.get('Esquema_Marcado', 'N/A')}")
                        st.write(f"**Mecânica:** Rolamentos: {row.get('Rolamentos')} | Eixos: {row.get('Eixo_X')}/{row.get('Eixo_Y')}")

                    with c_btns:
                        if st.button("🔄 ALTERAR (Opções de Cópia)", key=f"alt_{idx}"):
                            st.session_state[f"show_alt_{idx}"] = not st.session_state.get(f"show_alt_{idx}", False)
                        if e_admin:
                            if st.button("📝 EDITAR ORIGINAL", key=f"ed_{idx}"):
                                st.session_state[f"show_ed_{idx}"] = not st.session_state.get(f"show_ed_{idx}", False)
                            if st.button("🗑️ EXCLUIR", key=f"del_{idx}"):
                                df.at[idx, 'status'] = 'deletado'
                                df.at[idx, 'data_del'] = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
                                salvar_dados(df); st.rerun()

                    # --- INTERFACE: ABA ALTERAR (GERA OPÇÕES AUTOMÁTICAS) ---
                    if st.session_state.get(f"show_alt_{idx}"):
                        st.markdown("---")
                        st.subheader("🛠️ Sugestões de Rebobinagem")
                        opcoes = gerar_sugestoes_com_risco(area_orig)
                        for op in opcoes[:10]:
                            st.markdown(f"""
                                <div style="border-left: 10px solid {op['cor']}; background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-bottom: 5px; color: black;">
                                    <b>{op['fio']}</b> ({op['diff']:.2f}%) - <span style="color:{op['cor']};"><b>{op['status']}</b></span>
                                </div>
                            """, unsafe_allow_html=True)

                    # --- INTERFACE: ABA EDITAR (ADMIN) ---
                    if e_admin and st.session_state.get(f"show_ed_{idx}"):
                        st.markdown("---")
                        with st.form(f"form_ed_{idx}"):
                            st.warning("✍️ ALTERANDO DADOS DEFINITIVOS")
                            n_fio = st.text_input("Fio Principal", value=row.get('Fio_Principal'))
                            n_amp = st.text_input("Amperagem", value=row.get('Amperagem'))
                            if st.form_submit_button("SALVAR"):
                                df.at[idx, 'Fio_Principal'] = n_fio
                                df.at[idx, 'Amperagem'] = n_amp
                                salvar_dados(df); st.rerun()

    # --- ABA: NOVO CADASTRO (TODOS OS CAMPOS) ---
    elif escolha == "➕ NOVO CADASTRO" and e_admin:
        st.title("➕ Cadastrar Motor")
        with st.form("novo_motor"):
            c1, c2, c3 = st.columns(3)
            with c1:
                m = st.text_input("Marca"); cv = st.text_input("CV"); r = st.text_input("RPM")
            with c2:
                f_p = st.text_input("Fio Principal"); amp = st.text_input("Amperagem")
            with c3:
                rol = st.text_input("Rolamentos"); ex = st.text_input("Eixo")
            
            if st.form_submit_button("CADASTRAR"):
                # Lógica de salvar motor ativo
                pass

    # --- ABA: LIXEIRA ---
    elif escolha == "🗑️ LIXEIRA" and e_admin:
        st.title("🗑️ Lixeira")
        # Lógica de visualização e restauração
