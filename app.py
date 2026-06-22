import streamlit as st
from infra.banco_dados import supabase
from telas import tela_busca_ativa, tela_cadastro, tela_busca

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
    padding-bottom: 2rem !important;
}
[data-testid="InputInstructions"] { display: none; }
section[data-testid="stSidebarUserContent"] {
    padding-top: 0.5rem !important;
}
div[data-testid="stSidebarHeader"] {
    padding-top: 1rem !important;
    height: auto !important;
}
section[data-testid="stSidebar"] [data-testid="stImage"] {
    width: 100% !important;
    display: flex !important;
    justify-content: center !important;
}
section[data-testid="stSidebar"] [data-testid="stImageContainer"] {
    display: flex !important;
    justify-content: center !important;
    width: 100% !important;
}
section[data-testid="stSidebar"] img {
    margin-left: auto !important;
    margin-right: auto !important;
    display: block !important;
}
section[data-testid="stSidebar"] [data-testid="stFullScreenFrame"] {
    display: flex !important;
    justify-content: center !important;
    width: 100% !important;
}
hr {
    margin-top: 0.5rem !important;
    margin-bottom: 0.5rem !important;
}

/* ── Menu de navegação estilo link (sem radio button) ── */
section[data-testid="stSidebar"] div[data-testid="stRadio"] > label {
    display: none !important;
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] > div {
    gap: 0.25rem;
}
section[data-testid="stSidebar"] div[data-testid="stRadio"] > div > label {
    display: block;
    padding: 0.5rem 0.5rem;
    border-radius: 6px;
    transition: all 0.15s ease;
    cursor: pointer;
}
/* Esconde o círculo do radio */
section[data-testid="stSidebar"] div[data-testid="stRadio"] > div > label > div:first-child {
    display: none !important;
}
/* Texto do menu */
section[data-testid="stSidebar"] div[data-testid="stRadio"] > div > label p {
    font-size: 1.05rem !important;
    font-weight: 500 !important;
    color: #c8d3e8 !important;
}
/* Item selecionado: sublinhado e texto branco em negrito */
section[data-testid="stSidebar"] div[data-testid="stRadio"] > div > label:has(input:checked) p {
    color: #ffffff !important;
    font-weight: 700 !important;
    border-bottom: 2px solid #ffffff;
    padding-bottom: 0.3rem;
}
/* Hover: texto branco */
section[data-testid="stSidebar"] div[data-testid="stRadio"] > div > label:hover p {
    color: #ffffff !important;
}

/* ── Rodapé fixo da sidebar (Alterar senha + Sair) ── */
.sidebar-rodape-fixo {
    position: sticky;
    bottom: 0;
    padding-bottom: 1rem;
    background-color: #000c21;
}

/* ── Sidebar: azul marinho fixo em ambos os temas ── */
section[data-testid="stSidebar"] {
    background-color: #000c21 !important;
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
section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
    background-color: transparent !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    color: #c8d3e8 !important;
}
/* Hover padrão de todos os botões da sidebar: vermelho */
section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
    background-color: #cc0000 !important;
    border-color: #cc0000 !important;
    color: #ffffff !important;
}
/* Exceção: hover do "Alterar senha": cinza neutro (identificado pela key do botão) */
.st-key-btn_alterar_senha button:hover {
    background-color: rgba(255,255,255,0.15) !important;
    border-color: rgba(255,255,255,0.4) !important;
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

/* ── Oculta toolbar do Streamlit Cloud (temporariamente desativado) ── */

[data-testid="stToolbar"] {
    visibility: hidden !important;
}

[data-testid="stDecoration"] {
    visibility: hidden !important;
}
.viewerBadge_container__1QSob,
.styles_viewerBadge__1yB5_,
#MainMenu {
    display: none !important;
    visibility: hidden !important;
}
footer {
    visibility: hidden !important;
}
/* Garante que o botão de colapsar/expandir sidebar permaneça visível */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"] {
    visibility: visible !important;
    display: block !important;
}

/* ── Largura fixa da sidebar ── */
section[data-testid="stSidebar"] {
    min-width: 280px !important;
    max-width: 280px !important;
}

/* ── Remove recorte/arredondamento na logo da sidebar ── */
section[data-testid="stSidebar"] [data-testid="stImage"],
section[data-testid="stSidebar"] [data-testid="stImageContainer"],
section[data-testid="stSidebar"] [data-testid="stImage"] img {
    border-radius: 0 !important;
    overflow: visible !important;
    box-shadow: none !important;
}

/* ── Botão Descartar no dialog ── */
div[role="dialog"] div[data-testid="stColumn"]:last-child button[data-testid="stBaseButton-secondary"]:hover {
    background-color: #cc0000 !important;
    border-color: #cc0000 !important;
    color: #ffffff !important;
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
        img_esq, img_mid, img_dir = st.columns([1, 2, 1])
        with img_mid:
            st.markdown('<div style="padding-top: 2rem"></div>', unsafe_allow_html=True)
            try:
                st.image("assets/logo_marina.png", width=240)
            except Exception:
                st.markdown(
                    "<h3 style='text-align:center'>⚓ Marina Barra Clube</h3>",
                    unsafe_allow_html=True,
                )
            st.markdown(
                "<b>Sistema de Achados e Perdidos</b>",
                unsafe_allow_html=True
            )
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
        if "_msg_senha" in st.session_state:
            st.toast(st.session_state.pop("_msg_senha"), icon="✅")

        try:
            st.image("assets/logo_marina.png", width=150)
        except Exception:
            st.markdown("**⚓ Marina Barra Clube**")

        st.markdown("---")
        st.markdown(
            f"<p style='font-size:0.85rem;margin:0;text-align:center'>Olá, <strong>{st.session_state['usuario']}</strong></p>"
            f"<p style='font-size:0.75rem;opacity:0.6;margin:0 0 0.3rem 0;text-align:center'>{st.session_state['perfil']}</p>",
            unsafe_allow_html=True,
        )
        st.markdown("---")

        opcoes_menu = {
            "🔍︎  Pesquisa de Item": "Buscar",
            "🔍︎  Busca Ativa":      "Busca Ativa",
            "🞦  Registrar":        "Registrar Item",
            "🗠  Dashboard":        "Dashboard",
        }
        if st.session_state["perfil"] == "Admin":
            opcoes_menu["⛭  Configurações"] = "Configurações"

        menu_label = st.radio(
            "nav",
            options=list(opcoes_menu.keys()),
            label_visibility="collapsed",
        )
        menu = opcoes_menu[menu_label]

        st.markdown("---")
        st.markdown('<div class="sidebar-rodape-fixo">', unsafe_allow_html=True)
        col_senha, col_sair = st.columns(2)
        with col_senha:
            if st.button("Alterar senha", use_container_width=True, key="btn_alterar_senha"):
                st.session_state["mostrar_alterar_senha"] = True
        with col_sair:
            if st.button("Sair", use_container_width=True, key="btn_sair"):
                for k in ["autenticado", "usuario", "perfil", "login"]:
                    st.session_state[k] = None
                st.session_state["autenticado"] = False
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.get("mostrar_alterar_senha"):
        st.session_state["mostrar_alterar_senha"] = False

        @st.dialog("Alterar Senha")
        def _dialog_alterar_senha():
            senha_atual = st.text_input("Senha atual", type="password", key="ds_atual")
            nova_senha = st.text_input("Nova senha", type="password", key="ds_nova")
            confirmar_senha = st.text_input("Confirmar nova senha", type="password", key="ds_conf")

            col_s, col_c = st.columns(2)
            with col_s:
                if st.button("Salvar", use_container_width=True, key="ds_salvar"):
                    if not senha_atual or not nova_senha or not confirmar_senha:
                        st.toast("Preencha todos os campos.", icon="⚠️")
                    elif len(nova_senha) < 6:
                        st.toast("A nova senha precisa ter ao menos 6 caracteres.", icon="⚠️")
                    elif nova_senha != confirmar_senha:
                        st.toast("As senhas não coincidem.", icon="⚠️")
                    elif nova_senha == senha_atual:
                        st.toast("A nova senha deve ser diferente da senha atual.", icon="⚠️")
                    else:
                        try:
                            login = st.session_state["login"]
                            resp = supabase.table("usuarios").select("senha").eq("login", login).execute()
                            if not resp.data or resp.data[0]["senha"] != senha_atual:
                                st.toast("Senha atual incorreta.", icon="❌")
                            else:
                                supabase.table("usuarios").update({"senha": nova_senha}).eq("login", login).execute()
                                st.session_state["mostrar_alterar_senha"] = False
                                st.session_state["_msg_senha"] = "Senha alterada com sucesso!"
                                st.rerun()
                        except Exception as e:
                            st.toast(f"Erro ao alterar senha: {e}", icon="❌")
            with col_c:
                if st.button("Cancelar", use_container_width=True, key="ds_cancelar"):
                    st.session_state["mostrar_alterar_senha"] = False
                    st.rerun()

        _dialog_alterar_senha()

    if menu == "Buscar":
        tela_busca.mostrar_tela()
    elif menu == "Busca Ativa":
        tela_busca_ativa.mostrar_tela()
    elif menu == "Registrar Item":
        tela_cadastro.mostrar_tela()
    elif menu == "Dashboard":
        st.title("Dashboard")
        st.info("Módulo de indicadores em desenvolvimento.")
    elif menu == "Configurações":
        st.title("Configurações")
        st.info("Módulo de administração de usuários em desenvolvimento.")