import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from PIL import Image

# --- CONFIGURAÇÕES DE ARQUIVOS ---
ARQUIVO_CSV = 'meubancodedados.csv'
ARQUIVO_LIXEIRA = 'lixeira_motores.csv'
PASTA_ESQUEMAS = 'esquemas_fotos'

if not os.path.exists(PASTA_ESQUEMAS):
    os.makedirs(PASTA_ESQUEMAS)

# --- FUNÇÃO DE AUTO-LIMPEZA DA LIXEIRA (SÓ ADMIN CONTROLA) ---
def gerenciar_lixeira():
    if os.path.exists(ARQUIVO_LIXEIRA):
        df_lixo = pd.read_csv(ARQUIVO_LIXEIRA, sep=';', encoding='utf-8-sig')
        if not df_lixo.empty:
            # Converte a coluna de data
            df_lixo['Data_Exclusao'] = pd.to_datetime(df_lixo['Data_Exclusao'])
            # Filtra o que tem menos de 20 dias
            limite = datetime.now() - timedelta(days=20)
            df_limpo = df_lixo[df_lixo['Data_Exclusao'] > limite]
            # Salva de volta (o que sumiu daqui foi excluído permanentemente)
            df_limpo.to_csv(ARQUIVO_LIXEIRA, index=False, sep=';', encoding='utf-8-sig')

# Executa a limpeza automática
gerenciar_lixeira()

st.set_page_config(page_title="Pablo Motores | Gestão", layout="wide")

# --- CSS (MANTIDO O SEU PADRÃO) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .titulo-secao { color: #f1c40f !important; font-size: 1.1rem !important; font-weight: bold !important; border-bottom: 2px solid #f1c40f; margin-bottom: 10px; padding-bottom: 5px; }
    input { background-color: #ffffff !important; color: #000000 !important; font-weight: bold !important; }
    .stButton>button { width: 100%; background-color: #f1c40f !important; color: #000000 !important; font-weight: bold !important; border: 1px solid #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ADMIN ---
with st.sidebar:
    st.markdown("### 🔐 ACESSO")
    senha = st.text_input("Senha Admin", type="password")
    e_admin = (senha == "pablo123")
    
    if e_admin:
        st.divider()
        st.markdown("### 🛠️ FERRAMENTAS")
        aba_admin = st.radio("Navegar para:", ["Consultar Motores", "Lixeira (20 dias)"])

st.markdown("<h1 style='text-align: center; color: #f1c40f;'>⚙️ PABLO MOTORES</h1>", unsafe_allow_html=True)

# --- CARREGAR DADOS ---
if os.path.exists(ARQUIVO_CSV):
    df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig').fillna("---")
else:
    df = pd.DataFrame()

# --- LÓGICA DA ABA DA LIXEIRA ---
if e_admin and aba_admin == "Lixeira (20 dias)":
    st.markdown("## 🗑️ Lixeira de Segurança")
    st.info("Motores aqui serão apagados permanentemente após 20 dias da data de exclusão.")
    
    if os.path.exists(ARQUIVO_LIXEIRA):
        df_lixo = pd.read_csv(ARQUIVO_LIXEIRA, sep=';', encoding='utf-8-sig')
        if not df_lixo.empty:
            for idx_l, row_l in df_lixo.iterrows():
                with st.expander(f"❌ {row_l['Marca']} | Excluído em: {row_l['Data_Exclusao']}"):
                    if st.button(f"🔄 Recuperar Motor: {row_l['Marca']}", key=f"rec_{idx_l}"):
                        # Devolve ao banco principal
                        motor_rec = pd.DataFrame([row_l]).drop(columns=['Data_Exclusao'])
                        motor_rec.to_csv(ARQUIVO_CSV, mode='a', header=not os.path.exists(ARQUIVO_CSV), index=False, sep=';', encoding='utf-8-sig')
                        # Tira da lixeira
                        df_lixo.drop(idx_l).to_csv(ARQUIVO_LIXEIRA, index=False, sep=';', encoding='utf-8-sig')
                        st.success("Motor recuperado com sucesso!")
                        st.rerun()
        else:
            st.write("A lixeira está vazia.")
    else:
        st.write("Nenhum histórico de lixeira encontrado.")

# --- LÓGICA DE CONSULTA (COM A NOVA EXCLUSÃO) ---
else:
    busca = st.text_input("🔍 Pesquisar Motor para Consultar ou Editar...")
    if not df.empty:
        df_f = df[df.astype(str).apply(lambda x: busca.lower() in x.str.lower().any(), axis=1)] if busca else df
        
        for idx, row in df_f.iterrows():
            label_motor = f"📦 {row.get('Marca')} | {row.get('Potencia_CV')} CV | {row.get('RPM')} RPM"
            with st.expander(label_motor):
                # ... (Seu código de exibição c1, c2, c3, c4 permanece igual)
                st.write(f"Dados do Motor: {row.get('Marca')}") # Resumo visual
                
                if e_admin:
                    st.divider()
                    col_ed, col_del = st.columns(2)
                    
                    if col_del.button(f"🗑️ EXCLUIR MOTOR", key=f"btn_ask_{idx}"):
                        st.session_state[f"confirmar_{idx}"] = True

                    if st.session_state.get(f"confirmar_{idx}"):
                        st.warning("⚠️ **Você tem certeza?** Ele irá para a lixeira por 20 dias.")
                        ca1, ca2 = st.columns(2)
                        
                        if ca1.button("✅ SIM, MOVER P/ LIXEIRA", key=f"sim_{idx}"):
                            # Prepara os dados para a lixeira
                            dados_exclusao = pd.DataFrame([row])
                            dados_exclusao['Data_Exclusao'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            
                            # Salva na lixeira
                            dados_exclusao.to_csv(ARQUIVO_LIXEIRA, mode='a', header=not os.path.exists(ARQUIVO_LIXEIRA), index=False, sep=';', encoding='utf-8-sig')
                            
                            # Remove do principal
                            df_novo = df.drop(idx)
                            df_novo.to_csv(ARQUIVO_CSV, index=False, sep=';', encoding='utf-8-sig')
                            
                            st.session_state[f"confirmar_{idx}"] = False
                            st.rerun()
                        
                        if ca2.button("❌ CANCELAR", key=f"nao_{idx}"):
                            st.session_state[f"confirmar_{idx}"] = False
                            st.rerun()

                    # (Lógica de edição permanece abaixo)
                    
