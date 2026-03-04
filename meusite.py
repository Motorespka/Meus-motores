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
    # O .fillna("") garante que nenhum 'nan' apareça na tela
    df = pd.read_csv(arq, sep=';', encoding='utf-8-sig', dtype=str).fillna("")
    # Garante que todas as colunas necessárias existam sem perder dados
    for col in colunas:
        if col not in df.columns:
            df[col] = ""
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

def analisar_viabilidade(area_orig, area_nova):
    if area_orig <= 0: return None
    diff = ((area_nova - area_orig) / area_orig) * 100
    if diff < -7.0:
        return {"diff": diff, "status": "CRÍTICO", "cor": "#dc3545", "msg": "Risco de Queima / Perda de Torque"}
    elif diff < -3.0:
        return {"diff": diff, "status": "ALERTA", "cor": "#ffc107", "msg": "Aquecimento Moderado"}
    else:
        return {"diff": diff, "status": "SEGURO", "cor": "#28a745", "msg": "Motor funcionará bem"}

# --- 4. CONFIGURAÇÃO ---
st.set_page_config(page_title="Pablo Motores Pro", layout="wide")

# Colunas do Banco de Dados (Incluindo as novas de análise)
COL_MOTORES = [
    'Marca', 'Potencia_CV', 'RPM', 'Voltagem', 'Amperagem', 'Polaridade', 
    'Bobina_Principal', 'Fio_Principal', 'Bobina_Auxiliar', 'Fio_Auxiliar', 
    'Tipo_Ligacao', 'Rolamentos', 'Eixo_X', 'Eixo_Y', 'Capacitor', 'status',
    'Ultima_Analise', 'Resultado_Tecnico'
]
COL_FOTOS = ['nome_ligacao', 'caminho_arquivo']

df_motores = carregar_dados(ARQUIVO_CSV, COL_MOTORES)
df_fotos = carregar_dados(ARQUIVO_FOTOS, COL_FOTOS)
lista_ligacoes = [""] + df_fotos['nome_ligacao'].tolist()

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ PABLO MOTORES")
    menu = st.radio("Navegação", ["🔍 CONSULTA", "➕ NOVO MOTOR", "🖼️ BIBLIOTECA", "🗑️ LIXEIRA"])

# --- ABA CONSULTA ---
if menu == "🔍 CONSULTA":
    st.header("🔍 Consulta e Simulação")
    busca = st.text_input("Buscar motor...")
    
    df_f = df_motores[df_motores['status'] != 'deletado']
    if busca:
        df_f = df_f[df_f.apply(lambda r: r.astype(str).str.contains(busca, case=False).any(), axis=1)]

    for idx, row in df_f.iterrows():
        label = f"📦 {row['Marca']} {row['Potencia_CV']}CV - {row['RPM']} RPM"
        with st.expander(label):
            col1, col2, col3 = st.columns([1, 1, 1.2])
            with col1:
                st.write(f"**Fio Principal:** {row['Fio_Principal']}")
                st.write(f"**Amperagem:** {row['Amperagem']}")
                st.write(f"**Capacitor:** {row['Capacitor']}")
            with col2:
                st.write(f"**Rolamentos:** {row['Rolamentos']}")
                st.write(f"**Eixos:** {row['Eixo_X']} / {row['Eixo_Y']}")
            with col3:
                # Mostrar resultado da última análise salva, se houver
                if row['Resultado_Tecnico']:
                    st.info(f"Último teste: {row['Ultima_Analise']} -> {row['Resultado_Tecnico']}")

            # Botões de Ação
            btn_calc, btn_edit, btn_del = st.columns(3)
            if btn_calc.button("🔄 ANALISAR FIOS", key=f"c_{idx}"):
                st.session_state[f"show_calc_{idx}"] = not st.session_state.get(f"show_calc_{idx}", False)
            
            if btn_del.button("🗑️ EXCLUIR", key=f"d_{idx}"):
                df_motores.at[idx, 'status'] = 'deletado'
                salvar_dados(df_motores, ARQUIVO_CSV)
                st.rerun()

            # Área de Cálculo Interativo
            if st.session_state.get(f"show_calc_{idx}"):
                st.markdown("---")
                fio_teste = st.text_input("Fio para teste (Ex: 2x19):", key=f"t_{idx}")
                if fio_teste:
                    a_orig = calcular_area_mm2(row['Fio_Principal'])
                    a_nova = calcular_area_mm2(fio_teste)
                    res = analisar_viabilidade(a_orig, a_nova)
                    if res:
                        st.metric("Diferença de Cobre", f"{res['diff']:.2f}%", delta=f"{res['status']}")
                        st.markdown(f"<div style='background:{res['cor']};color:white;padding:10px;border-radius:5px'>{res['msg']}</div>", unsafe_allow_html=True)
                        
                        if st.button("💾 Salvar esta análise", key=f"sv_{idx}"):
                            df_motores.at[idx, 'Ultima_Analise'] = fio_teste
                            df_motores.at[idx, 'Resultado_Tecnico'] = res['status']
                            salvar_dados(df_motores, ARQUIVO_CSV)
                            st.success("Análise gravada no banco!")

# --- ABA NOVO MOTOR ---
elif menu == "➕ NOVO MOTOR":
    st.header("Cadastrar Motor")
    with st.form("novo"):
        # ... campos de input ...
        # (Omitido para brevidade, mas segue o padrão de preencher o dicionário 'novo' e salvar)
        if st.form_submit_button("Salvar"):
            pass # Lógica de salvamento igual ao seu anterior
