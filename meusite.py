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

# --- 3. FUNÇÕES DE APOIO (CORRIGIDAS PARA EVITAR KEYERROR) ---
def carregar_dados(arq, colunas_padrao):
    if not os.path.exists(arq) or os.stat(arq).st_size == 0:
        return pd.DataFrame(columns=colunas_padrao)
    try:
        df = pd.read_csv(arq, sep=';', encoding='utf-8-sig', dtype=str)
        # Garante que todas as colunas necessárias existam
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

# --- 4. INTERFACE ---
st.set_page_config(page_title="Pablo Motores Pro", layout="wide")

# Definição das colunas para evitar o erro de KeyError
COLUNAS_MOTORES = ['Marca', 'Potencia_CV', 'RPM', 'Voltagem', 'Amperagem', 'Polaridade', 'Fio_Principal', 
                   'Bobina_Principal', 'Fio_Auxiliar', 'Bobina_Auxiliar', 'Tipo_Ligacao', 'Rolamentos', 
                   'Eixo_X', 'Eixo_Y', 'Capacitor', 'status']
COLUNAS_FOTOS = ['nome_ligacao', 'caminho_arquivo']

if 'user_data' not in st.session_state: st.session_state['user_data'] = None

if not st.session_state['user_data']:
    st.session_state['user_data'] = {'usuario': 'admin', 'perfil': 'admin'}
    st.rerun()

else:
    df_motores = carregar_dados(ARQUIVO_CSV, COLUNAS_MOTORES)
    df_fotos = carregar_dados(ARQUIVO_FOTOS, COLUNAS_FOTOS)
    lista_ligacoes = ["Nenhuma"] + df_fotos['nome_ligacao'].tolist()

    with st.sidebar:
        st.title("PABLO MOTORES")
        menu = ["🔍 CONSULTAR", "➕ NOVO MOTOR", "🖼️ BIBLIOTECA DE LIGAÇÕES", "🗑️ LIXEIRA"]
        escolha = st.radio("Menu:", menu)

    # --- ABA: BIBLIOTECA ---
    if escolha == "🖼️ BIBLIOTECA DE LIGAÇÕES":
        st.title("🖼️ Biblioteca de Esquemas")
        with st.form("form_lib"):
            nome_lig = st.text_input("Nome da Ligação (ex: Série)")
            arq_foto = st.file_uploader("Imagem", type=['png', 'jpg', 'jpeg'])
            if st.form_submit_button("Salvar"):
                if nome_lig and arq_foto:
                    caminho = os.path.join(PASTA_UPLOADS, arq_foto.name)
                    with open(caminho, "wb") as f: f.write(arq_foto.getbuffer())
                    nova_foto = {'nome_ligacao': nome_lig, 'caminho_arquivo': caminho}
                    df_fotos = pd.concat([df_fotos, pd.DataFrame([nova_foto])], ignore_index=True)
                    salvar_dados(df_fotos, ARQUIVO_FOTOS)
                    st.success("Salvo!"); st.rerun()
        
        for i, r in df_fotos.iterrows():
            st.image(r['caminho_arquivo'], caption=r['nome_ligacao'], width=200)

    # --- ABA: CONSULTA ---
    elif escolha == "🔍 CONSULTAR":
        st.title("🔍 Consulta Técnica")
        busca = st.text_input("Filtrar motor...")
        df_f = df_motores[df_motores.apply(lambda row: row.astype(str).str.contains(busca, case=False).any(), axis=1)] if busca else df_motores

        for idx, row in df_f.iterrows():
            area_base = calcular_area_mm2(row.get('Fio_Principal'))
            with st.expander(f"📦 {row.get('Marca')} | {row.get('Potencia_CV')} CV"):
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.write(f"**Fio:** {row.get('Fio_Principal')} | **Ligação:** {row.get('Tipo_Ligacao')}")
                    tipo = row.get('Tipo_Ligacao')
                    if tipo in df_fotos['nome_ligacao'].values:
                        img_p = df_fotos[df_fotos['nome_ligacao'] == tipo]['caminho_arquivo'].values[0]
                        st.image(img_p, width=400)
                        

[Image of electric motor wiring diagram]


                with c2:
                    if st.button("🔄 CALCULAR", key=f"alt_{idx}"):
                        st.session_state[f"a_{idx}"] = not st.session_state.get(f"a_{idx}", False)
                    if st.button("📝 EDITAR", key=f"ed_{idx}"):
                        st.session_state[f"e_{idx}"] = not st.session_state.get(f"e_{idx}", False)

                if st.session_state.get(f"a_{idx}"):
                    opcoes = gerar_opcoes_calculadas(area_base)
                    for op in opcoes[:5]:
                        st.markdown(f"<div style='border-left:5px solid {op['cor']}; padding:10px; background:#f0f2f6;'>{op['fio']} ({op['diff']:.2f}%)</div>", unsafe_allow_html=True)

                if st.session_state.get(f"e_{idx}"):
                    with st.form(f"f_{idx}"):
                        n_fio = st.text_input("Fio", value=row.get('Fio_Principal'))
                        n_lig = st.selectbox("Ligação", lista_ligacoes, index=lista_ligacoes.index(row.get('Tipo_Ligacao', 'Nenhuma')) if row.get('Tipo_Ligacao') in lista_ligacoes else 0)
                        if st.form_submit_button("✅ SALVAR E FECHAR"):
                            df_motores.at[idx, 'Fio_Principal'] = n_fio
                            df_motores.at[idx, 'Tipo_Ligacao'] = n_lig
                            salvar_dados(df_motores, ARQUIVO_CSV)
                            st.session_state[f"e_{idx}"] = False; st.rerun()

    # --- ABA: NOVO MOTOR (CAMPOS COMPLETOS) ---
    elif escolha == "➕ NOVO MOTOR":
        st.title("➕ Novo Motor")
        with st.form("n_m"):
            c1, c2, c3 = st.columns(3)
            with c1:
                m = st.text_input("Marca"); cv = st.text_input("CV"); r = st.text_input("RPM")
                v = st.text_input("Voltagem"); a = st.text_input("Amperagem"); pol = st.text_input("Pólos")
            with c2:
                fp = st.text_input("Fio Principal"); gp = st.text_input("Grupo Principal")
                fa = st.text_input("Fio Auxiliar"); ga = st.text_input("Grupo Auxiliar"); lig = st.selectbox("Ligação", lista_ligacoes)
            with c3:
                rol = st.text_input("Rolamentos"); ex_x = st.text_input("Eixo X"); ex_y = st.text_input("Eixo Y"); cap = st.text_input("Capacitor")
            
            if st.form_submit_button("SALVAR"):
                novo = {'Marca': m, 'Potencia_CV': cv, 'RPM': r, 'Voltagem': v, 'Amperagem': a, 'Polaridade': pol,
                        'Fio_Principal': fp, 'Bobina_Principal': gp, 'Fio_Auxiliar': fa, 'Bobina_Auxiliar': ga,
                        'Tipo_Ligacao': lig, 'Rolamentos': rol, 'Eixo_X': ex_x, 'Eixo_Y': ex_y, 'Capacitor': cap, 'status': 'ativo'}
                df_motores = pd.concat([df_motores, pd.DataFrame([novo])], ignore_index=True)
                salvar_dados(df_motores, ARQUIVO_CSV); st.success("Salvo!"); st.rerun()

    # --- ABA: LIXEIRA ---
    elif escolha == "🗑️ LIXEIRA":
        st.title("🗑️ Lixeira")
        deletados = df_motores[df_motores.get('status') == 'deletado']
        for i, r in deletados.iterrows():
            if st.button(f"Restaurar {r['Marca']} - {i}"):
                df_motores.at[i, 'status'] = 'ativo'; salvar_dados(df_motores, ARQUIVO_CSV); st.rerun()
