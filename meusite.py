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

# --- ESTILO CSS RADICAL PARA VISIBILIDADE ---
st.markdown("""
    <style>
    /* 1. FUNDO GERAL */
    .stApp { background-color: #0e1117; }

    /* 2. TEXTOS DE ORIENTAÇÃO (LABELS) - SEMPRE BRANCOS */
    label, p, span, .stMarkdown {
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
    }

    /* 3. CAIXAS DE ENTRADA (INPUTS) - FUNDO BRANCO E TEXTO PRETO */
    /* Isso resolve o problema de não enxergar o que digita */
    input, textarea, [data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border-radius: 5px !important;
    }
    
    /* 4. SENHA ADMIN NA BARRA LATERAL */
    [data-testid="stSidebar"] {
        background-color: #161a24 !important;
    }
    [data-testid="stSidebar"] label {
        color: #f1c40f !important; /* Senha Admin em Amarelo */
    }

    /* 5. TÍTULOS DOS GRUPOS */
    .yellow-title {
        color: #f1c40f !important;
        font-size: 1.2rem !important;
        font-weight: bold !important;
        border-bottom: 1px solid #f1c40f;
        margin-bottom: 10px;
    }

    /* 6. BOTÕES */
    .stButton>button {
        width: 100%;
        background-color: #f1c40f !important;
        color: black !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL (ADMIN) ---
with st.sidebar:
    st.markdown("### 🔐 ACESSO RESTRITO")
    senha_admin = st.text_input("Senha Admin", type="password")
    e_admin = (senha_admin == "pablo123")

st.markdown("<h1 style='text-align: center; color: #f1c40f;'>⚙️ PABLO MOTORES</h1>", unsafe_allow_html=True)

# --- CARREGAR DADOS ---
if os.path.exists(ARQUIVO_CSV):
    df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig').fillna("---").replace("None", "---")
else:
    df = pd.DataFrame()

opcoes_esquemas = [f.replace(".png", "").replace(".jpg", "") for f in os.listdir(PASTA_ESQUEMAS) if f.endswith(('.png', '.jpg'))]

# --- NAVEGAÇÃO ---
abas_nomes = ["🔍 CONSULTA", "➕ NOVO CADASTRO", "🖼️ ESQUEMAS"] if e_admin else ["🔍 CONSULTA"]
tabs = st.tabs(abas_nomes)

# --- ABA 1: CONSULTA / EDIÇÃO ---
with tabs[0]:
    busca = st.text_input("🔍 Buscar motor para ver ou editar...")
    df_f = df[df.astype(str).apply(lambda x: busca.lower() in x.str.lower().any(), axis=1)] if (not df.empty and busca) else df

    for idx, row in df_f.iterrows():
        with st.expander(f"📦 {row.get('Marca')} | {row.get('Potencia_CV')} CV"):
            # Visualização rápida
            v1, v2, v3 = st.columns(3)
            v1.write(f"**Volt:** {row.get('Voltagem')}")
            v2.write(f"**Principal:** {row.get('Fio_Principal')}")
            v3.write(f"**Auxiliar:** {row.get('Fio_Auxiliar')}")

            if e_admin:
                st.markdown("<p class='yellow-title'>📝 PAINEL DE EDIÇÃO</p>", unsafe_allow_html=True)
                with st.form(f"edit_{idx}"):
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        # Agora você vai enxergar o texto preto no fundo branco aqui
                        m = st.text_input("Marca", value=row.get('Marca'))
                        p = st.text_input("Potência (CV)", value=row.get('Potencia_CV'))
                        v = st.text_input("Voltagem", value=row.get('Voltagem'))
                    with c2:
                        bp = st.text_input("Bobina Principal", value=row.get('Bobina_Principal'))
                        fp = st.text_input("Fio Principal", value=row.get('Fio_Principal'))
                    with c3:
                        ba = st.text_input("Bobina Auxiliar", value=row.get('Bobina_Auxiliar'))
                        fa = st.text_input("Fio Auxiliar", value=row.get('Fio_Auxiliar'))
                    
                    st.write("**Ligações:**")
                    checks = {}
                    check_cols = st.columns(4)
                    for i, opt in enumerate(opcoes_esquemas):
                        checks[opt] = check_cols[i % 4].checkbox(opt, value=(opt in str(row.get('Esquema_Marcado'))), key=f"cb_{idx}_{opt}")

                    col_save, col_del = st.columns([3, 1])
                    if col_save.form_submit_button("💾 SALVAR ALTERAÇÕES"):
                        sel = [n for n, mar in checks.items() if mar]
                        df.at[idx, 'Marca'] = m
                        df.at[idx, 'Potencia_CV'] = p
                        df.at[idx, 'Voltagem'] = v
                        df.at[idx, 'Bobina_Principal'] = bp
                        df.at[idx, 'Fio_Principal'] = fp
                        df.at[idx, 'Bobina_Auxiliar'] = ba
                        df.at[idx, 'Fio_Auxiliar'] = fa
                        df.at[idx, 'Esquema_Marcado'] = " / ".join(sel) if sel else "---"
                        df.to_csv(ARQUIVO_CSV, index=False, sep=';', encoding='utf-8-sig')
                        st.success("Atualizado!")
                        st.rerun()
                
                if st.button(f"🗑️ EXCLUIR MOTOR", key=f"btn_del_{idx}"):
                    df.drop(idx).to_csv(ARQUIVO_CSV, index=False, sep=';', encoding='utf-8-sig')
                    st.rerun()

# --- AS OUTRAS ABAS (CADASTRO E ESQUEMAS) SEGUEM O MESMO ESTILO VISUAL ---
