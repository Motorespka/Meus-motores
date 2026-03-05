import streamlit as st
import pandas as pd
import os
import math

st.set_page_config(page_title="Pablo Motores PRO", layout="wide")

# =========================
# ESTILO
# =========================

st.markdown("""
<style>

body{
background-color:#0e1117;
}

h1,h2,h3{
color:#00d4ff;
}

.stButton>button{
background-color:#00d4ff;
color:black;
border-radius:8px;
}

</style>
""", unsafe_allow_html=True)

# =========================
# CONFIG
# =========================

ARQUIVO = "motores.csv"

TOKEN_PRO = "PABLO123"
TOKEN_MESTRE = "MESTRE99"

# =========================
# CRIAR BANCO
# =========================

if not os.path.exists(ARQUIVO):

    df = pd.DataFrame([{
        "Marca":"WEG",
        "Potencia":"5",
        "RPM":"1750",
        "Voltagem":"220/380",
        "Corrente":"14",
        "Polos":"4",
        "Ranhuras":"36",
        "Espiras":"45",
        "Bobinas":"12",
        "Fio":"1.2",
        "status":"ativo"
    }])

    df.to_csv(ARQUIVO,index=False)

df = pd.read_csv(ARQUIVO)

# =========================
# FUNÇÕES
# =========================

def salvar():

    df.to_csv(ARQUIVO,index=False)

def espiras_por_polo(e,p):

    if p==0:
        return 0

    return e/p

def bobinas_por_fase(b):

    return b/3

def ranhuras_por_polo_fase(r,p):

    if p==0:
        return 0

    return r/(p*3)

def peso_cobre(fio,espiras):

    area = math.pi*(fio/2)**2

    comprimento = espiras*0.15

    volume = area*comprimento

    densidade = 8.96

    return volume*densidade

def sugerir_fio(c):

    if c<=5:
        return 0.8
    if c<=10:
        return 1.0
    if c<=20:
        return 1.3
    if c<=30:
        return 1.6
    return 2.0

def gerar_bobinagem(ranhuras,polos):

    lista=[]

    passo=int(ranhuras/polos)

    for i in range(1,ranhuras+1):

        fim=i+passo

        if fim>ranhuras:
            fim=fim-ranhuras

        lista.append((i,fim))

    return lista

# =========================
# LOGIN
# =========================

if "login" not in st.session_state:

    st.title("Sistema Pablo Motores")

    tipo=st.selectbox("Entrar como",["Cliente","Profissional","Mestre"])

    if tipo=="Cliente":

        if st.button("Entrar"):

            st.session_state.login="cliente"

            st.rerun()

    else:

        senha=st.text_input("Token",type="password")

        if st.button("Entrar"):

            if tipo=="Profissional" and senha==TOKEN_PRO:

                st.session_state.login="pro"

                st.rerun()

            elif tipo=="Mestre" and senha==TOKEN_MESTRE:

                st.session_state.login="mestre"

                st.rerun()

            else:

                st.error("Token errado")

    st.stop()

perfil=st.session_state.login

# =========================
# MENU
# =========================

menu=["Consulta","Gerador Bobinagem","Dashboard"]

if perfil in ["pro","mestre"]:

    menu.append("Cadastrar Motor")

if perfil=="mestre":

    menu.append("Lixeira")

op=st.sidebar.radio("Menu",menu)

# =========================
# CONSULTA
# =========================

if op=="Consulta":

    busca=st.text_input("Buscar motor")

    df2=df[df["status"]!="deletado"]

    if busca:

        df2=df2[df2.apply(lambda r:r.astype(str).str.contains(busca,case=False).any(),axis=1)]

    for i,row in df2.iterrows():

        with st.expander(f"{row['Marca']} {row['Potencia']}CV"):

            c1,c2=st.columns(2)

            with c1:

                st.write("Voltagem:",row["Voltagem"])
                st.write("RPM:",row["RPM"])
                st.write("Corrente:",row["Corrente"])

            with c2:

                st.write("Polos:",row["Polos"])
                st.write("Ranhuras:",row["Ranhuras"])

            st.subheader("Cálculos")

            epp=espiras_por_polo(int(row["Espiras"]),int(row["Polos"]))
            bpf=bobinas_por_fase(int(row["Bobinas"]))
            q=ranhuras_por_polo_fase(int(row["Ranhuras"]),int(row["Polos"]))

            st.write("Espiras por polo:",round(epp,2))
            st.write("Bobinas por fase:",round(bpf,2))
            st.write("Ranhuras por polo por fase:",round(q,2))

            fio=float(row["Fio"])

            peso=peso_cobre(fio,int(row["Espiras"]))

            st.write("Peso estimado cobre:",round(peso,2),"g")

            corrente=float(row["Corrente"])

            st.write("Fio sugerido:",sugerir_fio(corrente),"mm")

            if perfil=="mestre":

                st.subheader("Editar")

                novo_fio=st.text_input("Fio",row["Fio"],key=i)

                if st.button("Salvar",key="s"+str(i)):

                    df.at[i,"Fio"]=novo_fio

                    salvar()

                    st.rerun()

                if st.button("Excluir",key="d"+str(i)):

                    df.at[i,"status"]="deletado"

                    salvar()

                    st.rerun()

# =========================
# CADASTRAR
# =========================

if op=="Cadastrar Motor":

    st.title("Cadastrar Motor")

    marca=st.text_input("Marca")

    pot=st.text_input("Potencia CV")

    rpm=st.text_input("RPM")

    vol=st.text_input("Voltagem")

    cor=st.text_input("Corrente")

    polos=st.text_input("Polos")

    ran=st.text_input("Ranhuras")

    esp=st.text_input("Espiras")

    bob=st.text_input("Bobinas")

    fio=st.text_input("Fio")

    if st.button("Salvar"):

        novo=pd.DataFrame([{

        "Marca":marca,
        "Potencia":pot,
        "RPM":rpm,
        "Voltagem":vol,
        "Corrente":cor,
        "Polos":polos,
        "Ranhuras":ran,
        "Espiras":esp,
        "Bobinas":bob,
        "Fio":fio,
        "status":"ativo"

        }])

        df=pd.concat([df,novo])

        salvar()

        st.success("Motor salvo")

# =========================
# GERADOR
# =========================

if op=="Gerador Bobinagem":

    st.title("Gerador de Bobinagem")

    r=st.number_input("Ranhuras",6,120,24)

    p=st.number_input("Polos",2,12,4)

    if st.button("Gerar"):

        lista=gerar_bobinagem(r,p)

        for i,b in enumerate(lista):

            st.write(f"Bobina {i+1} → {b[0]} - {b[1]}")

# =========================
# DASHBOARD
# =========================

if op=="Dashboard":

    st.title("Dashboard")

    st.metric("Motores cadastrados",len(df[df["status"]!="deletado"]))

    st.bar_chart(df["Polos"].value_counts())

# =========================
# LIXEIRA
# =========================

if op=="Lixeira":

    lixo=df[df["status"]=="deletado"]

    for i,row in lixo.iterrows():

        st.write(row["Marca"],row["Potencia"])

        if st.button("Restaurar",key=i):

            df.at[i,"status"]="ativo"

            salvar()

            st.rerun()
