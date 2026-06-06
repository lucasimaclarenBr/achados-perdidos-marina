import streamlit as st
import pandas as pd
from infra.banco_dados import supabase
from telas import tela_cadastro

# 1. Configuração inicial da tela
st.set_page_config(page_title="Achados & Perdidos Marina", layout="wide", page_icon="⚓")

# Oculta a instrução "Press Enter to submit form" dentro dos formulários
st.markdown("""
    <style>
    [data-testid="InputInstructions"] { display: none; }
    .block-container { padding-top: 2rem; padding-bottom: 0rem; }
    </style>
    """, unsafe_allow_html=True)

# 2. Controle do estado da sessão
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False
    st.session_state['usuario'] = None
    st.session_state['perfil'] = None

# --- FUNÇÃO DE VALIDAÇÃO DE LOGIN ---
def verificar_login(usuario_input, senha_input):
    try:
        # Consulta a tabela de usuários no Supabase
        resposta = supabase.table("usuarios").select("*").eq("login", usuario_input).execute()
        dados = resposta.data
        
        if dados:
            if dados[0]['senha'] == senha_input:
                st.session_state['autenticado'] = True
                st.session_state['usuario'] = dados[0]['nome']
                st.session_state['perfil'] = dados[0]['perfil']
                return True
        return False
    except Exception as e:
        print(f"Erro ao ligar à base de dados: {e}")
        return False

# --- TELA DE LOGIN ---
if not st.session_state['autenticado']:
    st.markdown("<h2 style='text-align: center;'>Achados e Perdidos</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("form_login"):
            usuario_form = st.text_input("Usuário:", autocomplete="username")
            senha_form = st.text_input("Senha:", type="password", autocomplete="current-password")
            botao_entrar = st.form_submit_button("Login")
            
            if botao_entrar:
                if verificar_login(usuario_form, senha_form):
                    st.success("Sessão iniciada com sucesso!")
                    st.rerun()
                else:
                    st.error("Usuário ou senha inválidos.")

# --- CONTEÚDO PRINCIPAL (APÓS AUTENTICAÇÃO) ---
else:
    # Menu Lateral
    st.sidebar.title("Achados & Perdidos Marina")
    st.sidebar.write(f"Olá, **{st.session_state['usuario']}** ({st.session_state['perfil']})")
    st.sidebar.divider()

    # Opções de Navegação de acordo com o perfil
    opcoes_menu = ["Buscar", "Registrar Item", "Dashboard"]
    if st.session_state['perfil'] == 'Admin':
        opcoes_menu.append("Configurações")

    menu = st.sidebar.radio("Navegação", opcoes_menu)
    st.sidebar.divider()
    
    if st.sidebar.button("Terminar Sessão (Logout)"):
        st.session_state['autenticado'] = False
        st.session_state['usuario'] = None
        st.session_state['perfil'] = None
        st.rerun()

    # Roteamento das Páginas
    if menu == "Buscar":
        st.title("🔍 Buscar")
        st.write("Módulo de consulta à base de dados em desenvolvimento.")

    elif menu == "Registrar Item":
        tela_cadastro.mostrar_tela()

    elif menu == "Dashboard":
        st.title("📊 Dashboard")
        st.write("Módulo de indicadores em desenvolvimento.")

    elif menu == "Configurações":
        st.title("⚙️ Configurações do Sistema")
        st.write("Módulo de administração de usuários em desenvolvimento.")