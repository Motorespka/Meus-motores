import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
from PIL import Image
from datetime import datetime

# --- CONFIGURAÇÃO DA IA ---
# Nota: Recomendo usar st.secrets para chaves de API em produção
CHAVE_API = "AIzaSyBcwcsk-wcOGIeHZAuEoGjx4LkNQA5CCF4"
genai.configure(api_key=CHAVE_API)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Pablo Motores | Gestão Pro", layout="wide")

# --- ESTILO CSS PROFISSIONAL ---
st.markdown("""
    <style>
    .stApp { background-color: #121212; color: #e0e0e0; }
    .main-header {
        background: linear-gradient(90deg, #1e1e1e 0%, #333333 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-bottom: 4px solid #f1c40f;
        margin-bottom: 2rem;
        text-align: center;
    }
    .motor-card {
        background-color: #ffffff;
        color: #121212;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 8px solid #f1c40f;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e1e1e;
        border-radius: 5px;
        color: white;
        padding: 10px 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1 style="color:#f1c40f; margin:0;">PABLO MOTORES</h1><p style="margin:0; color:#bbb;">Engenharia de Rebobinagem e Dados Técnicos</p></div>', unsafe_allow_html=True)

# --- ARQUIVO E PASTAS ---
ARQUIVO_CSV = 'meubancodedados.csv'
PASTA_ESQUEMAS = 'esquemas_fotos'
if not os.path.exists(PASTA_ESQUEMAS):
    os.makedirs(PASTA_ESQUEMAS)

# --- NAVEGAÇÃO POR ABAS ---
tab1, tab2, tab3 = st.tabs(["🔍 CONSULTA RÁPIDA", "➕ ADICIONAR MOTOR", "📚 ESQUEMA DE LIGAÇÃO"])

# --- ABA 1: CONSULTA ---
with tab1:
    busca = st.text_input("Buscar por Marca, CV ou Modelo...")
    
    if os.path.exists(ARQUIVO_CSV):
        df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig')
        if busca:
            df_filtrado = df[df.astype(str).apply(lambda x: busca.lower() in x.str.lower().any(), axis=1)]
        else:
            df_filtrado = df

        for _, row in df_filtrado.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="motor-card">
                    <h3 style="margin:0;">{row.get('Marca', 'MOTOR')} | {row.get('Potencia_CV', '-')} CV</h3>
                    <p style="color:#444;"><b>RPM:</b> {row.get('RPM', '-')} | <b>Polaridade:</b> {row.get('Polaridade', '-')} | <b>Volt:</b> {row.get('Voltagem', '-')}</p>
                    <hr>
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 15px; font-size: 0.9rem;">
                        <div>
                            <p><b>🧵 Princ:</b> {row.get('Bobina_Principal', '-')} | <b>Fio:</b> {row.get('Fio_Principal', '-')}</p>
                            <p><b>⚡ Aux:</b> {row.get('Bobina_Auxiliar', '-')} | <b>Fio:</b> {row.get('Fio_Auxiliar', '-')}</p>
                            <p><b>📏 Eixo X:</b> {row.get('Eixo_X', '-')} | <b>Eixo Y:</b> {row.get('Eixo_Y', '-')}</p>
                        </div>
                        <div>
                            <p><b>🔋 Capacitor:</b> {row.get('Capacitor', '-')}</p>
                            <p><b>⚙️ Rolamentos:</b> {row.get('Rolamentos', '-')}</p>
                            <p><b>📉 Amperagem:</b> {row.get('Amperagem', '-')}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# --- ABA 2: ADICIONAR NOVO CÁLCULO ---
with tab2:
    st.subheader("📝 Cadastro Técnico de Rebobinagem")
    
    with st.form("form_cadastro", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            marca = st.text_input("Marca do Motor")
            potencia = st.text_input("Potência (CV)")
            rpm = st.text_input("RPM")
            polaridade = st.selectbox("Polaridade (Polos)", ["2", "4", "6", "8", "12"])
            amperagem = st.text_input("Amperagem (A)")
            voltagem = st.text_input("Voltagem (V)")

        with col2:
            b_princ = st.text_input("Bobina Principal (Espiras/Passo)")
            f_princ = st.text_input("Fio Principal")
            b_aux = st.text_input("Bobina Auxiliar (Espiras/Passo)")
            f_aux = st.text_input("Fio Auxiliar")
            capacitor = st.text_input("Capacitor")
            rolamentos = st.text_input("Rolamentos")

        with col3:
            st.markdown("---")
            st.write("📐 **Medidas do Eixo**")
            eixo_x = st.text_input("Tamanho do eixo X")
            eixo_y = st.text_input("Tamanho do eixo Y")
        
        enviar = st.form_submit_button("💾 SALVAR DADOS NO BANCO")
        
        if enviar:
            novo_dado = {
                'Marca': marca, 'Potencia_CV': potencia, 'RPM': rpm, 'Polaridade': polaridade,
                'Bobina_Principal': b_princ, 'Fio_Principal': f_princ, 
                'Bobina_Auxiliar': b_aux, 'Fio_Auxiliar': f_aux,
                'Amperagem': amperagem, 'Voltagem': voltagem, 
                'Capacitor': capacitor, 'Rolamentos': rolamentos,
                'Eixo_X': eixo_x, 'Eixo_Y': eixo_y
            }
            
            df_novo = pd.DataFrame([novo_dado])
            if os.path.exists(ARQUIVO_CSV):
                df_novo.to_csv(ARQUIVO_CSV, mode='a', header=False, index=False, sep=';', encoding='utf-8-sig')
            else:
                df_novo.to_csv(ARQUIVO_CSV, index=False, sep=';', encoding='utf-8-sig')
            
            st.success(f"✅ Motor {marca} de {potencia}CV salvo com sucesso!")

# --- ABA 3: ESQUEMAS DE LIGAÇÃO ---
with tab3:
    st.subheader("🖼️ Biblioteca de Esquemas (Monofásicos e Trifásicos)")
    st.write("Faça o upload dos seus esquemas feitos no Paint aqui para consulta rápida.")
    
    up_foto = st.file_uploader("Enviar novo esquema (JPG/PNG)", type=['png', 'jpg', 'jpeg'])
    if up_foto:
        nome_esquema = st.text_input("Nome para este esquema (ex: Monofasico_4polos_Weg)")
        if st.button("Salvar Imagem"):
            img = Image.open(up_foto)
            img.save(os.path.join(PASTA_ESQUEMAS, f"{nome_esquema}.png"))
            st.success("Imagem salva com sucesso!")

    st.divider()
    
    # Mostrar galeria de fotos salvas
    fotos_salvas = os.listdir(PASTA_ESQUEMAS)
    if fotos_salvas:
        escolha_img = st.selectbox("Selecione um esquema para visualizar", fotos_salvas)
        if escolha_img:
            imagem_aberta = Image.open(os.path.join(PASTA_ESQUEMAS, escolha_img))
            st.image(imagem_aberta, caption=escolha_img, use_container_width=True)
    else:
        st.info("Nenhum esquema salvo ainda. Use o campo acima para subir suas fotos do Paint.")

st.markdown("<br><p style='text-align:center; color:#555;'>Pablo Motores © 2026</p>", unsafe_allow_html=True)
