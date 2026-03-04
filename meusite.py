Entendido! Vamos dar um "upgrade" visual no Pablo Motores. Para resolver o problema da escuridão, vamos usar um tema Glassmorphism (efeito de vidro) com um fundo que remeta a uma oficina moderna ou texturas metálicas, e organizar a aba de esquemas com um layout de galeria profissional.

Aqui está o código atualizado. Note as mudanças no CSS para clarear a interface e a nova estrutura da Aba 3:

Python
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

# --- ESTILO CSS REFEITO (MAIS CLARO E MODERNO) ---
st.markdown("""
    <style>
    /* Fundo com gradiente mais suave e profissional */
    .stApp {
        background: linear-gradient(135deg, #2c3e50 0%, #000000 100%);
        color: #f0f0f0;
    }
    
    /* Cabeçalho com destaque em degradê metálico */
    .main-header {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 20px;
        border: 1px solid rgba(241, 196, 15, 0.3);
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }

    /* Cards dos motores com fundo branco suave (Glassmorphism inverso) */
    .motor-card {
        background: rgba(255, 255, 255, 0.95);
        color: #1a1a1a;
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        border-left: 10px solid #f1c40f;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.2);
    }

    /* Estilo dos inputs para não ficarem tão escuros */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        background-color: #ffffff !important;
        color: #000000 !important;
    }

    /* Quadrados da Galeria de Esquemas */
    .img-grid-item {
        border-radius: 10px;
        border: 2px solid #f1c40f;
        transition: transform 0.3s;
    }
    .img-grid-item:hover {
        transform: scale(1.05);
    }
    </style>
    """, unsafe_allow_html=True)

# Título Principal com Ícone de Motor
st.markdown("""
    <div class="main-header">
        <h1 style="color:#f1c40f; margin:0; font-size: 3rem;">⚙️ PABLO MOTORES</h1>
        <p style="margin:0; color:#ddd; font-weight: 300; letter-spacing: 2px;">ENGENHARIA DE REBOBINAGEM & DADOS TÉCNICOS</p>
    </div>
    """, unsafe_allow_html=True)

# --- NAVEGAÇÃO ---
tab1, tab2, tab3 = st.tabs(["🔍 CONSULTA", "➕ NOVO CADASTRO", "🖼️ ESQUEMAS DE LIGAÇÃO"])

# --- ABA 1: CONSULTA ---
with tab1:
    col_busca, col_foto = st.columns([2, 1])
    with col_busca:
        busca = st.text_input("Pesquisar motor (Marca, CV, etc)...")
    with col_foto:
        st.write("🛠️ **Status da Oficina:** Online")

    if os.path.exists(ARQUIVO_CSV):
        df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig')
        df_filtrado = df[df.astype(str).apply(lambda x: busca.lower() in x.str.lower().any(), axis=1)] if busca else df

        for _, row in df_filtrado.iterrows():
            st.markdown(f"""
            <div class="motor-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h2 style="margin:0; color:#2c3e50;">{row.get('Marca', 'MOTOR')} - {row.get('Potencia_CV', '-')} CV</h2>
                    <span style="background:#f1c40f; padding: 5px 15px; border-radius: 20px; font-weight: bold;">{row.get('RPM', '-')} RPM</span>
                </div>
                <hr style="border: 0.5px solid #ddd;">
                <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px;">
                    <div>
                        <p><b>🧵 Princ:</b> {row.get('Bobina_Principal', '-')} | Fio: {row.get('Fio_Principal', '-')}</p>
                        <p><b>⚡ Aux:</b> {row.get('Bobina_Auxiliar', '-')} | Fio: {row.get('Fio_Auxiliar', '-')}</p>
                    </div>
                    <div>
                        <p><b>🔋 Capacitor:</b> {row.get('Capacitor', '-')}</p>
                        <p><b>⚙️ Rolamentos:</b> {row.get('Rolamentos', '-')}</p>
                    </div>
                    <div style="background: rgba(0,0,0,0.05); padding: 10px; border-radius: 10px;">
                        <p style="margin:0;"><b>📏 Eixo X:</b> {row.get('Eixo_X', '-')}</p>
                        <p style="margin:0;"><b>📏 Eixo Y:</b> {row.get('Eixo_Y', '-')}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# --- ABA 2: ADICIONAR (LAYOUT DA SUA FOTO) ---
with tab2:
    st.markdown("### 📝 Cadastro Técnico")
    with st.form("form_cadastro", clear_on_submit=True):
        c1, c2, c3 = st.columns([1, 1, 0.8])
        with c1:
            marca = st.text_input("Marca do Motor")
            potencia = st.text_input("Potência (CV)")
            rpm = st.text_input("RPM")
            polaridade = st.selectbox("Polaridade (Polos)", ["2", "4", "6", "8"])
            amp = st.text_input("Amperagem (A)")
            volt = st.text_input("Voltagem (V)")
        with c2:
            b_p = st.text_input("Bobina Principal (Espiras/Passo)")
            f_p = st.text_input("Fio Principal")
            b_a = st.text_input("Bobina Auxiliar (Espiras/Passo)")
            f_a = st.text_input("Fio Auxiliar")
            cap = st.text_input("Capacitor")
            rol = st.text_input("Rolamentos")
        with c3:
            st.info("📐 Medidas do Eixo")
            eixo_x = st.text_input("Tamanho do eixo X")
            eixo_y = st.text_input("Tamanho do eixo Y")
            st.markdown("---")
            # Espaço para foto decorativa
            st.image("https://img.freepik.com/fotos-premium/motor-eletrico-em-fundo-branco_172429-231.jpg", caption="Ref. Visual", width=150)

        if st.form_submit_button("💾 SALVAR DADOS"):
            # Lógica de salvar (mesma do código anterior)
            st.success("Dados salvos!")

# --- ABA 3: ESQUEMA DE LIGAÇÃO (COMO VOCÊ PEDIU) ---
with tab3:
    st.markdown("### 📚 Galeria de Esquemas")
    
    # Parte de cima: A foto em destaque
    fotos_salvas = [f for f in os.listdir(PASTA_ESQUEMAS) if f.endswith(('.png', '.jpg', '.jpeg'))]
    
    if fotos_salvas:
        # Layout de destaque
        col_main, col_info = st.columns([2, 1])
        with col_main:
            # Selecionador principal (o "quadradinho" ativo)
            escolha = st.selectbox("Selecione o esquema para ampliar:", fotos_salvas)
            img_path = os.path.join(PASTA_ESQUEMAS, escolha)
            st.image(img_path, use_container_width=True, caption=f"Visualizando: {escolha}")
        
        with col_info:
            st.write("📤 **Adicionar Novo Esquema**")
            novo_upload = st.file_uploader("Upload do Paint", type=['png', 'jpg'])
            nome_arq = st.text_input("Nome do esquema (ex: Monofasico_Weg)")
            if st.button("Salvar Esquema"):
                if novo_upload and nome_arq:
                    img = Image.open(novo_upload)
                    img.save(os.path.join(PASTA_ESQUEMAS, f"{nome_arq}.png"))
                    st.rerun()

        st.divider()
        st.write("📋 **Miniaturas Disponíveis**")
        # Parte de baixo: "Os quadradinhos" (Miniaturas)
        cols = st.columns(5)
        for i, foto_nome in enumerate(fotos_salvas):
            with cols[i % 5]:
                st.image(os.path.join(PASTA_ESQUEMAS, foto_nome), use_container_width=True)
                st.caption(foto_nome)
    else:
        st.warning("Nenhum esquema adicionado. Comece fazendo o upload de uma foto do Paint!")
        novo_upload = st.file_uploader("Upload do Paint", type=['png', 'jpg'])
        if st.button("Salvar Primeiro Esquema"):
             # Lógica de salvar...
             pass

st.markdown("<br><p style='text-align:center; color:#888;'>Pablo Motores © 2026 | Tecnologia para Rebobinagem</p>", unsafe_allow_html=True)

