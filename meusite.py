import streamlit as st
import pandas as pd
import os
import re

# --- 1. CONFIGURAÇÕES DE ARQUIVOS E PASTAS ---
ARQUIVO_CSV = 'meubancodedados.csv'
ARQUIVO_FOTOS = 'biblioteca_fotos.csv'
PASTA_UPLOADS = 'uploads_ligacoes'

if not os.path.exists(PASTA_UPLOADS):
    os.makedirs(PASTA_UPLOADS)

# --- 2. TABELA TÉCNICA AWG (DA SUA IMAGEM) ---
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

# --- 3. FUNÇÕES DE APOIO E SEGURANÇA ---
def carregar_dados(arq, colunas_padrao):
    if not os.path.exists(arq) or os.stat(arq).st_size == 0:
        return pd.DataFrame(columns=colunas_padrao)
    try:
        df = pd.read_csv(arq, sep=';', encoding='utf-8-sig', dtype=str)
        for col in colunas_padrao:
            if col not in df.columns:
                df[col] = ""
        return df
    except:
        return pd.DataFrame(columns=colunas_padrao)

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

# --- 4. CONFIGURAÇÃO DA INTERFACE ---
st.set_page_config(page_title="Pablo Motores Pro", layout="wide")

COLUNAS_MOTORES = [
    'Marca', 'Potencia_CV', 'RPM', 'Voltagem', 'Amperagem', 'Polaridade', 
    'Bobina_Principal', 'Fio_Principal', 'Bobina_Auxiliar', 'Fio_Auxiliar', 
    'Tipo_Ligacao', 'Rolamentos', 'Eixo_X', 'Eixo_Y', 'Capacitor', 'status'
]
COLUNAS_FOTOS = ['nome_ligacao', 'caminho_arquivo']

if 'user_data' not in st.session_state: st.session_state['user_data'] = None

if not st.session_state['user_data']:
    st.session_state['user_data'] = {'usuario': 'admin', 'perfil': 'admin'}
    st.rerun()

else:
    user = st.session_state['user_data']
    e_admin = (user['perfil'] == 'admin')
    df_motores = carregar_dados(ARQUIVO_CSV, COLUNAS_MOTORES)
    df_fotos = carregar_dados(ARQUIVO_FOTOS, COLUNAS_FOTOS)
    lista_ligacoes = ["Nenhuma"] + df_fotos['nome_ligacao'].tolist()

    with st.sidebar:
        st.title("PABLO MOTORES")
        menu = ["🔍 CONSULTAR", "➕ NOVO MOTOR", "🖼️ BIBLIOTECA DE LIGAÇÕES", "🗑️ LIXEIRA"]
        escolha = st.radio("Menu:", menu if e_admin else ["🔍 CONSULTAR"])
        if st.button("Sair"):
            st.session_state['user_data'] = None
            st.rerun()

    # --- ABA: BIBLIOTECA DE LIGAÇÕES ---
    if escolha == "🖼️ BIBLIOTECA DE LIGAÇÕES":
        st.title("🖼️ Biblioteca de Esquemas")
        with st.form("form_lib"):
            nome_lig = st.text_input("Nome da Ligação (Ex: Série, Paralelo, Estrela)")
            arq_foto = st.file_uploader("Upload do Esquema", type=['png', 'jpg', 'jpeg'])
            if st.form_submit_button("Salvar na Biblioteca"):
                if nome_lig and arq_foto:
                    caminho = os.path.join(PASTA_UPLOADS, arq_foto.name)
                    with open(caminho, "wb") as f: f.write(arq_foto.getbuffer())
                    nova_foto = {'nome_ligacao': nome_lig, 'caminho_arquivo': caminho}
                    df_fotos = pd.concat([df_fotos, pd.DataFrame([nova_foto])], ignore_index=True)
                    salvar_dados(df_fotos, ARQUIVO_FOTOS)
                    st.success("Salvo com sucesso!"); st.rerun()
        
        st.write("### Esquemas Cadastrados")
        for i, r in df_fotos.iterrows():
            col_img, col_del = st.columns([4, 1])
            col_img.image(r['caminho_arquivo'], caption=r['nome_ligacao'], width=300)
            if col_del.button("Excluir", key=f"del_lib_{i}"):
                df_fotos = df_fotos.drop(i); salvar_dados(df_fotos, ARQUIVO_FOTOS); st.rerun()

    # --- ABA: CONSULTAR ---
    elif escolha == "🔍 CONSULTAR":
        st.title("🔍 Consulta Técnica")
        busca = st.text_input("Buscar por Marca, CV, Fio...")
        
        # Filtro de ativos
        if not e_admin: df_motores = df_motores[df_motores.get('status') != 'deletado']
        df_f = df_motores[df_motores.apply(lambda row: row.astype(str).str.contains(busca, case=False).any(), axis=1)] if busca else df_motores

        for idx, row in df_f.iterrows():
            if row.get('status') == 'deletado' and not e_admin: continue
            
            area_base = calcular_area_mm2(row.get('Fio_Principal'))
            with st.expander(f"📦 {row.get('Marca')} | {row.get('Potencia_CV')} CV | {row.get('RPM')} RPM"):
                c1, c2, c3 = st.columns([1.5, 1, 1])
                with c1:
                    st.write(f"**Fio Principal:** {row.get('Fio_Principal')} ({area_base:.3f} mm²)")
                    st.write(f"**Amperagem:** {row.get('Amperagem')} | **Voltagem:** {row.get('Voltagem')}")
                    st.write(f"**Pólos:** {row.get('Polaridade')} | **Capacitor:** {row.get('Capacitor')}")
                    st.write(f"**Rolamentos:** {row.get('Rolamentos')}")
                    st.write(f"**Eixos:** X: {row.get('Eixo_X')} / Y: {row.get('Eixo_Y')}")
                    st.write(f"**Grupos:** P: {row.get('Bobina_Principal')} / A: {row.get('Bobina_Auxiliar')}")
                
                with c2:
                    st.write(f"**Esquema:** {row.get('Tipo_Ligacao')}")
                    tipo = row.get('Tipo_Ligacao')
                    if tipo in df_fotos['nome_ligacao'].values:
                        img_path = df_fotos[df_fotos['nome_ligacao'] == tipo]['caminho_arquivo'].values[0]
                        st.image(img_path, use_container_width=True)
                
                with c3:
                    if st.button("🔄 CALCULAR ALTERAÇÃO", key=f"btn_alt_{idx}"):
                        st.session_state[f"aba_alt_{idx}"] = not st.session_state.get(f"aba_alt_{idx}", False)
                    if e_admin:
                        if st.button("📝 EDITAR MOTOR", key=f"btn_ed_{idx}"):
                            st.session_state[f"aba_ed_{idx}"] = not st.session_state.get(f"aba_ed_{idx}", False)
                        if st.button("🗑️ DELETAR", key=f"btn_del_{idx}"):
                            df_motores.at[idx, 'status'] = 'deletado'
                            salvar_dados(df_motores, ARQUIVO_CSV); st.rerun()

                if st.session_state.get(f"aba_alt_{idx}"):
                    st.markdown("---")
                    st.subheader("🛠️ Sugestões AWG")
                    opcoes = gerar_opcoes_calculadas(area_base)
                    for op in opcoes[:8]:
                        st.markdown(f"<div style='border-left:8px solid {op['cor']}; background:#f8f9fa; padding:10px; margin-bottom:5px; color:black;'><b>{op['fio']}</b> ({op['diff']:.2f}%) - {op['status']}</div>", unsafe_allow_html=True)

                if st.session_state.get(f"aba_ed_{idx}"):
                    st.markdown("---")
                    with st.form(f"form_ed_{idx}"):
                        st.info("Editando Dados Técnicos")
                        col_e1, col_e2 = st.columns(2)
                        with col_e1:
                            e_m = st.text_input("Marca", value=row.get('Marca'))
                            e_cv = st.text_input("CV", value=row.get('Potencia_CV'))
                            e_fp = st.text_input("Fio Principal", value=row.get('Fio_Principal'))
                            e_lig = st.selectbox("Ligação", lista_ligacoes, index=lista_ligacoes.index(row.get('Tipo_Ligacao')) if row.get('Tipo_Ligacao') in lista_ligacoes else 0)
                        with col_e2:
                            e_amp = st.text_input("Amperagem", value=row.get('Amperagem'))
                            e_rol = st.text_input("Rolamentos", value=row.get('Rolamentos'))
                            e_cap = st.text_input("Capacitor", value=row.get('Capacitor'))
                        
                        if st.form_submit_button("✅ SALVAR E FECHAR"):
                            df_motores.at[idx, 'Marca'] = e_m
                            df_motores.at[idx, 'Potencia_CV'] = e_cv
                            df_motores.at[idx, 'Fio_Principal'] = e_fp
                            df_motores.at[idx, 'Tipo_Ligacao'] = e_lig
                            df_motores.at[idx, 'Amperagem'] = e_amp
                            df_motores.at[idx, 'Rolamentos'] = e_rol
                            df_motores.at[idx, 'Capacitor'] = e_cap
                            salvar_dados(df_motores, ARQUIVO_CSV)
                            st.session_state[f"aba_ed_{idx}"] = False; st.rerun()

    # --- ABA: NOVO MOTOR (CAMPOS COMPLETOS) ---
    elif escolha == "➕ NOVO MOTOR":
        st.title("➕ Cadastrar Novo Motor")
        with st.form("form_novo"):
            c1, c2, c3 = st.columns(3)
            with c1:
                m = st.text_input("Marca"); cv = st.text_input("CV"); r = st.text_input("RPM")
                v = st.text_input("Voltagem"); a = st.text_input("Amperagem"); pol = st.text_input("Pólos")
            with c2:
                fp = st.text_input("Fio Principal"); gp = st.text_input("Grupo Principal")
                fa = st.text_input("Fio Auxiliar"); ga = st.text_input("Grupo Auxiliar")
                lig = st.selectbox("Esquema de Ligação", lista_ligacoes)
            with c3:
                rol = st.text_input("Rolamentos"); ex_x = st.text_input("Eixo X"); ex_y = st.text_input("Eixo Y")
                cap = st.text_input("Capacitor")
            
            if st.form_submit_button("CADASTRAR MOTOR"):
                novo = {
                    'Marca': m, 'Potencia_CV': cv, 'RPM': r, 'Voltagem': v, 'Amperagem': a, 'Polaridade': pol,
                    'Bobina_Principal': gp, 'Fio_Principal': fp, 'Bobina_Auxiliar': ga, 'Fio_Auxiliar': fa,
                    'Tipo_Ligacao': lig, 'Rolamentos': rol, 'Eixo_X': ex_x, 'Eixo_Y': ex_y, 'Capacitor': cap, 'status': 'ativo'
                }
                df_motores = pd.concat([df_motores, pd.DataFrame([novo])], ignore_index=True)
                salvar_dados(df_motores, ARQUIVO_CSV); st.success("Motor salvo no banco de dados!"); st.rerun()

    # --- ABA: LIXEIRA ---
    elif escolha == "🗑️ LIXEIRA":
        st.title("🗑️ Motores Deletados")
        deletados = df_motores[df_motores.get('status') == 'deletado']
        for i, r in deletados.iterrows():
            st.warning(f"{r['Marca']} - {r['Potencia_CV']} CV")
            if st.button(f"Restaurar #{i}"):
                df_motores.at[i, 'status'] = 'ativo'; salvar_dados(df_motores, ARQUIVO_CSV); st.rerun()
