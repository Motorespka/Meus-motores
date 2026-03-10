# app.py
import streamlit as st
import pandas as pd

page_mestre = None
CHAVE_MESTRE = "Pablo123"

if "logado" not in st.session_state:
    st.session_state.logado = False

# --- Configurações da página ---
st.set_page_config(
    page_title="Rebobineiro",
    page_icon="🌐",
    layout="wide"
)
st.sidebar.title("Acesso")
# --- Cabeçalho ---
st.title("🌐 Bem-vindo ao Rebobineiro")
st.markdown("Este site é feito de Rebobinador para Rebobinador!")
                 
senha = st.sidebar.text_input("Chave mestre", type="password")

if st.sidebar.button("Entrar"):
    if senha == CHAVE_MESTRE:
        st.session_state.logado = True
        st.sidebar.success("Acesso liberado")
else:
    st.sidebar.error("Chave incorreta")
    st.sidebar.markdown("---")

# --- Menu lateral ---
st.sidebar.title("Menu")

st.sidebar.markdown("### Consulta")
page = st.sidebar.radio(
    "",
    ["Consultar Cálculo"]
)

if st.session_state.logado:

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Mestre")

    page_mestre = st.sidebar.radio(
    "",
    ["Orçamento", "Cadastrar Motor", "Imagem"]
)

# define qual página está ativa
if page_mestre: page = page_mestre
    
# --- Navegação ---
if page == "Consultar Cálculo":
    st.header("Consultar Cálculo")

elif page == "Orçamento":
    st.header("Orçamento")

elif page == "Cadastrar Motor":
    st.header("Cadastrar Motor")

elif page == "Imagem":
    st.header("Imagem")

# --- Página Home ---
if page == "Home":
    st.header("Página Inicial")
    st.write("Aqui você pode colocar informações sobre seu site, projetos ou serviços.")
    st.image("https://via.placeholder.com/600x200.png?text=Imagem+de+Cabeçalho", width=600)

# --- Página Dados ---
elif page == "Dados":
    st.header("Visualização de Dados")
    # Exemplo de DataFrame
    data = {
        "Nome": ["Alice", "Bob", "Carlos", "Diana"],
        "Idade": [25, 30, 22, 28],
        "Cidade": ["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Curitiba"]
    }
    df = pd.DataFrame(data)
    st.dataframe(df)
    
    st.download_button(
        label="Baixar dados",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name='dados.csv',
        mime='text/csv'
    )

# --- Página Sobre ---
elif page == "Sobre":
    st.header("Sobre Este Site")
    st.markdown("""
    - Criado com [Streamlit](https://streamlit.io/)
    - Modelo básico atualizado sem bibliotecas extras
    - Ideal para dashboards, portfólios ou projetos de dados
    """)