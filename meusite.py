import streamlit as st
import pandas as pd
import os
import re
import urllib.parse
import random
import string
from datetime import datetime, timedelta

# --- 1. CONFIGURAÇÕES DE ARQUIVOS E SESSÃO ---
ARQUIVO_CSV = 'meubancodedados.csv'
ARQUIVO_FOTOS = 'biblioteca_fotos.csv'
PASTA_UPLOADS = 'uploads_ligacoes'

if not os.path.exists(PASTA_UPLOADS):
    os.makedirs(PASTA_UPLOADS)

# Inicialização do Banco de Dados de OS Temporárias (30 dias)
if 'db_os' not in st.session_state:
    st.session_state['db_os'] = []

if 'token_grupo' not in st.session_state:
    st.session_state['token_grupo'] = None

# --- 2. BANCO TÉCNICO AWG ---
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

# --- 3. FUNÇÕES DE APOIO ---
def carregar_dados(arq, colunas):
    if not os.path.exists(arq) or os.stat(arq).st_size == 0:
        return pd.DataFrame(columns=colunas)
    df = pd.read_csv(arq, sep=';', encoding='utf-8-sig', dtype=str).fillna("")
    for col in colunas:
        if col not in df.columns: df[col] = ""
    return df

def salvar_dados(df, arq):
    df.fillna("").to_csv(arq, index=False, sep=';', encoding='utf-8-sig')

def gerar_token():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def limpar_os_vencidas():
    hoje = datetime.now()
    st.session_state['db_os'] = [
        os_item for os_item in st.session_state['db_os'] 
        if os_item.get('expira_em') is None or os_item['expira_em'] > hoje
    ]

def calcular_area_mm2(texto_fio):
    try:
        if not texto_fio or str(texto_fio).lower() in ["nan", ""]: return 0.0
        texto = str(texto_fio).lower().replace('awg', '').strip()
        if 'x' in texto:
            partes = texto.split('x')
            qtd = int(re.findall(r'\d+', partes[0])[0])
            bitola = partes[1].strip()
            return qtd * TABELA_AWG_TECNICA.get(bitola, 0.0)
        bitolas = re.findall(r'\d+', texto)
        return TABELA_AWG_TECNICA.get(bitolas[0], 0.0) if bitolas else 0.0
    except: return 0.0

def gerar_sugestoes(area_alvo):
    sugestoes = []
    if area_alvo <= 0: return []
    for bitola, area_u in TABELA_AWG_TECNICA.items():
        for qtd in range(1, 5):
            area_sim = area_u * qtd
            diff = ((area_sim - area_alvo) / area_alvo) * 100
            if -10.0 <= diff <= 10.0:
                if abs(diff) <= 2.5: cor, status = "#28a745", "EXCELENTE"
                elif abs(diff) <= 6.0: cor, status = "#ffc107", "ACEITÁVEL"
                else: cor, status = "#dc3545", "PERIGOSO"
                sugestoes.append({'fio': f"{qtd}x{bitola} AWG", 'diff': diff, 'cor': cor, 'status': status})
    return sorted(sugestoes, key=lambda x: abs(x['diff']))

# --- 4. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Pablo Motores Pro", layout="wide")
limpar_os_vencidas()

st.markdown("""
    <style>
    .stExpander { border: 1px solid #444 !important; border-radius: 8px !important; margin-bottom: 10px !important; }
    .status-card { padding: 10px; border-radius: 5px; text-align: center; color: white; font-weight: bold; margin: 10px 0; }
    .calc-box { background-color: #1e1e1e; padding: 15px; border-radius: 10px; border-left: 5px solid #007bff; }
    </style>
""", unsafe_allow_html=True)

COL_MOTORES = [
    'Marca', 'Potencia_CV', 'RPM', 'Voltagem', 'Amperagem', 'Polaridade', 
    'Bobina_Principal', 'Fio_Principal', 'Bobina_Auxiliar', 'Fio_Auxiliar', 
    'Tipo_Ligacao', 'Rolamentos', 'Eixo_X', 'Eixo_Y', 'Capacitor', 'status'
]
df_motores = carregar_dados(ARQUIVO_CSV, COL_MOTORES)
df_fotos = carregar_dados(ARQUIVO_FOTOS, ['nome_ligacao', 'caminho_arquivo'])
lista_ligacoes = [""] + df_fotos['nome_ligacao'].tolist()

with st.sidebar:
    st.title("⚙️ PABLO MOTORES")
    
    # --- NOVO: SISTEMA DE GRUPOS POR TOKEN ---
    st.subheader("👥 Grupos de Trabalho")
    if not st.session_state['token_grupo']:
        if st.button("🆕 Criar Novo Grupo"):
            st.session_state['token_grupo'] = gerar_token()
            st.rerun()
        token_input = st.text_input("Ou digite um Token:")
        if st.button("🔗 Entrar"):
            st.session_state['token_grupo'] = token_input.upper()
            st.rerun()
    else:
        st.success(f"Conectado: **{st.session_state['token_grupo']}**")
        if st.button("🚪 Sair do Grupo"):
            st.session_state['token_grupo'] = None
            st.rerun()
    
    st.divider()
    menu = st.radio("Menu Principal", ["🔍 CONSULTA", "➕ NOVO MOTOR", "🖼️ BIBLIOTECA", "📊 PAINEL DE OS", "🗑️ LIXEIRA"])
    st.divider()
    st.subheader("📏 Consulta AWG")
    fio_q = st.text_input("Bitola (ex: 20):")
    if fio_q in TABELA_AWG_TECNICA:
        st.success(f"**{fio_q} AWG** = {TABELA_AWG_TECNICA[fio_q]} mm²")

# --- ABA CONSULTA ---
if menu == "🔍 CONSULTA":
    st.header("🔍 Banco de Dados Técnico")
    busca = st.text_input("Filtrar motor...")
    
    df_f = df_motores[df_motores['status'] != 'deletado']
    if busca:
        df_f = df_f[df_f.apply(lambda r: r.astype(str).str.contains(busca, case=False).any(), axis=1)]

    for idx, row in df_f.iterrows():
        area_ref = calcular_area_mm2(row['Fio_Principal'])
        espiras_base = re.findall(r'\d+', str(row['Bobina_Principal']))
        espiras_ref = int(espiras_base[0]) if espiras_base else 0

        label = f"📦 {row['Marca']} | {row['Potencia_CV']} CV | {row['RPM']} RPM"
        
        with st.expander(label):
            tab1, tab2, tab3 = st.tabs(["📋 DADOS GERAIS", "⚙️ ÁREA TÉCNICA", "👑 PAINEL CHEFE"])
            
            with tab1:
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown("#### ⚡ Elétrica")
                    st.write(f"**Fio Principal:** `{row['Fio_Principal']}`")
                    st.write(f"**Fio Auxiliar:** {row['Fio_Auxiliar']}")
                    st.write(f"**Amperagem:** {row['Amperagem']} A")
                    st.write(f"**Voltagem:** {row['Voltagem']} V")
                    st.write(f"**Pólos:** {row['Polaridade']}")
                    st.write(f"**Capacitor:** {row['Capacitor']}")
                with c2:
                    st.markdown("#### 🔧 Mecânica e Grupos")
                    st.write(f"**Grupos (P/A):** {row['Bobina_Principal']} / {row['Bobina_Auxiliar']}")
                    st.write(f"**Rolamentos:** {row['Rolamentos']}")
                    st.write(f"**Eixo X:** {row['Eixo_X']}")
                    st.write(f"**Eixo Y:** {row['Eixo_Y']}")
                with c3:
                    st.markdown("#### 🖼️ Esquema")
                    tipo = row['Tipo_Ligacao']
                    if tipo and tipo in df_fotos['nome_ligacao'].values:
                        img_path = df_fotos[df_fotos['nome_ligacao'] == tipo]['caminho_arquivo'].values[0]
                        st.image(img_path, use_container_width=True)
                    else: st.caption("Sem esquema.")

            with tab2:
                st.subheader("🛠️ Cálculos e Orçamentos")
                
                # NOVO: ÁREA DO MECÂNICO
                st.markdown("---")
                st.markdown("### 🔧 Orçamento Mecânico")
                with st.container(border=True):
                    col_m1, col_m2 = st.columns(2)
                    check_rol = col_m1.checkbox("Troca de Rolamentos", key=f"rol_{idx}")
                    check_selo = col_m2.checkbox("Troca de Selo Mecânico", key=f"selo_{idx}")
                    
                    obs_mec = st.text_input("Observação Mecânica:", placeholder="Ex: Tampa danificada", key=f"obsm_{idx}")
                    
                    if st.button("✈️ Enviar Orçamento Mecânico", key=f"btnm_{idx}"):
                        msg_mec = f"*OFICINA PABLO MOTORES*\n*GRUPO:* {st.session_state['token_grupo']}\n*Motor:* {row['Marca']} {row['Potencia_CV']}CV\n"
                        if check_rol: msg_mec += f"- Troca de Rolamentos ({row['Rolamentos']})\n"
                        if check_selo: msg_mec += f"- Troca de Selo Mecânico\n"
                        if obs_mec: msg_mec += f"- Obs: {obs_mec}\n"
                        st.markdown(f"[CLIQUE AQUI PARA WHATSAPP](https://wa.me/5531999999999?text={urllib.parse.quote(msg_mec)})")

                # NOVO: ÁREA DO REBOBINADOR
                st.markdown("---")
                st.markdown("### ⚡ Ficha de Rebobinagem")
                with st.container(border=True):
                    r1, r2, r3 = st.columns(3)
                    canais = r1.number_input("Quantidade de Canais", value=24, key=f"can_{idx}")
                    peso_fio = r2.number_input("Peso de Fio (Kg)", value=0.0, step=0.05, key=f"kg_{idx}")
                    isol_tipo = r3.selectbox("Isolação", ["Papel Branco", "Papel Verde"], key=f"iso_{idx}")
                    
                    r4, r5 = st.columns(2)
                    fio_real = r4.text_input("Fio Utilizado (Ex: 2x19 AWG)", value=row['Fio_Principal'], key=f"freal_{idx}")
                    lig_tipo = r5.selectbox("Ligação Feita", ["Série", "Paralelo"], key=f"lreal_{idx}")
                    
                    obs_reb = st.text_area("Observações da Ligação:", placeholder="Ex: Foi feita a ligação de tal forma...", key=f"obsr_{idx}")
                    
                    if st.button("✈️ Enviar Dados Rebobinagem", key=f"btnr_{idx}"):
                        msg_reb = (f"*REBOBINAGEM CONCLUÍDA*\n*GRUPO:* {st.session_state['token_grupo']}\n"
                                   f"*Motor:* {row['Marca']} {row['Potencia_CV']}CV\n"
                                   f"- Canais: {canais}\n- Fio: {fio_real}\n- Peso: {peso_fio}kg\n"
                                   f"- Isolação: {isol_tipo}\n- Ligação: {lig_tipo}\n"
                                   f"- Obs: {obs_reb}")
                        
                        # SALVAR NA LISTA DE 30 DIAS
                        st.session_state['db_os'].append({
                            'token': st.session_state['token_grupo'],
                            'data': datetime.now().strftime("%d/%m/%Y %H:%M"),
                            'info': msg_reb,
                            'expira_em': datetime.now() + timedelta(days=30)
                        })
                        
                        st.markdown(f"[CLIQUE AQUI PARA WHATSAPP](https://wa.me/5531999999999?text={urllib.parse.quote(msg_reb)})")
                        st.success("OS enviada e agendada para exclusão em 30 dias.")

                # CONVERSOR DE TENSÃO (ORIGINAL)
                st.markdown("---")
                with st.container(border=True):
                    st.markdown("### 🔌 Conversor de Tensão e Espiras")
                    col_v1, col_v2 = st.columns(2)
                    v_de = col_v1.number_input("Tensão Original (V):", value=float(row['Voltagem']) if row['Voltagem'].isdigit() else 220.0, key=f"vde_{idx}")
                    v_para = col_v2.number_input("Nova Tensão (V):", value=380.0, key=f"vpa_{idx}")
                    
                    if v_de > 0:
                        fator = v_para / v_de
                        nova_area = area_ref / fator
                        novas_espiras = espiras_ref * fator
                        c_res1, c_res2 = st.columns(2)
                        with c_res1: st.metric("Novas Espiras", f"{round(novas_espiras)} esp")
                        with c_res2: st.metric("Nova Seção", f"{nova_area:.4f} mm²")
                        st.markdown("#### 💡 Sugestões de Bitola:")
                        sugs = gerar_sugestoes(nova_area)
                        for s in sugs[:3]: st.write(f"- {s['fio']} ({s['diff']:.2f}%)")

            with tab3:
                st.subheader("📝 Edição Completa do Motor")
                with st.form(f"form_total_ed_{idx}"):
                    e1, e2, e3 = st.columns(3)
                    with e1:
                        new_marca = st.text_input("Marca", row['Marca'])
                        new_cv = st.text_input("CV", row['Potencia_CV'])
                        new_rpm = st.text_input("RPM", row['RPM'])
                        new_vol = st.text_input("Voltagem", row['Voltagem'])
                        new_amp = st.text_input("Amperagem", row['Amperagem'])
                    with e2:
                        new_fp = st.text_input("Fio Principal", row['Fio_Principal'])
                        new_bp = st.text_input("Bobina Principal (Espiras)", row['Bobina_Principal'])
                        new_fa = st.text_input("Fio Auxiliar", row['Fio_Auxiliar'])
                        new_ba = st.text_input("Bobina Auxiliar (Espiras)", row['Bobina_Auxiliar'])
                        new_pol = st.text_input("Polaridade/Pólos", row['Polaridade'])
                    with e3:
                        new_lig = st.selectbox("Ligação", lista_ligacoes, index=lista_ligacoes.index(row['Tipo_Ligacao']) if row['Tipo_Ligacao'] in lista_ligacoes else 0)
                        new_rol = st.text_input("Rolamentos", row['Rolamentos'])
                        new_ex = st.text_input("Eixo X", row['Eixo_X'])
                        new_ey = st.text_input("Eixo Y", row['Eixo_Y'])
                        new_cap = st.text_input("Capacitor", row['Capacitor'])
                    
                    if st.form_submit_button("💾 SALVAR TODAS AS ALTERAÇÕES"):
                        df_motores.loc[idx, COL_MOTORES[:-1]] = [new_marca, new_cv, new_rpm, new_vol, new_amp, new_pol, new_bp, new_fp, new_ba, new_fa, new_lig, new_rol, new_ex, new_ey, new_cap]
                        salvar_dados(df_motores, ARQUIVO_CSV); st.success("Atualizado!"); st.rerun()
                
                if st.button("🗑️ EXCLUIR MOTOR", key=f"bd_{idx}", type="secondary"):
                    df_motores.at[idx, 'status'] = 'deletado'
                    salvar_dados(df_motores, ARQUIVO_CSV); st.rerun()

elif menu == "➕ NOVO MOTOR":
    st.header("➕ Cadastro de Novo Motor")
    with st.form("add"):
        c1, c2, c3 = st.columns(3)
        with c1:
            m = st.text_input("Marca"); cv = st.text_input("CV"); r = st.text_input("RPM")
            v = st.text_input("Voltagem"); a = st.text_input("Amperagem"); pol = st.text_input("Pólos")
        with c2:
            fp = st.text_input("Fio Principal"); gp = st.text_input("Grupo Principal")
            fa = st.text_input("Fio Auxiliar"); ga = st.text_input("Grupo Auxiliar")
            lig = st.selectbox("Ligação", lista_ligacoes)
        with c3:
            rol = st.text_input("Rolamentos"); ex = st.text_input("Eixo X"); ey = st.text_input("Eixo Y"); cap = st.text_input("Capacitor")
        if st.form_submit_button("SALVAR"):
            novo = {'Marca': m, 'Potencia_CV': cv, 'RPM': r, 'Voltagem': v, 'Amperagem': a, 'Polaridade': pol,
                    'Fio_Principal': fp, 'Bobina_Principal': gp, 'Fio_Auxiliar': fa, 'Bobina_Auxiliar': ga,
                    'Tipo_Ligacao': lig, 'Rolamentos': rol, 'Eixo_X': ex, 'Eixo_Y': ey, 'Capacitor': cap, 'status': 'ativo'}
            df_motores = pd.concat([df_motores, pd.DataFrame([novo])], ignore_index=True)
            salvar_dados(df_motores, ARQUIVO_CSV); st.rerun()

elif menu == "🖼️ BIBLIOTECA":
    st.header("🖼️ Biblioteca de Esquemas")
    with st.form("lib"):
        n = st.text_input("Nome"); f = st.file_uploader("Foto", type=['png','jpg','jpeg'])
        if st.form_submit_button("Subir Foto"):
            if n and f:
                path = os.path.join(PASTA_UPLOADS, f.name)
                with open(path, "wb") as fi: fi.write(f.getbuffer())
                df_f_new = pd.DataFrame([{'nome_ligacao': n, 'caminho_arquivo': path}])
                df_fotos = pd.concat([df_fotos, df_f_new], ignore_index=True)
                salvar_dados(df_fotos, ARQUIVO_FOTOS); st.rerun()
    st.divider()
    cols = st.columns(4)
    for i, r in df_fotos.iterrows():
        with cols[i % 4]:
            st.image(r['caminho_arquivo'], use_container_width=True)
            st.caption(r['nome_ligacao'])
            if st.button("Remover", key=f"rm_{i}"):
                df_fotos = df_fotos.drop(i); salvar_dados(df_fotos, ARQUIVO_FOTOS); st.rerun()

elif menu == "📊 PAINEL DE OS":
    st.header("📊 Histórico de OS Concluídas")
    st.info("As OS abaixo serão excluídas automaticamente após 30 dias da data de conclusão.")
    
    if st.session_state['token_grupo']:
        os_grupo = [x for x in st.session_state['db_os'] if x['token'] == st.session_state['token_grupo']]
        if os_grupo:
            for item in os_grupo:
                with st.expander(f"📌 OS Concluída em {item['data']}"):
                    st.code(item['info'])
                    st.caption(f"🚮 Exclusão agendada para: {item['expira_em'].strftime('%d/%m/%Y')}")
        else:
            st.write("Nenhuma OS registrada para este grupo.")
    else:
        st.warning("Conecte-se a um Grupo na barra lateral para ver o histórico.")

elif menu == "🗑️ LIXEIRA":
    st.header("🗑️ Lixeira")
    deletados = df_motores[df_motores['status'] == 'deletado']
    for i, r in deletados.iterrows():
        col_l1, col_l2 = st.columns([3, 1])
        col_l1.write(f"Motor: {r['Marca']} {r['Potencia_CV']} CV")
        if col_l2.button("Restaurar", key=f"res_{i}"):
            df_motores.at[i, 'status'] = 'ativo'; salvar_dados(df_motores, ARQUIVO_CSV); st.rerun()
