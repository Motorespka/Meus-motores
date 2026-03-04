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

# --- 2. BANCO TÉCNICO AWG (DA SUA IMAGEM) ---
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
    df = pd.read_csv(arq, sep=';', encoding='utf-8-sig', dtype=str)
    for col in colunas:
        if col not in df.columns: df[col] = "nan"
    return df

def salvar_dados(df, arq):
    df.to_csv(arq, index=False, sep=';', encoding='utf-8-sig')

def calcular_area_mm2(texto_fio):
    try:
        if not texto_fio or str(texto_fio) == "nan": return 0.0
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

# Estilo CSS para Cards
st.markdown("""
    <style>
    .motor-card { background-color: #1e1e1e; border-radius: 10px; padding: 20px; border: 1px solid #333; margin-bottom: 20px; }
    .status-box { padding: 8px; border-radius: 5px; color: white; font-weight: bold; text-align: center; margin-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

COL_MOTORES = ['Marca', 'Potencia_CV', 'RPM', 'Voltagem', 'Amperagem', 'Polaridade', 'Bobina_Principal', 
               'Fio_Principal', 'Bobina_Auxiliar', 'Fio_Auxiliar', 'Tipo_Ligacao', 'Rolamentos', 
               'Eixo_X', 'Eixo_Y', 'Capacitor', 'status']
COL_FOTOS = ['nome_ligacao', 'caminho_arquivo']

if 'user_data' not in st.session_state: st.session_state['user_data'] = {'usuario': 'admin', 'perfil': 'admin'}

df_motores = carregar_dados(ARQUIVO_CSV, COL_MOTORES)
df_fotos = carregar_dados(ARQUIVO_FOTOS, COL_FOTOS)
lista_ligacoes = ["Nenhuma"] + df_fotos['nome_ligacao'].tolist()

with st.sidebar:
    st.title("⚙️ PABLO MOTORES")
    menu = st.radio("Navegação", ["🔍 CONSULTA", "➕ NOVO MOTOR", "🖼️ BIBLIOTECA", "🗑️ LIXEIRA"])

# --- ABA CONSULTA (REFEITA) ---
if menu == "🔍 CONSULTA":
    st.title("🔍 Consulta Técnica de Motores")
    busca = st.text_input("Busque por Marca, Potência ou Fio...", placeholder="Ex: WEG 2 CV")
    
    df_f = df_motores[df_motores['status'] != 'deletado']
    if busca:
        df_f = df_f[df_f.apply(lambda r: r.astype(str).str.contains(busca, case=False).any(), axis=1)]

    for idx, row in df_f.iterrows():
        area_ref = calcular_area_mm2(row['Fio_Principal'])
        
        with st.expander(f"📦 {row['Marca']} | {row['Potencia_CV']} CV | {row['RPM']} RPM", expanded=False):
            # Layout em Colunas para Dados Técnicos
            col1, col2, col3 = st.columns([1, 1, 1.2])
            
            with col1:
                st.markdown("### ⚡ Elétrica")
                st.write(f"**Fio Principal:** `{row['Fio_Principal']}`")
                st.write(f"**Amperagem:** {row['Amperagem']} A")
                st.write(f"**Voltagem:** {row['Voltagem']} V")
                st.write(f"**Capacitor:** {row['Capacitor']}")
                st.write(f"**Pólos:** {row['Polaridade']}")

            with col2:
                st.markdown("### 🔧 Mecânica")
                st.write(f"**Rolamentos:** {row['Rolamentos']}")
                st.write(f"**Eixo X:** {row['Eixo_X']} | **Y:** {row['Eixo_Y']}")
                st.write(f"**Bobina P:** {row['Bobina_Principal']}")
                st.write(f"**Bobina A:** {row['Bobina_Auxiliar']}")

            with col3:
                st.markdown("### 🖼️ Ligação")
                tipo = row['Tipo_Ligacao']
                if tipo in df_fotos['nome_ligacao'].values:
                    img_path = df_fotos[df_fotos['nome_ligacao'] == tipo]['caminho_arquivo'].values[0]
                    st.image(img_path, caption=f"Esquema: {tipo}", use_container_width=True)
                else:
                    st.info("Sem esquema definido.")

            st.divider()
            
            # Botões de Ação
            bt_c1, bt_c2, bt_c3 = st.columns(3)
            if bt_c1.button("📊 CALCULAR ALTERAÇÃO", key=f"calc_{idx}"):
                st.session_state[f"show_calc_{idx}"] = not st.session_state.get(f"show_calc_{idx}", False)
            if bt_c2.button("📝 EDITAR MOTOR", key=f"edit_{idx}"):
                st.session_state[f"show_edit_{idx}"] = not st.session_state.get(f"show_edit_{idx}", False)
            if bt_c3.button("🗑️ DELETAR", key=f"del_{idx}"):
                df_motores.at[idx, 'status'] = 'deletado'
                salvar_dados(df_motores, ARQUIVO_CSV); st.rerun()

            # Área de Cálculo (Estilizada conforme sua imagem)
            if st.session_state.get(f"show_calc_{idx}"):
                st.markdown("#### 🛠️ Sugestões AWG para Rebobinagem")
                sugest = gerar_sugestoes(area_ref)
                for s in sugest[:6]:
                    st.markdown(f"""
                        <div style="background-color: white; padding: 10px; border-radius: 5px; border-left: 10px solid {s['cor']}; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                            <span style="color: black; font-weight: bold; font-size: 16px;">{s['fio']}</span>
                            <span style="color: #333;">({s['diff']:.2f}%) - <b>{s['status']}</b></span>
                        </div>
                    """, unsafe_allow_html=True)
            
            # Formulário de Edição
            if st.session_state.get(f"show_edit_{idx}"):
                with st.form(f"edit_form_{idx}"):
                    st.write("### Editar Cadastro")
                    e_fio = st.text_input("Fio Principal", value=row['Fio_Principal'])
                    e_lig = st.selectbox("Esquema", lista_ligacoes, index=lista_ligacoes.index(row['Tipo_Ligacao']) if row['Tipo_Ligacao'] in lista_ligacoes else 0)
                    e_rol = st.text_input("Rolamentos", value=row['Rolamentos'])
                    if st.form_submit_button("✅ SALVAR ALTERAÇÕES"):
                        df_motores.at[idx, 'Fio_Principal'] = e_fio
                        df_motores.at[idx, 'Tipo_Ligacao'] = e_lig
                        df_motores.at[idx, 'Rolamentos'] = e_rol
                        salvar_dados(df_motores, ARQUIVO_CSV)
                        st.session_state[f"show_edit_{idx}"] = False; st.rerun()

# --- ABA NOVO MOTOR (FORMULÁRIO COMPLETO) ---
elif menu == "➕ NOVO MOTOR":
    st.title("➕ Cadastrar Novo Motor")
    with st.form("novo_motor"):
        c1, c2, c3 = st.columns(3)
        with c1:
            m = st.text_input("Marca"); cv = st.text_input("CV"); r = st.text_input("RPM")
            v = st.text_input("Voltagem"); a = st.text_input("Amperagem"); pol = st.text_input("Pólos")
        with c2:
            fp = st.text_input("Fio Principal"); gp = st.text_input("Grupo Principal")
            fa = st.text_input("Fio Auxiliar"); ga = st.text_input("Grupo Auxiliar")
            lig = st.selectbox("Esquema de Ligação", lista_ligacoes)
        with c3:
            rol = st.text_input("Rolamentos"); ex = st.text_input("Eixo X"); ey = st.text_input("Eixo Y"); cap = st.text_input("Capacitor")
        
        if st.form_submit_button("💾 SALVAR MOTOR NO BANCO"):
            novo = {'Marca': m, 'Potencia_CV': cv, 'RPM': r, 'Voltagem': v, 'Amperagem': a, 'Polaridade': pol,
                    'Fio_Principal': fp, 'Bobina_Principal': gp, 'Fio_Auxiliar': fa, 'Bobina_Auxiliar': ga,
                    'Tipo_Ligacao': lig, 'Rolamentos': rol, 'Eixo_X': ex, 'Eixo_Y': ey, 'Capacitor': cap, 'status': 'ativo'}
            df_motores = pd.concat([df_motores, pd.DataFrame([novo])], ignore_index=True)
            salvar_dados(df_motores, ARQUIVO_CSV); st.success("Motor cadastrado!"); st.rerun()

# --- ABA BIBLIOTECA (UPLOADS) ---
elif menu == "🖼️ BIBLIOTECA":
    st.title("🖼️ Biblioteca de Esquemas")
    with st.form("add_foto"):
        n = st.text_input("Nome da Ligação (ex: Série)"); f = st.file_uploader("Foto", type=['png','jpg','jpeg'])
        if st.form_submit_button("Adicionar"):
            if n and f:
                path = os.path.join(PASTA_UPLOADS, f.name)
                with open(path, "wb") as file: file.write(f.getbuffer())
                df_fotos = pd.concat([df_fotos, pd.DataFrame([{'nome_ligacao': n, 'caminho_arquivo': path}])], ignore_index=True)
                salvar_dados(df_fotos, ARQUIVO_FOTOS); st.rerun()
    for i, r in df_fotos.iterrows():
        st.image(r['caminho_arquivo'], caption=r['nome_ligacao'], width=200)

elif menu == "🗑️ LIXEIRA":
    st.title("🗑️ Lixeira")
    for i, r in df_motores[df_motores['status'] == 'deletado'].iterrows():
        if st.button(f"Restaurar {r['Marca']} - {r['Potencia_CV']} CV"):
            df_motores.at[i, 'status'] = 'ativo'; salvar_dados(df_motores, ARQUIVO_CSV); st.rerun()
