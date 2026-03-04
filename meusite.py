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

# --- 2. MOTOR DE CÁLCULO E PERFORMANCE ---
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

# --- 3. GESTÃO DE ARQUIVOS ---
ARQUIVO_CSV = 'meubancodedados.csv'

def carregar_dados():
    if not os.path.exists(ARQUIVO_CSV): return pd.DataFrame()
    df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig', dtype=str)
    df.columns = df.columns.str.strip()
    return df

def salvar_dados(df):
    df.to_csv(ARQUIVO_CSV, index=False, sep=';', encoding='utf-8-sig')

# --- 4. INTERFACE E LOGIN ---
st.set_page_config(page_title="Pablo Motores - Sistema de Engenharia", layout="wide")

if 'user_data' not in st.session_state:
    st.session_state['user_data'] = None

if not st.session_state['user_data']:
    st.title("🔐 Pablo Motores - Acesso")
    with st.form("login_pablo"):
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        if st.form_submit_button("Entrar"):
            if u == "admin" and p == "pablo2026":
                st.session_state['user_data'] = {'usuario': u, 'perfil': 'admin'}
                st.rerun()
            else: st.error("Acesso Negado")
else:
    user = st.session_state['user_data']
    e_admin = (user['perfil'] == 'admin')

    with st.sidebar:
        st.header(f"Olá, {user['usuario'].upper()}")
        menu = ["🔍 CONSULTAR MOTORES", "➕ CADASTRAR NOVO", "🗑️ LIXEIRA"]
        escolha = st.radio("Selecione a tarefa:", menu if e_admin else ["🔍 CONSULTAR MOTORES"])
        if st.button("Sair do Sistema"):
            st.session_state['user_data'] = None
            st.rerun()

    # --- ABA 1: CONSULTA (CÉREBRO DO SISTEMA) ---
    if escolha == "🔍 CONSULTAR MOTORES":
        st.title("🔍 Busca Técnica e Simulação")
        df = carregar_dados()
        busca = st.text_input("Pesquise por Marca, CV, Fio, RPM ou Rolamento...")

        if not df.empty:
            if not e_admin: df = df[df.get('status', 'ativo') != 'deletado']
            df_f = df[df.apply(lambda row: row.astype(str).str.contains(busca, case=False).any(), axis=1)] if busca else df

            for idx, row in df_f.iterrows():
                area_orig = calcular_area_mm2(row.get('Fio_Principal'))
                with st.expander(f"📦 {row.get('Marca')} | {row.get('Potencia_CV')} CV | {row.get('RPM')} RPM"):
                    col_info, col_opc = st.columns([2, 1])
                    
                    with col_info:
                        st.markdown("### 📊 Dados Técnicos de Fábrica")
                        st.write(f"**Fio Principal:** {row.get('Fio_Principal')} ({area_orig:.3f} mm²)")
                        st.write(f"**Amperagem:** {row.get('Amperagem')} | **Voltagem:** {row.get('Voltagem')}")
                        st.write(f"**Pólos:** {row.get('Polaridade')} | **RPM:** {row.get('RPM')}")
                        st.write(f"**Bobina Principal:** {row.get('Bobina_Principal')}")
                        st.write(f"**Bobina Auxiliar:** {row.get('Bobina_Auxiliar')} | **Fio Aux:** {row.get('Fio_Auxiliar')}")
                        st.write(f"**Capacitor:** {row.get('Capacitor')} | **Rolamentos:** {row.get('Rolamentos')}")
                        st.write(f"**Mecânica:** Eixo X: {row.get('Eixo_X')} | Eixo Y: {row.get('Eixo_Y')}")

                    with col_opc:
                        st.markdown("### 🛠️ Ações")
                        if st.button("🔄 ABRIR ABA ALTERAR", key=f"alt_btn_{idx}"):
                            st.session_state[f"aba_alt_{idx}"] = not st.session_state.get(f"aba_alt_{idx}", False)
                        
                        if e_admin:
                            if st.button("📝 EDITAR ORIGINAL", key=f"ed_btn_{idx}"):
                                st.session_state[f"aba_ed_{idx}"] = not st.session_state.get(f"aba_ed_{idx}", False)
                            if st.button("🗑️ ENVIAR PARA LIXEIRA", key=f"del_btn_{idx}"):
                                df.at[idx, 'status'] = 'deletado'
                                salvar_dados(df); st.rerun()

                    # --- LÓGICA: SIMULADOR DE CORES ---
                    if st.session_state.get(f"aba_alt_{idx}"):
                        st.markdown("---")
                        st.subheader("💡 Sugestões de Fios para Rebobinagem")
                        opcoes = gerar_opcoes_calculadas(area_orig)
                        for op in opcoes[:10]:
                            st.markdown(f"""
                                <div style="border-left: 10px solid {op['cor']}; background-color: #f8f9fa; padding: 12px; border-radius: 8px; margin-bottom: 8px; color: black; border: 1px solid #ddd;">
                                    <span style="font-size: 18px;"><b>{op['fio']}</b></span> 
                                    <span style="color: #555;">(Diferença: {op['diff']:.2f}%)</span><br>
                                    <b style="color: {op['cor']};">{op['status']}</b>
                                </div>
                            """, unsafe_allow_html=True)
                        if st.button("Fechar Alteração", key=f"cls_alt_{idx}"):
                            st.session_state[f"aba_alt_{idx}"] = False; st.rerun()

                    # --- LÓGICA: EDITAR ORIGINAL (SALVA E FECHA) ---
                    if e_admin and st.session_state.get(f"aba_ed_{idx}"):
                        st.markdown("---")
                        with st.form(f"form_ed_{idx}"):
                            st.warning("⚠️ Você está editando os dados permanentes de fábrica.")
                            f_p = st.text_input("Fio Principal", value=row.get('Fio_Principal'))
                            amp = st.text_input("Amperagem", value=row.get('Amperagem'))
                            rol = st.text_input("Rolamentos", value=row.get('Rolamentos'))
                            v_v = st.text_input("Voltagem", value=row.get('Voltagem'))
                            if st.form_submit_button("✅ SALVAR E FECHAR ABA"):
                                df.at[idx, 'Fio_Principal'] = f_p
                                df.at[idx, 'Amperagem'] = amp
                                df.at[idx, 'Rolamentos'] = rol
                                df.at[idx, 'Voltagem'] = v_v
                                salvar_dados(df)
                                st.session_state[f"aba_ed_{idx}"] = False
                                st.rerun()

    # --- ABA 2: NOVO CADASTRO (TODOS OS CAMPOS) ---
    elif escolha == "➕ CADASTRAR NOVO" and e_admin:
        st.title("➕ Inserir Novo Motor no Banco")
        with st.form("novo_motor_completo"):
            c1, c2, c3 = st.columns(3)
            with c1:
                marca = st.text_input("Marca"); cv = st.text_input("Potência (CV)"); rpm = st.text_input("RPM")
                pol = st.text_input("Polaridade/Pólos"); volt = st.text_input("Voltagem"); amp = st.text_input("Amperagem")
            with c2:
                g_p = st.text_input("Grupo Principal"); f_p = st.text_input("Fio Principal")
                g_a = st.text_input("Grupo Auxiliar"); f_a = st.text_input("Fio Auxiliar")
                cap = st.text_input("Capacitor")
            with c3:
                rol = st.text_input("Rolamentos"); ex_x = st.text_input("Eixo X"); ex_y = st.text_input("Eixo Y")
                obs = st.text_area("Observações Adicionais")
            
            if st.form_submit_button("💾 SALVAR MOTOR DEFINITIVAMENTE"):
                novo = {
                    'Marca': marca, 'Potencia_CV': cv, 'RPM': rpm, 'Polaridade': pol, 'Voltagem': volt,
                    'Amperagem': amp, 'Bobina_Principal': g_p, 'Fio_Principal': f_p, 'Bobina_Auxiliar': g_a,
                    'Fio_Auxiliar': f_a, 'Capacitor': cap, 'Rolamentos': rol, 'Eixo_X': ex_x, 'Eixo_Y': ex_y,
                    'status': 'ativo'
                }
                df_novo = pd.concat([carregar_dados(), pd.DataFrame([novo])], ignore_index=True)
                salvar_dados(df_novo); st.success("Motor cadastrado com sucesso!"); st.rerun()

    # --- ABA 3: LIXEIRA ---
    elif escolha == "🗑️ LIXEIRA" and e_admin:
        st.title("🗑️ Motores em Quarentena")
        df = carregar_dados()
        deletados = df[df.get('status') == 'deletado']
        if deletados.empty: st.info("Lixeira vazia.")
        for idx, r in deletados.iterrows():
            col_l1, col_l2 = st.columns([3, 1])
            col_l1.write(f"❌ {r['Marca']} - {r['Potencia_CV']} CV")
            if col_l2.button(f"Restaurar #{idx}"):
                df.at[idx, 'status'] = 'ativo'
                salvar_dados(df); st.rerun()
