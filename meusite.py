import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Oficina Pablo - Motores", layout="wide")

st.title("🔌 Painel de Rebobinagem e Motores")
st.markdown("---")

ARQUIVO_CSV = 'meubancodedados.csv' 

if os.path.exists(ARQUIVO_CSV):
    try:
        df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig')
        busca = st.text_input("🔍 Buscar por Marca, Modelo ou CV")
        
        df_filtrado = df[df.astype(str).apply(lambda x: busca.lower() in x.str.lower().any(), axis=1)] if busca else df

        st.write(f"Exibindo **{len(df_filtrado)}** motor(es)")

        for index, row in df_filtrado.iterrows():
            titulo = f"📦 {row.get('Marca', 'S/M')} | {row.get('Motor_CV', 'N/A')} CV | {row.get('Modelo', 'S/M')}"
            with st.expander(titulo):
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown("### 📋 Placa")
                    st.write(f"**RPM:** {row.get('RPM', 'N/A')} | **Polos:** {row.get('Polos', 'N/A')}")
                    st.write(f"**Tensão:** {row.get('Tensao', 'N/A')}")
                    st.write(f"**Amp:** {row.get('Amperagem', 'N/A')}")
                with c2:
                    st.markdown("### 🛠️ Principal")
                    st.write(f"**Passo:** {row.get('Passo_Princ', 'N/A')}")
                    st.write(f"**Espiras:** {row.get('Espiras_Princ', 'N/A')}")
                    st.write(f"**Fio:** {row.get('Fio_Princ', 'N/A')}")
                with c3:
                    st.markdown("### ⚡ Aux/Outros")
                    st.write(f"**Passo Aux:** {row.get('Passo_Aux', 'N/A')}")
                    st.write(f"**Capacitor:** {row.get('Capacitores', 'N/A')}")
                    st.write(f"**Rolam.:** {row.get('Rolamentos', 'N/A')}")
                
                st.caption(f"Texto extraído: {row.get('Texto_Completo', '')[:100]}...")
    except Exception as e:
        st.error(f"Erro: {e}")
else:
    st.warning("Aguardando upload do primeiro motor...")
