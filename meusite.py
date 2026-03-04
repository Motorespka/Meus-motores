import streamlit as st
import pandas as pd
import os
import hashlib
import re
from PIL import Image

# --- 1. CONFIGURAÇÕES E PASTAS ---
ARQUIVO_USUARIOS = 'usuarios.csv'
ARQUIVO_CSV = 'meubancodedados.csv'
LINK_SHEETS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTFbH81UYKGJ6dQvKotxdv4hDxecLmiGUPHN46iexbw8NeS8_e2XdyZnZ8WJnL2XRTLCbFDbBKo_NGE/pub?output=csv"
PASTA_ESQUEMAS = 'esquemas_fotos'
CHAVE_MESTRA_CHEFIA = "PABLO2026"

if not os.path.exists(PASTA_ESQUEMAS): os.makedirs(PASTA_ESQUEMAS)

# --- 2. BANCO DE DADOS TÉCNICO UNIFICADO (WEG / HERCULES / NBR) ---
# Seção em mm² para fios de cobre esmaltado (Dados oficiais de engenharia)
TABELA_AWG_OFICIAL = {
    '10': 5.26, '11': 4.17, '12': 3.31, '13': 2.63, '14': 2.08, 
    '15': 1.65, '16': 1.31, '17': 1.04, '18': 0.823, '19': 0.653,
    '20': 0.518, '21': 0.410, '22': 0.326, '23': 0.258, '24': 0.205, 
    '25': 0.162, '26': 0.129, '27': 0.102, '28': 0.081, '29': 0.064, '30': 0.051
}

# --- 3. FUNÇÕES DE ENGENHARIA AUTOMÁTICA ---
def calcular_secao_tecnica(texto_fio):
    """Detecta automaticamente fios simples ou múltiplos e calcula a área real em mm²"""
    try:
        texto = str(texto_fio).lower().replace('awg', '').strip()
        # Padrão para múltiplos fios (ex: 2x21, 3 x 20)
        if 'x' in texto:
            partes = texto.split('x')
            quantidade = int(re.findall(r'\d+', partes[0])[0])
            bitola = partes[1].strip()
            return quantidade * TABELA_AWG_OFICIAL.get(bitola, 0)
        # Padrão para fio único
        bitola_unica = re.findall(r'\d+', texto)[0]
        return TABELA_AWG_OFICIAL.get(bitola_unica, 0)
    except:
        return 0

def validar_seguranca_motor(area_orig, area_nova):
    """Analisa o risco técnico com base na perda de condutividade"""
    if area_orig <= 0: return "#7f8c8d", "DADOS ORIGINAIS NÃO ENCONTRADOS"
    
    # Diferença percentual de cobre
    diff = ((area_nova - area_orig) / area_orig) * 100
    
    if -2.0 <= diff <= 5.0:
        return "#2ecc71", f"✅ SEGURANÇA MÁXIMA: {diff:.1f}% (Equivalente WEG)"
    elif -5.0 <= diff < -2.0:
        return "#f1c40f", f"⚠️ ATENÇÃO: Perda de {abs(diff):.1f}%. Motor pode aquecer acima do normal."
    elif diff > 5.0:
        return "#3498db", f"🔵 ALERTA: Excesso de {diff:.1f}%. Verifique se o fio cabe na ranhura!"
    else:
        return "#e74c3c", f"🚨 RISCO CRÍTICO: Falta {abs(diff):.1f}% de cobre. O motor irá queimar!"

# --- 4. FUNÇÕES DE DADOS ---
@st.cache_data(ttl=60)
def carregar_dados():
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
    return pd.concat(dfs, ignore_index=True).fillna("None") if dfs else pd.DataFrame()

# --- 5. INTERFACE (ÁREA LOGADA) ---
st.set_page_config(page_title="Pablo Motores | Gestão Pro", layout="wide")

if 'user_data' not in st.session_state or st.session_state['user_data'] is None:
    st.error("Acesso Negado. Faça Login.")
    st.stop()

user = st.session_state['user_data']
e_admin = (user['perfil'] == 'admin')

# Menu Lateral com Selos
with st.sidebar:
    st.markdown(f"### 👤 {user['usuario'].upper()}")
    f_list = str(user.get('funcoes', '')).split('|')
    badges = ""
    if e_admin: badges += '👑 ADMIN '
    if 'rebobinagem' in f_list: badges += '⚡ REBOBINADOR '
    st.write(badges)
    
    menu = ["🔍 CONSULTA"]
    if e_admin: menu += ["➕ NOVO CADASTRO", "🖼️ ADICIONAR FOTO", "🗑️ LIXEIRA"]
    escolha = st.radio("Navegação:", menu)
    
    if st.button("Sair"):
        st.session_state['user_data'] = None
        st.rerun()

# --- ABA DE CONSULTA COM CÁLCULO AUTOMÁTICO ---
if escolha == "🔍 CONSULTA":
    st.markdown("<h1 style='text-align: center; color: #f1c40f;'>⚙️ PABLO UNIÃO MOTORES</h1>", unsafe_allow_html=True)
    df = carregar_dados()
    busca = st.text_input("🔍 Pesquisar por Marca, CV ou Dados Técnicos...")

    if not df.empty:
        df_f = df[df.apply(lambda row: row.astype(str).str.contains(busca, case=False).any(), axis=1)] if busca else df
        
        for idx, row in df_f.iterrows():
            with st.expander(f"📦 {row.get('Marca')} | {row.get('Potencia_CV')} CV | {row.get('RPM')} RPM"):
                c_original, c_simulador = st.columns([2, 2])
                
                # Extração Automática de Área
                fio_original_texto = str(row.get('Fio_Principal'))
                area_orig = calcular_secao_tecnica(fio_original_texto)
                
                with c_original:
                    st.markdown("### 📊 Dados de Fábrica")
                    st.write(f"**Fio Original:** {fio_original_texto}")
                    st.write(f"**Área do Cobre:** {area_orig:.3f} mm²")
                    st.info(f"**Esquema:** {row.get('Esquema_Marcado')}")
                    
                    # Exibe Esquema Visual se houver
                    for n in str(row.get('Esquema_Marcado')).split(" / "):
                        for ext in [".png", ".jpg", ".jpeg"]:
                            p = os.path.join(PASTA_ESQUEMAS, f"{n.strip()}{ext}")
                            if os.path.exists(p): st.image(p, caption=f"Esquema: {n}", width=300)

                with c_simulador:
                    st.markdown("### 🛠️ Simulador de Segurança")
                    st.write("Calcule a substituição com fios em estoque:")
                    
                    sub_col1, sub_col2 = st.columns(2)
                    qtd_simu = sub_col1.number_input("Qtd Fios", 1, 10, 2, key=f"q_{idx}")
                    bitola_simu = sub_col2.selectbox("Bitola AWG", list(TABELA_AWG_OFICIAL.keys()), index=7, key=f"b_{idx}")
                    
                    area_simu = qtd_simu * TABELA_AWG_OFICIAL[bitola_simu]
                    cor_status, msg_status = validar_seguranca_motor(area_orig, area_simu)
                    
                    st.markdown(f"""
                        <div style="background-color:{cor_status}; padding:20px; border-radius:12px; text-align:center; border: 2px solid white;">
                            <h3 style="color:white; margin:0; font-size:18px;">{msg_status}</h3>
                            <hr style="margin:10px 0;">
                            <p style="color:white; margin:0;"><b>Área Calculada: {area_simu:.3f} mm²</b></p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if e_admin:
                        st.divider()
                        if st.button("🗑️ Excluir Registro", key=f"del_{idx}"):
                            st.error("Remoção disponível na aba LIXEIRA.")

# --- DEMAIS ABAS (Cadastro, Foto, Lixeira) seguem conforme seu código original ---
