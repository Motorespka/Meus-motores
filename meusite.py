import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime, timedelta
from PIL import Image

# --- 1. CONFIGURAÇÕES E PASTAS ---
ARQUIVO_USUARIOS = 'usuarios.csv'
ARQUIVO_CSV = 'meubancodedados.csv'
LINK_SHEETS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTFbH81UYKGJ6dQvKotxdv4hDxecLmiGUPHN46iexbw8NeS8_e2XdyZnZ8WJnL2XRTLCbFDbBKo_NGE/pub?output=csv"
PASTA_ESQUEMAS = 'esquemas_fotos'
CHAVE_MESTRA_CHEFIA = "PABLO2026"

if not os.path.exists(PASTA_ESQUEMAS): os.makedirs(PASTA_ESQUEMAS)

st.set_page_config(page_title="Pablo Motores | Gestão & Engenharia", layout="wide")

# --- 2. FUNÇÕES DE DADOS ---
def carregar_dados():
    if not os.path.exists(ARQUIVO_CSV):
        return pd.DataFrame()
    return pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8-sig', dtype=str)

def salvar_dados(df):
    df.to_csv(ARQUIVO_CSV, index=False, sep=';', encoding='utf-8-sig')
    st.cache_data.clear()

# --- 3. FLUXO DE ACESSO (Login mantido da base) ---
if 'user_data' not in st.session_state: st.session_state['user_data'] = None

# ... (Lógica de Login aqui) ...

if st.session_state['user_data']:
    user = st.session_state['user_data']
    e_admin = (user['perfil'] == 'admin')
    
    with st.sidebar:
        st.markdown(f"### 👤 {user['usuario'].upper()}")
        menu = ["🔍 CONSULTA"]
        if e_admin: menu += ["➕ NOVO CADASTRO", "🖼️ ADICIONAR FOTO", "🗑️ LIXEIRA"]
        escolha = st.radio("Navegação:", menu)
        if st.button("Sair / Logoff"):
            st.session_state['user_data'] = None
            st.rerun()

    # --- ABA: CONSULTA (COM EDITAR E ALTERAR) ---
    if escolha == "🔍 CONSULTA":
        st.title("⚙️ SISTEMA PABLO MOTORES")
        df = carregar_dados()
        busca = st.text_input("🔍 Pesquisar motor por Marca, CV, RPM ou Fio...")

        if not df.empty:
            # Filtro de segurança para usuários comuns não verem excluídos
            if not e_admin:
                df = df[df['status'] != 'deletado']
            
            df_f = df[df.apply(lambda row: row.astype(str).str.contains(busca, case=False).any(), axis=1)] if busca else df
            
            for idx, row in df_f.iterrows():
                # Define cor se estiver na lixeira
                is_del = row.get('status') == 'deletado'
                label = f"📦 {row['Marca']} | {row['Potencia_CV']} CV" + (" (NA LIXEIRA)" if is_del else "")
                
                with st.expander(label):
                    col_info, col_acoes = st.columns([2, 1])
                    
                    with col_info:
                        st.markdown("### 📋 Dados Atuais")
                        st.write(f"**Fio Principal:** {row.get('Fio_Principal')} | **Fio Aux:** {row.get('Fio_Auxiliar')}")
                        st.write(f"**Grupos:** P: {row.get('Bobina_Principal')} / A: {row.get('Bobina_Auxiliar')}")
                        st.write(f"**Mecânica:** Rol: {row.get('Rolamentos')} | Eixos: {row.get('Eixo_X')} / {row.get('Eixo_Y')}")

                    with col_acoes:
                        st.markdown("### 🛠️ Ações")
                        
                        # 1. ABA ALTERAR (GERAR CÓPIA VISUAL)
                        if st.button("🔄 Alterar (Gerar Cópia)", key=f"btn_alt_{idx}"):
                            st.session_state[f"view_copy_{idx}"] = True

                        # 2. ABA EDITAR (SOMENTE ADMIN - ALTERA O ORIGINAL)
                        if e_admin:
                            if st.button("📝 Editar Original", key=f"btn_edit_{idx}"):
                                st.session_state[f"mode_edit_{idx}"] = True
                            
                            if st.button("🗑️ Excluir", key=f"btn_del_{idx}"):
                                df.at[idx, 'status'] = 'deletado'
                                df.at[idx, 'data_expiracao'] = (datetime.now() + timedelta(days=5)).strftime('%d/%m/%Y')
                                salvar_dados(df)
                                st.rerun()

                    # --- INTERFACE DE CÓPIA (Visualização Apenas) ---
                    if st.session_state.get(f"view_copy_{idx}"):
                        st.divider()
                        st.info("📋 **CÓPIA PARA REBOBINAMENTO (Visualização)**")
                        # Simulamos uma alteração visual rápida
                        fio_copia = st.text_input("Simular Fio Diferente", value=row.get('Fio_Principal'), key=f"f_copy_{idx}")
                        st.success(f"DADOS PARA FOTO: Fio {fio_copia} | Marca {row['Marca']} | CV {row['Potencia_CV']}")
                        st.caption("Nota: Esta cópia não altera o banco de dados oficial.")
                        if st.button("Fechar Cópia", key=f"close_c_{idx}"):
                            del st.session_state[f"view_copy_{idx}"]
                            st.rerun()

                    # --- INTERFACE DE EDIÇÃO (Admin - Altera o Banco) ---
                    if e_admin and st.session_state.get(f"mode_edit_{idx}"):
                        st.divider()
                        st.warning("⚠️ **EDITANDO CADASTRO ORIGINAL**")
                        with st.form(f"form_edit_{idx}"):
                            new_fio_p = st.text_input("Novo Fio Principal", value=row.get('Fio_Principal'))
                            new_amp = st.text_input("Nova Amperagem", value=row.get('Amperagem'))
                            new_rol = st.text_input("Novo Rolamento", value=row.get('Rolamentos'))
                            
                            if st.form_submit_button("Confirmar Alteração no Banco"):
                                df.at[idx, 'Fio_Principal'] = new_fio_p
                                df.at[idx, 'Amperagem'] = new_amp
                                df.at[idx, 'Rolamentos'] = new_rol
                                salvar_dados(df)
                                del st.session_state[f"mode_edit_{idx}"]
                                st.success("Banco de dados atualizado!")
                                st.rerun()

    # --- ABA: NOVO CADASTRO (Com todos os seus campos) ---
    elif escolha == "➕ NOVO CADASTRO" and e_admin:
        st.title("➕ Cadastrar Novo Motor")
        with st.form("cad_novo"):
            c1, c2, c3 = st.columns(3)
            with c1:
                marca = st.text_input("Marca"); cv = st.text_input("Potência (CV)"); rpm = st.text_input("RPM")
                pol = st.text_input("Polaridade"); volt = st.text_input("Voltagem"); amp = st.text_input("Amperagem")
            with c2:
                g_p = st.text_input("Grupo Principal"); f_p = st.text_input("Fio Principal")
                rol = st.text_input("Rolamentos"); ex_x = st.text_input("Eixo X")
            with c3:
                g_a = st.text_input("Grupo Auxiliar"); f_a = st.text_input("Fio Auxiliar")
                cap = st.text_input("Capacitor"); ex_y = st.text_input("Eixo Y")
            
            if st.form_submit_button("SALVAR"):
                # ... lógica de salvar novo registro ...
                st.success("Salvo!")
