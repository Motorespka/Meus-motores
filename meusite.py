import streamlit as st
import pandas as pd
import os
import hashlib
from PIL import Image

# --- 1. CONFIGURAÇÕES E PASTAS ---
ARQUIVO_USUARIOS = 'usuarios.csv'
ARQUIVO_CSV = 'meubancodedados.csv'
LINK_SHEETS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTFbH81UYKGJ6dQvKotxdv4hDxecLmiGUPHN46iexbw8NeS8_e2XdyZnZ8WJnL2XRTLCbFDbBKo_NGE/pub?output=csv"
PASTA_ESQUEMAS = 'esquemas_fotos'
CHAVE_MESTRA_CHEFIA = "PABLO2026"

if not os.path.exists(PASTA_ESQUEMAS): os.makedirs(PASTA_ESQUEMAS)

st.set_page_config(page_title="Pablo Motores | Gestão Profissional", layout="wide", initial_sidebar_state="expanded")

# --- 2. FUNÇÕES DE SEGURANÇA E DADOS ---
def hash_senha(senha):
    return hashlib.sha256(str.encode(senha)).hexdigest()

def validar_login(usuario, senha):
    if not os.path.exists(ARQUIVO_USUARIOS): return False
    try:
        df = pd.read_csv(ARQUIVO_USUARIOS, sep=';', encoding='utf-8-sig')
        senha_h = hash_senha(senha)
        u_check = df[(df['usuario'].astype(str).str.lower() == usuario.lower()) & (df['senha'] == senha_h)]
        if not u_check.empty: return u_check.iloc[0].to_dict()
    except: pass
    return False

@st.cache_data(ttl=60)
def carregar_dados():
    dfs = []
    try:
        df_nuvem = pd.read_csv(LINK_SHEETS, dtype=str, storage_options={'timeout': 5})
        if not df_nuvem.empty: dfs.append(df_nuvem)
    except: pass
    if os.path.exists(ARQUIVO_CSV):
        try:
            df_local = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig', dtype=str)
            if not df_local.empty: dfs.append(df_local)
        except: pass
    if not dfs: return pd.DataFrame()
    return pd.concat(dfs, ignore_index=True).fillna("None")

def salvar_csv_local(df):
    df.to_csv(ARQUIVO_CSV, index=False, sep=';', encoding='utf-8-sig')
    st.cache_data.clear()

# --- 3. FLUXO DE ACESSO (LOGIN) ---
if 'user_data' not in st.session_state: st.session_state['user_data'] = None

if not st.session_state['user_data']:
    # [Mantém o seu formulário de login/cadastro original aqui...]
    # (Para brevidade, assumimos que o usuário loga e preenche o session_state)
    st.warning("Por favor, faça login para acessar o sistema.")
    st.stop()

# --- 4. ÁREA LOGADA ---
user = st.session_state['user_data']
e_admin = (user['perfil'] == 'admin')
funcoes_usuario = str(user.get('funcoes', '')).split("|")

with st.sidebar:
    st.markdown(f"### 👤 {user['usuario'].upper()}")
    # Selos
    selos = ""
    if e_admin: selos += ' <span style="background: #f1c40f; color: black; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: bold;">👑 ADMIN</span>'
    if "rebobinagem" in funcoes_usuario: selos += ' <span style="background: #3498db; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: bold;">⚡ REBOBINADOR</span>'
    st.markdown(selos, unsafe_allow_html=True)
    
    menu = ["🔍 CONSULTA"]
    if e_admin: menu += ["➕ NOVO CADASTRO", "🖼️ ADICIONAR FOTO", "🗑️ LIXEIRA"]
    escolha = st.radio("Navegação:", menu)
    
    if st.button("Sair"):
        st.session_state['user_data'] = None
        st.rerun()

# --- ABA: CONSULTA ---
if escolha == "🔍 CONSULTA":
    st.markdown("<h1 style='text-align: center; color: #f1c40f;'>⚙️ PABLO MOTORES</h1>", unsafe_allow_html=True)
    df = carregar_dados()
    busca = st.text_input("🔍 Pesquisar por Marca, CV, RPM ou Fio...")

    if not df.empty:
        # Filtro de busca
        df_f = df[df.apply(lambda row: row.astype(str).str.contains(busca, case=False).any(), axis=1)] if busca else df
        
        for idx, row in df_f.iterrows():
            with st.expander(f"📦 {row.get('Marca')} | {row.get('Potencia_CV')} CV | {row.get('RPM')} RPM"):
                col_info, col_btns = st.columns([3, 1])
                
                with col_info:
                    st.write(f"**⚡ Fio Principal:** {row.get('Fio_Principal')}")
                    st.write(f"**🌀 Grupo:** {row.get('Bobina_Principal')}")
                    st.write(f"**🔗 Ligação:** {row.get('Esquema_Marcado')}")
                    
                    # Mostrar Esquema se existir
                    lig = str(row.get('Esquema_Marcado'))
                    for n in lig.split(" / "):
                        for ext in [".png", ".jpg", ".jpeg"]:
                            p = os.path.join(PASTA_ESQUEMAS, f"{n.strip()}{ext}")
                            if os.path.exists(p): st.image(p, width=300)

                with col_btns:
                    # BOTÃO GAMBIARRA (SIMULADOR)
                    if st.button("🛠️ Gambiarra", key=f"gamb_{idx}"):
                        st.session_state[f"show_gamb_{idx}"] = not st.session_state.get(f"show_gamb_{idx}", False)
                    
                    if e_admin:
                        # BOTÃO EDITAR (ADMIN)
                        if st.button("📝 Editar", key=f"edit_{idx}"):
                            st.session_state[f"edit_mode_{idx}"] = True
                        
                        # BOTÃO EXCLUIR (ADMIN)
                        if st.button("🗑️ Excluir", key=f"del_{idx}"):
                            df = df.drop(idx)
                            salvar_csv_local(df)
                            st.success("Motor removido!")
                            st.rerun()

                # --- MODO GAMBIARRA (NÃO SALVA NO BANCO) ---
                if st.session_state.get(f"show_gamb_{idx}"):
                    st.info("💡 **SIMULADOR DE GAMBIARRA** (Cálculo temporário)")
                    c1, c2 = st.columns(2)
                    fio_fake = c1.text_input("Simular novo fio", placeholder="Ex: 2x 21 AWG", key=f"fake_fio_{idx}")
                    c2.write(f"Original: {row.get('Fio_Principal')}")
                    st.warning("Esta alteração é apenas visual e não será salva no sistema.")

                # --- MODO EDIÇÃO (SALVA NO BANCO) ---
                if e_admin and st.session_state.get(f"edit_mode_{idx}"):
                    with st.form(f"edit_form_{idx}"):
                        st.write("🔧 **Editando dados originais**")
                        novo_fio = st.text_input("Alterar Fio Principal", value=row.get('Fio_Principal'))
                        nova_marca = st.text_input("Alterar Marca", value=row.get('Marca'))
                        
                        if st.form_submit_button("💾 Confirmar Alteração"):
                            df.at[idx, 'Fio_Principal'] = novo_fio
                            df.at[idx, 'Marca'] = nova_marca
                            salvar_csv_local(df)
                            st.session_state[f"edit_mode_{idx}"] = False
                            st.success("Dados atualizados!")
                            st.rerun()

# --- (Restante das Abas: Novo Cadastro, Adicionar Foto e Lixeira permanecem iguais) ---
