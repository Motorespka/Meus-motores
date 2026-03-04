import streamlit as st
import pandas as pd
import os

# Configuração da página para celular
st.set_page_config(page_title="Oficina Pablo - Motores", layout="wide")

st.title("🔌 Consulta de Motores - Oficina Pablo")
st.markdown("---")

# O nome do arquivo deve ser exatamente o que o seu PC envia
ARQUIVO_CSV = 'meubancodedados.csv' 

if os.path.exists(ARQUIVO_CSV):
    try:
        # Lendo o banco de dados enviado pelo PC
        df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig')
        
        busca = st.text_input("🔍 Buscar por Marca, CV ou Fio")
        
        # Lógica de busca simples
        if busca:
            df_filtrado = df[df.astype(str).apply(lambda x: busca.lower() in x.str.lower().any(), axis=1)]
        else:
            df_filtrado = df

        st.write(f"Exibindo **{len(df_filtrado)}** motores cadastrados.")

        # Exibição dos motores em "cards" expansíveis (ótimos para celular)
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
