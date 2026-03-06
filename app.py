# app.py
import streamlit as st
import os

# Configuração da página
st.set_page_config(
    page_title="Pablo Motores Pro",
    page_icon="⚙️",
    layout="wide"
)

# --- Sessão de login simples (exemplo) ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False
    st.session_state['perfil'] = None

# --- TELA DE LOGIN ---
if not st.session_state['autenticado']:
    st.title("⚙️ Sistema Pablo Motores")
    tipo = st.selectbox("Entrar como:", ["Cliente", "Profissional", "Mestre"])
    token_input = ""
    if tipo != "Cliente":
        token_input = st.text_input("Token:", type="password")

    if st.button("Entrar"):
        if tipo == "Cliente":
            st.session_state['autenticado'] = True
            st.session_state['perfil'] = 'cliente'
            st.experimental_rerun()
        elif tipo == "Profissional" and token_input == "PABLO123":
            st.session_state['autenticado'] = True
            st.session_state['perfil'] = 'pro'
            st.experimental_rerun()
        elif tipo == "Mestre" and token_input == "MESTRE99":
            st.session_state['autenticado'] = True
            st.session_state['perfil'] = 'mestre'
            st.experimental_rerun()
        else:
            st.error("Token incorreto")
    st.stop()  # Para não mostrar nada abaixo se não logado

# --- INTERFACE PRINCIPAL ---
st.title("⚙️ Pablo Motores PRO")
st.markdown("""
Sistema profissional para:

🔧 Rebobinadores  
🔩 Mecânicos  
⚙️ Tornearia  
📦 Controle de estoque  
🧾 Ordem de serviço  
🛒 Fornecedores
""")
st.info("Use o menu lateral para navegar pelo sistema.")

# --- MENU LATERAL ---
menu = ["Dashboard", "Rebobinagem", "Mecânica", "Tornearia", "Estoque", "OS", "Fornecedores"]
escolha = st.sidebar.radio(f"Acesso: {st.session_state['perfil'].upper()}", menu)

# --- ABAS SIMPLES ---
if escolha == "Dashboard":
    st.subheader("📊 Dashboard geral")
    st.write("Resumo do sistema (indicadores, notificações, alertas).")

elif escolha == "Rebobinagem":
    st.subheader("🔧 Rebobinagem")
    st.write("Tela de cadastro e edição de motores para rebobinadores.")

elif escolha == "Mecânica":
    st.subheader("🔩 Mecânica")
    st.write("Tela de cadastro de peças, manutenção e serviços de mecânica.")

elif escolha == "Tornearia":
    st.subheader("⚙️ Tornearia")
    st.write("Cadastro e controle de serviços de tornearia.")

elif escolha == "Estoque":
    st.subheader("📦 Estoque")
    st.write("Controle de itens, baixas e fornecedores.")

elif escolha == "OS":
    st.subheader("🧾 Ordens de Serviço")
    st.write("Criação, alteração e envio de ordens de serviço.")

elif escolha == "Fornecedores":
    st.subheader("🛒 Fornecedores")
    st.write("Cadastro de fornecedores, itens, preços e entregas.")

# Rodando isso como app.py já funciona no Streamlit Cloud
