import streamlit as st
import pandas as pd
import os
import re
import urllib.parse
import random
import string
from datetime import datetime, timedelta

# --- 1. CONFIGURAÇÕES DE SEGURANÇA E ARQUIVOS ---
# Defina aqui os seus tokens de acesso (Você pode mudar esses nomes)
TOKEN_PRO = "PABLO123"      # Acesso para Wesley/Pablo
TOKEN_MESTRE = "MESTRE99"   # Acesso Total para Você

ARQUIVO_CSV = 'meubancodedados.csv'
ARQUIVO_FOTOS = 'biblioteca_fotos.csv'
PASTA_UPLOADS = 'uploads_ligacoes'

if not os.path.exists(PASTA_UPLOADS):
    os.makedirs(PASTA_UPLOADS)

# --- INICIALIZAÇÃO DE SESSÃO ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False
if 'perfil' not in st.session_state:
    st.session_state['perfil'] = None # 'cliente', 'pro', 'mestre'
if 'db_os' not in st.session_state:
    st.session_state['db_os'] = []

# --- 2. FUNÇÕES TÉCNICAS E AUXILIARES ---
def carregar_dados(arq, colunas):
    if not os.path.exists(arq) or os.stat(arq).st_size == 0:
        return pd.DataFrame(columns=colunas)
    df = pd.read_csv(arq, sep=';', encoding='utf-8-sig', dtype=str).fillna("")
    for col in colunas:
        if col not in df.columns: df[col] = ""
    return df

def salvar_dados(df, arq):
    df.fillna("").to_csv(arq, index=False, sep=';', encoding='utf-8-sig')

def calcular_area_mm2(texto_fio):
    # (Lógica AWG mantida conforme original)
    TABELA_AWG_TECNICA = {'4/0': 107.0, '3/0': 85.0, '2/0': 67.4, '1/0': 53.5, '1': 42.41, '2': 33.63, '3': 26.67, '4': 21.147, '5': 16.764, '6': 13.299, '7': 10.55, '8': 8.367, '9': 6.633, '10': 5.26, '11': 4.169, '12': 3.307, '13': 2.627, '14': 2.082, '15': 1.651, '16': 1.307, '17': 1.04, '18': 0.8235, '19': 0.6533, '20': 0.5191, '21': 0.4117, '22': 0.3247, '23': 0.2588, '24': 0.2051, '25': 0.1626, '26': 0.1282, '27': 0.1024, '28': 0.0804, '29': 0.0647, '30': 0.0507, '31': 0.0401, '32': 0.0324, '33': 0.0254, '34': 0.0201}
    try:
        texto = str(texto_fio).lower().replace('awg', '').strip()
        if 'x' in texto:
            partes = texto.split('x'); qtd = int(re.findall(r'\d+', partes[0])[0])
            bitola = partes[1].strip()
            return qtd * TABELA_AWG_TECNICA.get(bitola, 0.0)
        bitolas = re.findall(r'\d+', texto)
        return TABELA_AWG_TECNICA.get(bitolas[0], 0.0) if bitolas else 0.0
    except: return 0.0

# --- 3. TELA DE LOGIN / CADASTRO ---
def tela_login():
    st.title("⚙️ PABLO MOTORES - ACESSO")
    
    aba_login, aba_cad_cliente = st.tabs(["🔐 Entrar", "🆕 Cadastro Cliente"])
    
    with aba_login:
        tipo = st.radio("Entrar como:", ["👤 Cliente", "🛠️ Mecânico/Rebobinador", "🧠 Chefe"])
        
        if tipo == "👤 Cliente":
            user_cli = st.text_input("Usuário (Email ou Nome)")
            pass_cli = st.text_input("Senha", type="password")
            if st.button("Acessar Catálogo"):
                st.session_state['autenticado'] = True
                st.session_state['perfil'] = 'cliente'
                st.rerun()
        
        elif tipo == "🛠️ Mecânico/Rebobinador":
            token_p = st.text_input("Digite o Token da Oficina", type="password")
            if st.button("Validar Acesso Profissional"):
                if token_p == TOKEN_PRO:
                    st.session_state['autenticado'] = True
                    st.session_state['perfil'] = 'pro'
                    st.rerun()
                else: st.error("Token Profissional Inválido")

        elif tipo == "🧠 Chefe":
            token_m = st.text_input("Digite o Token Mestre", type="password")
            if st.button("Acesso Total"):
                if token_m == TOKEN_MESTRE:
                    st.session_state['autenticado'] = True
                    st.session_state['perfil'] = 'mestre'
                    st.rerun()
                else: st.error("Token Mestre Inválido")

    with aba_cad_cliente:
        st.info("Clientes podem visualizar dados básicos e esquemas de ligação.")
        new_user = st.text_input("Escolha um Nome de Usuário")
        new_pass = st.text_input("Escolha uma Senha", type="password")
        if st.button("Criar Minha Conta"):
            st.success("Conta criada! Vá na aba 'Entrar' para acessar.")

# --- 4. SISTEMA PRINCIPAL (PÓS-LOGIN) ---
if not st.session_state['autenticado']:
    tela_login()
else:
    # --- INTERFACE LOGADA ---
    st.set_page_config(page_title="Pablo Motores Pro", layout="wide")
    
    COL_MOTORES = ['Marca', 'Potencia_CV', 'RPM', 'Voltagem', 'Amperagem', 'Polaridade', 'Bobina_Principal', 'Fio_Principal', 'Bobina_Auxiliar', 'Fio_Auxiliar', 'Tipo_Ligacao', 'Rolamentos', 'Eixo_X', 'Eixo_Y', 'Capacitor', 'status']
    df_motores = carregar_dados(ARQUIVO_CSV, COL_MOTORES)
    df_fotos = carregar_dados(ARQUIVO_FOTOS, ['nome_ligacao', 'caminho_arquivo'])

    with st.sidebar:
        st.title(f"Perfil: {st.session_state['perfil'].upper()}")
        if st.button("🚪 Sair"):
            st.session_state['autenticado'] = False
            st.rerun()
        
        st.divider()
        opcoes_menu = ["🔍 CONSULTA"]
        if st.session_state['perfil'] in ['pro', 'mestre']:
            opcoes_menu += ["➕ NOVO MOTOR", "📊 PAINEL DE OS"]
        if st.session_state['perfil'] == 'mestre':
            opcoes_menu += ["🖼️ BIBLIOTECA", "🗑️ LIXEIRA"]
            
        menu = st.radio("Menu", opcoes_menu)

    # --- LÓGICA DE CONSULTA HIERÁRQUICA ---
    if menu == "🔍 CONSULTA":
        st.header("🔍 Banco de Dados")
        busca = st.text_input("Buscar motor...")
        df_f = df_motores[df_motores['status'] != 'deletado']
        if busca:
            df_f = df_f[df_f.apply(lambda r: r.astype(str).str.contains(busca, case=False).any(), axis=1)]

        for idx, row in df_f.iterrows():
            with st.expander(f"📦 {row['Marca']} | {row['Potencia_CV']} CV"):
                
                # ABA 1: CLIENTE (BÁSICO)
                tab_cli, tab_pro, tab_mestre = st.tabs(["🟢 BÁSICO", "🛠️ TÉCNICO", "🧠 ENGENHARIA"])
                
                with tab_cli:
                    st.subheader("Informações de Uso")
                    c1, c2 = st.columns(2)
                    c1.write(f"**Tensão:** {row['Voltagem']}V")
                    c1.write(f"**Amperagem:** {row['Amperagem']}A")
                    c1.write(f"**Capacitor:** {row['Capacitor']}")
                    
                    tipo = row['Tipo_Ligacao']
                    if tipo in df_fotos['nome_ligacao'].values:
                        c2.image(df_fotos[df_fotos['nome_ligacao'] == tipo]['caminho_arquivo'].values[0], caption="Ligação")
                    else: c2.info("Esquema na oficina.")

                with tab_pro:
                    if st.session_state['perfil'] in ['pro', 'mestre']:
                        st.subheader("Dados de Bancada")
                        p1, p2 = st.columns(2)
                        p1.write(f"**Fio Principal:** {row['Fio_Principal']}")
                        p1.write(f"**Espiras:** {row['Bobina_Principal']}")
                        p2.write(f"**Rolamentos:** {row['Rolamentos']}")
                        
                        if st.button("✈️ Enviar OS WhatsApp", key=f"z_{idx}"):
                            st.write("Link gerado!")
                    else:
                        st.warning("Acesso restrito a profissionais.")

                with tab_mestre:
                    if st.session_state['perfil'] == 'mestre':
                        st.subheader("Ferramentas de Engenharia")
                        # (Lógica de conversão de fios e exclusão aqui)
                        if st.button("🗑️ Deletar", key=f"d_{idx}"):
                            df_motores.at[idx, 'status'] = 'deletado'
                            salvar_dados(df_motores, ARQUIVO_CSV); st.rerun()
                    else:
                        st.warning("Acesso restrito ao Chefe.")

    # --- ABA NOVO MOTOR (RESTRITO) ---
    elif menu == "➕ NOVO MOTOR":
        if st.session_state['perfil'] in ['pro', 'mestre']:
            st.header("Cadastrar Motor")
            # (Seu formulário de cadastro aqui...)
        else:
            st.error("Você não tem permissão para cadastrar.")

    # (Restante das abas seguem a mesma lógica de permissão)
