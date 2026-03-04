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

# --- ESTILO CSS RADICAL PARA VISIBILIDADE NO PC ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    
    /* Labels e Textos sempre brancos */
    label, p, span, .stMarkdown, h3 {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }

    /* Campos de entrada: Fundo Branco, Texto Preto (Máxima Visibilidade) */
    input, textarea, [data-baseweb="select"] > div, .stNumberInput div {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border-radius: 5px !important;
        font-weight: bold !important;
    }

    /* Barra Lateral */
    [data-testid="stSidebar"] { background-color: #161a24 !important; }
    [data-testid="stSidebar"] label { color: #f1c40f !important; }

    /* Estilo dos Botões */
    .stButton>button {
        width: 100%;
        background-color: #f1c40f !important;
        color: black !important;
        font-weight: bold !important;
        border: none !important;
    }
    
    .yellow-title {
        color: #f1c40f !important;
        font-size: 1.3rem !important;
        font-weight: bold !important;
        margin-top: 15px;
        border-bottom: 2px solid #f1c40f;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL ---
with st.sidebar:
    st.markdown("### 🔐 ADMIN")
    senha_admin = st.text_input("Senha", type="password")
    e_admin = (senha_admin == "pablo123")

st.markdown("<h1 style='text-align: center; color: #f1c40f;'>⚙️ PABLO MOTORES</h1>", unsafe_allow_html=True)

# --- CARREGAR DADOS ---
if os.path.exists(ARQUIVO_CSV):
    df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig').fillna("---").replace("None", "---")
else:
    df = pd.DataFrame()

# Pegar opções de esquemas da pasta
opcoes_esquemas = [f.replace(".png", "").replace(".jpg", "") for f in os.listdir(PASTA_ESQUEMAS) if f.endswith(('.png', '.jpg'))]

# --- NAVEGAÇÃO ---
abas_nomes = ["🔍 CONSULTA", "➕ NOVO CADASTRO", "🖼️ ESQUEMAS"] if e_admin else ["🔍 CONSULTA"]
tabs = st.tabs(abas_nomes)

# --- ABA 1: CONSULTA E EDIÇÃO ---
with tabs[0]:
    busca = st.text_input("🔍 Buscar motor...")
    df_f = df[df.astype(str).apply(lambda x: busca.lower() in x.str.lower().any(), axis=1)] if (not df.empty and busca) else df

    if not df.empty:
        for idx, row in df_f.iterrows():
            with st.expander(f"📦 {row.get('Marca')} | {row.get('Potencia_CV')} CV"):
                # Visualização rápida (Consulta)
                c1, c2, c3 = st.columns(3)
                c1.write(f"**RPM:** {row.get('RPM')}")
                c2.write(f"**Voltagem:** {row.get('Voltagem')}")
                c3.write(f"**Ligações:** {row.get('Esquema_Marcado')}")
                
                # Exibição das Imagens na Consulta
                ligs_lista = str(row.get('Esquema_Marcado')).split(" / ")
                img_cols = st.columns(4)
                for i, nome_lig in enumerate(ligs_lista):
                    path = os.path.join(PASTA_ESQUEMAS, f"{nome_lig}.png")
                    if os.path.exists(path):
                        img_cols[i % 4].image(path, caption=nome_lig, use_container_width=True)

                if e_admin:
                    st.markdown("<p class='yellow-title'>📝 EDITAR REGISTRO</p>", unsafe_allow_html=True)
                    with st.form(f"edit_{idx}"):
                        ce1, ce2, ce3 = st.columns(3)
                        with ce1:
                            m = st.text_input("Marca", value=row.get('Marca'))
                            p = st.text_input("Potência (CV)", value=row.get('Potencia_CV'))
                        with ce2:
                            bp = st.text_input("Bobina Principal", value=row.get('Bobina_Principal'))
                            fp = st.text_input("Fio Principal", value=row.get('Fio_Principal'))
                        with ce3:
                            ba = st.text_input("Bobina Auxiliar", value=row.get('Bobina_Auxiliar'))
                            fa = st.text_input("Fio Auxiliar", value=row.get('Fio_Auxiliar'))
                        
                        st.write("**Ligações:**")
                        edits_ligs = {opt: st.checkbox(opt, value=(opt in str(row.get('Esquema_Marcado'))), key=f"ed_{idx}_{opt}") for opt in opcoes_esquemas}
                        
                        if st.form_submit_button("💾 SALVAR ALTERAÇÃO"):
                            selecionados = [n for n, v in edits_ligs.items() if v]
                            df.at[idx, 'Marca'], df.at[idx, 'Potencia_CV'] = m, p
                            df.at[idx, 'Bobina_Principal'], df.at[idx, 'Fio_Principal'] = bp, fp
                            df.at[idx, 'Bobina_Auxiliar'], df.at[idx, 'Fio_Auxiliar'] = ba, fa
                            df.at[idx, 'Esquema_Marcado'] = " / ".join(selecionados) if selecionados else "---"
                            df.to_csv(ARQUIVO_CSV, index=False, sep=';', encoding='utf-8-sig')
                            st.rerun()
                    
                    if st.button(f"🗑️ EXCLUIR MOTOR", key=f"del_btn_{idx}"):
                        df.drop(idx).to_csv(ARQUIVO_CSV, index=False, sep=';', encoding='utf-8-sig')
                        st.rerun()

# --- ABA 2: NOVO CADASTRO ---
if e_admin:
    with tabs[1]:
        st.markdown("<p class='yellow-title'>📝 CADASTRO TÉCNICO</p>", unsafe_allow_html=True)
        with st.form("novo_motor_pablo", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                marca = st.text_input("Marca do Motor")
                potencia = st.text_input("Potência (CV)")
                polos = st.selectbox("Polos", ["2", "4", "6", "8"])
                volt = st.text_input("Voltagem (Ex: 110/220)")
            with col2:
                b_p = st.text_input("Bobina Principal")
                f_p = st.text_input("Fio Principal")
                b_a = st.text_input("Bobina Auxiliar")
                f_a = st.text_input("Fio Auxiliar")
            with col3:
                st.write("**Ligações:**")
                # Checkboxes dinâmicos baseados nas fotos da pasta
                novas_ligs = {opt: st.checkbox(opt, key=f"new_{opt}") for opt in opcoes_esquemas}
            
            if st.form_submit_button("💾 SALVAR NOVO MOTOR"):
                sel_ligs = [n for n, v in novas_ligs.items() if v]
                novo = {
                    'Marca': marca, 'Potencia_CV': potencia, 'Polaridade': polos, 'Voltagem': volt,
                    'Bobina_Principal': b_p, 'Fio_Principal': f_p, 'Bobina_Auxiliar': b_a, 'Fio_Auxiliar': f_a,
                    'Esquema_Marcado': " / ".join(sel_ligs) if sel_ligs else "---"
                }
                pd.DataFrame([novo]).to_csv(ARQUIVO_CSV, mode='a', header=not os.path.exists(ARQUIVO_CSV), index=False, sep=';', encoding='utf-8-sig')
                st.success("✅ Motor cadastrado!")
                st.rerun()

# --- ABA 3: ESQUEMAS ---
if e_admin:
    with tabs[2]:
        st.markdown("<p class='yellow-title'>🖼️ GERENCIAR ESQUEMAS TÉCNICOS</p>", unsafe_allow_html=True)
        up = st.file_uploader("Subir Desenho do Paint", type=['png', 'jpg'])
        nome_esq = st.text_input("Nome da Ligação (Ex: Estrela, 12 Pontas)")
        
        if st.form_submit_button("Criar Nova Opção") if st.button("Gravar Nova Opção") else None:
            if up and nome_esq:
                Image.open(up).save(os.path.join(PASTA_ESQUEMAS, f"{nome_esq}.png"))
                st.rerun()
        
        st.divider()
        st.write("### Suas Ligações Atuais:")
        if opcoes_esquemas:
            for f in opcoes_esquemas:
                c_img, c_txt, c_del = st.columns([1, 3, 1])
                c_img.image(os.path.join(PASTA_ESQUEMAS, f"{f}.png"), width=100)
                c_txt.write(f"**{f}**")
                if c_del.button("🗑️ Remover", key=f"del_opt_{f}"):
                    os.remove(os.path.join(PASTA_ESQUEMAS, f"{f}.png"))
                    st.rerun()

st.markdown("<p style='text-align:center; color:#555; margin-top:50px;'>Pablo Motores © 2026</p>", unsafe_allow_html=True)
