import streamlit as st
import pandas as pd
import os
from PIL import Image

# --- CONFIGURAÇÕES DE DIRETÓRIOS ---
ARQUIVO_CSV = 'meubancodedados.csv'
PASTA_ESQUEMAS = 'esquemas_fotos'
if not os.path.exists(PASTA_ESQUEMAS):
    os.makedirs(PASTA_ESQUEMAS)

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Pablo Motores | Gestão Pro", layout="wide")

# --- ESTILO CSS REFEITO (FOCO EM LEITURA E PC/MOBILE) ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #1e272e 0%, #000000 100%);
        color: #ffffff;
    }
    .main-header {
        background: rgba(255, 255, 255, 0.05);
        padding: 1.5rem;
        border-radius: 15px;
        border-bottom: 4px solid #f1c40f;
        margin-bottom: 2rem;
        text-align: center;
    }
    /* Estilo das etiquetas de campo para aparecerem bem no fundo escuro */
    label {
        color: #f1c40f !important;
        font-weight: bold !important;
        font-size: 1rem !important;
    }
    .motor-card {
        background: #ffffff;
        color: #1a1a1a;
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        border-left: 10px solid #f1c40f;
    }
    /* Ajuste para inputs ficarem brancos e legíveis */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1 style="color:#f1c40f; margin:0;">⚙️ PABLO MOTORES</h1></div>', unsafe_allow_html=True)

# --- NAVEGAÇÃO ---
tab1, tab2, tab3 = st.tabs(["🔍 CONSULTA", "➕ NOVO CADASTRO", "🖼️ ESQUEMAS DE LIGAÇÃO"])

# --- ABA 1: CONSULTA ---
with tab1:
    busca = st.text_input("Filtrar por Marca ou CV...")
    if os.path.exists(ARQUIVO_CSV):
        df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig')
        df_filtrado = df[df.astype(str).apply(lambda x: busca.lower() in x.str.lower().any(), axis=1)] if busca else df
        for _, row in df_filtrado.iterrows():
            st.markdown(f"""
            <div class="motor-card">
                <h2 style="margin:0;">{row.get('Marca', 'MOTOR')} - {row.get('Potencia_CV', '-')} CV</h2>
                <p><b>RPM:</b> {row.get('RPM', '-')} | <b>Polos:</b> {row.get('Polaridade', '-')} | <b>Ligação:</b> {row.get('Esquema_Marcado', 'N/A')}</p>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 0.9rem;">
                    <div>🧵 <b>Princ:</b> {row.get('Fio_Principal', '-')} | ⚡ <b>Aux:</b> {row.get('Fio_Auxiliar', '-')}</div>
                    <div>📐 <b>Eixo X:</b> {row.get('Eixo_X', '-')} | <b>Eixo Y:</b> {row.get('Eixo_Y', '-')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# --- ABA 2: ADICIONAR (COM CAIXINHAS DE MARCAR) ---
with tab2:
    st.markdown("### 📝 Cadastro Técnico")
    with st.form("form_cadastro", clear_on_submit=True):
        c1, c2, c3 = st.columns([1, 1, 1])
        
        with c1:
            marca = st.text_input("Marca do Motor")
            potencia = st.text_input("Potência (CV)")
            rpm = st.text_input("RPM")
            polaridade = st.selectbox("Polaridade (Polos)", ["2", "4", "6", "8"])
            amp = st.text_input("Amperagem (A)")
            volt = st.text_input("Voltagem (V)")
            
        with c2:
            b_p = st.text_input("Bobina Principal")
            f_p = st.text_input("Fio Principal")
            b_a = st.text_input("Bobina Auxiliar")
            f_a = st.text_input("Fio Auxiliar")
            cap = st.text_input("Capacitor")
            rol = st.text_input("Rolamentos")
            
        with c3:
            st.markdown("#### 📐 Medidas do Eixo")
            eixo_x = st.text_input("Tamanho Eixo X")
            eixo_y = st.text_input("Tamanho Eixo Y")
            
            st.markdown("---")
            st.markdown("#### 🔗 Esquema de Ligação")
            # Caixinhas de marcar (Checkboxes)
            m_s = st.checkbox("Monofásico Série")
            m_p = st.checkbox("Monofásico Paralelo")
            t_y = st.checkbox("Trifásico Estrela (Y)")
            t_d = st.checkbox("Trifásico Triângulo (Δ)")
            t_yy = st.checkbox("Trifásico Duplo Estrela")

        if st.form_submit_button("💾 SALVAR DADOS"):
            # Junta as opções marcadas em uma frase
            ligacoes = []
            if m_s: ligacoes.append("Mono-Série")
            if m_p: ligacoes.append("Mono-Paralelo")
            if t_y: ligacoes.append("Tri-Estrela")
            if t_d: ligacoes.append("Tri-Triângulo")
            if t_yy: ligacoes.append("Tri-Duplo-Y")
            esquema_texto = ", ".join(ligacoes)

            novo_dado = {
                'Marca': marca, 'Potencia_CV': potencia, 'RPM': rpm, 'Polaridade': polaridade,
                'Bobina_Principal': b_p, 'Fio_Principal': f_p, 'Bobina_Auxiliar': b_a, 
                'Fio_Auxiliar': f_a, 'Amperagem': amp, 'Voltagem': volt, 
                'Capacitor': cap, 'Rolamentos': rol, 'Eixo_X': eixo_x, 'Eixo_Y': eixo_y,
                'Esquema_Marcado': esquema_texto
            }
            pd.DataFrame([novo_dado]).to_csv(ARQUIVO_CSV, mode='a', header=not os.path.exists(ARQUIVO_CSV), index=False, sep=';', encoding='utf-8-sig')
            st.success("Motor salvo!")

# --- ABA 3: ESQUEMAS ---
with tab3:
    st.markdown("### 🖼️ Sua Galeria de Esquemas (Paint)")
    col_upload, col_view = st.columns([1, 2])
    
    with col_upload:
        up = st.file_uploader("Subir foto do Paint", type=['png', 'jpg'])
        nome = st.text_input("Nome da Ligação (Ex: 6 Terminais Weg)")
        if st.button("Salvar na Galeria") and up and nome:
            Image.open(up).save(os.path.join(PASTA_ESQUEMAS, f"{nome}.png"))
            st.rerun()

    fotos = [f for f in os.listdir(PASTA_ESQUEMAS) if f.endswith(('.png', '.jpg'))]
    if fotos:
        with col_view:
            escolha = st.selectbox("Ver Esquema Ampliado:", fotos)
            st.image(os.path.join(PASTA_ESQUEMAS, escolha), use_container_width=True)
        
        st.divider()
        st.write("📋 **Miniaturas**")
        cols = st.columns(4)
        for i, f in enumerate(fotos):
            cols[i % 4].image(os.path.join(PASTA_ESQUEMAS, f), caption=f, use_container_width=True)

st.markdown("<br><p style='text-align:center; color:#555;'>Pablo Motores © 2026</p>", unsafe_allow_html=True)
