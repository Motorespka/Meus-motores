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

# --- LOGIN ADMIN ---
st.sidebar.markdown("<h2 style='color: #f1c40f;'>🔐 Acesso Admin</h2>", unsafe_allow_html=True)
senha_admin = st.sidebar.text_input("Senha", type="password")
e_admin = (senha_admin == "pablo123")

# --- ESTILO CSS PARA CONTRASTE E CORES ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    h1, h2, h3, p, span, li, label, .stMarkdown { color: #FFFFFF !important; }
    strong, b { color: #f1c40f !important; }
    
    /* Estilo do Expander */
    .streamlit-expanderHeader {
        background-color: #1e2130 !important;
        color: #f1c40f !important;
        border: 1px solid #34495e !important;
        font-size: 1.2rem !important;
    }
    
    /* Inputs Brancos */
    input { background-color: #ffffff !important; color: #000000 !important; }
    
    /* Caixa de Ligação com destaque */
    .caixa-ligacao {
        background-color: #f1c40f;
        color: #000000 !important;
        padding: 10px;
        border-radius: 8px;
        font-weight: bold;
        text-align: center;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #f1c40f;'>⚙️ PABLO MOTORES</h1>", unsafe_allow_html=True)

# --- NAVEGAÇÃO ---
if e_admin:
    abas = ["🔍 CONSULTA RÁPIDA", "➕ NOVO CADASTRO", "🖼️ ESQUEMAS (ADMIN)"]
else:
    abas = ["🔍 CONSULTA RÁPIDA"]
tabs = st.tabs(abas)

# --- ABA 1: CONSULTA ---
with tabs[0]:
    busca = st.text_input("🔍 Buscar motor...")
    
    if os.path.exists(ARQUIVO_CSV):
        # Carrega e substitui "None" ou vazios por "---"
        df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig').fillna("---")
        df = df.replace("None", "---")
        
        df_filtrado = df[df.astype(str).apply(lambda x: busca.lower() in x.str.lower().any(), axis=1)] if busca else df

        for idx, row in df_filtrado.iterrows():
            with st.expander(f"📦 {row.get('Marca')} | {row.get('Potencia_CV')} CV"):
                c1, c2, c3 = st.columns(3)
                
                with c1:
                    st.markdown(f"**RPM:** {row.get('RPM')}")
                    st.markdown(f"**Polos:** {row.get('Polaridade')}")
                    # Lógica da barra na Voltagem e Amperagem
                    v = str(row.get('Voltagem'))
                    a = str(row.get('Amperagem'))
                    st.markdown(f"**Voltagem:** {v}")
                    st.markdown(f"**Amperagem:** {a}")
                
                with c2:
                    # Organização em cascata: Grupo em cima, Fio em baixo
                    st.markdown("---")
                    st.markdown(f"**Bobina Principal:**\n\n{row.get('Bobina_Principal')}")
                    st.markdown(f"**Fio Principal:**\n\n{row.get('Fio_Principal')}")
                    st.markdown("---")
                    st.markdown(f"**Bobina Auxiliar:**\n\n{row.get('Bobina_Auxiliar')}")
                    st.markdown(f"**Fio Auxiliar:**\n\n{row.get('Fio_Auxiliar')}")
                
                with c3:
                    st.markdown(f"**Capacitor:** {row.get('Capacitor')}")
                    st.markdown(f"**Rolamentos:** {row.get('Rolamentos')}")
                    st.markdown(f"**Eixo X:** {row.get('Eixo_X')}")
                    st.markdown(f"**Eixo Y:** {row.get('Eixo_Y')}")
                    
                    lig = row.get('Esquema_Marcado')
                    st.markdown(f"<div class='caixa-ligacao'>🔗 LIGAÇÕES: {lig}</div>", unsafe_allow_html=True)
                
                if e_admin:
                    if st.button(f"🗑️ Excluir Motor", key=f"del_{idx}"):
                        df.drop(idx).to_csv(ARQUIVO_CSV, index=False, sep=';', encoding='utf-8-sig')
                        st.rerun()

# --- ABA 2: CADASTRO (ADMIN) ---
if e_admin:
    with tabs[1]:
        st.subheader("📝 Cadastrar Dados do Motor")
        with st.form("cadastro_pablo", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                marca = st.text_input("Marca do Motor")
                potencia = st.text_input("Potência (CV)")
                rpm = st.text_input("RPM")
                polos = st.selectbox("Polaridade", ["2", "4", "6", "8", "12"])
                st.info("Dica: Use '/' para separar (ex: 110/220)")
                volt = st.text_input("Voltagem (V)")
                amp = st.text_input("Amperagem (A)")
            with col2:
                b_p = st.text_input("Bobina Principal (Grupo)")
                f_p = st.text_input("Fio Principal")
                b_a = st.text_input("Bobina Auxiliar (Grupo)")
                f_a = st.text_input("Fio Auxiliar")
                cap = st.text_input("Capacitor")
                rol = st.text_input("Rolamentos")
            with col3:
                ex = st.text_input("Tamanho Eixo X")
                ey = st.text_input("Tamanho Eixo Y")
                st.write("**Ligações:**")
                l1 = st.checkbox("Estrela (Y)")
                l2 = st.checkbox("Triângulo (Δ)")
                l3 = st.checkbox("Série")
                l4 = st.checkbox("Paralelo")

            if st.form_submit_button("💾 SALVAR NO BANCO"):
                ligs = []
                if l1: ligs.append("Estrela")
                if l2: ligs.append("Triângulo")
                if l3: ligs.append("Série")
                if l4: ligs.append("Paralelo")
                
                novo = {
                    'Marca': marca, 'Potencia_CV': potencia, 'RPM': rpm, 'Polaridade': polos,
                    'Voltagem': volt, 'Amperagem': amp, 
                    'Bobina_Principal': b_p, 'Fio_Principal': f_p,
                    'Bobina_Auxiliar': b_a, 'Fio_Auxiliar': f_a,
                    'Capacitor': cap, 'Rolamentos': rol, 'Eixo_X': ex, 'Eixo_Y': ey,
                    'Esquema_Marcado': ", ".join(ligs) if ligs else "---"
                }
                pd.DataFrame([novo]).to_csv(ARQUIVO_CSV, mode='a', header=not os.path.exists(ARQUIVO_CSV), index=False, sep=';', encoding='utf-8-sig')
                st.success("✅ Motor salvo!")

# --- ABA 3: ESQUEMAS ---
if e_admin:
    with tabs[2]:
        st.subheader("🖼️ Galeria de Esquemas")
        up = st.file_uploader("Upload do Paint", type=['png', 'jpg'])
        if up:
            nome_f = st.text_input("Nome do esquema")
            if st.button("Gravar"):
                Image.open(up).save(os.path.join(PASTA_ESQUEMAS, f"{nome_f}.png"))
                st.rerun()
        
        st.divider()
        fotos = [f for f in os.listdir(PASTA_ESQUEMAS) if f.endswith(('.png', '.jpg'))]
        if fotos:
            escolha = st.selectbox("Abrir desenho:", fotos)
            st.image(os.path.join(PASTA_ESQUEMAS, escolha), use_container_width=True)

st.markdown("<br><p style='text-align:center; color:#555;'>Pablo Motores © 2026</p>", unsafe_allow_html=True)
