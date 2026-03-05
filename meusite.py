# =============================================
# SISTEMA PROFISSIONAL DE REBOBINAGEM DE MOTORES
# Versão: Pablo Motores Pro
# Framework: Streamlit
# =============================================
import streamlit as st
import pandas as pd
import os
import math
from datetime import datetime
# ---------------- CONFIG ----------------
ARQUIVO_MOTORES = "motores.csv"
ARQUIVO_CLIENTES = "clientes.csv"
ARQUIVO_OS = "ordens_servico.csv"
if not os.path.exists(ARQUIVO_MOTORES):
 df = pd.DataFrame(columns=[
 "Marca","Modelo","Potencia_CV","RPM","Voltagem",
 "Corrente","Polos","Ranhuras","Espiras",
 "Bobinas","Fio","Passo","Tipo_Ligacao","status"
 ])
 df.to_csv(ARQUIVO_MOTORES,index=False)
# ---------------- FUNÇÕES ----------------
def carregar_motores():
 df = pd.read_csv(ARQUIVO_MOTORES)
 if "status" not in df.columns:
 df["status"]="ativo"
 return df
def salvar_motores(df):
 df.to_csv(ARQUIVO_MOTORES,index=False)
def calcular_area_fio(diametro):
 return math.pi*(diametro/2)**2
def densidade_corrente(corrente,area):
 if area==0:
 return 0
 return corrente/area
def gerar_bobinagem(ranhuras,polos):
 passo=int(ranhuras/polos)
 esquema=[]
 for i in range(1,ranhuras+1):
 fim=i+passo
 if fim>ranhuras:
 fim-=ranhuras
 esquema.append((i,fim))
 return esquema
# ---------------- UI ----------------
st.set_page_config(page_title="Pablo Motores Pro",layout="wide")
st.title("■ Sistema Profissional de Rebobinagem")
menu=st.sidebar.radio("Menu",[
"Consultar motores",
"Cadastrar motor",
"Gerador de bobinagem",
"Calculadora elétrica"
])
# ---------------- CONSULTA ----------------
if menu=="Consultar motores":
 df=carregar_motores()
 busca=st.text_input("Buscar motor")
 if busca:
 df=df[df.apply(lambda r:r.astype(str).str.contains(busca,case=False).any(),axis=1)]
 df=df[df["status"]!="deletado"]
 for i,row in df.iterrows():
 with st.expander(f"{row['Marca']} {row['Potencia_CV']} CV"):
 c1,c2=st.columns(2)
 with c1:
 st.write("RPM:",row["RPM"])
 st.write("Voltagem:",row["Voltagem"])
 st.write("Corrente:",row["Corrente"])
 with c2:
 st.write("Polos:",row["Polos"])
 st.write("Ranhuras:",row["Ranhuras"])
 st.write("Espiras:",row["Espiras"])
 if st.button("Excluir",key=i):
 df.at[i,"status"]="deletado"
 salvar_motores(df)
 st.experimental_rerun()
# ---------------- CADASTRO ----------------
elif menu=="Cadastrar motor":
 st.header("Cadastro de motor")
 marca=st.text_input("Marca")
 modelo=st.text_input("Modelo")
 potencia=st.text_input("Potência CV")
 rpm=st.text_input("RPM")
 voltagem=st.text_input("Voltagem")
 corrente=st.text_input("Corrente")
 polos=st.number_input("Polos",2,12,4)
 ranhuras=st.number_input("Ranhuras",6,120,24)
 espiras=st.number_input("Espiras",1,500,100)
 fio=st.text_input("Fio")
 if st.button("Salvar motor"):
 df=carregar_motores()
 novo={
 "Marca":marca,
 "Modelo":modelo,
 "Potencia_CV":potencia,
 "RPM":rpm,
 "Voltagem":voltagem,
 "Corrente":corrente,
 "Polos":polos,
 "Ranhuras":ranhuras,
 "Espiras":espiras,
 "Bobinas":ranhuras//2,
 "Fio":fio,
 "Passo":ranhuras//polos,
 "Tipo_Ligacao":"",
 "status":"ativo"
 }
 df=pd.concat([df,pd.DataFrame([novo])],ignore_index=True)
 salvar_motores(df)
 st.success("Motor cadastrado")
# ---------------- GERADOR ----------------
elif menu=="Gerador de bobinagem":
 st.header("Gerador automático")
ranhuras=st.number_input("Ranhuras",6,120,24)
 polos=st.number_input("Polos",2,12,4)
 if st.button("Gerar"):
 esquema=gerar_bobinagem(ranhuras,polos)
 for i,b in enumerate(esquema):
 st.write(f"Bobina {i+1}: {b[0]} - {b[1]}")
# ---------------- CALCULADORA ----------------
elif menu=="Calculadora elétrica":
 st.header("Calculadora técnica")
 corrente=st.number_input("Corrente A",0.0)
 diametro=st.number_input("Diâmetro fio mm",0.0)
 area=calcular_area_fio(diametro)
 dens=densidade_corrente(corrente,area)
 st.write("Área do fio:",area)
 st.write("Densidade de corrente:",dens,"A/mm²")
# =============================================
# FIM DO SISTEMA
# ============================================
