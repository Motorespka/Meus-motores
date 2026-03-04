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
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #f1c40f;'>⚙️ PABLO MOTORES</h1>", unsafe_allow_html=True)

# --- LÓGICA DE ESQUEMAS DINÂMICOS ---
# Lista todos os nomes de arquivos na pasta (sem a extensão .png) para gerar os quadradinhos
opcoes_esquemas = [f.replace(".png", "").replace(".jpg", "") for f in os.listdir(PASTA_ESQUEMAS) if f.endswith(('.png', '.jpg'))]

# --- NAVEGAÇÃO ---
abas = ["🔍 CONSULTA", "➕ NOVO CADASTRO", "🖼️ ESQUEMAS"] if e_admin else ["🔍 CONSULTA"]
tabs = st.tabs(abas)

# --- ABA 1: CONSULTA ---
with tabs[0]:
    _, col_busca, _ = st.columns([1, 2, 1])
    with col_busca:
        busca = st.text_input("🔍 Buscar motor...")
    
    if os.path.exists(ARQUIVO_CSV):
        df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig').fillna("---").replace("None", "---")
        df_filtrado = df[df.astype(str).apply(lambda x: busca.lower() in x.str.lower().any(), axis=1)] if busca else df

        for idx, row in df_filtrado.iterrows():
            with st.expander(f"📦 {row.get('Marca')} | {row.get('Potencia_CV')} CV"):
                c1, c2, c3, c4 = st.columns([1, 1.2, 1.2, 2.5])
                
                with c1:
                    st.write("**DADOS**")
                    st.write(f"Polos: {row.get('Polaridade')}")
                    st.write(f"Volt: {row.get('Voltagem')}")
                
                with c2:
                    st.write("**PRINCIPAL**")
                    st.write(f"🔢 {row.get('Bobina_Principal')}")
                    st.write(f"🧵 {row.get('Fio_Principal')}")
                
                with c3:
                    st.write("**AUXILIAR**")
                    st.write(f"🔢 {row.get('Bobina_Auxiliar')}")
                    st.write(f"🧵 {row.get('Fio_Auxiliar')}")
                
                with c4:
                    st.write("**ESQUEMAS TÉCNICOS**")
                    ligacao_salva = str(row.get('Esquema_Marcado'))
                    st.markdown(f"<div class='caixa-ligacao'>🔗 {ligacao_salva}</div>", unsafe_allow_html=True)
                    
                    # Mostra as imagens de todos os esquemas que foram marcados
                    ligacoes_lista = ligacao_salva.split(" / ")
                    cols_img = st.columns(len(ligacoes_lista) if len(ligacoes_lista) > 0 else 1)
                    for i, nome_lig in enumerate(ligacoes_lista):
                        caminho = os.path.join(PASTA_ESQUEMAS, f"{nome_lig}.png")
                        if os.path.exists(caminho):
                            cols_img[i].image(caminho, caption=nome_lig, use_container_width=True)

                if e_admin:
                    if st.button(f"🗑️ Apagar Registro", key=f"del_{idx}"):
                        df.drop(idx).to_csv(ARQUIVO_CSV, index=False, sep=';', encoding='utf-8-sig')
                        st.rerun()

# --- ABA 2: CADASTRO (DINÂMICO) ---
if e_admin:
    with tabs[1]:
        st.subheader("📝 Novo Cadastro")
        with st.form("form_pablo", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                marca = st.text_input("Marca")
                potencia = st.text_input("Potência (CV)")
                polos = st.selectbox("Polaridade", ["2", "4", "6", "8", "12"])
                volt = st.text_input("Voltagem")
            with col2:
                b_p = st.text_input("Bobina Principal")
                f_p = st.text_input("Fio Principal")
                b_a = st.text_input("Bobina Auxiliar")
                f_a = st.text_input("Fio Auxiliar")
            with col3:
                st.write("**Marque as Ligações Disponíveis:**")
                # AQUI A MAGIA ACONTECE: Gera um checkbox para cada foto na pasta
                dict_checkboxes = {}
                for opt in opcoes_esquemas:
                    dict_checkboxes[opt] = st.checkbox(opt)

            if st.form_submit_button("💾 SALVAR MOTOR"):
                # Filtra apenas o que foi marcado
                selecionados = [nome for nome, marcado in dict_checkboxes.items() if marcado]
                
                novo = {
                    'Marca': marca, 'Potencia_CV': potencia, 'Polaridade': polos,
                    'Voltagem': volt, 'Bobina_Principal': b_p, 'Fio_Principal': f_p,
                    'Bobina_Auxiliar': b_a, 'Fio_Auxiliar': f_a,
                    'Esquema_Marcado': " / ".join(selecionados) if selecionados else "---"
                }
                pd.DataFrame([novo]).to_csv(ARQUIVO_CSV, mode='a', header=not os.path.exists(ARQUIVO_CSV), index=False, sep=';', encoding='utf-8-sig')
                st.success("✅ Motor e Ligações Salvas!")

# --- ABA 3: ESQUEMAS (GERADOR DE OPÇÕES) ---
if e_admin:
    with tabs[2]:
        st.subheader("🖼️ Gerenciador de Ligações")
        st.info("Ao salvar uma foto aqui, ela vira uma opção de 'quadradinho' no cadastro automaticamente!")
        
        up = st.file_uploader("Upload do Desenho (Paint)", type=['png', 'jpg'])
        nome_esquema = st.text_input("Nome da Ligação (Ex: Estrela, 6 Pontas, Dahlander)")
        
        if st.button("Criar Nova Opção de Ligação") and up and nome_esquema:
            # Salva a imagem com o nome digitado
            Image.open(up).save(os.path.join(PASTA_ESQUEMAS, f"{nome_esquema}.png"))
            st.success(f"Opção '{nome_esquema}' criada! Vá na aba de Cadastro para ver o novo quadrado.")
            st.rerun()
        
        st.divider()
        st.write("📋 **Ligações já cadastradas:**")
        if opcoes_esquemas:
            cols = st.columns(4)
            for i, foto in enumerate(opcoes_esquemas):
                cols[i % 4].image(os.path.join(PASTA_ESQUEMAS, f"{foto}.png"), caption=foto, use_container_width=True)
