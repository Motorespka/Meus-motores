import streamlit as st
import pandas as pd
import os
from PIL import Image

# --- CONFIGURAÇÕES ---
ARQUIVO_CSV = 'meubancodedados.csv'
PASTA_ESQUEMAS = 'esquemas_fotos'

if not os.path.exists(PASTA_ESQUEMAS):
    os.makedirs(PASTA_ESQUEMAS)

st.set_page_config(page_title="Pablo Motores | Gestão", layout="wide")

# --- CSS REFINADO ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    
    /* Títulos das Seções */
    .titulo-secao {
        color: #f1c40f !important;
        font-size: 1.1rem !important;
        font-weight: bold !important;
        border-bottom: 2px solid #f1c40f;
        margin-bottom: 10px;
        padding-bottom: 5px;
    }

    /* Estilo dos Dados */
    .dado-item { margin-bottom: 8px; font-size: 1.05rem !important; }
    .dado-label { color: #f1c40f !important; font-weight: bold !important; }
    .dado-valor { color: #ffffff !important; font-weight: bold !important; }

    /* Caixa de Ligações */
    .caixa-ligacao {
        background-color: #1c202a;
        border: 2px solid #f1c40f;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        margin-top: 10px;
    }
    .texto-ligacao { color: #f1c40f !important; font-size: 1.3rem !important; font-weight: 900 !important; }

    /* Inputs */
    input { background-color: #ffffff !important; color: #000000 !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #f1c40f;'>⚙️ PABLO MOTORES</h1>", unsafe_allow_html=True)

# --- CARREGAR DADOS ---
if os.path.exists(ARQUIVO_CSV):
    # Forçamos a limpeza de dados para evitar erros de leitura
    df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig').fillna("---")
else:
    df = pd.DataFrame()

# --- CONSULTA ---
busca = st.text_input("🔍 Pesquisar por Marca, Potência ou Detalhes...")

if not df.empty:
    df_f = df[df.astype(str).apply(lambda x: busca.lower() in x.str.lower().any(), axis=1)] if busca else df
    
    for idx, row in df_f.iterrows():
        label_motor = f"📦 {row.get('Marca')} | {row.get('Potencia_CV')} CV | {row.get('RPM')} RPM"
        with st.expander(label_motor):
            
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1.2])

            with col1:
                st.markdown('<div class="titulo-secao">📊 GERAL</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="dado-item"><span class="dado-label">Polos:</span> <span class="dado-valor">{row.get("Polaridade")}</span></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="dado-item"><span class="dado-label">Volt:</span> <span class="dado-valor">{row.get("Voltagem")}</span></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="dado-item"><span class="dado-label">Amp:</span> <span class="dado-valor">{row.get("Amperagem")}</span></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="dado-item"><span class="dado-label">Capac.:</span> <span class="dado-valor">{row.get("Capacitor")}</span></div>', unsafe_allow_html=True)

            with col2:
                st.markdown('<div class="titulo-secao">🌀 PRINCIPAL</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="dado-item"><span class="dado-label">Camas:</span> <span class="dado-valor">{row.get("Bobina_Principal")}</span></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="dado-item"><span class="dado-label">Fio:</span> <span class="dado-valor">{row.get("Fio_Principal")}</span></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="dado-item"><span class="dado-label">Rolam.:</span> <span class="dado-valor">{row.get("Rolamentos")}</span></div>', unsafe_allow_html=True)

            with col3:
                st.markdown('<div class="titulo-secao">⚡ AUXILIAR</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="dado-item"><span class="dado-label">Camas:</span> <span class="dado-valor">{row.get("Bobina_Auxiliar")}</span></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="dado-item"><span class="dado-label">Fio:</span> <span class="dado-valor">{row.get("Fio_Auxiliar")}</span></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="dado-item"><span class="dado-label">Eixo:</span> <span class="dado-valor">{row.get("Eixo_X")} x {row.get("Eixo_Y")}</span></div>', unsafe_allow_html=True)

            with col4:
                st.markdown('<div class="titulo-secao">🔗 LIGAÇÃO</div>', unsafe_allow_html=True)
                lig_texto = str(row.get('Esquema_Marcado'))
                st.markdown(f'<div class="caixa-ligacao"><span class="texto-ligacao">{lig_texto}</span></div>', unsafe_allow_html=True)
                
                # CORREÇÃO DO ERRO: Busca correta da imagem
                lista_ligs = lig_texto.split(" / ")
                for nome_lig in lista_ligs:
                    nome_limpo = nome_lig.strip()
                    # Tenta carregar como .png ou .jpg
                    path_png = os.path.join(PASTA_ESQUEMAS, f"{nome_limpo}.png")
                    path_jpg = os.path.join(PASTA_ESQUEMAS, f"{nome_limpo}.jpg")
                    
                    if os.path.exists(path_png):
                        st.image(path_png, use_container_width=True)
                    elif os.path.exists(path_jpg):
                        st.image(path_jpg, use_container_width=True)
