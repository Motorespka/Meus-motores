import streamlit as st
import pandas as pd
import os
import re
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

# --- 2. FUNÇÕES DE ENGENHARIA ---
def calcular_area_mm2(texto_fio):
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
    sugestoes = []
    if area_alvo <= 0: return []
    for bitola, area_u in TABELA_AWG_TECNICA.items():
        for qtd in range(1, 5):
            area_sim = area_u * qtd
            diff = ((area_sim - area_alvo) / area_alvo) * 100
            if -12.0 <= diff <= 12.0:
                if abs(diff) <= 2.5: cor, status = "#2ecc71", "SEGURA (Verde)"
                elif 2.5 < diff <= 7.5 or -7.5 <= diff < -2.5: cor, status = "#f1c40f", "ALERTA (Amarelo)"
                else: cor, status = "#e74c3c", "ARRISCADA (Vermelho)"
                sugestoes.append({'fio': f"{qtd}x{bitola} AWG", 'diff': diff, 'cor': cor, 'status': status})
    return sorted(sugestoes, key=lambda x: abs(x['diff']))

# --- 3. BANCO DE DADOS ---
ARQUIVO_CSV = 'meubancodedados.csv'
def carregar_dados():
    if not os.path.exists(ARQUIVO_CSV): return pd.DataFrame()
    df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig', dtype=str)
    return df

def salvar_dados(df):
    df.to_csv(ARQUIVO_CSV, index=False, sep=';', encoding='utf-8-sig')

# --- 4. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Pablo Motores Pro", layout="wide")

if 'user_data' not in st.session_state: st.session_state['user_data'] = None

# Login Automático para teste (Substitua pela sua lógica se necessário)
if not st.session_state['user_data']:
    st.session_state['user_data'] = {'usuario': 'admin', 'perfil': 'admin'}
    st.rerun()

else:
    user = st.session_state['user_data']
    e_admin = (user['perfil'] == 'admin')

    with st.sidebar:
        st.title("PABLO MOTORES")
        menu = ["🔍 CONSULTAR", "➕ NOVO MOTOR", "🗑️ LIXEIRA"]
        escolha = st.radio("Menu:", menu)
        if st.button("Sair"):
            st.session_state['user_data'] = None
            st.rerun()

    # --- ABA 1: CONSULTA ---
    if escolha == "🔍 CONSULTAR":
        st.title("🔍 Consulta e Engenharia")
        df = carregar_dados()
        busca = st.text_input("Pesquisar motor...")

        if not df.empty:
            df_f = df[df.apply(lambda row: row.astype(str).str.contains(busca, case=False).any(), axis=1)] if busca else df

            for idx, row in df_f.iterrows():
                area_base = calcular_area_mm2(row.get('Fio_Principal'))
                
                with st.expander(f"📦 {row.get('Marca')} | {row.get('Potencia_CV')} CV"):
                    c1, c2, c3 = st.columns([1.5, 1, 1])
                    
                    with c1:
                        st.write(f"**Fio Fábrica:** {row.get('Fio_Principal')} ({area_base:.3f} mm²)")
                        st.write(f"**Amperagem:** {row.get('Amperagem')} | **RPM:** {row.get('RPM')}")
                        st.write(f"**Rolamentos:** {row.get('Rolamentos')}")

                    with c2:
                        if st.button("🔄 ALTERAR", key=f"alt_{idx}"):
                            st.session_state[f"show_alt_{idx}"] = not st.session_state.get(f"show_alt_{idx}", False)
                        if st.button("🖼️ FOTOS", key=f"img_{idx}"):
                            st.session_state[f"show_img_{idx}"] = not st.session_state.get(f"show_img_{idx}", False)

                    with c3:
                        if e_admin:
                            if st.button("📝 EDITAR", key=f"ed_{idx}"):
                                st.session_state[f"show_ed_{idx}"] = not st.session_state.get(f"show_ed_{idx}", False)
                            if st.button("🗑️ EXCLUIR", key=f"del_{idx}"):
                                df.at[idx, 'status'] = 'deletado'
                                salvar_dados(df); st.rerun()

                    # --- ABA FOTOS (CORRIGIDA) ---
                    if st.session_state.get(f"show_img_{idx}"):
                        st.markdown("---")
                        st.subheader("🖼️ Esquema Visual")
                        img_url = row.get('Link_Foto', '')
                        if img_url and str(img_url) != "nan":
                            st.image(img_url)
                        else:
                            st.info("Sem foto cadastrada.")

                    # --- ABA ALTERAR ---
                    if st.session_state.get(f"show_alt_{idx}"):
                        st.markdown("---")
                        st.subheader("🛠️ Opções de Rebobinagem")
                        opcoes = gerar_opcoes_calculadas(area_base)
                        for op in opcoes[:8]:
                            st.markdown(f"<div style='border-left:8px solid {op['cor']}; background:#f8f9fa; padding:10px; margin-bottom:5px; color:black;'><b>{op['fio']}</b> ({op['diff']:.2f}%) - {op['status']}</div>", unsafe_allow_html=True)

                    # --- ABA EDITAR (SALVAR E FECHAR TUDO) ---
                    if e_admin and st.session_state.get(f"show_ed_{idx}"):
                        st.markdown("---")
                        with st.form(f"form_ed_{idx}"):
                            st.warning("✍️ Editando Cadastro")
                            # TODOS OS CAMPOS REESTABELECIDOS PARA O CÓDIGO NÃO ENCOLHER
                            ed_fio = st.text_input("Fio Principal", value=row.get('Fio_Principal'))
                            ed_amp = st.text_input("Amperagem", value=row.get('Amperagem'))
                            ed_rol = st.text_input("Rolamentos", value=row.get('Rolamentos'))
                            ed_rpm = st.text_input("RPM", value=row.get('RPM'))
                            ed_volt = st.text_input("Voltagem", value=row.get('Voltagem'))
                            ed_link = st.text_input("Link da Foto", value=row.get('Link_Foto', ''))
                            
                            if st.form_submit_button("✅ SALVAR E FECHAR"):
                                df.at[idx, 'Fio_Principal'] = ed_fio
                                df.at[idx, 'Amperagem'] = ed_amp
                                df.at[idx, 'Rolamentos'] = ed_rol
                                df.at[idx, 'RPM'] = ed_rpm
                                df.at[idx, 'Voltagem'] = ed_volt
                                df.at[idx, 'Link_Foto'] = ed_link
                                salvar_dados(df)
                                # Lógica para fechar todas as abas
                                st.session_state[f"show_ed_{idx}"] = False
                                st.session_state[f"show_alt_{idx}"] = False
                                st.session_state[f"show_img_{idx}"] = False
                                st.rerun()

    # --- ABA NOVO MOTOR (FORMULÁRIO COMPLETO) ---
    elif escolha == "➕ NOVO MOTOR" and e_admin:
        st.title("➕ Novo Cadastro")
        with st.form("form_novo"):
            c1, c2, c3 = st.columns(3)
            with c1:
                m = st.text_input("Marca"); cv = st.text_input("CV"); r = st.text_input("RPM")
                v = st.text_input("Voltagem"); a = st.text_input("Amperagem")
            with c2:
                fp = st.text_input("Fio Principal"); gp = st.text_input("Grupo Principal")
                fa = st.text_input("Fio Auxiliar"); ga = st.text_input("Grupo Auxiliar")
                cp = st.text_input("Capacitor")
            with c3:
                rol = st.text_input("Rolamentos"); ex_x = st.text_input("Eixo X"); ex_y = st.text_input("Eixo Y")
                foto = st.text_input("Link da Foto")
            
            if st.form_submit_button("CADASTRAR"):
                novo = {'Marca': m, 'Potencia_CV': cv, 'RPM': r, 'Voltagem': v, 'Amperagem': a,
                        'Fio_Principal': fp, 'Bobina_Principal': gp, 'Fio_Auxiliar': fa, 'Bobina_Auxiliar': ga,
                        'Capacitor': cp, 'Rolamentos': rol, 'Eixo_X': ex_x, 'Eixo_Y': ex_y, 'Link_Foto': foto, 'status': 'ativo'}
                df_n = pd.concat([carregar_dados(), pd.DataFrame([novo])], ignore_index=True)
                salvar_dados(df_n); st.success("Salvo!"); st.rerun()
