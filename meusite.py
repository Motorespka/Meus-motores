import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
from PIL import Image

# --- CONFIGURAÇÃO DA IA ---
CHAVE_API = "AIzaSyBcwcsk-wcOGIeHZAuEoGjx4LkNQA5CCF4"
genai.configure(api_key=CHAVE_API)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Pablo Motores | Engenharia de Rebobinagem", layout="wide")

# --- ESTILO PROFISSIONAL (CSS) ---
st.markdown("""
    <style>
    /* Estilo do Fundo e Container */
    .stApp { background-color: #121212; color: #e0e0e0; }
    
    /* Header Profissional */
    .main-header {
        background: linear-gradient(90deg, #1e1e1e 0%, #333333 100%);
        padding: 2rem;
        border-radius: 15px;
        border-bottom: 4px solid #f1c40f;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    /* Card de Motor */
    .motor-card {
        background-color: #ffffff;
        color: #121212;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 8px solid #f1c40f;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    /* Botões Customizados */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        text-transform: uppercase;
        transition: 0.3s;
    }
    
    /* Esconder câmera no PC */
    @media (min-width: 1024px) { .camera-off-pc { display: none; } }
    </style>
    """, unsafe_allow_html=True)

# --- CABEÇALHO ---
st.markdown("""
    <div class="main-header">
        <h1 style='margin:0; color:#f1c40f;'>PABLO MOTORES</h1>
        <p style='margin:0; color:#bbb;'>Engenharia e Rebobinagem Técnica</p>
    </div>
    """, unsafe_allow_html=True)

# --- ABAS NAVEGACIONAIS ---
tab1, tab2 = st.tabs(["🔍 CONSULTA TÉCNICA", "📚 ESQUEMAS DE LIGAÇÃO"])

with tab1:
    st.markdown("### 🛠️ Localizar Motor")
    
    # Seção de IA
    with st.expander("📸 Escanear Placa com Inteligência Artificial"):
        st.markdown('<div class="camera-off-pc">', unsafe_allow_html=True)
        foto = st.camera_input("Focar na placa do motor")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if foto:
            with st.spinner('Decodificando especificações técnicas...'):
                img = Image.open(foto)
                prompt = "Identifique Marca, Potência CV, RPM. Retorne apenas o valor principal para busca."
                response = model.generate_content([prompt, img])
                st.session_state.busca_ia = response.text
                st.success(f"Busca sugerida: {st.session_state.busca_ia}")

    # Campo de busca principal
    busca_val = st.session_state.get('busca_ia', "")
    termo_busca = st.text_input("Digite Marca, Potência ou Detalhe do Cálculo", value=busca_val)

    # Lógica do Banco de Dados
    ARQUIVO_CSV = 'meubancodedados.csv'
    if os.path.exists(ARQUIVO_CSV):
        df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig')
        
        if termo_busca:
            mask = df.astype(str).apply(lambda x: x.str.contains(termo_busca, case=False, na=False)).any(axis=1)
            df_filtrado = df[mask]
        else:
            df_filtrado = df

        st.write(f"Resultados encontrados: **{len(df_filtrado)}**")

        for index, row in df_filtrado.iterrows():
            with st.container():
                # Design do Card Profissional
                st.markdown(f"""
                <div class="motor-card">
                    <h2 style='margin-top:0; color:#2c3e50;'>{row.get('Marca', 'MOTOR')} | {row.get('Motor_CV', '-')} CV</h2>
                    <hr style='margin: 10px 0;'>
                    <div style='display: flex; justify-content: space-between; flex-wrap: wrap;'>
                        <div style='flex: 1; min-width: 150px;'>
                            <p><b>⚙️ Mecânica:</b> {row.get('RPM', '-')} RPM | {row.get('Polos', '-')} Polos</p>
                            <p><b>🧵 Bobina:</b> Fio {row.get('Fio_Princ', '-')} | Passo {row.get('Passo_Princ', '-')}</p>
                        </div>
                        <div style='flex: 1; min-width: 150px;'>
                            <p><b>⚡ Elétrica:</b> {row.get('Capacitores', '-')} Cap.</p>
                            <p><b>📐 Auxiliar:</b> Fio {row.get('Fio_Aux', '-')}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("🖼️ VER LIGAÇÃO", key=f"lig_{index}"):
                    st.info(f"Carregando esquema técnico para {row.get('Polos', '-')} polos...")
                    # Aqui você pode usar st.image("caminho/da/foto.jpg")
                st.markdown("---")
    else:
        st.error("Banco de dados não encontrado. Verifique o arquivo CSV.")

with tab2:
    st.header("📖 Biblioteca de Esquemas")
    st.write("Selecione o tipo de ligação para visualizar o diagrama:")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⚡ Ligação 2 Polos"): st.image("https://via.placeholder.com/400x300.png?text=Esquema+2+Polos")
        if st.button("⚡ Ligação 4 Polos"): st.image("https://via.placeholder.com/400x300.png?text=Esquema+4+Polos")
    with col2:
        if st.button("⚡ Ligação 6 Polos"): st.image("https://via.placeholder.com/400x300.png?text=Esquema+6+Polos")
        if st.button("⚡ Ligação 8 Polos"): st.image("https://via.placeholder.com/400x300.png?text=Esquema+8+Polos")

# --- RODAPÉ ---
st.markdown("<p style='text-align: center; color: #555;'>Pablo Motores © 2024 | Sistema de Rebobinagem Inteligente</p>", unsafe_allow_html=True)
