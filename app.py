import streamlit as st
import pandas as pd
import os

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Inventário de Motores", layout="centered")

st.title("🔌 Painel de Motores")

# 2. NOME DO ARQUIVO
# Se estiver no PC, use o caminho completo: r'C:\Users\pablo\Desktop\tentativa site motore\meubancodedados.csv'
# Se estiver no GitHub/Nuvem, use apenas: 'meubancodedados.csv'
ARQUIVO_CSV = 'meubancodedados.csv' 

# 3. LÓGICA DO SITE
if os.path.exists(ARQUIVO_CSV):
    # Carrega os dados
    df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig')

    # Campo de busca rápida
    busca = st.text_input("🔍 Buscar Modelo ou Marca")
    
    # Filtra os dados conforme você digita
    if busca:
        mask = df.apply(lambda row: busca.lower() in str(row).lower(), axis=1)
        df_filtrado = df[mask]
    else:
        df_filtrado = df

    st.write(f"Exibindo **{len(df_filtrado)}** motor(es)")

    # Exibe cada motor em um "Card" (melhor para a tela do celular)
    for index, row in df_filtrado.iterrows():
        with st.expander(f"📦 {row['Marca']} - {row['Modelo']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**RPM:** {row['RPM']}")
                st.write(f"**Tensão:** {row['Tensao']}")
            with col2:
                st.write(f"**Amperagem:** {row['Amperagem']}")
            
            st.markdown("---")
            st.caption("Texto extraído da placa:")
            st.text(row['Texto_Completo'])
else:
    st.error(f"Arquivo '{ARQUIVO_CSV}' não encontrado. Verifique se o nome está correto!")
