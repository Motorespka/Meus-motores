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

# --- 2. BANCO DE DADOS TÉCNICO (PADRÃO WEG/HERCULES) ---
TABELA_AWG_OFICIAL = {
    '10': 5.26, '11': 4.17, '12': 3.31, '13': 2.63, '14': 2.08, 
    '15': 1.65, '16': 1.31, '17': 1.04, '18': 0.823, '19': 0.653,
    '20': 0.518, '21': 0.410, '22': 0.326, '23': 0.258, '24': 0.205, 
    '25': 0.162, '26': 0.129, '27': 0.102, '28': 0.081, '29': 0.064, '30': 0.051
}

# --- 3. MOTOR DE INTELIGÊNCIA E CÁLCULO AUTOMÁTICO ---
def calcular_area_mm2(texto_fio):
    try:
        texto = str(texto_fio).lower().replace('awg', '').strip()
        if 'x' in texto:
            partes = texto.split('x')
            qtd = int(re.findall(r'\d+', partes[0])[0])
            bitola = partes[1].strip()
            return qtd * TABELA_AWG_OFICIAL.get(bitola, 0)
        bitola = re.findall(r'\d+', texto)[0]
        return TABELA_AWG_OFICIAL.get(bitola, 0)
    except:
        return 0

def gerar_sugestoes_automaticas(area_alvo):
    """Varre as bitolas e encontra combinações que batem com a área original"""
    if area_alvo <= 0: return []
    sugestoes = []
    bitolas_estoque = ['14', '15', '16', '17', '18', '19', '20', '21', '22', '23']
    
    for bitola in bitolas_estoque:
        area_unit = TABELA_AWG_OFICIAL[bitola]
        for qtd in range(1, 6): # Testa de 1x até 5x o fio
            area_teste = area_unit * qtd
            diff = ((area_teste - area_alvo) / area_alvo) * 100
            # Margem de segurança rigorosa: -3% a +5%
            if -3.0 <= diff <= 5.0:
                sugestoes.append({'label': f"{qtd}x {bitola}", 'diff': diff})
    
    # Ordena pela menor diferença (mais preciso primeiro)
    return sorted(sugestoes, key=lambda x: abs(x['diff']))

# --- 4. FUNÇÕES DE DADOS ---
@st.cache_data(ttl=60)
def carregar_dados():
    dfs = []
    try:
        df_n = pd.read_csv(LINK_SHEETS, dtype=str)
        if not df_n.empty: dfs.append(df_n)
    except: pass
    if os.path.exists(ARQUIVO_CSV):
        df_l = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig', dtype=str)
        if not df_l.empty: dfs.append(df_l)
    return pd.concat(dfs, ignore_index=True).fillna("None") if dfs else pd.DataFrame()

# --- 5. INTERFACE DO SISTEMA ---
st.set_page_config(page_title="Pablo Motores | Gestão & Cálculo", layout="wide")

# (Lógica de Login e Session State omitida para brevidade, mantendo seu padrão)
if 'user_data' not in st.session_state or st.session_state['user_data'] is None:
    st.info("Acesse o sistema para visualizar os cálculos.")
    st.stop()

user = st.session_state['user_data']
e_admin = (user['perfil'] == 'admin')

# Sidebar
with st.sidebar:
    st.markdown(f"### 👤 {user['usuario'].upper()}")
    if e_admin: st.markdown('<span style="background:#f1c40f;color:black;padding:2px 8px;border-radius:10px;font-weight:bold;">👑 ADMIN</span>', unsafe_allow_html=True)
    menu = ["🔍 CONSULTA", "➕ NOVO CADASTRO", "🖼️ ADICIONAR FOTO", "🗑️ LIXEIRA"] if e_admin else ["🔍 CONSULTA"]
    escolha = st.radio("Navegação:", menu)

# --- ABA CONSULTA ---
if escolha == "🔍 CONSULTA":
    st.markdown("<h1 style='text-align: center; color: #f1c40f;'>🛠️ PABLO UNIÃO MOTORES</h1>", unsafe_allow_html=True)
    df = carregar_dados()
    busca = st.text_input("🔍 Pesquisar motor...")

    if not df.empty:
        df_f = df[df.apply(lambda row: row.astype(str).str.contains(busca, case=False).any(), axis=1)] if busca else df
        
        for idx, row in df_f.iterrows():
            with st.expander(f"📦 {row.get('Marca')} | {row.get('Potencia_CV')} CV | {row.get('RPM')} RPM"):
                col_info, col_auto = st.columns([2, 2])
                
                fio_orig = str(row.get('Fio_Principal'))
                area_orig = calcular_area_mm2(fio_orig)

                with col_info:
                    st.subheader("📋 Dados de Fábrica")
                    st.write(f"**Fio Original:** {fio_orig}")
                    st.write(f"**Seção do Cobre:** {area_orig:.3f} mm²")
                    
                    # Exibir Imagem se existir
                    for n in str(row.get('Esquema_Marcado')).split(" / "):
                        for ext in [".png", ".jpg", ".jpeg"]:
                            p = os.path.join(PASTA_ESQUEMAS, f"{n.strip()}{ext}")
                            if os.path.exists(p): st.image(p, width=280)

                with col_auto:
                    st.subheader("💡 Opções Automáticas (Seguras)")
                    st.write("Combinações calculadas com base no seu estoque:")
                    
                    sugestoes = gerar_sugestoes_automaticas(area_orig)
                    
                    if not sugestoes:
                        st.error("DADOS ORIGINAIS NÃO ENCONTRADOS OU INVÁLIDOS")
                    else:
                        for s in sugestoes:
                            cor = "#2ecc71" if abs(s['diff']) <= 1.5 else "#f1c40f"
                            st.markdown(f"""
                                <div style="background-color:{cor}; color:black; padding:8px; border-radius:8px; 
                                margin-bottom:5px; font-weight:bold; display:flex; justify-content:space-between; border: 1px solid white;">
                                    <span>{s['label']} AWG</span>
                                    <span>{s['diff']:.1f}%</span>
                                </div>
                            """, unsafe_allow_html=True)
                    
                    if e_admin:
                        st.divider()
                        if st.button("🗑️ Excluir Registro", key=f"del_{idx}"):
                            st.warning("Para excluir, use a aba LIXEIRA.")
