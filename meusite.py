import streamlit as st
import pandas as pd
import os
import re
import hashlib
from datetime import datetime, timedelta

# --- 1. BANCO TÉCNICO DE ENGENHARIA (TABELA AWG DA IMAGEM) ---
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

# --- 2. FUNÇÕES DE CÁLCULO E PERFORMANCE ---
def calcular_area_mm2(texto_fio):
    try:
        if not texto_fio or str(texto_fio) == "None": return 0.0
        texto = str(texto_fio).lower().replace('awg', '').strip()
        if 'x' in texto:
            qtd, bitola = texto.split('x')
            return int(re.findall(r'\d+', qtd)[0]) * TABELA_AWG_TECNICA.get(bitola.strip(), 0.0)
        bitolas = re.findall(r'\d+', texto)
        return TABELA_AWG_TECNICA.get(bitolas[0], 0.0) if bitolas else 0.0
    except: return 0.0

def gerar_opcoes_calculadas(area_alvo):
    sugestoes = []
    if area_alvo <= 0: return []
    for bitola, area_u in TABELA_AWG_TECNICA.items():
        for qtd in range(1, 5):
            area_sim = area_u * qtd
            diff = ((area_sim - area_alvo) / area_alvo) * 100
            if -15.0 <= diff <= 15.0:
                if abs(diff) <= 2.5: cor, status = "#2ecc71", "SEGURA"
                elif 2.5 < diff <= 8.0 or -8.0 <= diff < -2.5: cor, status = "#f1c40f", "ALERTA"
                else: cor, status = "#e74c3c", "ARRISCADA"
                sugestoes.append({'fio': f"{qtd}x{bitola} AWG", 'diff': diff, 'cor': cor, 'status': status})
    return sorted(sugestoes, key=lambda x: abs(x['diff']))

# --- 3. CONFIGURAÇÕES E DADOS ---
ARQUIVO_CSV = 'meubancodedados.csv'

def carregar_dados():
    if not os.path.exists(ARQUIVO_CSV): return pd.DataFrame()
    df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig', dtype=str)
    df.columns = df.columns.str.strip()
    return df

def salvar_dados(df):
    df.to_csv(ARQUIVO_CSV, index=False, sep=';', encoding='utf-8-sig')

st.set_page_config(page_title="Pablo Motores", layout="wide")

# --- LOGIN (Simplificado para o exemplo) ---
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = None

if not st.session_state['user_data']:
    # [Lógica de formulário de login aqui...]
    st.session_state['user_data'] = {'usuario': 'admin', 'perfil': 'admin'} # Remova esta linha no seu código real
    st.rerun()

else:
    user = st.session_state['user_data']
    e_admin = (user['perfil'] == 'admin')
    
    with st.sidebar:
        menu = ["🔍 CONSULTA"]
        if e_admin: menu += ["➕ NOVO CADASTRO", "🗑️ LIXEIRA"]
        escolha = st.radio("Menu", menu)

    if escolha == "🔍 CONSULTA":
        st.title("🔍 Consulta Técnica")
        df = carregar_dados()
        busca = st.text_input("Buscar motor...")

        if not df.empty:
            if not e_admin: df = df[df.get('status', 'ativo') != 'deletado']
            df_f = df[df.apply(lambda row: row.astype(str).str.contains(busca, case=False).any(), axis=1)] if busca else df

            for idx, row in df_f.iterrows():
                area_orig = calcular_area_mm2(row.get('Fio_Principal'))
                
                with st.expander(f"📦 {row.get('Marca')} | {row.get('Potencia_CV')} CV"):
                    c1, c2 = st.columns([2, 1])
                    with c1:
                        st.write(f"**Fio Original:** {row.get('Fio_Principal')} ({area_orig:.3f} mm²)")
                        st.write(f"**Esquema:** {row.get('Esquema_Marcado', 'N/A')}")
                    
                    with c2:
                        # Abre/Fecha abas
                        if st.button("🔄 ALTERAR", key=f"alt_btn_{idx}"):
                            st.session_state[f"aba_alt_{idx}"] = not st.session_state.get(f"aba_alt_{idx}", False)
                        if e_admin:
                            if st.button("📝 EDITAR", key=f"ed_btn_{idx}"):
                                st.session_state[f"aba_ed_{idx}"] = not st.session_state.get(f"aba_ed_{idx}", False)

                    # --- ABA ALTERAR (SUGESTÕES) ---
                    if st.session_state.get(f"aba_alt_{idx}"):
                        st.info("💡 Opções calculadas automaticamente:")
                        opcoes = gerar_opcoes_calculated(area_orig)
                        for op in opcoes[:8]:
                            st.markdown(f"<div style='border-left:5px solid {op['cor']}; padding:5px; margin-bottom:5px; background:#f0f2f6; color:black;'><b>{op['fio']}</b> ({op['diff']:.2f}%) - {op['status']}</div>", unsafe_allow_html=True)
                        if st.button("Fechar Sugestões", key=f"close_alt_{idx}"):
                            st.session_state[f"aba_alt_{idx}"] = False
                            st.rerun()

                    # --- ABA EDITAR (SALVA E FECHA) ---
                    if e_admin and st.session_state.get(f"aba_ed_{idx}"):
                        with st.form(f"form_ed_{idx}"):
                            st.warning("Editando Original")
                            novo_fio = st.text_input("Novo Fio", value=row.get('Fio_Principal'))
                            if st.form_submit_button("SALVAR E FECHAR"):
                                df.at[idx, 'Fio_Principal'] = novo_fio
                                salvar_dados(df)
                                # Lógica para fechar: limpamos o estado e damos rerun
                                st.session_state[f"aba_ed_{idx}"] = False
                                st.success("Salvo com sucesso!")
                                st.rerun()
