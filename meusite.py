import streamlit as st
import pandas as pd
import os
import hashlib
from PIL import Image

# --- 1. CONFIGURAÇÕES DE ARQUIVOS ---
ARQUIVO_USUARIOS = 'usuarios.csv'
ARQUIVO_CSV = 'meubancodedados.csv'
LINK_SHEETS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTFbH81UYKGJ6dQvKotxdv4hDxecLmiGUPHN46iexbw8NeS8_e2XdyZnZ8WJnL2XRTLCbFDbBKo_NGE/pub?output=csv"
PASTA_ESQUEMAS = 'esquemas_fotos'
CHAVE_MESTRA_CHEFIA = "PABLO2026"

if not os.path.exists(PASTA_ESQUEMAS): os.makedirs(PASTA_ESQUEMAS)

# Tabela AWG Técnica
TABELA_AWG = {
    10: 5.26, 11: 4.17, 12: 3.31, 13: 2.63, 14: 2.08, 15: 1.65, 16: 1.31,
    17: 1.04, 18: 0.823, 19: 0.653, 20: 0.518, 21: 0.410, 22: 0.326,
    23: 0.258, 24: 0.205, 25: 0.162, 26: 0.129
}

# --- 2. FUNÇÕES DE SEGURANÇA E DADOS ---
def hash_senha(senha):
    return hashlib.sha256(str.encode(senha)).hexdigest()

def salvar_usuario(usuario, senha, funcoes, perfil):
    colunas = ['usuario', 'senha', 'funcoes', 'perfil']
    if not os.path.exists(ARQUIVO_USUARIOS):
        pd.DataFrame(columns=colunas).to_csv(ARQUIVO_USUARIOS, index=False, sep=';', encoding='utf-8-sig')
    
    df = pd.read_csv(ARQUIVO_USUARIOS, sep=';', encoding='utf-8-sig')
    if usuario.lower() in df['usuario'].astype(str).str.lower().values:
        return False
    
    funcoes_str = "|".join(funcoes)
    novo_u = pd.DataFrame([{'usuario': usuario.lower(), 'senha': hash_senha(senha), 'funcoes': funcoes_str, 'perfil': perfil}])
    novo_u.to_csv(ARQUIVO_USUARIOS, mode='a', header=False, index=False, sep=';', encoding='utf-8-sig')
    return True

def validar_login(usuario, senha):
    if not os.path.exists(ARQUIVO_USUARIOS): return False
    try:
        df = pd.read_csv(ARQUIVO_USUARIOS, sep=';', encoding='utf-8-sig')
        senha_h = hash_senha(senha)
        u_check = df[(df['usuario'].astype(str).str.lower() == usuario.lower()) & (df['senha'] == senha_h)]
        if not u_check.empty:
            return u_check.iloc[0].to_dict()
    except: pass
    return False

@st.cache_data(ttl=60)
def carregar_motores():
    dfs = []
    try:
        df_n = pd.read_csv(LINK_SHEETS, dtype=str)
        if not df_n.empty: dfs.append(df_n)
    except: pass
    if os.path.exists(ARQUIVO_CSV):
        try:
            df_l = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig', dtype=str)
            if not df_l.empty: dfs.append(df_l)
        except: pass
    return pd.concat(dfs, ignore_index=True).drop_duplicates() if dfs else pd.DataFrame()

# --- 3. INTERFACE DE ACESSO ---
st.set_page_config(page_title="Pablo União", layout="wide", page_icon="⚙️")

if 'user_data' not in st.session_state:
    st.session_state['user_data'] = None

if not st.session_state['user_data']:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; color: #f1c40f;'>🛠️ PABLO UNIÃO</h1>", unsafe_allow_html=True)
        t_login, t_cad = st.tabs(["🔐 ACESSAR", "📝 CADASTRAR-SE"])
        
        with t_login:
            u = st.text_input("Usuário", key="l_u")
            s = st.text_input("Senha", type="password", key="l_s")
            if st.button("ENTRAR 🚀", use_container_width=True):
                dados = validar_login(u, s)
                if dados:
                    st.session_state['user_data'] = dados
                    st.rerun()
                else: st.error("Usuário ou senha inválidos.")

        with t_cad:
            nu = st.text_input("Novo Usuário")
            ns = st.text_input("Nova Senha", type="password")
            st.markdown("**Selecione suas funções:**")
            fm = st.checkbox("Mecânica 🔧"); fr = st.checkbox("Rebobinagem ⚡"); fc = st.checkbox("Chefia 👑")
            cv = ""
            if fc: cv = st.text_input("Chave de Chefia", type="password")
            
            if st.button("FINALIZAR CADASTRO ✅", use_container_width=True):
                f_list = []
                if fm: f_list.append("mecanica")
                if fr: f_list.append("rebobinagem")
                if fc: f_list.append("chefia")
                
                if not f_list: st.warning("Selecione uma função.")
                elif fc and cv != CHAVE_MESTRA_CHEFIA: st.error("Chave inválida.")
                elif nu and ns:
                    perf = "admin" if fc else "mecanico"
                    if salvar_usuario(nu, ns, f_list, perf): st.success("Sucesso! Vá em Acessar.")
                    else: st.error("Usuário já existe.")
    st.stop()

# --- 4. ÁREA DO SISTEMA ---
user = st.session_state['user_data']
funcoes = str(user['funcoes']).split("|")

with st.sidebar:
    st.title("PABLO UNIÃO")
    st.write(f"👤 **{user['usuario'].upper()}**")
    if st.button("Sair"):
        st.session_state['user_data'] = None
        st.rerun()

# Definição de Abas por Permissão
abas = []
if "mecanica" in funcoes or user['perfil'] == "admin": abas.append("🔧 MECÂNICA")
if "rebobinagem" in funcoes or user['perfil'] == "admin": abas.append("⚡ REBOBINAGEM")
if user['perfil'] == "admin": abas.append("📊 ADMINISTRAÇÃO")

if abas:
    tabs = st.tabs(abas)
    for i, nome in enumerate(abas):
        with tabs[i]:
            if "MECÂNICA" in nome:
                st.subheader("Manutenção Mecânica")
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.text_input("Ordem de Serviço (OS)")
                    st.selectbox("Serviço", ["Troca de Rolamentos", "Embuchar Tampa", "Troca de Eixo", "Pintura"])
                with col_m2:
                    st.text_area("Observações da Mecânica")
                st.button("Salvar Registro Mecânico")

            if "REBOBINAGEM" in nome:
                st.subheader("Consulta Técnica e Fios")
                df_m = carregar_motores()
                busca = st.text_input("🔍 Pesquisar Motor (Marca, CV, RPM...)")
                if not df_m.empty:
                    df_f = df_m[df_m.apply(lambda r: r.astype(str).str.contains(busca, case=False).any(), axis=1)] if busca else df_m
                    for idx, row in df_f.iterrows():
                        with st.expander(f"📦 {row.get('Marca')} - {row.get('Potencia_CV')} CV"):
                            st.write(f"**Fio Principal:** {row.get('Fio_Principal')} | **Auxiliar:** {row.get('Fio_Auxiliar')}")
                            # Lógica de Imagem
                            lig = str(row.get('Esquema_Marcado'))
                            if lig != "None":
                                for ext in [".png", ".jpg"]:
                                    p = os.path.join(PASTA_ESQUEMAS, f"{lig.strip()}{ext}")
                                    if os.path.exists(p): st.image(p, width=400)
                
                st.divider()
                st.subheader("🧪 Simulador AWG")
                ca, cb = st.columns(2)
                f_o = ca.selectbox("Fio Original", list(TABELA_AWG.keys()))
                q_o = ca.number_input("Qtd Fios", min_value=1, value=1)
                f_s = cb.selectbox("Substituir por", list(TABELA_AWG.keys()))
                area = TABELA_AWG[f_o] * q_o
                st.success(f"Área Total: {area:.3f} mm² | Necessário: **{(area/TABELA_AWG[f_s]):.2f}** fios do {f_s}")

            if "ADMINISTRAÇÃO" in nome:
                st.subheader("Painel de Controle Pablo")
                st.write("Aqui você pode gerenciar o banco de dados e usuários.")
                if st.button("Limpar Cache de Dados"):
                    st.cache_data.clear()
                    st.rerun()
