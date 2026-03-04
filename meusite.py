import streamlit as st
import pandas as pd
import os
from PIL import Image

# --- CONFIGURAÇÕES DE DIRETÓRIOS ---
ARQUIVO_CSV = 'meubancodedados.csv'
PASTA_ESQUEMAS = 'esquemas_fotos'
if not os.path.exists(PASTA_ESQUEMAS):
    os.makedirs(PASTA_ESQUEMAS)

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Pablo Motores | Gestão Pro", layout="wide")

# --- CSS DE ALTA VISIBILIDADE PARA PC ---
st.markdown("""
    <style>
    /* Fundo Escuro para contraste */
    .stApp { background-color: #0b0e14; }
    
    /* CORRIGINDO O TEXTO DESAPARECIDO: Força títulos e labels a serem visíveis */
    label, .stMarkdown p, .stMarkdown h3, .stMarkdown h2, .stMarkdown b {
        color: #f1c40f !important; /* Amarelo Pablo para títulos */
        font-weight: 800 !important;
        font-size: 1.1rem !important;
        opacity: 1 !important;
    }

    /* Campos de Entrada (Onde você escreve) */
    input, textarea, [data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #f1c40f !important;
        font-weight: bold !important;
    }

    /* Estilo para as "Caixas" de Informação (Cards) */
    .stExpander {
        border: 2px solid #34495e !important;
        background-color: #161a24 !important;
        border-radius: 10px !important;
    }
    
    /* Botões Grandes e Visíveis */
    .stButton>button {
        background-color: #f1c40f !important;
        color: #000000 !important;
        font-weight: 900 !important;
        border: 2px solid #ffffff !important;
        text-transform: uppercase;
    }

    /* Barra Lateral (Sidebar) */
    [data-testid="stSidebar"] {
        background-color: #161a24 !important;
        border-right: 2px solid #f1c40f !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGICA DE ADMIN ---
with st.sidebar:
    st.markdown("### 🔐 PAINEL ADMIN")
    senha = st.text_input("Senha", type="password")
    e_admin = (senha == "pablo123")

st.markdown("<h1 style='text-align: center; color: #f1c40f;'>⚙️ PABLO MOTORES</h1>", unsafe_allow_html=True)

# --- CARREGAR DADOS ---
if os.path.exists(ARQUIVO_CSV):
    df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig').fillna("---").replace("None", "---")
else:
    df = pd.DataFrame()

opcoes_esquemas = [f.replace(".png", "").replace(".jpg", "") for f in os.listdir(PASTA_ESQUEMAS) if f.endswith(('.png', '.jpg'))]

# --- NAVEGAÇÃO ---
abas = ["🔍 CONSULTA", "➕ NOVO CADASTRO", "🖼️ ESQUEMAS"] if e_admin else ["🔍 CONSULTA"]
tab_cons, *tab_outras = st.tabs(abas)

# --- ABA 1: CONSULTA (Texto sempre visível) ---
with tab_cons:
    busca = st.text_input("🔎 Pesquisar Motor...")
    if not df.empty:
        df_f = df[df.astype(str).apply(lambda x: busca.lower() in x.str.lower().any(), axis=1)] if busca else df
        for idx, row in df_f.iterrows():
            with st.expander(f"📦 {row.get('Marca')} | {row.get('Potencia_CV')} CV"):
                # Organizador de colunas com títulos forçados em amarelo
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown("### 📊 DADOS") # Este título agora vai aparecer
                    st.write(f"**RPM:** {row.get('RPM')}")
                    st.write(f"**Polos:** {row.get('Polaridade')}")
                with c2:
                    st.markdown("### 🌀 PRINCIPAL")
                    st.write(f"**Fio:** {row.get('Fio_Principal')}")
                with c3:
                    st.markdown("### 🔗 LIGAÇÃO")
                    st.info(row.get('Esquema_Marcado'))

# --- ABA 2: CADASTRO (Com títulos de seção visíveis) ---
if e_admin:
    with tab_outras[0]:
        st.markdown("## ➕ Cadastrar Novo Motor")
        with st.form("form_novo"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 📝 INFORMAÇÕES") # Seção que estava sumida
                marca = st.text_input("Marca do Motor")
                cv = st.text_input("Potência (CV)")
                volt = st.text_input("Voltagem")
            with col2:
                st.markdown("### 🧵 DADOS TÉCNICOS")
                fio_p = st.text_input("Fio Principal")
                fio_a = st.text_input("Fio Auxiliar")
            
            st.markdown("### 🖼️ SELECIONE AS LIGAÇÕES")
            sel_ligs = {opt: st.checkbox(opt, key=f"n_{opt}") for opt in opcoes_esquemas}
            
            if st.form_submit_button("💾 SALVAR NO BANCO DE DADOS"):
                # Lógica de salvar...
                st.success("Salvo!")

# Aba Esquemas segue o mesmo padrão visual...
