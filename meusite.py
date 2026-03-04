import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from PIL import Image

# --- CONFIGURAÇÕES ---
ARQUIVO_CSV = 'meubancodedados.csv'
ARQUIVO_LIXEIRA = 'lixeira_motores.csv'
PASTA_ESQUEMAS = 'esquemas_fotos'

if not os.path.exists(PASTA_ESQUEMAS): os.makedirs(PASTA_ESQUEMAS)

st.set_page_config(page_title="Pablo Motores | Oficial", layout="wide")

# --- FUNÇÃO DE CARREGAMENTO (SEM ERROS) ---
def carregar_dados():
    if os.path.exists(ARQUIVO_CSV):
        try:
            # Lemos o CSV garantindo que ele não confunda as colunas
            df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig').fillna("---")
            return df.replace("None", "---")
        except:
            return pd.DataFrame()
    return pd.DataFrame()

# --- CSS PARA DEIXAR IGUAL ÀS SUAS FOTOS ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .titulo-secao { color: #f1c40f !important; font-size: 1.1rem; font-weight: bold; border-bottom: 2px solid #f1c40f; margin-bottom: 15px; }
    .stExpander { border: 1px solid #34495e !important; background-color: #1c202a !important; }
    label { color: #f1c40f !important; font-weight: bold !important; }
    .stButton>button { background-color: #f1c40f !important; color: black !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR (ADMIN E LIXEIRA) ---
with st.sidebar:
    st.header("⚙️ CONFIGURAÇÕES")
    senha = st.text_input("Senha Admin", type="password")
    e_admin = (senha == "pablo123")
    
    menu = ["🔍 CONSULTA"]
    if e_admin:
        menu = ["🔍 CONSULTA", "➕ NOVO CADASTRO", "🖼️ GERENCIAR ESQUEMAS", "🗑️ LIXEIRA"]
    
    escolha = st.radio("Navegar para:", menu)

# --- LOGICA DAS ABAS ---

# 1. ABA DE CONSULTA (A que você usa no dia a dia)
if escolha == "🔍 CONSULTA":
    st.markdown("<h1 style='text-align: center; color: #f1c40f;'>⚙️ PABLO MOTORES</h1>", unsafe_allow_html=True)
    df = carregar_dados()
    busca = st.text_input("🔍 Buscar por Marca, CV, RPM ou Ligação...")
    
    if not df.empty:
        df_f = df[df.astype(str).apply(lambda x: busca.lower() in x.str.lower().any(), axis=1)] if busca else df
        
        for idx, row in df_f.iterrows():
            # Pegando os dados com segurança para evitar o erro de KeyError
            nome_expander = f"📦 {row.get('Marca', '---')} | {row.get('Potencia_CV', '---')} CV | {row.get('RPM', '---')} RPM"
            with st.expander(nome_expander):
                c1, c2, c3, c4 = st.columns([1, 1, 1, 1.2])
                with c1:
                    st.markdown('<div class="titulo-secao">📊 GERAL</div>', unsafe_allow_html=True)
                    st.write(f"**Polos:** {row.get('Polaridade', '---')}")
                    st.write(f"**Volt:** {row.get('Voltagem', '---')}")
                    st.write(f"**Amp:** {row.get('Amperagem', '---')}")
                with c2:
                    st.markdown('<div class="titulo-secao">🌀 PRINCIPAL</div>', unsafe_allow_html=True)
                    st.write(f"**Fio:** {row.get('Fio_Principal', '---')}")
                    st.write(f"**Camas:** {row.get('Bobina_Principal', '---')}")
                with c3:
                    st.markdown('<div class="titulo-secao">⚡ AUXILIAR</div>', unsafe_allow_html=True)
                    st.write(f"**Fio:** {row.get('Fio_Auxiliar', '---')}")
                    st.write(f"**Eixo:** {row.get('Eixo_X', '---')} x {row.get('Eixo_Y', '---')}")
                with c4:
                    st.markdown('<div class="titulo-secao">🔗 LIGAÇÃO</div>', unsafe_allow_html=True)
                    lig = str(row.get('Esquema_Marcado', '---'))
                    st.warning(f"**{lig}**")
                    # Mostrar as fotos
                    for n in lig.split(" / "):
                        for ext in [".png", ".jpg"]:
                            p = os.path.join(PASTA_ESQUEMAS, f"{n.strip()}{ext}")
                            if os.path.exists(p): st.image(p, caption=n)

# 2. ABA DE NOVO CADASTRO (Onde você marca os quadrados das fotos)
elif escolha == "➕ NOVO CADASTRO":
    st.markdown("## ➕ CADASTRAR NOVO MOTOR")
    # Pega as fotos que você já tem na pasta de esquemas
    lista_fotos = [f.split(".")[0] for f in os.listdir(PASTA_ESQUEMAS) if f.endswith(('.png', '.jpg'))]
    
    with st.form("form_cadastro"):
        col_a, col_b = st.columns(2)
        m = col_a.text_input("Marca")
        cv = col_a.text_input("Potencia (CV)")
        rpm = col_b.text_input("RPM")
        pol = col_b.text_input("Polaridade")
        
        st.markdown("### 🖼️ SELECIONE AS LIGAÇÕES DESTE MOTOR")
        # Aqui estão os quadrados (checkboxes) que você pediu
        selecionados = []
        c_fotos = st.columns(3)
        for i, foto in enumerate(lista_fotos):
            if c_fotos[i % 3].checkbox(foto, key=f"check_{foto}"):
                selecionados.append(foto)
        
        if st.form_submit_button("💾 SALVAR MOTOR NO BANCO"):
            nova_ligacao = " / ".join(selecionados) if selecionados else "---"
            novo_dado = pd.DataFrame([{
                'Marca': m, 'Potencia_CV': cv, 'RPM': rpm, 'Polaridade': pol,
                'Esquema_Marcado': nova_ligacao
            }])
            novo_dado.to_csv(ARQUIVO_CSV, mode='a', header=not os.path.exists(ARQUIVO_CSV), index=False, sep=';', encoding='utf-8-sig')
            st.success("Motor cadastrado com sucesso!")

# 3. ABA DE GERENCIAR ESQUEMAS (Para subir novas fotos)
elif escolha == "🖼️ GERENCIAR ESQUEMAS":
    st.markdown("## 🖼️ ADICIONAR NOVAS FOTOS DE LIGAÇÃO")
    up = st.file_uploader("Escolha a foto da ligação", type=['png', 'jpg'])
    nome_f = st.text_input("Nome da Ligação (Ex: Estrela 12 Pontas)")
    if st.button("Gravar Imagem") and up and nome_f:
        img = Image.open(up)
        img.save(os.path.join(PASTA_ESQUEMAS, f"{nome_f}.png"))
        st.success(f"Foto '{nome_f}' salva! Agora ela aparecerá nos quadrados do cadastro.")

# 4. ABA LIXEIRA (Acesso Admin)
elif escolha == "🗑️ LIXEIRA":
    st.markdown("## 🗑️ RECUPERAÇÃO DE DADOS (20 DIAS)")
    # (Logica da lixeira aqui...)
