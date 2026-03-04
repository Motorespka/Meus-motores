import streamlit as st
import pandas as pd
import os
import hashlib
from PIL import Image

# --- 1. CONFIGURAÇÕES ---
ARQUIVO_USUARIOS = 'usuarios.csv'
ARQUIVO_CSV = 'meubancodedados.csv'
LINK_SHEETS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTFbH81UYKGJ6dQvKotxdv4hDxecLmiGUPHN46iexbw8NeS8_e2XdyZnZ8WJnL2XRTLCbFDbBKo_NGE/pub?output=csv"
CHAVE_MESTRA_CHEFIA = "PABLO2026"

# --- 2. FUNÇÕES DE SEGURANÇA ---
def hash_senha(senha):
    return hashlib.sha256(str.encode(senha)).hexdigest()

def salvar_usuario(usuario, senha, funcoes, perfil):
    # Criar DataFrame se não existir
    if not os.path.exists(ARQUIVO_USUARIOS):
        df = pd.DataFrame(columns=['usuario', 'senha', 'funcoes', 'perfil'])
        df.to_csv(ARQUIVO_USUARIOS, index=False, sep=';')
    
    df = pd.read_csv(ARQUIVO_USUARIOS, sep=';')
    
    if usuario.lower() in df['usuario'].astype(str).str.lower().values:
        return False
    
    # Usamos o separador "|" para as funções para não confundir com a vírgula do CSV
    funcoes_str = "|".join(funcoes) 
    novo_u = pd.DataFrame([{'usuario': usuario.lower(), 'senha': hash_senha(senha), 'funcoes': funcoes_str, 'perfil': perfil}])
    
    novo_u.to_csv(ARQUIVO_USUARIOS, mode='a', header=False, index=False, sep=';')
    return True

def validar_login(usuario, senha):
    if not os.path.exists(ARQUIVO_USUARIOS): 
        return False
    try:
        # Lendo com separador ';' para evitar erro de colunas
        df = pd.read_csv(ARQUIVO_USUARIOS, sep=';')
        senha_h = hash_senha(senha)
        u_check = df[(df['usuario'].astype(str).str.lower() == usuario.lower()) & (df['senha'] == senha_h)]
        
        if not u_check.empty:
            return u_check.iloc[0].to_dict()
    except Exception as e:
        st.error(f"Erro ao ler banco de usuários: {e}")
    return False

# --- 3. INTERFACE DE ENTRADA ---
st.set_page_config(page_title="Pablo União", layout="centered", page_icon="⚙️")

if 'user_data' not in st.session_state:
    st.session_state['user_data'] = None

if not st.session_state['user_data']:
    st.markdown("<h1 style='text-align: center; color: #f1c40f;'>🛠️ PABLO UNIÃO</h1>", unsafe_allow_html=True)
    
    t_login, t_cad = st.tabs(["🔐 ACESSAR", "📝 CADASTRAR-SE"])
    
    with t_login:
        u = st.text_input("Usuário", key="login_u")
        s = st.text_input("Senha", type="password", key="login_s")
        if st.button("ENTRAR 🚀", use_container_width=True):
            dados = validar_login(u, s)
            if dados:
                st.session_state['user_data'] = dados
                st.rerun()
            else:
                st.error("❌ Usuário ou senha incorretos.")

    with t_cad:
        new_u = st.text_input("Novo Usuário")
        new_s = st.text_input("Nova Senha", type="password")
        
        st.markdown("---")
        st.subheader("📋 Suas Funções")
        f_mec = st.checkbox("Mecânica 🔧")
        f_reb = st.checkbox("Rebobinagem ⚡")
        f_che = st.checkbox("Chefia / Admin 👑")
        
        perfil_final = "mecanico"
        chave_validacao = ""
        
        if f_che:
            chave_validacao = st.text_input("Chave de Liberação Chefia", type="password")
        
        if st.button("FINALIZAR CADASTRO ✅", use_container_width=True):
            funcoes_list = []
            if f_mec: funcoes_list.append("mecanica")
            if f_reb: funcoes_list.append("rebobinagem")
            if f_che: funcoes_list.append("chefia")
            
            if not funcoes_list:
                st.warning("Selecione pelo menos uma função.")
            elif f_che and chave_validacao != CHAVE_MESTRA_CHEFIA:
                st.error("Chave de Chefia inválida!")
            elif new_u and new_s:
                if f_che: perfil_final = "admin"
                if salvar_usuario(new_u, new_s, funcoes_list, perfil_final):
                    st.success("✅ Cadastro realizado! Agora vá em 'Acessar'.")
                else:
                    st.error("Este usuário já existe.")
    st.stop()

# --- 4. ÁREA LOGADA ---
user = st.session_state['user_data']
# Convertendo de volta a string das funções para lista
funcoes_usuario = str(user['funcoes']).split("|")

st.sidebar.title("🛠️ PABLO UNIÃO")
st.sidebar.write(f"👤 Olá, **{user['usuario'].upper()}**")
if st.sidebar.button("Sair"):
    st.session_state['user_data'] = None
    st.rerun()

# Montagem das Abas por Permissão
abas_disponiveis = []
if "mecanica" in funcoes_usuario or user['perfil'] == "admin":
    abas_disponiveis.append("🔧 MECÂNICA")
if "rebobinagem" in funcoes_usuario or user['perfil'] == "admin":
    abas_disponiveis.append("⚡ REBOBINAGEM")
if user['perfil'] == "admin":
    abas_disponiveis.append("📊 ADMINISTRAÇÃO")

if abas_disponiveis:
    tabs = st.tabs(abas_disponiveis)
    for i, nome_tab in enumerate(abas_disponiveis):
        with tabs[i]:
            if "MECÂNICA" in nome_tab:
                st.header("Painel de Mecânica")
                st.write("Dados de Rolamentos e Eixos.")
            if "REBOBINAGEM" in nome_tab:
                st.header("Painel de Rebobinagem")
                st.write("Esquemas de Motores e Fios.")
            if "ADMINISTRAÇÃO" in nome_tab:
                st.header("Painel do Pablo")
                st.write("Controle Geral do Sistema.")
else:
    st.warning("Seu usuário não possui funções atribuídas. Fale com o Pablo.")
