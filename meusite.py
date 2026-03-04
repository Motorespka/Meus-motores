import streamlit as st
import pandas as pd
import os
from PIL import Image

# --- 1. CONFIGURAÇÃO DE APARÊNCIA (ESTILO APP) ---
st.set_page_config(
    page_title="Pablo Motores",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS para esconder menus do Streamlit e dar destaque ao amarelo/preto
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #0e1117; }
    h1, h2, h3 { color: #f1c40f !important; }
    .stExpander { border: 1px solid #f1c40f !important; background-color: #1a1c23 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONFIGURAÇÕES DE ARQUIVOS ---
ARQUIVO_CSV = 'meubancodedados.csv'
PASTA_ESQUEMAS = 'esquemas_fotos'

if not os.path.exists(PASTA_ESQUEMAS): 
    os.makedirs(PASTA_ESQUEMAS)

def carregar_dados():
    if os.path.exists(ARQUIVO_CSV):
        return pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig', dtype=str).fillna("None")
    return pd.DataFrame()

# --- 3. NAVEGAÇÃO LATERAL ---
with st.sidebar:
    st.header("🔐 ACESSO")
    senha = st.text_input("Senha Admin", type="password")
    e_admin = (senha == "pablo123")
    
    menu = ["🔍 CONSULTA"]
    if e_admin:
        menu = ["🔍 CONSULTA", "➕ NOVO CADASTRO", "🖼️ ADICIONAR FOTO"]
    escolha = st.radio("Ir para:", menu)

# --- 4. ABA DE CONSULTA ---
if escolha == "🔍 CONSULTA":
    st.markdown("<h1 style='text-align: center;'>⚙️ PABLO MOTORES</h1>", unsafe_allow_html=True)
    df = carregar_dados()
    busca = st.text_input("🔍 Pesquisar por Marca, CV ou detalhes...")
    
    if not df.empty:
        df_f = df[df.apply(lambda row: row.astype(str).str.contains(busca, case=False).any(), axis=1)] if busca else df

        for idx, row in df_f.iterrows():
            with st.expander(f"📦 {row.get('Marca')} | {row.get('Potencia_CV')} CV | {row.get('RPM')} RPM"):
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.markdown("### 📊 GERAL")
                    st.write(f"**Polos:** {row.get('Polaridade')}")
                    st.write(f"**Volt:** {row.get('Voltagem')}")
                    st.write(f"**Amp:** {row.get('Amperagem')}")
                    st.write(f"**Rolamentos:** {row.get('Rolamentos')}")
                with c2:
                    st.markdown("### 🌀 PRINCIPAL")
                    st.write(f"**Grupo:** {row.get('Bobina_Principal')}")
                    st.write(f"**Fio:** {row.get('Fio_Principal')}")
                with c3:
                    st.markdown("### ⚡ AUXILIAR")
                    st.write(f"**Grupo:** {row.get('Bobina_Auxiliar')}")
                    st.write(f"**Fio:** {row.get('Fio_Auxiliar')}")
                    st.write(f"**Eixo:** {row.get('Eixo_X')} x {row.get('Eixo_Y')}")
                with c4:
                    st.markdown("### 🔗 LIGAÇÃO")
                    lig = str(row.get('Esquema_Marcado'))
                    st.info(f"Esquema: {lig}")
                    for n in lig.split(" / "):
                        for ext in [".png", ".jpg", ".jpeg"]:
                            p = os.path.join(PASTA_ESQUEMAS, f"{n.strip()}{ext}")
                            if os.path.exists(p): st.image(p)

# --- 5. ABA DE CADASTRO ---
elif escolha == "➕ NOVO CADASTRO":
    st.markdown("## ➕ Cadastrar Novo Motor")
    lista_fotos = [f.split(".")[0] for f in os.listdir(PASTA_ESQUEMAS) if f.endswith(('.png', '.jpg', '.jpeg'))]
    
    with st.form("cadastro_pablo", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.subheader("📊 Placa")
            marca = st.text_input("Marca")
            cv = st.text_input("CV")
            rpm = st.text_input("RPM")
            pol = st.text_input("Polos")
            volt = st.text_input("Volt")
            amp = st.text_input("Amp")
        with c2:
            st.subheader("🌀 Principal")
            camas_p = st.text_input("Grupo (Camas)")
            fio_p = st.text_input("Fio")
            st.divider()
            st.subheader("⚙️ Mecânica")
            rolam = st.text_input("Rolamentos")
            eixo_x = st.text_input("Eixo X")
            eixo_y = st.text_input("Eixo Y")
        with c3:
            st.subheader("⚡ Auxiliar")
            camas_a = st.text_input("Grupo Auxiliar")
            fio_a = st.text_input("Fio Auxiliar")
            st.divider()
            st.subheader("🔋 Partida")
            capac = st.text_input("Capacitor")

        st.markdown("### 🖼️ Vincular Esquemas")
        selecionados = []
        cols = st.columns(4)
        for i, foto in enumerate(lista_fotos):
            if cols[i % 4].checkbox(foto): selecionados.append(foto)
        
        if st.form_submit_button("💾 SALVAR MOTOR"):
            nova_lig = " / ".join(selecionados) if selecionados else "None"
            novo_motor = {
                'Marca': marca, 'Potencia_CV': cv, 'RPM': rpm, 'Polaridade': pol,
                'Voltagem': volt, 'Amperagem': amp, 'Fio_Principal': fio_p,
                'Bobina_Principal': camas_p, 'Rolamentos': rolam, 
                'Fio_Auxiliar': fio_a, 'Bobina_Auxiliar': camas_a,
                'Capacitor': capac, 'Eixo_X': eixo_x, 'Eixo_Y': eixo_y, 
                'Esquema_Marcado': nova_lig
            }
            pd.DataFrame([novo_motor]).to_csv(ARQUIVO_CSV, mode='a', header=not os.path.exists(ARQUIVO_CSV), index=False, sep=';', encoding='utf-8-sig')
            st.success("Salvo com sucesso!")

# --- 6. ABA DE FOTOS ---
elif escolha == "🖼️ ADICIONAR FOTO":
    st.markdown("## 🖼️ Enviar Novo Esquema")
    arq = st.file_uploader("Escolha a foto (Esquema de ligação)", type=['png', 'jpg', 'jpeg'])
    nome_f = st.text_input("Dê um nome para este esquema (ex: Weg_6_Cabos)")
    if st.button("Gravar no Sistema") and arq and nome_f:
        Image.open(arq).save(os.path.join(PASTA_ESQUEMAS, f"{nome_f}.png"))
        st.success(f"Esquema '{nome_f}' guardado!")
