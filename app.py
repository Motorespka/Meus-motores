import streamlit as st
import pandas as pd
import os

# --- Configuração da página ---
st.set_page_config(
    page_title="Pablo Motores Pro",
    page_icon="⚙️",
    layout="wide"
)

# --- Arquivo CSV ---
ARQUIVO_CSV = 'meubancodedados.csv'

# --- Menu lateral ---
menu = ["Dashboard", "Rebobinagem", "Mecânica", "Tornearia", "Estoque", "OS", "Fornecedores"]
escolha = st.sidebar.radio("Menu", menu)

# --- Dashboard (Página inicial) ---
if escolha == "Dashboard":
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

# --- Rebobinagem / mecânica / tornearia ---
elif escolha in ["Rebobinagem", "Mecânica", "Tornearia"]:
    st.subheader(f"🔧 {escolha}")
    st.write(f"Tela de cadastro e edição de motores / serviços de {escolha.lower()}.")
    
    # --- Carregar CSV ---
    if os.path.exists(ARQUIVO_CSV):
        df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig')
        busca = st.text_input("🔍 Buscar Modelo ou Marca")
        if busca:
            mask = df.apply(lambda row: busca.lower() in str(row).lower(), axis=1)
            df_filtrado = df[mask]
        else:
            df_filtrado = df

        st.write(f"Exibindo **{len(df_filtrado)}** motor(es)")

        for index, row in df_filtrado.iterrows():
            with st.expander(f"📦 {row['Marca']} - {row['Modelo']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**RPM:** {row.get('RPM','')}")
                    st.write(f"**Tensão:** {row.get('Tensao','')}")
                with col2:
                    st.write(f"**Amperagem:** {row.get('Amperagem','')}")
                st.markdown("---")
                st.caption("Texto extraído da placa:")
                st.text(row.get('Texto_Completo',''))
    else:
        st.error(f"Arquivo '{ARQUIVO_CSV}' não encontrado. Verifique se está na raiz do repositório.")

# --- Estoque ---
elif escolha == "Estoque":
    st.subheader("📦 Estoque")
    st.write("Controle de itens, baixas e fornecedores. (Placeholder)")

# --- Ordens de Serviço ---
elif escolha == "OS":
    st.subheader("🧾 Ordens de Serviço")
    st.write("Criação, alteração e envio de ordens de serviço. (Placeholder)")

# --- Fornecedores ---
elif escolha == "Fornecedores":
    st.subheader("🛒 Fornecedores")
    st.write("Cadastro de fornecedores, itens, preços e entregas. (Placeholder)")
