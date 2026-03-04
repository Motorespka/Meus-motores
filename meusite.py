import streamlit as st
import pandas as pd
import os
import re
import hashlib
from datetime import datetime, timedelta

# --- 1. BANCO TÉCNICO DE ENGENHARIA ---
TABELA_AWG = {
    '14': 2.08, '15': 1.65, '16': 1.31, '17': 1.04, '18': 0.823, '19': 0.653,
    '20': 0.518, '21': 0.410, '22': 0.326, '23': 0.258, '24': 0.205, '25': 0.162
}

# --- 2. MOTOR DE CÁLCULO DE RISCO ---
def analisar_risco(area_alvo, area_teste):
    if area_alvo <= 0: return None
    diff = ((area_teste - area_alvo) / area_alvo) * 100
    
    if abs(diff) <= 2.0:
        return {"cor": "#2ecc71", "status": "VERDE: EXCELENTE", "msg": "Motor idêntico ao original. Desempenho 100%."}
    elif 2.0 < diff <= 6.0:
        return {"cor": "#f1c40f", "status": "AMARELO: BOM", "msg": "Motor terá leve ganho de força, mas o fio ocupará mais espaço na ranhura."}
    elif -6.0 <= diff < -2.0:
        return {"cor": "#e67e22", "status": "LARANJA: REGULAR", "msg": "Motor perderá torque e terá aquecimento acima do normal."}
    else:
        return {"cor": "#e74c3c", "status": "VERMELHO: PERIGOSO", "msg": "ALTO RISCO! O motor pode queimar ou não ter força para rodar."}

def buscar_possibilidades(area_alvo):
    resultados = []
    if area_alvo <= 0: return []
    for bitola, area_u in TABELA_AWG.items():
        for qtd in range(1, 5):
            area_t = area_u * qtd
            diff = ((area_t - area_alvo) / area_alvo) * 100
            # Mostra possibilidades de -12% até +15% para dar visão total de erro
            if -12.0 <= diff <= 15.0:
                analise = analisar_risco(area_alvo, area_t)
                resultados.append({'fio': f"{qtd}x {bitola} AWG", 'diff': diff, 'analise': analise})
    return sorted(resultados, key=lambda x: abs(x['diff']))

# --- 3. FUNÇÕES DE DADOS ---
ARQUIVO_CSV = 'meubancodedados.csv'

def carregar_dados():
    if not os.path.exists(ARQUIVO_CSV): return pd.DataFrame()
    df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig', dtype=str)
    df.columns = df.columns.str.strip()
    return df

def salvar_dados(df):
    df.to_csv(ARQUIVO_CSV, index=False, sep=';', encoding='utf-8-sig')

# --- 4. INTERFACE ---
st.set_page_config(page_title="Pablo Motores Pro", layout="wide")

if 'user_data' in st.session_state and st.session_state['user_data']:
    user = st.session_state['user_data']
    e_admin = user.get('perfil') == 'admin'

    escolha = st.sidebar.radio("Navegação:", ["🔍 CONSULTA", "➕ NOVO CADASTRO", "🗑️ LIXEIRA"])

    if escolha == "🔍 CONSULTA":
        st.title("⚙️ PABLO UNIÃO - CONSULTA TÉCNICA")
        df = carregar_dados()
        busca = st.text_input("🔍 Pesquisar por Marca ou Dados...")

        if not df.empty:
            if not e_admin: df = df[df.get('status', 'ativo') != 'deletado']
            df_f = df[df.apply(lambda row: row.astype(str).str.contains(busca, case=False).any(), axis=1)] if busca else df

            for idx, row in df_f.iterrows():
                # Cálculo da área original
                f_orig = str(row.get('Fio_Principal', ''))
                area_base = 0
                try:
                    if 'x' in f_orig.lower():
                        q, b = f_orig.lower().split('x')
                        area_base = int(re.findall(r'\d+', q)[0]) * TABELA_AWG.get(re.findall(r'\d+', b)[0], 0)
                    else:
                        area_base = TABELA_AWG.get(re.findall(r'\d+', f_orig)[0], 0)
                except: pass

                with st.expander(f"📦 {row.get('Marca')} | {row.get('Potencia_CV')} CV"):
                    col_d, col_a = st.columns([2, 1])
                    with col_d:
                        st.write(f"**Fio de Fábrica:** {f_orig} ({area_base:.3f} mm²)")
                        st.write(f"**Amperagem:** {row.get('Amperagem')} | **RPM:** {row.get('RPM')}")

                    with col_a:
                        if st.button("🔄 ABA ALTERAR (Ver Riscos)", key=f"alt_{idx}"):
                            st.session_state[f"calc_{idx}"] = True
                        if e_admin:
                            if st.button("📝 EDITAR ORIGINAL", key=f"ed_{idx}"):
                                st.session_state[f"edit_{idx}"] = True
                            if st.button("🗑️ EXCLUIR", key=f"del_{idx}"):
                                df.at[idx, 'status'] = 'deletado'
                                df.at[idx, 'data_del'] = datetime.now().strftime('%Y-%m-%d')
                                salvar_dados(df); st.rerun()

                    # --- LÓGICA ALTERAR (SUGESTÕES POR CORES) ---
                    if st.session_state.get(f"calc_{idx}"):
                        st.markdown("---")
                        st.subheader("💡 Análise de Possibilidades")
                        possibilidades = buscar_possibilidades(area_base)
                        for p in possibilidades:
                            st.markdown(f"""
                                <div style="border-left: 8px solid {p['analise']['cor']}; background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-bottom: 8px;">
                                    <span style="color: black; font-weight: bold; font-size: 16px;">{p['fio']}</span> 
                                    <span style="color: #666;">({p['diff']:.2f}%)</span><br>
                                    <b style="color: {p['analise']['cor']};">{p['analise']['status']}</b><br>
                                    <small style="color: #333;">{p['analise']['msg']}</small>
                                </div>
                            """, unsafe_allow_html=True)
                        if st.button("Fechar Alteração", key=f"cls_{idx}"):
                            del st.session_state[f"calc_{idx}"]; st.rerun()

                    # --- LÓGICA EDITAR (ADMIN) ---
                    if e_admin and st.session_state.get(f"edit_{idx}"):
                        with st.form(f"f_ed_{idx}"):
                            st.warning("✍️ EDITANDO BANCO DE DADOS ORIGINAL")
                            n_fio = st.text_input("Fio Principal", value=row.get('Fio_Principal'))
                            n_amp = st.text_input("Amperagem", value=row.get('Amperagem'))
                            if st.form_submit_button("SALVAR"):
                                df.at[idx, 'Fio_Principal'] = n_fio
                                df.at[idx, 'Amperagem'] = n_amp
                                salvar_dados(df); st.rerun()

