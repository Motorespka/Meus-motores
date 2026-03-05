import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime
from core.database import carregar_dados, salvar_dados
from modules.calculos import calcular_area_mm2
from modules.funcionarios import autenticar_usuario
from modules.grupos import criar_grupo, entrar_grupo
from modules.vendas import criar_pedido, listar_fornecedores

# --- CONFIGURAÇÕES ---
ARQUIVO_CSV = 'data/meubancodedados.csv'
ARQUIVO_FOTOS = 'data/biblioteca_fotos.csv'
PASTA_UPLOADS = 'uploads_ligacoes'

# Cria pastas se não existirem
for pasta in [PASTA_UPLOADS, 'data']:
    if not os.path.exists(pasta):
        os.makedirs(pasta)

# Inicializa sessão
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False
if 'perfil' not in st.session_state:
    st.session_state['perfil'] = None

# --- TELA DE LOGIN ---
if not st.session_state['autenticado']:
    st.set_page_config(page_title="⚙ Sistema Profissional Rebobineiros", layout="wide")
    st.markdown("## ⚙ Sistema Profissional para Rebobinagem e Mecânica")
    st.markdown("Bem-vindo! Escolha seu perfil e entre no sistema.")
    tipo = st.selectbox("Entrar como:", ["Cliente", "Profissional", "Mestre"])
    if tipo == "Cliente":
        if st.button("Entrar"):
            st.session_state['autenticado'] = True
            st.session_state['perfil'] = 'cliente'
            st.experimental_rerun()
    else:
        tk = st.text_input("Token:", type="password")
        if st.button("Entrar"):
            perfil = autenticar_usuario(tipo, tk)
            if perfil:
                st.session_state['autenticado'] = True
                st.session_state['perfil'] = perfil
                st.experimental_rerun()
            else:
                st.error("Token incorreto")
    st.stop()

# --- APP LOGADO ---
st.set_page_config(page_title="Pablo Motores Pro", layout="wide")
st.sidebar.title(f"Acesso: {st.session_state['perfil'].upper()}")
if st.sidebar.button("🚪 Sair"):
    st.session_state['autenticado'] = False
    st.experimental_rerun()

# Menu principal
opcoes = ["🔍 CONSULTA"]
if st.session_state['perfil'] in ['pro', 'mestre']:
    opcoes += ["➕ NOVO MOTOR", "🔧 FUNCIONÁRIOS"]
if st.session_state['perfil'] == 'mestre':
    opcoes += ["🖼️ BIBLIOTECA", "📊 PAINEL DE OS", "🗑️ LIXEIRA", "👥 GRUPOS", "💰 VENDAS"]

menu = st.sidebar.radio("Menu", opcoes)

# --- CONSULTA ---
if menu == "🔍 CONSULTA":
    st.header("🔍 Consulta de Motores")
    df_motores = carregar_dados(ARQUIVO_CSV, [])
    busca = st.text_input("Filtrar motor...")
    df_f = df_motores[df_motores['status'] != 'deletado']
    if busca:
        df_f = df_f[df_f.apply(lambda r: r.astype(str).str.contains(busca, case=False).any(), axis=1)]
    for idx, row in df_f.iterrows():
        with st.expander(f"📦 {row.get('Marca', '')} | {row.get('Potencia_CV', '')} CV"):
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**Voltagem:** {row.get('Voltagem', '')}")
                st.write(f"**Amperagem:** {row.get('Amperagem', '')}")
                st.write(f"**Rolamentos:** {row.get('Rolamentos', '')}")
                st.write(f"**Selo Mecânico:** {row.get('Selo_Mecanico', '')}")
            with c2:
                st.write(f"**Fio Principal:** {row.get('Fio_Principal', '')} | Espiras: {row.get('Bobina_Principal', '')}")
                st.write(f"**Passo P:** {row.get('Passo_P', '')}")
                st.write(f"**Ligação:** {row.get('Tipo_Ligacao', '')}")
                st.write(f"**Obs:** {row.get('Obs', '')}")

# --- NOVO MOTOR ---
elif menu == "➕ NOVO MOTOR":
    st.header("➕ Cadastrar Motor")
    with st.form("novo_motor"):
        marca = st.text_input("Marca")
        cv = st.text_input("CV")
        voltagem = st.text_input("Voltagem")
        fio_p = st.text_input("Fio Principal")
        espiras_p = st.text_input("Espiras Principal")
        passo_p = st.text_input("Passo P")
        rolamentos = st.text_input("Rolamentos")
        selo = st.text_input("Selo Mecânico")
        tipo_ligacao = st.text_input("Tipo Ligação")
        if st.form_submit_button("Salvar"):
            novo = {
                "Marca": marca, "Potencia_CV": cv, "Voltagem": voltagem,
                "Fio_Principal": fio_p, "Bobina_Principal": espiras_p, "Passo_P": passo_p,
                "Rolamentos": rolamentos, "Selo_Mecanico": selo, "Tipo_Ligacao": tipo_ligacao,
                "status": "ativo", "Obs": ""
            }
            df_motores = carregar_dados(ARQUIVO_CSV, [])
            df_motores = pd.concat([df_motores, pd.DataFrame([novo])], ignore_index=True)
            salvar_dados(df_motores, ARQUIVO_CSV)
            st.success("Motor salvo!")

# --- FUNCIONÁRIOS ---
elif menu == "🔧 FUNCIONÁRIOS":
    st.header("🔧 Funcionários")
    st.write("Gerencie rebobinadores, mecânicos e tornearia aqui.")
    # Exemplo: listar, adicionar e editar funcionários

# --- BIBLIOTECA ---
elif menu == "🖼️ BIBLIOTECA":
    st.header("🖼️ Biblioteca de Fotos")
    df_fotos = carregar_dados(ARQUIVO_FOTOS, [])
    st.write(df_fotos)

# --- GRUPOS ---
elif menu == "👥 GRUPOS":
    st.header("👥 Grupos de Trabalho")
    if st.button("Criar Grupo"):
        criar_grupo()
    entrar_grupo()

# --- VENDAS ---
elif menu == "💰 VENDAS":
    st.header("💰 Vendas e Fornecedores")
    criar_pedido()
    listar_fornecedores()

# --- LIXEIRA ---
elif menu == "🗑️ LIXEIRA":
    st.header("🗑️ Motores Deletados")
    df_motores = carregar_dados(ARQUIVO_CSV, [])
    deletados = df_motores[df_motores['status'] == 'deletado']
    for i, r in deletados.iterrows():
        st.write(f"{r.get('Marca', '')} | {r.get('Potencia_CV', '')} CV")
