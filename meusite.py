import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
from PIL import Image

# --- CONFIGURAÇÃO DA IA ---
CHAVE_API = "AIzaSyBcwcsk-wcOGIeHZAuEoGjx4LkNQA5CCF4"
genai.configure(api_key=CHAVE_API)
model = genai.GenerativeModel('gemini-1.5-flash')

# Configuração visual profissional
st.set_page_config(page_title="Oficina Pablo | Rebobinagem Pro", layout="wide")

# Estilização CSS personalizada
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stHeader { background-color: #1e1e1e; color: white; padding: 1rem; border-radius: 10px; }
    .card-motor { background-color: white; padding: 20px; border-left: 5px solid #ff4b4b; border-radius: 5px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    @media (min-width: 1024px) { .camera-off-pc { display: none; } }
    </style>
    """, unsafe_allow_html=True)

# Cabeçalho fixo
with st.container():
    st.markdown('<div class="stHeader"><h1>⚡ Oficina Pablo: Gestão de Rebobinagem</h1></div>', unsafe_allow_html=True)

# --- SISTEMA DE LEITURA (IA) ---
st.subheader("📸 Scan de Placa do Motor")
col_botoes = st.columns([1, 1])

with col_botoes[0]:
    if st.button("🔍 Escanear Placa com Foto"):
        st.session_state.abrir_camera = True

if st.session_state.get('abrir_camera', False):
    st.markdown('<div class="camera-off-pc">', unsafe_allow_html=True)
    foto = st.camera_input("Capture a placa para análise")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if foto:
        with st.spinner('IA analisando especificações...'):
            img = Image.open(foto)
            prompt = "Identifique: Marca, Potência (CV/KW), RPM e Tensão. Responda apenas os valores separados por vírgula."
            response = model.generate_content([prompt, img])
            st.session_state.resultado_ia = response.text
            st.session_state.abrir_camera = False # Fecha a câmera após ler

# Cabeçalho de Informações da IA (Aparece após o scan)
if st.session_state.get('resultado_ia'):
    st.info(f"📋 **Dados Detectados pela IA:** {st.session_state.resultado_ia}")

st.markdown("---")

# --- BANCO DE DADOS E BUSCA ---
ARQUIVO_CSV = 'meubancodedados.csv'

if os.path.exists(ARQUIVO_CSV):
    df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig')
    
    # Busca integrada com a IA
    sugestao = st.session_state.get('resultado_ia', "")
    busca = st.text_input("🔍 Buscar Motor (Marca, CV ou Carcaça)", value=sugestao)
    
    if busca:
        mask = df.astype(str).apply(lambda x: x.str.contains(busca, case=False, na=False)).any(axis=1)
        df_filtrado = df[mask]
    else:
        df_filtrado = df

    # Exibição Profissional dos Resultados
    for index, row in df_filtrado.iterrows():
        with st.container():
            st.markdown(f"""
            <div class="card-motor">
                <h3>📦 {row.get('Marca', 'GENÉRICO')} - {row.get('Motor_CV', 'N/A')} CV</h3>
            </div>
            """, unsafe_allow_html=True)
            
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown("**🔧 MECÂNICA**")
                st.write(f"RPM: {row.get('RPM', 'N/A')}")
                st.write(f"Polos: {row.get('Polos', 'N/A')}")
            with c2:
                st.markdown("**🧵 BOBINAGEM**")
                st.write(f"Fio: {row.get('Fio_Princ', 'N/A')}")
                st.write(f"Passo: {row.get('Passo_Princ', 'N/A')}")
            with c3:
                st.markdown("**⚡ ELÉTRICA**")
                st.write(f"Capacitor: {row.get('Capacitores', 'N/A')}")
                st.write(f"Fio Aux: {row.get('Fio_Aux', 'N/A')}")
            with c4:
                st.markdown("**🖼️ ESQUEMAS**")
                # Botões para ver as ligações
                polos = str(row.get('Polos', ''))
                if st.button(f"Ver Ligação {polos}P", key=f"btn_{index}"):
                    st.warning(f"Aqui abrirá a imagem da ligação de {polos} polos em breve.")
            st.markdown("<br>", unsafe_allow_html=True)

else:
    st.warning("Aguardando base de dados CSV...")
