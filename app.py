import streamlit as st
from infra.banco_dados import supabase
from telas import tela_cadastro, tela_busca

st.set_page_config(
    page_title="Achados & Perdidos Marina",
    layout="wide",
    page_icon="⚓",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
/* ── Margens ── */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 0rem !important;
}
[data-testid="InputInstructions"] { display: none; }
hr {
    margin-top: 0.5rem !important;
    margin-bottom: 0.5rem !important;
}

/* ── Sidebar: azul marinho fixo em ambos os temas ── */
section[data-testid="stSidebar"] {
    background-color: #141824 !important;
}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] p {
    color: #c8d3e8 !important;
}
section[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.1) !important;
}
section[data-testid="stSidebar"] button {
    background-color: transparent !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    color: #c8d3e8 !important;
}
section[data-testid="stSidebar"] button:hover {
    background-color: #cc0000 !important;
    border-color: #cc0000 !important;
    color: #ffffff !important;
}

/* ── Abas ── */
div[data-baseweb="tab-list"] button[aria-selected="true"] p {
    color: #ffffff !important;
    font-weight: 600 !important;
}
div[data-baseweb="tab-list"] button[aria-selected="true"] {
    border-bottom-color: #00897b !important;
}
div[data-baseweb="tab-highlight"] {
    background-color: #00897b !important;
}
div[data-baseweb="tab-list"] button[aria-selected="false"] p {
    color: #888888 !important;
}
div[data-baseweb="tab-list"] button:hover p {
    color: #ffffff !important;
}

/* ── Botões: verde padrão ── */
div[data-testid="stButton"] > button {
    border-radius: 6px !important;
    font-weight: 500 !important;
    transition: all 0.15s ease !important;
}
div[data-testid="stButton"] > button:not([disabled]):hover {
    background-color: #00897b !important;
    border-color: #00897b !important;
    color: #ffffff !important;
}

/* ── Download buttons ── */
div[data-testid="stDownloadButton"] > button {
    border-radius: 6px !important;
    font-weight: 500 !important;
}
div[data-testid="stDownloadButton"] > button:hover {
    background-color: #00897b !important;
    border-color: #00897b !important;
    color: #ffffff !important;
}

/* ── File uploader compacto ── */
[data-testid="stFileUploader"] section {
    padding: 0.4rem 0.75rem !important;
    min-height: unset !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] { display: none !important; }

/* ── Cabeçalho de seção ── */
.section-header {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #888;
    margin-bottom: 0.4rem;
    margin-top: 0rem;
}
</style>
""", unsafe_allow_html=True)

# ── Sessão ──
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
    st.session_state["usuario"] = None
    st.session_state["perfil"] = None
    st.session_state["login"] = None


def verificar_login(usuario_input, senha_input):
    try:
        resp = supabase.table("usuarios").select("*").eq("login", usuario_input).execute()
        dados = resp.data
        if dados and dados[0]["senha"] == senha_input:
            st.session_state["autenticado"] = True
            st.session_state["usuario"] = dados[0]["nome"]
            st.session_state["perfil"] = dados[0]["perfil"]
            st.session_state["login"] = dados[0]["login"]
            return True
        return False
    except Exception as e:
        print(f"Erro ao conectar: {e}")
        return False


# ── Login ──
if not st.session_state["autenticado"]:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        try:
            st.image("assets/logo_marina.png", width=160)
        except Exception:
            st.markdown("### ⚓ Marina Barra Clube")
        st.markdown("#### Sistema de Achados e Perdidos")
        st.markdown("---")
        with st.form("form_login"):
            usuario_form = st.text_input("Usuário", autocomplete="username")
            senha_form = st.text_input("Senha", type="password", autocomplete="current-password")
            if st.form_submit_button("Entrar", use_container_width=True):
                if verificar_login(usuario_form, senha_form):
                    st.rerun()
                else:
                    st.error("Usuário ou senha inválidos.")

# ── App principal ──
else:
    with st.sidebar:
        try:
            st.image("assets/logo_marina.png", width=140)
        except Exception:
            st.markdown("**⚓ Marina Barra Clube**")

        st.markdown("---")
        st.markdown(
            f"<p style='font-size:0.85rem;margin:0'>Olá, <strong>{st.session_state['usuario']}</strong></p>"
            f"<p style='font-size:0.75rem;opacity:0.6;margin:0'>{st.session_state['perfil']}</p>",
            unsafe_allow_html=True,
        )
        st.markdown("---")

        opcoes_menu = {
            "🔍  Buscar":         "Buscar",
            "📦  Registrar Item": "Registrar Item",
            "📊  Dashboard":      "Dashboard",
        }
        if st.session_state["perfil"] == "Admin":
            opcoes_menu["⚙️  Configurações"] = "Configurações"

        menu_label = st.radio(
            "nav",
            options=list(opcoes_menu.keys()),
            label_visibility="collapsed",
        )
        menu = opcoes_menu[menu_label]

        st.markdown("---")
        if st.button("Sair", use_container_width=True):
            for k in ["autenticado", "usuario", "perfil", "login"]:
                st.session_state[k] = None
            st.session_state["autenticado"] = False
            st.rerun()

    if menu == "Buscar":
        tela_busca.mostrar_tela()
    elif menu == "Registrar Item":
        tela_cadastro.mostrar_tela()
    elif menu == "Dashboard":
        st.title("📊 Dashboard")
        st.info("Módulo de indicadores em desenvolvimento.")
    elif menu == "Configurações":
        st.title("⚙️ Configurações")
        st.info("Módulo de administração de usuários em desenvolvimento.")