import streamlit as st
import pandas as pd
import os
from PIL import Image

# --- CONFIGURAÇÕES ---
ARQUIVO_CSV = 'meubancodedados.csv'
PASTA_ESQUEMAS = 'esquemas_fotos'

if not os.path.exists(PASTA_ESQUEMAS):
    os.makedirs(PASTA_ESQUEMAS)

st.set_page_config(page_title="Pablo Motores | Gestão", layout="wide")

# --- CSS REFINADO PARA PC ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    
    .titulo-secao {
        color: #f1c40f !important;
        font-size: 1.1rem !important;
        font-weight: bold !important;
        border-bottom: 2px solid #f1c40f;
        margin-bottom: 10px;
        padding-bottom: 5px;
    }

    .dado-item { margin-bottom: 8px; font-size: 1.05rem !important; }
    .dado-label { color: #f1c40f !important; font-weight: bold !important; }
    .dado-valor { color: #ffffff !important; font-weight: bold !important; }

    .caixa-ligacao {
        background-color: #1c202a;
        border: 2px solid #f1c40f;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
    }
    .texto-ligacao { color: #f1c40f !important; font-size: 1.3rem !important; font-weight: 900 !important; }

    /* Inputs e Botões */
    input { background-color: #ffffff !important; color: #000000 !important; font-weight: bold !important; }
    .stButton>button {
        width: 100%;
        background-color: #f1c40f !important;
        color: #000000 !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ADMIN NA SIDEBAR ---
with st.sidebar:
    st.markdown("### 🔐 ACESSO")
    senha = st.text_input("Senha Admin", type="password")
    e_admin = (senha == "pablo123")

st.markdown("<h1 style='text-align: center; color: #f1c40f;'>⚙️ PABLO MOTORES</h1>", unsafe_allow_html=True)

# --- CARREGAR DADOS ---
if os.path.exists(ARQUIVO_CSV):
    df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig').fillna("---")
else:
    df = pd.DataFrame()

opcoes_esquemas = [f.replace(".png", "").replace(".jpg", "") for f in os.listdir(PASTA_ESQUEMAS) if f.endswith(('.png', '.jpg'))]

# --- CONSULTA ---
busca = st.text_input("🔍 Pesquisar Motor...")

if not df.empty:
    df_f = df[df.astype(str).apply(lambda x: busca.lower() in x.str.lower().any(), axis=1)] if busca else df
    
    for idx, row in df_f.iterrows():
        label_motor = f"📦 {row.get('Marca')} | {row.get('Potencia_CV')} CV | {row.get('RPM')} RPM"
        with st.expander(label_motor):
            
            # --- PARTE 1: EXIBIÇÃO DOS DADOS ---
            c1, c2, c3, c4 = st.columns([1, 1, 1, 1.2])

            with c1:
                st.markdown('<div class="titulo-secao">📊 GERAL</div>', unsafe_allow_html=True)
                st.write(f"**Polos:** {row.get('Polaridade')}")
                st.write(f"**Volt:** {row.get('Voltagem')}")
                st.write(f"**Amp:** {row.get('Amperagem')}")

            with c2:
                st.markdown('<div class="titulo-secao">🌀 PRINCIPAL</div>', unsafe_allow_html=True)
                st.write(f"**Camas:** {row.get('Bobina_Principal')}")
                st.write(f"**Fio:** {row.get('Fio_Principal')}")

            with c3:
                st.markdown('<div class="titulo-secao">⚡ AUXILIAR</div>', unsafe_allow_html=True)
                st.write(f"**Camas:** {row.get('Bobina_Auxiliar')}")
                st.write(f"**Fio:** {row.get('Fio_Auxiliar')}")

            with c4:
                st.markdown('<div class="titulo-secao">🔗 LIGAÇÃO</div>', unsafe_allow_html=True)
                lig_texto = str(row.get('Esquema_Marcado'))
                st.markdown(f'<div class="caixa-ligacao"><span class="texto-ligacao">{lig_texto}</span></div>', unsafe_allow_html=True)
                
                # Fotos
                for nome in lig_texto.split(" / "):
                    for ext in [".png", ".jpg"]:
                        p = os.path.join(PASTA_ESQUEMAS, f"{nome.strip()}{ext}")
                        if os.path.exists(p): st.image(p)

            # --- PARTE 2: EDIÇÃO E EXCLUSÃO (SÓ APARECE SE LOGADO) ---
            if e_admin:
                st.markdown('<div class="titulo-secao">⚙️ CONTROLE DO MOTOR</div>', unsafe_allow_html=True)
                col_ed, col_del = st.columns([1, 1])

                # Botão de Excluir
                if col_del.button(f"🗑️ EXCLUIR MOTOR", key=f"del_{idx}"):
                    df.drop(idx).to_csv(ARQUIVO_CSV, index=False, sep=';', encoding='utf-8-sig')
                    st.success("Motor removido!")
                    st.rerun()

                # Checkbox para abrir o formulário de edição
                if col_ed.checkbox(f"📝 EDITAR INFORMAÇÕES", key=f"check_{idx}"):
                    with st.form(f"form_ed_{idx}"):
                        fe1, fe2, fe3 = st.columns(3)
                        # Preenche os campos com o que já existe no CSV
                        n_marca = fe1.text_input("Marca", value=row.get('Marca'))
                        n_cv = fe1.text_input("CV", value=row.get('Potencia_CV'))
                        n_f_p = fe2.text_input("Fio Principal", value=row.get('Fio_Principal'))
                        n_f_a = fe2.text_input("Fio Auxiliar", value=row.get('Fio_Auxiliar'))
                        
                        st.write("Atualizar Ligações:")
                        n_ligs = {opt: st.checkbox(opt, value=(opt in lig_texto), key=f"ed_lig_{idx}_{opt}") for opt in opcoes_esquemas}
                        
                        if st.form_submit_button("💾 SALVAR ALTERAÇÕES"):
                            # Atualiza o DataFrame
                            sel = [n for n, v in n_ligs.items() if v]
                            df.at[idx, 'Marca'] = n_marca
                            df.at[idx, 'Potencia_CV'] = n_cv
                            df.at[idx, 'Fio_Principal'] = n_f_p
                            df.at[idx, 'Fio_Auxiliar'] = n_f_a
                            df.at[idx, 'Esquema_Marcado'] = " / ".join(sel) if sel else "---"
                            
                            df.to_csv(ARQUIVO_CSV, index=False, sep=';', encoding='utf-8-sig')
                            st.success("Dados atualizados!")
                            st.rerun()
                            
