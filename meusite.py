import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from PIL import Image

# --- CONFIGURAÇÕES ---
ARQUIVO_CSV = 'meubancodedados.csv'
ARQUIVO_LIXEIRA = 'lixeira_motores.csv'
PASTA_ESQUEMAS = 'esquemas_fotos'

if not os.path.exists(PASTA_ESQUEMAS): os.makedirs(PASTA_ESQUEMAS)

# --- LIMPEZA AUTOMÁTICA DA LIXEIRA ---
if os.path.exists(ARQUIVO_LIXEIRA):
    try:
        df_lixo = pd.read_csv(ARQUIVO_LIXEIRA, sep=';', encoding='utf-8-sig')
        df_lixo['Data_Exclusao'] = pd.to_datetime(df_lixo['Data_Exclusao'])
        limite = datetime.now() - timedelta(days=20)
        df_lixo[df_lixo['Data_Exclusao'] > limite].to_csv(ARQUIVO_LIXEIRA, index=False, sep=';', encoding='utf-8-sig')
    except: pass

st.set_page_config(page_title="Pablo Motores", layout="wide")

# --- CSS (FORÇANDO VISIBILIDADE) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .titulo-secao { color: #f1c40f !important; font-size: 1.2rem !important; font-weight: bold; border-bottom: 2px solid #f1c40f; margin-bottom: 10px; }
    .label-fixo { color: #f1c40f !important; font-weight: bold; }
    .valor-fixo { color: #ffffff !important; font-weight: bold; }
    .stExpander { border: 1px solid #34495e !important; }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL (ADMIN) ---
with st.sidebar:
    st.markdown("### 🔐 ACESSO RESTRITO")
    senha = st.text_input("Senha Admin", type="password")
    e_admin = (senha == "pablo123")
    
    aba_selecionada = "Consultar"
    if e_admin:
        st.success("Logado como Admin")
        aba_selecionada = st.radio("MENU ADMIN", ["Consultar", "Lixeira (20 dias)"])

st.markdown("<h1 style='text-align: center; color: #f1c40f;'>⚙️ PABLO MOTORES</h1>", unsafe_allow_html=True)

# --- CARREGAR DADOS ---
def carregar_dados(caminho):
    if os.path.exists(caminho):
        return pd.read_csv(caminho, sep=';', encoding='utf-8-sig').fillna("---").replace("None", "---")
    return pd.DataFrame()

df = carregar_dados(ARQUIVO_CSV)

# --- TELA DA LIXEIRA (SÓ PARA ADMIN) ---
if e_admin and aba_selecionada == "Lixeira (20 dias)":
    st.markdown("## 🗑️ LIXEIRA (Recuperação)")
    df_lixo = carregar_dados(ARQUIVO_LIXEIRA)
    if not df_lixo.empty:
        for idx, row in df_lixo.iterrows():
            with st.expander(f"Motor: {row['Marca']} - Excluído em {row.get('Data_Exclusao', 'Desconhecido')}"):
                if st.button(f"🔄 RECUPERAR {row['Marca']}", key=f"rec_{idx}"):
                    # Salva no principal e tira do lixo
                    volta = pd.DataFrame([row]).drop(columns=['Data_Exclusao'], errors='ignore')
                    volta.to_csv(ARQUIVO_CSV, mode='a', header=not os.path.exists(ARQUIVO_CSV), index=False, sep=';', encoding='utf-8-sig')
                    df_lixo.drop(idx).to_csv(ARQUIVO_LIXEIRA, index=False, sep=';', encoding='utf-8-sig')
                    st.rerun()
    else: st.info("Lixeira vazia.")

# --- TELA DE CONSULTA ---
else:
    busca = st.text_input("🔍 Buscar motor por qualquer detalhe...")
    if not df.empty:
        # Filtro de busca
        df_f = df[df.astype(str).apply(lambda x: busca.lower() in x.str.lower().any(), axis=1)] if busca else df
        
        for idx, row in df_f.iterrows():
            with st.expander(f"📦 {row['Marca']} | {row['Potencia_CV']} CV | {row['RPM']} RPM"):
                c1, c2, c3, c4 = st.columns(4)
                
                with c1:
                    st.markdown('<div class="titulo-secao">📊 GERAL</div>', unsafe_allow_html=True)
                    st.markdown(f"<span class='label-fixo'>Polos:</span> <span class='valor-fixo'>{row['Polaridade']}</span>", unsafe_allow_html=True)
                    st.write(f"**Volt:** {row['Voltagem']}")
                    st.write(f"**Amp:** {row['Amperagem']}")
                
                with c2:
                    st.markdown('<div class="titulo-secao">🌀 PRINCIPAL</div>', unsafe_allow_html=True)
                    st.write(f"**Fio:** {row['Fio_Principal']}")
                    st.write(f"**Camas:** {row['Bobina_Principal']}")

                with c3:
                    st.markdown('<div class="titulo-secao">⚡ AUXILIAR</div>', unsafe_allow_html=True)
                    st.write(f"**Fio:** {row['Fio_Auxiliar']}")
                    st.write(f"**Eixo:** {row['Eixo_X']} x {row['Eixo_Y']}")

                with c4:
                    st.markdown('<div class="titulo-secao">🔗 LIGAÇÃO</div>', unsafe_allow_html=True)
                    st.info(row['Esquema_Marcado'])
                
                if e_admin:
                    if st.button(f"🗑️ APAGAR MOTOR", key=f"del_{idx}"):
                        # Mover para lixeira
                        row_lixo = pd.DataFrame([row])
                        row_lixo['Data_Exclusao'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        row_lixo.to_csv(ARQUIVO_LIXEIRA, mode='a', header=not os.path.exists(ARQUIVO_LIXEIRA), index=False, sep=';', encoding='utf-8-sig')
                        df.drop(idx).to_csv(ARQUIVO_CSV, index=False, sep=';', encoding='utf-8-sig')
                        st.rerun()
