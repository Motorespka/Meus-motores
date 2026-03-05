import streamlit as st
import pandas as pd
import os
import re

# --- 1. CONFIGURAÇÕES DE ARQUIVOS ---
ARQUIVO_CSV = 'meubancodedados.csv'
ARQUIVO_FOTOS = 'biblioteca_fotos.csv'
PASTA_UPLOADS = 'uploads_ligacoes'

if not os.path.exists(PASTA_UPLOADS):
    os.makedirs(PASTA_UPLOADS)

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

st.markdown("""
    <style>
    .stExpander { border: 1px solid #444 !important; border-radius: 8px !important; margin-bottom: 10px !important; }
    .status-card { padding: 10px; border-radius: 5px; text-align: center; color: white; font-weight: bold; margin: 10px 0; }
    .label-info { color: #666; font-size: 0.9em; }
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
    menu = st.radio("Menu Principal", ["🔍 CONSULTA", "➕ NOVO MOTOR", "🖼️ BIBLIOTECA", "🗑️ LIXEIRA"])
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
        label = f"📦 {row['Marca']} | {row['Potencia_CV']} CV | {row['RPM']} RPM"
        
        with st.expander(label):
            tab1, tab2, tab3 = st.tabs(["📋 DADOS GERAIS", "⚙️ ÁREA TÉCNICA", "👑 PAINEL CHEFE"])
            
            with tab1:
                # EXIBIÇÃO COMPLETA DE TODAS AS INFORMAÇÕES
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
                st.subheader("Ferramentas de Conversão")
                
                # CONVERSOR DE TENSÃO AUTOMÁTICO
                with st.container(border=True):
                    st.markdown("**🔌 Conversor de Tensão Automático**")
                    col_v1, col_v2 = st.columns(2)
                    v_de = col_v1.number_input("De (V):", value=220, key=f"vde_{idx}")
                    v_para = col_v2.number_input("Para (V):", value=380, key=f"vpa_{idx}")
                    
                    if v_de > 0:
                        fator = v_para / v_de
                        nova_area = area_ref / fator # Em alta tensão o fio é mais fino
                        st.info(f"💡 **Resultado:** Aumentar espiras em **{fator:.2f}x**. Nova área de fio necessária: **{nova_area:.4f} mm²**")
                
                # SIMULADOR DE FIOS (O que você quer usar vs O que o motor pede)
                st.markdown("**🔄 Simulador de Viabilidade de Fios**")
                fio_teste = st.text_input("Fio que você tem em mãos (Ex: 1x18 ou 2x21):", key=f"ft_{idx}")
                if fio_teste:
                    area_n = calcular_area_mm2(fio_teste)
                    diff = ((area_n - area_ref) / area_ref) * 100 if area_ref > 0 else 0
                    cor = "#28a745" if abs(diff) < 3 else "#ffc107" if abs(diff) < 7 else "#dc3545"
                    st.markdown(f"<div class='status-card' style='background:{cor}'>DIFERENÇA: {diff:.2f}%</div>", unsafe_allow_html=True)
                    
                    col_res1, col_res2 = st.columns(2)
                    col_res1.metric("Espaço na Ranhura", "OK" if diff < 5 else "Apertado")
                    col_res2.metric("Risco de Queima", "Baixo" if diff > -4 else "ALTO (Falta Cobre)")

            with tab3:
                st.subheader("Gestão de Custos")
                p_cobre = st.number_input("Preço KG Cobre (R$)", value=65.0, key=f"pc_{idx}")
                peso = st.number_input("Peso do Cobre no Motor (KG)", value=1.0, key=f"ps_{idx}")
                st.metric("Custo Total de Cobre", f"R$ {p_cobre * peso:.2f}")
                
                st.divider()
                if st.button("📝 EDITAR MOTOR", key=f"be_{idx}"):
                    st.session_state[f"ed_{idx}"] = not st.session_state.get(f"ed_{idx}", False)
                if st.button("🗑️ EXCLUIR", key=f"bd_{idx}"):
                    df_motores.at[idx, 'status'] = 'deletado'
                    salvar_dados(df_motores, ARQUIVO_CSV); st.rerun()

            if st.session_state.get(f"ed_{idx}"):
                with st.form(f"form_ed_{idx}"):
                    st.write("### Editar Informações")
                    new_fp = st.text_input("Fio Principal", value=row['Fio_Principal'])
                    new_amp = st.text_input("Amperagem", value=row['Amperagem'])
                    if st.form_submit_button("Salvar"):
                        df_motores.at[idx, 'Fio_Principal'] = new_fp
                        df_motores.at[idx, 'Amperagem'] = new_amp
                        salvar_dados(df_motores, ARQUIVO_CSV); st.rerun()

# --- DEMAIS ABAS ---
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

elif menu == "🗑️ LIXEIRA":
    st.header("🗑️ Lixeira")
    deletados = df_motores[df_motores['status'] == 'deletado']
    for i, r in deletados.iterrows():
        col_l1, col_l2 = st.columns([3, 1])
        col_l1.write(f"Motor: {r['Marca']} {r['Potencia_CV']} CV")
        if col_l2.button("Restaurar", key=f"res_{i}"):
            df_motores.at[i, 'status'] = 'ativo'; salvar_dados(df_motores, ARQUIVO_CSV); st.rerun()
