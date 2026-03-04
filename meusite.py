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
    # Carrega e substitui imediatamente qualquer valor nulo por vazio ""
    df = pd.read_csv(arq, sep=';', encoding='utf-8-sig', dtype=str).fillna("")
    for col in colunas:
        if col not in df.columns: df[col] = ""
    return df

def salvar_dados(df, arq):
    # Antes de salvar, garante que nans viraram vazios
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
                if abs(diff) <= 2.0: cor, status = "#28a745", "SEGURA"
                elif abs(diff) <= 6.0: cor, status = "#ffc107", "ALERTA"
                else: cor, status = "#dc3545", "ARRISCADA"
                sugestoes.append({'fio': f"{qtd}x{bitola} AWG", 'diff': diff, 'cor': cor, 'status': status})
    return sorted(sugestoes, key=lambda x: abs(x['diff']))

# --- 4. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Pablo Motores Pro", layout="wide")

# CSS para remover bordas indesejadas e melhorar cards
st.markdown("""
    <style>
    .stExpander { border: 1px solid #444 !important; border-radius: 8px !important; margin-bottom: 10px !important; }
    .calc-card {
        background-color: white; 
        padding: 12px; 
        border-radius: 8px; 
        color: black; 
        margin-bottom: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

COL_MOTORES = [
    'Marca', 'Potencia_CV', 'RPM', 'Voltagem', 'Amperagem', 'Polaridade', 
    'Bobina_Principal', 'Fio_Principal', 'Bobina_Auxiliar', 'Fio_Auxiliar', 
    'Tipo_Ligacao', 'Rolamentos', 'Eixo_X', 'Eixo_Y', 'Capacitor', 'status'
]
COL_FOTOS = ['nome_ligacao', 'caminho_arquivo']

if 'user_data' not in st.session_state: st.session_state['user_data'] = {'usuario': 'admin', 'perfil': 'admin'}

df_motores = carregar_dados(ARQUIVO_CSV, COL_MOTORES)
df_fotos = carregar_dados(ARQUIVO_FOTOS, COL_FOTOS)
lista_ligacoes = [""] + df_fotos['nome_ligacao'].tolist()

with st.sidebar:
    st.title("⚙️ PABLO MOTORES")
    menu = st.radio("Menu Principal", ["🔍 CONSULTA", "➕ NOVO MOTOR", "🖼️ BIBLIOTECA", "🗑️ LIXEIRA"])
    st.divider()
    st.info("Sistema v3.0 - Estável")

# --- ABA CONSULTA ---
if menu == "🔍 CONSULTA":
    st.header("🔍 Banco de Dados Técnico")
    busca = st.text_input("Filtrar motor...", placeholder="Digite marca, potência ou bitola...")
    
    df_f = df_motores[df_motores['status'] != 'deletado']
    if busca:
        df_f = df_f[df_f.apply(lambda r: r.astype(str).str.contains(busca, case=False).any(), axis=1)]

    if df_f.empty:
        st.warning("Nenhum motor encontrado.")
    
    for idx, row in df_f.iterrows():
        area_ref = calcular_area_mm2(row['Fio_Principal'])
        
        # Cabeçalho do Expander limpo
        label = f"📦 {row['Marca']} | {row['Potencia_CV']} CV | {row['RPM']} RPM"
        with st.expander(label):
            col1, col2, col3 = st.columns([1, 1, 1.2])
            
            with col1:
                st.markdown("#### ⚡ Parte Elétrica")
                st.write(f"**Fio Principal:** `{row['Fio_Principal']}`")
                st.write(f"**Amperagem:** {row['Amperagem']}")
                st.write(f"**Voltagem:** {row['Voltagem']}")
                st.write(f"**Capacitor:** {row['Capacitor']}")
                st.write(f"**Pólos:** {row['Polaridade']}")

            with col2:
                st.markdown("#### 🔧 Mecânica e Grupos")
                st.write(f"**Rolamentos:** {row['Rolamentos']}")
                st.write(f"**Eixos:** {row['Eixo_X']} / {row['Eixo_Y']}")
                st.write(f"**Grupos P:** {row['Bobina_Principal']}")
                st.write(f"**Grupos A:** {row['Bobina_Auxiliar']}")

            with col3:
                st.markdown("#### 🖼️ Esquema")
                tipo = row['Tipo_Ligacao']
                if tipo and tipo in df_fotos['nome_ligacao'].values:
                    img_path = df_fotos[df_fotos['nome_ligacao'] == tipo]['caminho_arquivo'].values[0]
                    st.image(img_path, use_container_width=True)
                else:
                    st.caption("Nenhum esquema vinculado.")

            st.write("")
            c_bt1, c_bt2, c_bt3 = st.columns(3)
            if c_bt1.button("🔄 CALCULAR AWG", key=f"c_{idx}", use_container_width=True):
                st.session_state[f"sc_{idx}"] = not st.session_state.get(f"sc_{idx}", False)
            if c_bt2.button("📝 EDITAR", key=f"e_{idx}", use_container_width=True):
                st.session_state[f"se_{idx}"] = not st.session_state.get(f"se_{idx}", False)
            if c_bt3.button("🗑️ EXCLUIR", key=f"d_{idx}", use_container_width=True):
                df_motores.at[idx, 'status'] = 'deletado'
                salvar_dados(df_motores, ARQUIVO_CSV); st.rerun()

            # Cálculo Intuitivo (Estilo sua imagem)
            if st.session_state.get(f"sc_{idx}"):
                st.markdown("---")
                st.subheader("🛠️ Simulação de Bitolas")
                sugest = gerar_sugestoes(area_ref)
                if not sugest: st.info("Insira um Fio Principal válido para calcular.")
                for s in sugest[:6]:
                    st.markdown(f"""
                        <div class="calc-card" style="border-left: 10px solid {s['cor']};">
                            <div style="display: flex; justify-content: space-between;">
                                <b>{s['fio']}</b>
                                <span>{s['diff']:.2f}% | <b>{s['status']}</b></span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            
            # Edição
            if st.session_state.get(f"se_{idx}"):
                st.markdown("---")
                with st.form(f"form_ed_{idx}"):
                    st.write("### ✏️ Editar Motor")
                    col_ed1, col_ed2 = st.columns(2)
                    with col_ed1:
                        ed_m = st.text_input("Marca", value=row['Marca'])
                        ed_cv = st.text_input("CV", value=row['Potencia_CV'])
                        ed_fp = st.text_input("Fio Principal", value=row['Fio_Principal'])
                    with col_ed2:
                        ed_lig = st.selectbox("Esquema", lista_ligacoes, index=lista_ligacoes.index(row['Tipo_Ligacao']) if row['Tipo_Ligacao'] in lista_ligacoes else 0)
                        ed_rol = st.text_input("Rolamentos", value=row['Rolamentos'])
                    if st.form_submit_button("✅ SALVAR"):
                        df_motores.loc[idx, ['Marca', 'Potencia_CV', 'Fio_Principal', 'Tipo_Ligacao', 'Rolamentos']] = [ed_m, ed_cv, ed_fp, ed_lig, ed_rol]
                        salvar_dados(df_motores, ARQUIVO_CSV)
                        st.session_state[f"se_{idx}"] = False; st.rerun()

# --- ABA NOVO MOTOR ---
elif menu == "➕ NOVO MOTOR":
    st.header("➕ Cadastro de Novo Motor")
    with st.form("add_motor"):
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
        
        if st.form_submit_button("💾 SALVAR DADOS"):
            novo = {'Marca': m, 'Potencia_CV': cv, 'RPM': r, 'Voltagem': v, 'Amperagem': a, 'Polaridade': pol,
                    'Fio_Principal': fp, 'Bobina_Principal': gp, 'Fio_Auxiliar': fa, 'Bobina_Auxiliar': ga,
                    'Tipo_Ligacao': lig, 'Rolamentos': rol, 'Eixo_X': ex, 'Eixo_Y': ey, 'Capacitor': cap, 'status': 'ativo'}
            df_motores = pd.concat([df_motores, pd.DataFrame([novo])], ignore_index=True)
            salvar_dados(df_motores, ARQUIVO_CSV); st.success("Cadastrado!"); st.rerun()

# --- ABA BIBLIOTECA ---
elif menu == "🖼️ BIBLIOTECA":
    st.header("🖼️ Biblioteca de Esquemas")
    with st.form("lib"):
        n = st.text_input("Nome (ex: Série)"); f = st.file_uploader("Foto", type=['png','jpg','jpeg'])
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

# --- ABA LIXEIRA ---
elif menu == "🗑️ LIXEIRA":
    st.header("🗑️ Lixeira")
    deletados = df_motores[df_motores['status'] == 'deletado']
    if deletados.empty: st.info("Lixeira vazia.")
    for i, r in deletados.iterrows():
        col_l1, col_l2 = st.columns([3, 1])
        col_l1.write(f"Motor: {r['Marca']} {r['Potencia_CV']} CV")
        if col_l2.button("Restaurar", key=f"res_{i}"):
            df_motores.at[i, 'status'] = 'ativo'; salvar_dados(df_motores, ARQUIVO_CSV); st.rerun()

altere a parte de "calcular awg" e como vamos calcular varias variaveis pra saber se o motor pode funcionar ou nao, acrescente algumas que faça sentido sem mudar o codigo base
