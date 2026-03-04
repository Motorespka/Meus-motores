import streamlit as st
import pandas as pd
import os
import random
import string
import hashlib
from PIL import Image

# --- 1. CONFIGURAÇÕES DE ARQUIVOS ---
ARQUIVO_USUARIOS = 'usuarios.csv'
ARQUIVO_CSV = 'meubancodedados.csv'
LINK_SHEETS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTFbH81UYKGJ6dQvKotxdv4hDxecLmiGUPHN46iexbw8NeS8_e2XdyZnZ8WJnL2XRTLCbFDbBKo_NGE/pub?output=csv"
PASTA_ESQUEMAS = 'esquemas_fotos'

if not os.path.exists(PASTA_ESQUEMAS): os.makedirs(PASTA_ESQUEMAS)

# Tabela AWG
TABELA_AWG = {
    10: 5.26, 11: 4.17, 12: 3.31, 13: 2.63, 14: 2.08, 15: 1.65, 16: 1.31,
    17: 1.04, 18: 0.823, 19: 0.653, 20: 0.518, 21: 0.410, 22: 0.326,
    23: 0.258, 24: 0.205, 25: 0.162, 26: 0.129
}

# --- 2. FUNÇÕES DE SEGURANÇA ---
def hash_senha(senha):
    return hashlib.sha256(str.encode(senha)).hexdigest()

def salvar_usuario(usuario, senha, perfil="mecanico"):
    df = pd.read_csv(ARQUIVO_USUARIOS) if os.path.exists(ARQUIVO_USUARIOS) else pd.DataFrame(columns=['usuario', 'senha', 'perfil'])
    if usuario.lower() in df['usuario'].str.lower().values:
        return False
    novo_u = pd.DataFrame([{'usuario': usuario.lower(), 'senha': hash_senha(senha), 'perfil': perfil}])
    novo_u.to_csv(ARQUIVO_USUARIOS, mode='a', header=not os.path.exists(ARQUIVO_USUARIOS), index=False)
    return True

def validar_login(usuario, senha):
    if not os.path.exists(ARQUIVO_USUARIOS): return False
    df = pd.read_csv(ARQUIVO_USUARIOS)
    senha_h = hash_senha(senha)
    user_check = df[(df['usuario'] == usuario.lower()) & (df['senha'] == senha_h)]
    if not user_check.empty:
        return user_check.iloc[0]['perfil']
    return False

@st.cache_data(ttl=60)
def carregar_dados_motores():
    dfs = []
    try:
        df_n = pd.read_csv(LINK_SHEETS, dtype=str)
        if not df_n.empty: dfs.append(df_n)
    except: pass
    if os.path.exists(ARQUIVO_CSV):
        try:
            df_l = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig', dtype=str)
            if not df_l.empty: dfs.append(df_l)
        except: pass
    return pd.concat(dfs, ignore_index=True).drop_duplicates() if dfs else pd.DataFrame()

# --- 3. INTERFACE DE ENTRADA (ESTILIZADA) ---
st.set_page_config(page_title="Pablo União", layout="centered", page_icon="⚙️")

# CSS para melhorar a aparência
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #1e1e1e;
        border-radius: 10px 10px 0px 0px;
        gap: 10px;
        padding: 10px;
    }
    .stTabs [aria-selected="true"] { background-color: #f1c40f !important; color: black !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.markdown("<h1 style='text-align: center; color: #f1c40f;'>🛠️ PABLO UNIÃO</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2em;'>Oficina e Gestão de Motores</p>", unsafe_allow_html=True)
    
    # Abas com Ícones
    tab_login, tab_cadastro = st.tabs(["🔐 ACESSAR SISTEMA", "📝 CRIAR NOVA CONTA"])
    
    with tab_login:
        with st.container(border=True):
            st.markdown("### 🔑 Login")
            u_login = st.text_input("Usuário", placeholder="Digite seu usuário...", key="u_login")
            s_login = st.text_input("Senha", type="password", placeholder="Digite sua senha...", key="s_login")
            if st.button("ENTRAR AGORA 🚀", use_container_width=True):
                perfil = validar_login(u_login, s_login)
                if perfil:
                    st.session_state['autenticado'] = True
                    st.session_state['usuario'] = u_login
                    st.session_state['perfil'] = perfil
                    st.rerun()
                else:
                    st.error("❌ Usuário ou senha incorretos.")
                
    with tab_cadastro:
        with st.container(border=True):
            st.markdown("### 🆕 Cadastro")
            u_novo = st.text_input("Definir Usuário", placeholder="Ex: pablo_motores")
            s_nova = st.text_input("Definir Senha", type="password", placeholder="Mínimo 6 caracteres")
            s_conf = st.text_input("Confirmar Senha", type="password")
            
            if st.button("FINALIZAR CADASTRO ✅", use_container_width=True):
                if s_nova == s_conf and u_novo:
                    if salvar_usuario(u_novo, s_nova):
                        st.success("✅ Conta criada com sucesso! Faça login na aba ao lado.")
                    else:
                        st.error("⚠️ Este usuário já está cadastrado.")
                else:
                    st.warning("⚠️ Verifique se as senhas coincidem.")
    st.stop()

# --- 4. ÁREA LOGADA ---
# (O restante do código segue aqui com o layout wide e as abas de trabalho)
st.sidebar.title("🛠️ PABLO UNIÃO")
st.sidebar.markdown(f"👤 Usuário: **{st.session_state['usuario'].upper()}**")
if st.sidebar.button("Sair"):
    st.session_state['autenticado'] = False
    st.rerun()

t1, t2, t3 = st.tabs(["🔍 CONSULTA TÉCNICA", "➕ CADASTRAR MOTOR", "🧪 SIMULADOR AWG"])

with t1:
    st.subheader("🔍 Busca de Dados e Esquemas")
    # Coloque aqui sua lógica de carregar_dados_motores()
    st.info("Digite os dados do motor para ver o esquema de ligação.")

with t3:
    st.subheader("🧪 Calculadora de Equivalência de Fios")
    # Lógica do simulador AWG
