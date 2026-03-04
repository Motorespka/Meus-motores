import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
from PIL import Image

# --- CONFIGURAÇÃO DA IA (GEMINI) ---
CHAVE_API = "AIzaSyDM8hUnNRwHz273er2BcqQwTIcPQmKECC0"
genai.configure(api_key=CHAVE_API)
model = genai.GenerativeModel('gemini-1.5-flash')

# Configuração da página para celular
st.set_page_config(page_title="Oficina Pablo - Motores", layout="wide")

st.title("🔌 Consulta de Motores - Oficina Pablo")

# --- NOVIDADE: LEITURA POR FOTO ---
st.markdown("### 📸 Leitura Automática")
foto = st.camera_input("Tire foto da placa do motor")

texto_da_foto = ""
if foto:
    with st.spinner('O Gemini está lendo a placa...'):
        img = Image.open(foto)
        # Instrução para a IA focar no que importa na oficina
        prompt = "Extraia apenas os dados principais desta placa de motor: Marca, CV e RPM. Seja direto."
        response = model.generate_content([prompt, img])
        texto_da_foto = response.text
        st.success(f"Identificado: {texto_da_foto}")

st.markdown("---")

# O nome do arquivo deve ser exatamente o que o seu PC envia
ARQUIVO_CSV = 'meubancodedados.csv' 

if os.path.exists(ARQUIVO_CSV):
    try:
        df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig')
        
        # Se a foto leu algo, o campo de busca já vem preenchido!
        valor_busca = texto_da_foto if texto_da_foto else ""
        busca = st.text_input("🔍 Buscar por Marca, CV ou Fio", value=valor_busca)
        
        if busca:
            # Busca inteligente que ignora maiúsculas/minúsculas
            mask = df.astype(str).apply(lambda x: x.str.contains(busca, case=False, na=False)).any(axis=1)
            df_filtrado = df[mask]
        else:
            df_filtrado = df

        st.write(f"Exibindo **{len(df_filtrado)}** motores encontrados.")

        for index, row in df_filtrado.iterrows():
            titulo = f"📦 {row.get('Marca', 'S/M')} | {row.get('Motor_CV', 'N/A')} CV"
            with st.expander(titulo):
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown("### 📋 Placa")
                    st.write(f"**RPM:** {row.get('RPM', 'N/A')}")
                    st.write(f"**Polos:** {row.get('Polos', 'N/A')}")
                with c2:
                    st.markdown("### 🛠️ Bobina Principal")
                    st.write(f"**Fio:** {row.get('Fio_Princ', 'N/A')}")
                    st.write(f"**Passo:** {row.get('Passo_Princ', 'N/A')}")
                with c3:
                    st.markdown("### ⚡ Bobina Auxiliar")
                    st.write(f"**Fio Aux:** {row.get('Fio_Aux', 'N/A')}")
                    st.write(f"**Capacitor:** {row.get('Capacitores', 'N/A')}")

    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
else:
    st.info("Aguardando o primeiro envio de dados do PC da oficina...")
