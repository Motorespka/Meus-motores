import streamlit as st
import pandas as pd
import os
import random
import string
from datetime import datetime, timedelta
from PIL import Image

# --- 1. CONFIGURAÇÕES E BANCO DE DADOS ---
ARQUIVO_CSV = 'meubancodedados.csv'
LINK_SHEETS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTFbH81UYKGJ6dQvKotxdv4hDxecLmiGUPHN46iexbw8NeS8_e2XdyZnZ8WJnL2XRTLCbFDbBKo_NGE/pub?output=csv"
PASTA_ESQUEMAS = 'esquemas_fotos'

if not os.path.exists(PASTA_ESQUEMAS): os.makedirs(PASTA_ESQUEMAS)

st.set_page_config(page_title="Pablo Motores | Gestão Profissional", layout="wide")

# Tabela AWG para o Simulador Técnico
TABELA_AWG = {
    10: 5.26, 12: 3.31, 14: 2.08, 15: 1.65, 16: 1.31, 17: 1.04, 
    18: 0.823, 19: 0.653, 20: 0.518, 21: 0.410, 22: 0.326, 23: 0.258
}

# Inicialização de estados
if 'db_os' not in st.session_state: st.session_state['db_os'] = []
if 'token_grupo' not in st.session_state: st.session_state['token_grupo'] = None

# --- 2. FUNÇÕES DE APOIO ---
@st.cache_data(ttl=60)
def carregar_dados():
    dfs = []
    try:
        df_nuvem = pd.read_csv(LINK_SHEETS, dtype=str)
        if not df_nuvem.empty: dfs.append(df_nuvem)
    except: pass
    if os.path.exists(ARQUIVO_CSV):
        try:
            df_local = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig', dtype=str)
            if not df_local.empty: dfs.append(df_local)
        except: pass
    return pd.concat(dfs, ignore_index=True).drop_duplicates() if dfs else pd.DataFrame()

def gerar_token():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# --- 3. BARRA LATERAL (ACESSO E EQUIPE) ---
with st.sidebar:
    st.header("👤 ACESSO")
    senha = st.text_input("Senha Admin", type="password")
    e_admin = (senha == "pablo123")
    
    st.divider()
    st.header("👥 CONEXÃO DE EQUIPE")
    if not st.session_state['token_grupo']:
        tipo_con = st.radio("Grupo:", ["Criar Novo", "Entrar com Token"])
        if tipo_con == "Criar Novo":
            if st.button("Gerar Código"):
                st.session_state['token_grupo'] = gerar_token()
                st.rerun()
        else:
            tk_input = st.text_input("Cole o Token")
            if st.button("Conectar"):
                st.session_state['token_grupo'] = tk_input
                st.rerun()
    else:
        st.success(f"Grupo Ativo: {st.session_state['token_grupo']}")
        if st.button("Sair do Grupo"):
            st.session_state['token_grupo'] = None
            st.rerun()

# --- 4. INTERFACE PRINCIPAL ---
tab_consulta, tab_cadastro, tab_simulador, tab_admin = st.tabs([
    "🔍 CONSULTA", "➕ NOVO CADASTRO", "🧪 SIMULADOR", "📊 PAINEL"
])

# --- ABA 1: CONSULTA ---
with tab_consulta:
    st.markdown("<h1 style='text-align: center; color: #f1c40f;'>⚙️ PABLO MOTORES</h1>", unsafe_allow_html=True)
    df = carregar_dados()
    busca = st.text_input("🔍 Pesquisar Marca, CV, Fio...")
    
    if not df.empty:
        df_f = df[df.apply(lambda row: row.astype(str).str.contains(busca, case=False).any(), axis=1)] if busca else df
        for idx, row in df_f.iterrows():
            with st.expander(f"📦 {row.get('Marca')} | {row.get('Potencia_CV')} CV"):
                c1, c2, c3 = st.columns(3)
                c1.write(f"**Polos:** {row.get('Polaridade')}\n**Volt:** {row.get('Voltagem')}")
                c2.write(f"**Fio Princ:** {row.get('Fio_Principal')}\n**Fio Aux:** {row.get('Fio_Auxiliar')}")
                c3.write(f"**Esquema:** {row.get('Esquema_Marcado')}")
                # Exibição de Imagem do Esquema
                lig = str(row.get('Esquema_Marcado'))
                if lig != "None":
                    for n in lig.split(" / "):
                        for ext in [".png", ".jpg"]:
                            p = os.path.join(PASTA_ESQUEMAS, f"{n.strip()}{ext}")
                            if os.path.exists(p): st.image(p, width=300)

# --- ABA 2: NOVO CADASTRO ---
with tab_cadastro:
    if e_admin:
        st.subheader("Cadastrar Dados Técnicos")
        with st.form("form_cadastro"):
            c1, c2 = st.columns(2)
            marca = c1.text_input("Marca"); cv = c2.text_input("Potência (CV)")
            fio_p = c1.text_input("Fio Principal"); fio_a = c2.text_input("Fio Auxiliar")
            esquema = st.text_input("Nome do Esquema de Ligação")
            if st.form_submit_button("Salvar no Banco"):
                novo = {'Marca': marca, 'Potencia_CV': cv, 'Fio_Principal': fio_p, 'Fio_Auxiliar': fio_a, 'Esquema_Marcado': esquema}
                pd.DataFrame([novo]).to_csv(ARQUIVO_CSV, mode='a', header=not os.path.exists(ARQUIVO_CSV), index=False, sep=';', encoding='utf-8-sig')
                st.success("Salvo!")
    else:
        st.warning("Acesso restrito ao Administrador.")

# --- ABA 3: SIMULADOR TÉCNICO (NOVO) ---
with tab_simulador:
    st.subheader("🧪 Simulador de Equivalência de Fios")
    c1, c2 = st.columns(2)
    fio_orig = c1.selectbox("AWG Original", list(TABELA_AWG.keys()))
    qtd_fios = c1.number_input("Quantidade de fios originais", min_value=1, value=1)
    
    area_total = TABELA_AWG[fio_orig] * qtd_fios
    st.info(f"Área Total necessária: **{area_total:.3f} mm²**")
    
    fio_sub = c2.selectbox("Substituir por AWG", list(TABELA_AWG.keys()))
    necessarios = area_total / TABELA_AWG[fio_sub]
    st.metric("Quantidade de fios necessária", f"{necessarios:.2f}")

# --- ABA 4: PAINEL DE CONTROLE ---
with tab_admin:
    st.subheader("📊 Resumo de Atividades")
    if e_admin:
        col1, col2 = st.columns(2)
        col1.metric("Motores no Banco", len(carregar_dados()))
        col2.metric("Grupo Atual", st.session_state['token_grupo'] if st.session_state['token_grupo'] else "Offline")
        
        if st.button("Limpar Banco Local (CUIDADO)"):
            if os.path.exists(ARQUIVO_CSV): os.remove(ARQUIVO_CSV); st.rerun()
    else:
        st.info("Painel de indicadores disponível apenas para Pablo (Admin).")
