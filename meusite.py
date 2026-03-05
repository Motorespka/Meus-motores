import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime

# ---------------- CONFIG ----------------

ARQUIVO_MOTORES = "motores.csv"
ARQUIVO_FOTOS = "fotos_ligacoes.csv"
ARQUIVO_CLIENTES = "clientes.csv"
ARQUIVO_OS = "ordens_servico.csv"

PASTA_UPLOADS = "uploads"

TOKEN_PRO = "PABLO123"
TOKEN_MESTRE = "MESTRE99"

if not os.path.exists(PASTA_UPLOADS):
    os.makedirs(PASTA_UPLOADS)

# ---------------- FUNÇÕES ----------------

def carregar(arq, colunas):
    if not os.path.exists(arq):
        return pd.DataFrame(columns=colunas)
    df = pd.read_csv(arq, sep=";", dtype=str).fillna("")
    for c in colunas:
        if c not in df.columns:
            df[c] = ""
    return df

def salvar(df, arq):
    df.to_csv(arq, index=False, sep=";")

# ---------------- COLUNAS ----------------

COL_MOTORES = [
    "Marca","Potencia","Voltagem",
    "Fio_P","Espiras_P","Passo_P",
    "Rolamentos","Selo","Ligacao","status"
]

COL_FOTOS = [
    "nome_ligacao",
    "caminho"
]

COL_CLIENTES = [
    "nome",
    "telefone",
    "cidade",
    "email",
    "data"
]

COL_OS = [
    "numero",
    "cliente",
    "telefone",
    "motor",
    "problema",
    "valor",
    "status",
    "data"
]

# ---------------- CARREGAR ----------------

df_motores = carregar(ARQUIVO_MOTORES, COL_MOTORES)
df_fotos = carregar(ARQUIVO_FOTOS, COL_FOTOS)
df_clientes = carregar(ARQUIVO_CLIENTES, COL_CLIENTES)
df_os = carregar(ARQUIVO_OS, COL_OS)

# ---------------- LOGIN ----------------

if "logado" not in st.session_state:
    st.session_state["logado"] = False
    st.session_state["perfil"] = ""

if not st.session_state["logado"]:

    st.title("Sistema Pablo Motores")

    tipo = st.selectbox(
        "Entrar como",
        ["Cliente","Profissional","Mestre"]
    )

    if tipo == "Cliente":

        if st.button("Entrar"):
            st.session_state["logado"] = True
            st.session_state["perfil"] = "cliente"
            st.rerun()

    else:

        token = st.text_input("Token", type="password")

        if st.button("Entrar"):

            if tipo == "Profissional" and token == TOKEN_PRO:
                st.session_state["logado"] = True
                st.session_state["perfil"] = "pro"
                st.rerun()

            elif tipo == "Mestre" and token == TOKEN_MESTRE:
                st.session_state["logado"] = True
                st.session_state["perfil"] = "mestre"
                st.rerun()

            else:
                st.error("Token incorreto")

    st.stop()

# ---------------- INTERFACE ----------------

st.set_page_config(layout="wide")

with st.sidebar:

    st.title("Menu")

    if st.button("Sair"):
        st.session_state["logado"] = False
        st.rerun()

    menu = st.radio(
        "Opções",
        [
            "Consulta",
            "Novo Motor",
            "Clientes",
            "Ordem de Serviço",
            "Biblioteca",
            "Lixeira"
        ]
    )

# ---------------- CONSULTA ----------------

if menu == "Consulta":

    st.title("Consulta de Motores")

    busca = st.text_input("Buscar")

    df = df_motores[df_motores["status"] != "deletado"]

    if busca:
        df = df[df.apply(
            lambda r: r.astype(str).str.contains(busca,case=False).any(),
            axis=1
        )]

    for i,r in df.iterrows():

        with st.expander(f"{r['Marca']} {r['Potencia']}CV"):

            c1,c2 = st.columns(2)

            with c1:
                st.write("Voltagem:",r["Voltagem"])
                st.write("Rolamentos:",r["Rolamentos"])
                st.write("Selo:",r["Selo"])

            with c2:
                st.write("Fio:",r["Fio_P"])
                st.write("Espiras:",r["Espiras_P"])
                st.write("Passo:",r["Passo_P"])

# ---------------- NOVO MOTOR ----------------

elif menu == "Novo Motor":

    st.title("Cadastrar Motor")

    with st.form("novo_motor"):

        c1,c2 = st.columns(2)

        marca = c1.text_input("Marca")
        pot = c1.text_input("Potência")

        volt = c2.text_input("Voltagem")

        fio = c1.text_input("Fio Principal")
        esp = c1.text_input("Espiras")

        passo = c2.text_input("Passo")

        rol = c1.text_input("Rolamentos")
        selo = c2.text_input("Selo")

        lig = st.text_input("Ligação")

        if st.form_submit_button("Salvar"):

            novo = {
                "Marca":marca,
                "Potencia":pot,
                "Voltagem":volt,
                "Fio_P":fio,
                "Espiras_P":esp,
                "Passo_P":passo,
                "Rolamentos":rol,
                "Selo":selo,
                "Ligacao":lig,
                "status":"ativo"
            }

            df_motores = pd.concat(
                [df_motores,pd.DataFrame([novo])],
                ignore_index=True
            )

            salvar(df_motores,ARQUIVO_MOTORES)

            st.success("Motor salvo")

# ---------------- CLIENTES ----------------

elif menu == "Clientes":

    st.title("Cadastro de Clientes")

    with st.form("cliente"):

        c1,c2 = st.columns(2)

        nome = c1.text_input("Nome")
        telefone = c1.text_input("Telefone")

        cidade = c2.text_input("Cidade")
        email = c2.text_input("Email")

        if st.form_submit_button("Cadastrar"):

            novo = {
                "nome":nome,
                "telefone":telefone,
                "cidade":cidade,
                "email":email,
                "data":datetime.now().strftime("%d/%m/%Y")
            }

            df_clientes = pd.concat(
                [df_clientes,pd.DataFrame([novo])],
                ignore_index=True
            )

            salvar(df_clientes,ARQUIVO_CLIENTES)

            st.success("Cliente cadastrado")

    st.divider()

    st.dataframe(df_clientes)

# ---------------- ORDEM DE SERVIÇO ----------------

elif menu == "Ordem de Serviço":

    st.title("Nova Ordem de Serviço")

    with st.form("os"):

        cliente = st.selectbox(
            "Cliente",
            df_clientes["nome"] if not df_clientes.empty else []
        )

        telefone = st.text_input("Telefone")

        motor = st.text_input("Motor")

        problema = st.text_area("Problema")

        valor = st.text_input("Valor")

        if st.form_submit_button("Abrir OS"):

            numero = str(len(df_os)+1)

            nova = {
                "numero":numero,
                "cliente":cliente,
                "telefone":telefone,
                "motor":motor,
                "problema":problema,
                "valor":valor,
                "status":"aberta",
                "data":datetime.now().strftime("%d/%m/%Y")
            }

            df_os = pd.concat(
                [df_os,pd.DataFrame([nova])],
                ignore_index=True
            )

            salvar(df_os,ARQUIVO_OS)

            st.success("OS criada")

    st.divider()

    st.dataframe(df_os)

# ---------------- BIBLIOTECA ----------------

elif menu == "Biblioteca":

    st.title("Biblioteca de Ligações")

    with st.form("foto"):

        nome = st.text_input("Nome ligação")

        file = st.file_uploader("Imagem")

        if st.form_submit_button("Enviar"):

            if file:

                path = os.path.join(PASTA_UPLOADS,file.name)

                with open(path,"wb") as f:
                    f.write(file.getbuffer())

                novo = {
                    "nome_ligacao":nome,
                    "caminho":path
                }

                df_fotos = pd.concat(
                    [df_fotos,pd.DataFrame([novo])],
                    ignore_index=True
                )

                salvar(df_fotos,ARQUIVO_FOTOS)

                st.success("Imagem salva")

    st.divider()

    for i,r in df_fotos.iterrows():

        st.image(r["caminho"],caption=r["nome_ligacao"])

# ---------------- LIXEIRA ----------------

elif menu == "Lixeira":

    st.title("Motores deletados")

    df = df_motores[df_motores["status"]=="deletado"]

    st.dataframe(df)
