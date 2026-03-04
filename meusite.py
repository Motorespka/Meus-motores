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
    """Calcula a área total baseado no texto (ex: 2x18)"""
    try:
        if not texto_fio or str(texto_fio) == "None": return 0.0
        texto = str(texto_fio).lower().replace('awg', '').strip()
        if 'x' in texto:
            partes = texto.split('x')
            qtd = int(re.findall(r'\d+', partes[0])[0])
            bitola = partes[1].strip()
            return qtd * TABELA_AWG_TECNICA.get(bitola, 0.0)
        bitolas = re.findall(r'\d+', texto)
        return TABELA_AWG_TECNICA.get(bitolas[0], 0.0) if bitolas else 0.0
    except: return 0.0

def gerar_opcoes_calculadas(area_alvo):
    """Varre a tabela AWG e sugere combinações seguras e arriscadas"""
    sugestoes = []
    if area_alvo <= 0: return []
    for bitola, area_u in TABELA_AWG_TECNICA.items():
        for qtd in range(1, 5):
            area_sim = area_u * qtd
            diff = ((area_sim - area_alvo) / area_alvo) * 100
            if -12.0 <= diff <= 12.0:
                if abs(diff) <= 2.5: cor, status = "#2ecc71", "SEGURA (Verde)"
                elif 2.5 < diff <= 7.0 or -7.0 <= diff < -2.5: cor, status = "#f1c40f", "ALERTA (Amarelo)"
                else: cor, status = "#e74c3c", "ARRISCADA (Vermelho)"
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

# --- 4. INTERFACE ---
st.set_page_config(page_title="Pablo Motores Pro", layout="wide")

# (Aqui você mantém seu código de login exatamente como está)
# Para este exemplo, consideraremos que o usuário já está logado
if 'user_data' in st.session_state and st.session_state['user_data']:
    user = st.session_state['user_data']
    e_admin = (user.get('perfil') == 'admin')
    
    escolha = st.sidebar.radio("Navegação:", ["🔍 CONSULTA", "➕ NOVO CADASTRO", "🗑️ LIXEIRA"])

    if escolha == "🔍 CONSULTA":
        st.title("⚙️ Consulta e Engenharia")
        df = carregar_dados()
        busca = st.text_input("Buscar motor...")

        if not df.empty:
            if not e_admin: df = df[df.get('status', 'ativo') != 'deletado']
            df_f = df[df.apply(lambda row: row.astype(str).str.contains(busca, case=False).any(), axis=1)] if busca else df

            for idx, row in df_f.iterrows():
                area_base = calcular_area_mm2(row.get('Fio_Principal'))
                
                with st.expander(f"📦 {row.get('Marca')} | {row.get('Potencia_CV')} CV"):
                    c1, c2 = st.columns([2, 1])
                    with c1:
                        st.write(f"**Fio de Fábrica:** {row.get('Fio_Principal')} ({area_base:.3f} mm²)")
                        st.write(f"**Mecânica:** Rolamentos {row.get('Rolamentos')} | Eixo {row.get('Eixo_X')}")
                    
                    with c2:
                        if st.button("🔄 ABA ALTERAR", key=f"alt_{idx}"):
                            st.session_state[f"aba_alt_{idx}"] = not st.session_state.get(f"aba_alt_{idx}", False)
                        
                        if e_admin:
                            if st.button("📝 EDITAR ORIGINAL", key=f"ed_{idx}"):
                                st.session_state[f"aba_ed_{idx}"] = not st.session_state.get(f"aba_ed_{idx}", False)

                    # --- ABA ALTERAR (SUGESTÕES AUTOMÁTICAS) ---
                    if st.session_state.get(f"aba_alt_{idx}"):
                        st.markdown("---")
                        st.subheader("🛠️ Opções de Rebobinagem (Cópia)")
                        opcoes = gerar_opcoes_calculadas(area_base)
                        for op in opcoes[:10]:
                            st.markdown(f"""
                                <div style="border-left: 10px solid {op['cor']}; background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-bottom: 5px; color: black;">
                                    <b>{op['fio']}</b> ({op['diff']:.2f}%) - <span style="color:{op['cor']};"><b>{op['status']}</b></span>
                                </div>
                            """, unsafe_allow_html=True)
                        if st.button("Fechar Aba", key=f"cls_alt_{idx}"):
                            st.session_state[f"aba_alt_{idx}"] = False
                            st.rerun()

                    # --- ABA EDITAR (SALVA E FECHA TUDO) ---
                    if e_admin and st.session_state.get(f"aba_ed_{idx}"):
                        st.markdown("---")
                        with st.form(f"f_ed_{idx}"):
                            st.warning("⚠️ ALTERANDO BANCO DE DADOS ORIGINAL")
                            n_fio = st.text_input("Fio Principal", value=row.get('Fio_Principal'))
                            n_amp = st.text_input("Amperagem", value=row.get('Amperagem'))
                            
                            if st.form_submit_button("SALVAR E FECHAR"):
                                # Atualiza o DataFrame
                                df.at[idx, 'Fio_Principal'] = n_fio
                                df.at[idx, 'Amperagem'] = n_amp
                                salvar_dados(df)
                                
                                # Limpa os estados das abas para elas fecharem no próximo ciclo
                                st.session_state[f"aba_ed_{idx}"] = False
                                st.session_state[f"aba_alt_{idx}"] = False
                                
                                st.success("Dados salvos com sucesso!")
                                st.rerun()
