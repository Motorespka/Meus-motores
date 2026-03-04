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
senha_admin = st.sidebar.text_input("Senha Admin", type="password")
e_admin = (senha_admin == "pablo123")

# --- ESTILO CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    h1, h2, h3, p, span, label { color: #FFFFFF !important; }
    strong, b { color: #f1c40f !important; }
    .streamlit-expanderHeader { background-color: #1e2130 !important; border: 1px solid #34495e !important; }
    input { background-color: #ffffff !important; color: #000000 !important; }
    .caixa-ligacao { background-color: #f1c40f; color: #000000 !important; padding: 5px; border-radius: 5px; font-weight: bold; text-align: center; }
    .btn-excluir { background-color: #e74c3c !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #f1c40f;'>⚙️ PABLO MOTORES</h1>", unsafe_allow_html=True)

# --- CARREGAR DADOS ---
if os.path.exists(ARQUIVO_CSV):
    df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig').fillna("---").replace("None", "---")
else:
    df = pd.DataFrame()

# Opções de esquemas dinâmicos
opcoes_esquemas = [f.replace(".png", "").replace(".jpg", "") for f in os.listdir(PASTA_ESQUEMAS) if f.endswith(('.png', '.jpg'))]

# --- NAVEGAÇÃO ---
abas = ["🔍 CONSULTA", "➕ NOVO CADASTRO", "🖼️ ESQUEMAS"] if e_admin else ["🔍 CONSULTA"]
tabs = st.tabs(abas)

# --- ABA 1: CONSULTA / EDIÇÃO / EXCLUSÃO ---
with tabs[0]:
    busca = st.text_input("🔍 Buscar motor para consultar ou editar...")
    df_filtrado = df[df.astype(str).apply(lambda x: busca.lower() in x.str.lower().any(), axis=1)] if (not df.empty and busca) else df

    if not df.empty:
        for idx, row in df_filtrado.iterrows():
            with st.expander(f"📦 {row.get('Marca')} | {row.get('Potencia_CV')} CV"):
                # Layout de visualização
                c1, c2, c3, c4 = st.columns([1, 1.2, 1.2, 2.5])
                with c1:
                    st.write(f"**RPM:** {row.get('RPM')}")
                    st.write(f"**Polos:** {row.get('Polaridade')}")
                    st.write(f"**Volt:** {row.get('Voltagem')}")
                with c2:
                    st.write(f"**PRINCIPAL**")
                    st.write(f"🔢 {row.get('Bobina_Principal')}")
                    st.write(f"🧵 {row.get('Fio_Principal')}")
                with c3:
                    st.write(f"**AUXILIAR**")
                    st.write(f"🔢 {row.get('Bobina_Auxiliar')}")
                    st.write(f"🧵 {row.get('Fio_Auxiliar')}")
                with c4:
                    lig_salva = str(row.get('Esquema_Marcado'))
                    st.markdown(f"<div class='caixa-ligacao'>🔗 {lig_salva}</div>", unsafe_allow_html=True)
                    
                    # Mostrar imagens
                    ligs_lista = lig_salva.split(" / ")
                    cols_img = st.columns(3)
                    for i, nome_lig in enumerate(ligs_lista):
                        caminho = os.path.join(PASTA_ESQUEMAS, f"{nome_lig}.png")
                        if os.path.exists(caminho):
                            cols_img[i % 3].image(caminho, caption=nome_lig, use_container_width=True)

                # --- ÁREA DE EDIÇÃO (SÓ ADMIN) ---
                if e_admin:
                    st.divider()
                    col_edit, col_del = st.columns([1, 1])
                    
                    if col_del.button(f"🗑️ EXCLUIR DEFINITIVAMENTE", key=f"del_{idx}"):
                        df.drop(idx).to_csv(ARQUIVO_CSV, index=False, sep=';', encoding='utf-8-sig')
                        st.rerun()

                    if col_edit.checkbox(f"📝 EDITAR INFORMAÇÕES", key=f"edit_check_{idx}"):
                        with st.form(f"form_edit_{idx}"):
                            st.write("### Corrigir Dados")
                            ce1, ce2, ce3 = st.columns(3)
                            with ce1:
                                n_marca = st.text_input("Marca", value=row.get('Marca'))
                                n_cv = st.text_input("CV", value=row.get('Potencia_CV'))
                                n_volt = st.text_input("Voltagem", value=row.get('Voltagem'))
                            with ce2:
                                n_bp = st.text_input("Bobina Principal", value=row.get('Bobina_Principal'))
                                n_fp = st.text_input("Fio Principal", value=row.get('Fio_Principal'))
                                n_ba = st.text_input("Bobina Auxiliar", value=row.get('Bobina_Auxiliar'))
                                n_fa = st.text_input("Fio Auxiliar", value=row.get('Fio_Auxiliar'))
                            with ce3:
                                st.write("Refazer Ligações:")
                                edits_ligs = {}
                                for opt in opcoes_esquemas:
                                    # Já deixa marcado o que estava salvo antes
                                    edits_ligs[opt] = st.checkbox(opt, value=(opt in lig_salva), key=f"cb_{idx}_{opt}")

                            if st.form_submit_button("💾 ATUALIZAR DADOS"):
                                novos_sel = [n for n, m in edits_ligs.items() if m]
                                df.at[idx, 'Marca'] = n_marca
                                df.at[idx, 'Potencia_CV'] = n_cv
                                df.at[idx, 'Voltagem'] = n_volt
                                df.at[idx, 'Bobina_Principal'] = n_bp
                                df.at[idx, 'Fio_Principal'] = n_fp
                                df.at[idx, 'Bobina_Auxiliar'] = n_ba
                                df.at[idx, 'Fio_Auxiliar'] = n_fa
                                df.at[idx, 'Esquema_Marcado'] = " / ".join(novos_sel) if novos_sel else "---"
                                
                                df.to_csv(ARQUIVO_CSV, index=False, sep=';', encoding='utf-8-sig')
                                st.success("Alterado com sucesso!")
                                st.rerun()

# --- ABA 2: NOVO CADASTRO ---
if e_admin:
    with tabs[1]:
        st.subheader("📝 Novo Cadastro")
        with st.form("form_novo", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                marca = st.text_input("Marca")
                potencia = st.text_input("Potência (CV)")
                rpm = st.text_input("RPM")
                polos = st.selectbox("Polaridade", ["2", "4", "6", "8"])
                volt = st.text_input("Voltagem")
            with col2:
                b_p = st.text_input("Bobina Principal")
                f_p = st.text_input("Fio Principal")
                b_a = st.text_input("Bobina Auxiliar")
                f_a = st.text_input("Fio Auxiliar")
            with col3:
                st.write("**Ligações Disponíveis:**")
                dict_new = {opt: st.checkbox(opt, key=f"new_{opt}") for opt in opcoes_esquemas}

            if st.form_submit_button("💾 SALVAR MOTOR"):
                sel = [n for n, m in dict_new.items() if m]
                novo_motor = {
                    'Marca': marca, 'Potencia_CV': potencia, 'RPM': rpm, 'Polaridade': polos,
                    'Voltagem': volt, 'Bobina_Principal': b_p, 'Fio_Principal': f_p,
                    'Bobina_Auxiliar': b_a, 'Fio_Auxiliar': f_a,
                    'Esquema_Marcado': " / ".join(sel) if sel else "---"
                }
                pd.DataFrame([novo_motor]).to_csv(ARQUIVO_CSV, mode='a', header=not os.path.exists(ARQUIVO_CSV), index=False, sep=';', encoding='utf-8-sig')
                st.success("✅ Cadastrado!")
                st.rerun()

# --- ABA 3: ESQUEMAS ---
if e_admin:
    with tabs[2]:
        st.subheader("🖼️ Gerenciar Ligações")
        up = st.file_uploader("Nova Foto do Paint", type=['png', 'jpg'])
        nome_e = st.text_input("Nome da Ligação")
        if st.button("Criar Opção") and up and nome_e:
            Image.open(up).save(os.path.join(PASTA_ESQUEMAS, f"{nome_e}.png"))
            st.rerun()
        
        st.divider()
        if opcoes_esquemas:
            st.write("Ligações Atuais (Clique no X para remover opção):")
            for f in opcoes_esquemas:
                c_img, c_btn = st.columns([4, 1])
                c_img.write(f"🔹 {f}")
                if c_btn.button("Excluir Opção", key=f"del_opt_{f}"):
                    os.remove(os.path.join(PASTA_ESQUEMAS, f"{f}.png"))
                    st.rerun()

st.markdown("<p style='text-align:center; color:#444; margin-top:50px;'>Pablo Motores © 2026</p>", unsafe_allow_html=True)
