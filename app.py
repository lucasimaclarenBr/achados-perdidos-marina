import streamlit as st
import pandas as pd
from supabase import create_client, Client
import hmac

# 1. Configuração inicial da tela
st.set_page_config(page_title="Achados & Perdidos Marina", layout="wide", page_icon="⚓")

# 2. Inicialização do Cliente Supabase utilizando os Secrets
@st.cache_resource
def iniciar_conexao() -> Client:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = iniciar_conexao()

# 3. Controle do estado da sessão
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
            # Na v1.0, comparamos o texto simples. Posteriormente aplicaremos criptografia hash.
            if dados[0]['senha'] == senha_input:
                st.session_state['autenticado'] = True
                st.session_state['usuario'] = dados[0]['nome']
                st.session_state['perfil'] = dados[0]['perfil']
                return True
        return False
    except Exception as e:
        st.error(f"Erro ao ligar à base de dados: {e}")
        return False

# --- TELA DE LOGIN ---
if not st.session_state['autenticado']:
    st.markdown("<h2 style='text-align: center;'>Achados e Perdidos</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("form_login"):
            usuario_form = st.text_input("Usuário:")
            senha_form = st.text_input("Senha:", type="password")
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
    opcoes_menu = ["Registrar Item", "Buscar", "Dashboard"]
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
    if menu == "Registrar Item":
        st.title("📦 Registar Novo Item")
        st.write("Módulo de inserção de dados em desenvolvimento.")

    elif menu == "Buscar":
        st.title("🔍 Buscar")
        st.write("Módulo de consulta à base de dados em desenvolvimento.")

    elif menu == "Dashboard":
        st.title("📊 Dashboard")
        st.write("Módulo de indicadores em desenvolvimento.")

    elif menu == "Configurações":
        st.title("⚙️ Configurações do Sistema")
        st.write("Módulo de administração de usuários em desenvolvimento.")