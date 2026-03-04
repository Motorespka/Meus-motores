import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime
from PIL import Image

# --- 1. CONFIGURAÇÕES E PASTAS ---
ARQUIVO_USUARIOS = 'usuarios.csv'
ARQUIVO_CSV = 'meubancodedados.csv'
LINK_SHEETS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTFbH81UYKGJ6dQvKotxdv4hDxecLmiGUPHN46iexbw8NeS8_e2XdyZnZ8WJnL2XRTLCbFDbBKo_NGE/pub?output=csv"
PASTA_ESQUEMAS = 'esquemas_fotos'
CHAVE_MESTRA_CHEFIA = "PABLO2026"

if not os.path.exists(PASTA_ESQUEMAS): os.makedirs(PASTA_ESQUEMAS)

st.set_page_config(page_title="Pablo Motores | Gestão Profissional", layout="wide", initial_sidebar_state="expanded")

# --- 2. FUNÇÕES DE SEGURANÇA (LOGIN) ---
def hash_senha(senha):
    return hashlib.sha256(str.encode(senha)).hexdigest()

def criar_csv_usuarios():
    df = pd.DataFrame(columns=['usuario', 'senha', 'funcoes', 'perfil'])
    df.to_csv(ARQUIVO_USUARIOS, index=False, sep=';', encoding='utf-8-sig')
    return df

def salvar_usuario(usuario, senha, funcoes, perfil):
    if not os.path.exists(ARQUIVO_USUARIOS):
        df = criar_csv_usuarios()
    else:
        try:
            df = pd.read_csv(ARQUIVO_USUARIOS, sep=';', encoding='utf-8-sig')
        except:
            df = criar_csv_usuarios()

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
    except:
        pass
    return False

# --- 3. FUNÇÕES DE DADOS (MOTORES) ---
@st.cache_data(ttl=60)
def carregar_dados():
    dfs = []
    try:
        df_nuvem = pd.read_csv(LINK_SHEETS, dtype=str, storage_options={'timeout': 5})
        if not df_nuvem.empty:
            df_nuvem.columns = df_nuvem.columns.str.strip()
            dfs.append(df_nuvem)
    except: pass

    if os.path.exists(ARQUIVO_CSV):
        try:
            df_local = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig', dtype=str)
            if not df_local.empty:
                df_local.columns = df_local.columns.str.strip()
                dfs.append(df_local)
        except: pass

    if not dfs: return pd.DataFrame()
    df_geral = pd.concat(dfs, ignore_index=True).fillna("None")
    colunas_chave = ['Marca', 'Potencia_CV', 'RPM']
    if all(c in df_geral.columns for c in colunas_chave):
        df_geral = df_geral.drop_duplicates(subset=colunas_chave, keep='first')
    return df_geral

# --- 4. FLUXO DE ACESSO ---
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = None

if not st.session_state['user_data']:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; color: #f1c40f;'>🛠️ PABLO UNIÃO</h1>", unsafe_allow_html=True)
        tab_login, tab_cad = st.tabs(["🔐 ACESSAR", "📝 CADASTRAR-SE"])
        
        with tab_login:
            u = st.text_input("Usuário", key="login_u")
            s = st.text_input("Senha", type="password", key="login_s")
            if st.button("ENTRAR 🚀", use_container_width=True):
                dados = validar_login(u, s)
                if dados:
                    st.session_state['user_data'] = dados
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")

        with tab_cad:
            nu = st.text_input("Escolha um Usuário", key="cad_u")
            ns = st.text_input("Escolha uma Senha", type="password", key="cad_s")
            st.markdown("---")
            st.write("📂 **Selecione sua função principal:**")
            fm = st.checkbox("Mecânica 🔧")
            fr = st.checkbox("Rebobinagem ⚡")
            fc = st.checkbox("Chefia / Admin 👑")
            
            chave = ""
            if fc: chave = st.text_input("Chave de Acesso Chefia", type="password")
            
            if st.button("FINALIZAR CADASTRO ✅", use_container_width=True):
                f_list = []
                if fm: f_list.append("mecanica")
                if fr: f_list.append("rebobinagem")
                if fc: f_list.append("admin")

                if not f_list:
                    st.warning("Selecione pelo menos uma função.")
                elif fc and chave != CHAVE_MESTRA_CHEFIA:
                    st.error("Chave de Chefia incorreta!")
                elif nu and ns:
                    perf = "admin" if fc else "usuario"
                    if salvar_usuario(nu, ns, f_list, perf):
                        st.success("Conta criada! Vá na aba ACESSAR.")
                    else:
                        st.error("Esse usuário já existe.")
    st.stop()

# --- 5. ÁREA DO SISTEMA (PÓS-LOGIN) ---
user = st.session_state['user_data']
e_admin = (user['perfil'] == 'admin')
funcoes_usuario = str(user.get('funcoes', '')).split("|")

with st.sidebar:
    st.markdown(f"### 👤 {user['usuario'].upper()}")
    
    # --- SISTEMA DE SELOS (BADGES) ---
    selos_html = '<div style="display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 10px;">'
    if e_admin:
        selos_html += '<span style="background-color: #f1c40f; color: black; padding: 2px 10px; border-radius: 12px; font-size: 11px; font-weight: bold;">👑 ADMIN</span>'
    if "rebobinagem" in funcoes_usuario:
        selos_html += '<span style="background-color: #3498db; color: white; padding: 2px 10px; border-radius: 12px; font-size: 11px; font-weight: bold;">⚡ REBOBINADOR</span>'
    if "mecanica" in funcoes_usuario:
        selos_html += '<span style="background-color: #2ecc71; color: white; padding: 2px 10px; border-radius: 12px; font-size: 11px; font-weight: bold;">🔧 MECÂNICO</span>'
    selos_html += '</div>'
    
    st.markdown(selos_html, unsafe_allow_html=True)
    st.markdown("---")

    menu = ["🔍 CONSULTA"]
    if e_admin:
        menu += ["➕ NOVO CADASTRO", "🖼️ ADICIONAR FOTO", "🗑️ LIXEIRA"]
    
    escolha = st.radio("Navegação:", menu)
    st.markdown("---")
    if st.button("Sair / Logoff", use_container_width=True):
        st.session_state['user_data'] = None
        st.rerun()

# --- LÓGICA DAS PÁGINAS ---
if escolha == "🔍 CONSULTA":
    st.markdown("<h1 style='text-align: center; color: #f1c40f;'>⚙️ PABLO MOTORES</h1>", unsafe_allow_html=True)
    df = carregar_dados()
    busca = st.text_input("🔍 Pesquisar por Marca, CV ou detalhes...")
    if not df.empty:
        df_f = df[df.apply(lambda row: row.astype(str).str.contains(busca, case=False).any(), axis=1)] if busca else df
        for idx, row in df_f.iterrows():
            with st.expander(f"📦 {row.get('Marca')} | {row.get('Potencia_CV')} CV | {row.get('RPM')} RPM"):
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.markdown("### 📊 GERAL")
                    st.write(f"**Polos:** {row.get('Polaridade')}"); st.write(f"**Volt:** {row.get('Voltagem')}")
                with c2:
                    st.markdown("### 🌀 PRINCIPAL")
                    st.write(f"**Grupo:** {row.get('Bobina_Principal')}"); st.write(f"**Fio:** {row.get('Fio_Principal')}")
                with c3:
                    st.markdown("### ⚡ AUXILIAR")
                    st.write(f"**Fio:** {row.get('Fio_Auxiliar')}"); st.write(f"**Capacitor:** {row.get('Capacitor')}")
                with c4:
                    st.markdown("### 🔗 LIGAÇÃO")
                    lig = str(row.get('Esquema_Marcado'))
                    for n in lig.split(" / "):
                        for ext in [".png", ".jpg", ".jpeg"]:
                            p = os.path.join(PASTA_ESQUEMAS, f"{n.strip()}{ext}")
                            if os.path.exists(p): st.image(p)

elif escolha == "➕ NOVO CADASTRO" and e_admin:
    st.markdown("## ➕ Cadastrar Novo Motor")
    lista_fotos = [f.split(".")[0] for f in os.listdir(PASTA_ESQUEMAS) if f.endswith(('.png', '.jpg', '.jpeg'))]
    with st.form("cadastro_pablo"):
        c1, c2, c3 = st.columns(3)
        with c1:
            marca = st.text_input("Marca"); cv = st.text_input("Potência (CV)"); rpm = st.text_input("RPM")
            pol = st.text_input("Polaridade"); volt = st.text_input("Voltagem"); amp = st.text_input("Amperagem")
        with c2:
            camas_p = st.text_input("Grupo Principal"); fio_p = st.text_input("Fio Principal")
            rolam = st.text_input("Rolamentos"); eixo_x = st.text_input("Eixo X")
        with c3:
            camas_a = st.text_input("Grupo Auxiliar"); fio_a = st.text_input("Fio Auxiliar")
            capac = st.text_input("Capacitor"); eixo_y = st.text_input("Eixo Y")
        
        selecionados = []
        if lista_fotos:
            st.markdown("### 🖼️ Selecione os Esquemas")
            cols = st.columns(4)
            for i, foto in enumerate(lista_fotos):
                if cols[i % 4].checkbox(foto): selecionados.append(foto)
        
        if st.form_submit_button("💾 SALVAR DADOS"):
            novo = {
                'Marca': marca, 'Potencia_CV': cv, 'RPM': rpm, 'Polaridade': pol, 'Voltagem': volt, 'Amperagem': amp,
                'Fio_Principal': fio_p, 'Bobina_Principal': camas_p, 'Rolamentos': rolam, 'Fio_Auxiliar': fio_a,
                'Bobina_Auxiliar': camas_a, 'Capacitor': capac, 'Eixo_X': eixo_x, 'Eixo_Y': eixo_y,
                'Esquema_Marcado': " / ".join(selecionados) if selecionados else "None"
            }
            pd.DataFrame([novo]).to_csv(ARQUIVO_CSV, mode='a', header=not os.path.exists(ARQUIVO_CSV), index=False, sep=';', encoding='utf-8-sig')
            st.success("Motor salvo!"); st.cache_data.clear()

elif escolha == "🖼️ ADICIONAR FOTO" and e_admin:
    st.markdown("### 🖼️ Enviar Novo Esquema")
    arq = st.file_uploader("Escolha a imagem", type=['png', 'jpg', 'jpeg'])
    nome_f = st.text_input("Nome do Esquema")
    if st.button("Gravar") and arq and nome_f:
        Image.open(arq).save(os.path.join(PASTA_ESQUEMAS, f"{nome_f}.png"))
        st.success("Esquema salvo!"); st.rerun()

elif escolha == "🗑️ LIXEIRA" and e_admin:
    st.markdown("## 🗑️ Lixeira")
    df = carregar_dados()
    if not df.empty:
        st.dataframe(df)
        if st.button("LIMPAR TODO O BANCO DE DADOS"):
            if os.path.exists(ARQUIVO_CSV):
                os.remove(ARQUIVO_CSV); st.warning("Dados apagados."); st.cache_data.clear(); st.rerun()
