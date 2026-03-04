import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime, timedelta

# --- 1. BANCO DE DADOS TÉCNICO (AWG - mm²) ---
# Puxado da sua tabela de conversão para precisão de 100%
TABELA_AWG_TECNICA = {
    '4/0': 107.0, '3/0': 85.0, '2/0': 67.4, '1/0': 53.5,
    '1': 42.41, '2': 33.63, '3': 26.67, '4': 21.147, '5': 16.764,
    '6': 13.299, '7': 10.55, '8': 8.367, '9': 6.633, '10': 5.26,
    '11': 4.169, '12': 3.307, '13': 2.627, '14': 2.082, '15': 1.651,
    '16': 1.307, '17': 1.04, '18': 0.8235, '19': 0.6533, '20': 0.5191,
    '21': 0.4117, '22': 0.3247, '23': 0.2588, '24': 0.2051, '25': 0.1626,
    '26': 0.1282, '27': 0.1024, '28': 0.0804, '29': 0.0647, '30': 0.0507,
    '31': 0.0401, '32': 0.0324, '33': 0.0254, '34': 0.0201
}

# --- 2. FUNÇÕES DE ENGENHARIA E CÁLCULO ---
def calcular_area_mm2(texto_fio):
    try:
        if not texto_fio or str(texto_fio) == "None": return 0.0
        texto = str(texto_fio).lower().replace('awg', '').strip()
        if 'x' in texto:
            qtd, bitola = texto.split('x')
            return int(re.findall(r'\d+', qtd)[0]) * TABELA_AWG_TECNICA.get(bitola.strip(), 0.0)
        bitola = re.findall(r'\d+', texto)[0]
        return TABELA_AWG_TECNICA.get(bitola, 0.0)
    except: return 0.0

def definir_risco(area_orig, area_sim):
    if area_orig <= 0: return "#7f8c8d", "DADOS INCOMPLETOS", "Fio original não identificado."
    diff = ((area_sim - area_orig) / area_orig) * 100
    if abs(diff) <= 2.5: return "#2ecc71", "VERDE: EXCELENTE", "Motor idêntico ao original."
    elif 2.5 < diff <= 7.0: return "#f1c40f", "AMARELO: BOM", "Fio mais grosso (ganho de força/menos espaço)."
    elif -7.0 <= diff < -2.5: return "#e67e22", "LARANJA: REGULAR", "Fio mais fino (perda de torque/aquecimento)."
    else: return "#e74c3c", "VERMELHO: PERIGOSO", "Risco alto de queima!"

# --- 3. GESTÃO DE DADOS ---
ARQUIVO_CSV = 'meubancodedados.csv'

def carregar_dados():
    if not os.path.exists(ARQUIVO_CSV): return pd.DataFrame()
    df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig', dtype=str)
    df.columns = df.columns.str.strip()
    return df

def salvar_dados(df):
    df.to_csv(ARQUIVO_CSV, index=False, sep=';', encoding='utf-8-sig')

# --- 4. INTERFACE ---
st.set_page_config(page_title="Pablo Motores | Gestão Técnica", layout="wide")

if 'user_data' in st.session_state and st.session_state['user_data']:
    user = st.session_state['user_data']
    e_admin = user.get('perfil') == 'admin'
    
    escolha = st.sidebar.radio("Navegação:", ["🔍 CONSULTA", "➕ NOVO CADASTRO", "🗑️ LIXEIRA"])

    if escolha == "🔍 CONSULTA":
        st.title("🔍 Consulta e Simulação")
        df = carregar_dados()
        busca = st.text_input("Pesquisar motor...")

        if not df.empty:
            if not e_admin: df = df[df.get('status', 'ativo') != 'deletado']
            df_f = df[df.apply(lambda row: row.astype(str).str.contains(busca, case=False).any(), axis=1)] if busca else df

            for idx, row in df_f.iterrows():
                area_base = calcular_area_mm2(row.get('Fio_Principal'))
                
                with st.expander(f"📦 {row.get('Marca')} | {row.get('Potencia_CV')} CV"):
                    col_info, col_botoes = st.columns([2, 1])
                    
                    with col_info:
                        st.write(f"**Fio de Fábrica:** {row.get('Fio_Principal')} ({area_base:.3f} mm²)")
                        st.write(f"**Amperagem:** {row.get('Amperagem')} | **RPM:** {row.get('RPM')}")

                    with col_botoes:
                        # BOTÃO ALTERAR (CÓPIA/SIMULADOR)
                        if st.button("🔄 ABA ALTERAR (Cópia)", key=f"btn_alt_{idx}"):
                            st.session_state[f"aba_alt_{idx}"] = not st.session_state.get(f"aba_alt_{idx}", False)
                        
                        # BOTÃO EDITAR (SÓ ADMIN - ORIGINAL)
                        if e_admin:
                            if st.button("📝 EDITAR CÁLCULO (Admin)", key=f"btn_edit_{idx}"):
                                st.session_state[f"aba_edit_{idx}"] = not st.session_state.get(f"aba_edit_{idx}", False)

                    # --- INTERFACE: ABA ALTERAR (CÓPIA VISUAL) ---
                    if st.session_state.get(f"aba_alt_{idx}"):
                        st.markdown("---")
                        st.subheader("🛠️ Simulador de Fios (Cópia)")
                        c_q, c_f = st.columns(2)
                        q_s = c_q.number_input("Qtd Fios", 1, 6, 1, key=f"q_s_{idx}")
                        f_s = c_f.selectbox("Bitola AWG", list(TABELA_AWG_TECNICA.keys()), index=15, key=f"f_s_{idx}")
                        
                        area_s = q_s * TABELA_AWG_TECNICA[f_s]
                        cor, status, msg = definir_risco(area_base, area_s)
                        
                        st.markdown(f"""<div style="background-color:{cor}; padding:20px; border-radius:10px; color:white; text-align:center;">
                            <h3>{status}</h3><p>Área: {area_s:.3f} mm²</p><small>{msg}</small></div>""", unsafe_allow_html=True)
                        st.caption("Nota: Estas alterações são apenas para visualização e não alteram o banco de dados.")

                    # --- INTERFACE: ABA EDITAR (ADMIN - ALTERA O BANCO) ---
                    if e_admin and st.session_state.get(f"aba_edit_{idx}"):
                        st.markdown("---")
                        with st.form(f"form_edit_{idx}"):
                            st.warning("⚠️ VOCÊ ESTÁ EDITANDO O CÁLCULO ORIGINAL")
                            novo_fio = st.text_input("Fio Principal", value=row.get('Fio_Principal'))
                            nova_amp = st.text_input("Amperagem", value=row.get('Amperagem'))
                            if st.form_submit_button("SALVAR ALTERAÇÕES NO ORIGINAL"):
                                df.at[idx, 'Fio_Principal'] = novo_fio
                                df.at[idx, 'Amperagem'] = nova_amp
                                salvar_dados(df)
                                st.success("Banco de dados atualizado!")
                                st.rerun()
