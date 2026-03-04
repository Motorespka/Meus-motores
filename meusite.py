import streamlit as st
import pandas as pd
import os
from datetime import datetime
from PIL import Image

# --- CONFIGURAÇÕES ---
ARQUIVO_CSV = 'meubancodedados.csv'
# Link do Google Sheets configurado para exportar CSV
LINK_SHEETS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTFbH81UYKGJ6dQvKotxdv4hDxecLmiGUPHN46iexbw8NeS8_e2XdyZnZ8WJnL2XRTLCbFDbBKo_NGE/pub?output=csv"
PASTA_ESQUEMAS = 'esquemas_fotos'

if not os.path.exists(PASTA_ESQUEMAS): os.makedirs(PASTA_ESQUEMAS)

# Configuração para parecer aplicativo (esconde menus laterais e barras)
st.set_page_config(page_title="Pablo Motores | Gestão Profissional", layout="wide", initial_sidebar_state="collapsed")

# Estilo para esconder os menus do Streamlit no celular
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO DE CARREGAMENTO (HÍBRIDA COM ANTI-DUPLICAÇÃO) ---
@st.cache_data(ttl=60) # Atualiza a cada 1 minuto para evitar travamentos
def carregar_dados():
    dfs = []
    
    # 1. Tenta carregar do Google Sheets (Nuvem)
    try:
        # Timeout de 5s para não travar o site se a internet estiver lenta
        df_nuvem = pd.read_csv(LINK_SHEETS, dtype=str, storage_options={'timeout': 5})
        if not df_nuvem.empty:
            df_nuvem.columns = df_nuvem.columns.str.strip() # Limpa nomes de colunas
            dfs.append(df_nuvem)
    except:
        pass # Se falhar, segue para o local silenciosamente

    # 2. Tenta carregar do CSV Local
    if os.path.exists(ARQUIVO_CSV):
        try:
            df_local = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig', dtype=str)
            if not df_local.empty:
                df_local.columns = df_local.columns.str.strip()
                dfs.append(df_local)
        except:
            pass

    if not dfs:
        return pd.DataFrame()

    # União das fontes
    df_geral = pd.concat(dfs, ignore_index=True).fillna("None")
    
    # --- SISTEMA ANTI-DUPLICAÇÃO ---
    # Consideramos motor duplicado se Marca, Potencia e RPM forem iguais
    colunas_chave = ['Marca', 'Potencia_CV', 'RPM']
    
    # Verifica se as colunas existem antes de remover duplicatas
    colunas_presentes = [c for c in colunas_chave if c in df_geral.columns]
    
    if colunas_presentes:
        # Remove espaços extras nos dados para comparação precisa
        for col in colunas_presentes:
            df_geral[col] = df_geral[col].astype(str).str.strip()
        
        # Mantém apenas a primeira ocorrência encontrada
        df_geral = df_geral.drop_duplicates(subset=colunas_presentes, keep='first')

    return df_geral

# --- LOGIN E NAVEGAÇÃO ---
with st.sidebar:
    st.header("🔐 ACESSO")
    senha = st.text_input("Senha Admin", type="password")
    e_admin = (senha == "pablo123")
    
    menu = ["🔍 CONSULTA"]
    if e_admin:
        menu = ["🔍 CONSULTA", "➕ NOVO CADASTRO", "🖼️ ADICIONAR FOTO", "🗑️ LIXEIRA"]
    escolha = st.radio("Ir para:", menu)

# --- ABA 1: CONSULTA ---
if escolha == "🔍 CONSULTA":
    st.markdown("<h1 style='text-align: center; color: #f1c40f;'>⚙️ PABLO MOTORES</h1>", unsafe_allow_html=True)
    df = carregar_dados()
    busca = st.text_input("🔍 Pesquisar por Marca, CV ou detalhes...")
    
    if not df.empty:
        if busca:
            df_f = df[df.apply(lambda row: row.astype(str).str.contains(busca, case=False).any(), axis=1)]
        else:
            df_f = df

        for idx, row in df_f.iterrows():
            with st.expander(f"📦 {row.get('Marca')} | {row.get('Potencia_CV')} CV | {row.get('RPM')} RPM"):
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.markdown("### 📊 GERAL")
                    st.write(f"**Polos:** {row.get('Polaridade')}")
                    st.write(f"**Volt:** {row.get('Voltagem')}")
                    st.write(f"**Amp:** {row.get('Amperagem')}")
                    st.write(f"**Rolamentos:** {row.get('Rolamentos')}")
                with c2:
                    st.markdown("### 🌀 PRINCIPAL")
                    st.write(f"**Grupo Principal:** {row.get('Bobina_Principal')}")
                    st.write(f"**Fio Principal:** {row.get('Fio_Principal')}")
                with c3:
                    st.markdown("### ⚡ AUXILIAR")
                    st.write(f"**Grupo Auxiliar:** {row.get('Bobina_Auxiliar')}")
                    st.write(f"**Fio Auxiliar:** {row.get('Fio_Auxiliar')}")
                    st.write(f"**Capacitor:** {row.get('Capacitor')}")
                    st.write(f"**Eixo:** {row.get('Eixo_X')} x {row.get('Eixo_Y')}")
                with c4:
                    st.markdown("### 🔗 LIGAÇÃO")
                    lig = str(row.get('Esquema_Marcado'))
                    st.info(f"Esquema: {lig}")
                    for n in lig.split(" / "):
                        for ext in [".png", ".jpg", ".jpeg"]:
                            p = os.path.join(PASTA_ESQUEMAS, f"{n.strip()}{ext}")
                            if os.path.exists(p): st.image(p)

# --- ABA 2: NOVO CADASTRO ---
elif escolha == "➕ NOVO CADASTRO":
    st.markdown("## ➕ Cadastrar Novo Motor")
    lista_fotos = [f.split(".")[0] for f in os.listdir(PASTA_ESQUEMAS) if f.endswith(('.png', '.jpg', '.jpeg'))]
    
    with st.form("cadastro_pablo"):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("### 📊 Dados de Placa")
            marca = st.text_input("Marca")
            cv = st.text_input("Potência (CV)")
            rpm = st.text_input("RPM")
            pol = st.text_input("Polaridade")
            volt = st.text_input("Voltagem")
            amp = st.text_input("Amperagem")
        
        with c2:
            st.markdown("### 🌀 Bobinagem Principal")
            camas_p = st.text_input("Grupo Principal (Camas)")
            fio_p = st.text_input("Fio Principal")
            st.divider()
            st.markdown("### ⚙️ Mecânica")
            rolam = st.text_input("Rolamentos")
            col_ex, col_ey = st.columns(2)
            eixo_x = col_ex.text_input("Eixo X")
            eixo_y = col_ey.text_input("Eixo Y")
            
        with c3:
            st.markdown("### ⚡ Bobinagem Auxiliar")
            camas_a = st.text_input("Grupo Auxiliar (Camas)")
            fio_a = st.text_input("Fio Auxiliar")
            st.divider()
            st.markdown("### 🔋 Partida")
            capac = st.text_input("Capacitor")

        st.markdown("### 🖼️ Marque os Esquemas de Ligação")
        selecionados = []
        if lista_fotos:
            cols = st.columns(4)
            for i, foto in enumerate(lista_fotos):
                if cols[i % 4].checkbox(foto): selecionados.append(foto)
        
        if st.form_submit_button("💾 SALVAR DADOS"):
            nova_lig = " / ".join(selecionados) if selecionados else "None"
            novo_motor = {
                'Marca': marca, 'Potencia_CV': cv, 'RPM': rpm, 'Polaridade': pol,
                'Voltagem': volt, 'Amperagem': amp, 'Fio_Principal': fio_p,
                'Bobina_Principal': camas_p, 'Rolamentos': rolam, 
                'Fio_Auxiliar': fio_a, 'Bobina_Auxiliar': camas_a,
                'Capacitor': capac, 'Eixo_X': eixo_x, 'Eixo_Y': eixo_y, 
                'Esquema_Marcado': nova_lig
            }
            df_n = pd.DataFrame([novo_motor])
            df_n.to_csv(ARQUIVO_CSV, mode='a', header=not os.path.exists(ARQUIVO_CSV), index=False, sep=';', encoding='utf-8-sig')
            st.success("Motor salvo com sucesso!")
            st.cache_data.clear() # Limpa o cache para mostrar o novo motor na consulta

# --- ABA 3: ADICIONAR FOTO ---
elif escolha == "🖼️ ADICIONAR FOTO":
    st.markdown("## 🖼️ Enviar Novo Esquema")
    arq = st.file_uploader("Foto", type=['png', 'jpg', 'jpeg'])
    nome_f = st.text_input("Nome do Esquema")
    if st.button("Gravar") and arq and nome_f:
        Image.open(arq).save(os.path.join(PASTA_ESQUEMAS, f"{nome_f}.png"))
        st.success("Foto salva!")

# --- ABA 4: LIXEIRA ---
elif escolha == "🗑️ LIXEIRA" and e_admin:
    st.markdown("## 🗑️ Lixeira (Somente Admin)")
    df = carregar_dados()
    if not df.empty:
        st.dataframe(df)
        if st.button("EXCLUIR TUDO (CUIDADO)"):
            if os.path.exists(ARQUIVO_CSV):
                os.remove(ARQUIVO_CSV)
                st.warning("O arquivo do banco de dados foi apagado.")
                st.cache_data.clear()
                st.rerun()
