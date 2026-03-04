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

# --- 2. FUNÇÕES DE SEGURANÇA E DADOS ---
def hash_senha(senha):
    return hashlib.sha256(str.encode(senha)).hexdigest()

def salvar_usuario(usuario, senha, perfil="mecanico"):
    df = pd.read_csv(ARQUIVO_USUARIOS) if os.path.exists(ARQUIVO_USUARIOS) else pd.DataFrame(columns=['usuario', 'senha', 'perfil'])
    if usuario in df['usuario'].values:
        return False
    novo_u = pd.DataFrame([{'usuario': usuario, 'senha': hash_senha(senha), 'perfil': perfil}])
    novo_u.to_csv(ARQUIVO_USUARIOS, mode='a', header=not os.path.exists(ARQUIVO_USUARIOS), index=False)
    return True

def validar_login(usuario, senha):
    if not os.path.exists(ARQUIVO_USUARIOS): return False
    df = pd.read_csv(ARQUIVO_USUARIOS)
    senha_h = hash_senha(senha)
    user_check = df[(df['usuario'] == usuario) & (df['senha'] == senha_h)]
    
    if not user_check.empty:
        return user_check.iloc[0]['perfil']  # Retorna o perfil se encontrar o usuário
    return False                             # Retorna Falso se não encontrar

# --- 3. INTERFACE DE ENTRADA (PABLO UNIÃO) ---
st.set_page_config(page_title="Pablo União", layout="centered")

if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.markdown("<h1 style='text-align: center; color: #f1c40f;'>🛠️ PABLO UNIÃO</h1>", unsafe_allow_html=True)
    
    aba_login, aba_cadastro = st.tabs(["Entrar", "Criar Conta"])
    
    with aba_login:
        u_login = st.text_input("Usuário", key="u_login")
        s_login = st.text_input("Senha", type="password", key="s_login")
        if st.button("Acessar Sistema", use_container_width=True):
            perfil = validar_login(u_login, s_login)
            if perfil:
                st.session_state['autenticado'] = True
                st.session_state['usuario'] = u_login
                st.session_state['perfil'] = perfil
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos.")
                
    with aba_cadastro:
        u_novo = st.text_input("Novo Usuário")
        s_nova = st.text_input("Nova Senha", type="password")
        if st.button("Cadastrar", use_container_width=True):
            if salvar_usuario(u_novo, s_nova):
                st.success("Cadastro realizado! Vá para a aba 'Entrar'.")
            else:
                st.error("Usuário já existe.")
    st.stop()

# --- 4. ÁREA DO SISTEMA (APÓS LOGIN) ---
st.sidebar.title("PABLO UNIÃO")
st.sidebar.write(f"Bem-vindo, **{st.session_state['usuario']}**")
if st.sidebar.button("Sair"):
    st.session_state['autenticado'] = False
    st.rerun()

st.success("Você está logado no sistema Pablo União!")
# Aqui você pode continuar com as abas de Consulta, Cadastro de Motores e Simulador.
