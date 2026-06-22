import streamlit as st
from infra.banco_dados import supabase


PERFIS_DISPONIVEIS = ["Consulta", "Edicao", "Admin"]
PERFIS_EXIBICAO = {"Consulta": "Consulta", "Edicao": "Edição", "Admin": "Admin"}
SENHA_PADRAO = "123456"


def _carregar_usuarios() -> list[dict]:
    try:
        resp = (
            supabase.table("usuarios")
            .select("id, login, nome, perfil, senha_temporaria")
            .order("nome")
            .execute()
        )
        return resp.data or []
    except Exception as e:
        st.error(f"Erro ao carregar usuários: {e}")
        return []


@st.dialog("Novo Usuário")
def _dialog_novo_usuario():
    nome = st.text_input("Nome completo", key="nu_nome")
    login = st.text_input("Login (usado para acessar o sistema)", key="nu_login")
    perfil = st.selectbox(
        "Perfil",
        options=PERFIS_DISPONIVEIS,
        format_func=lambda p: PERFIS_EXIBICAO.get(p, p),
        key="nu_perfil",
    )

    st.caption(f"A senha inicial será **{SENHA_PADRAO}** — o usuário deverá trocá-la no primeiro acesso.")

    if st.button("Criar usuário", use_container_width=True, key="nu_salvar"):
        if not nome or not login:
            st.toast("Preencha nome e login.", icon="⚠️")
            return

        try:
            existente = supabase.table("usuarios").select("id").eq("login", login).execute()
            if existente.data:
                st.toast("Já existe um usuário com esse login.", icon="❌")
                return

            supabase.table("usuarios").insert({
                "nome": nome.upper(),
                "login": login.lower().strip(),
                "senha": SENHA_PADRAO,
                "perfil": perfil,
                "senha_temporaria": True,
            }).execute()

            st.toast(f"Usuário {nome} criado com sucesso!", icon="✅")
            st.rerun()
        except Exception as e:
            st.toast(f"Erro ao criar usuário: {e}", icon="❌")


@st.dialog("Editar Perfil do Usuário", width="small")
def _dialog_editar_perfil(usuario_id: int, nome: str, login_alvo: str, perfil_atual: str, usuario_logado: str):
    st.markdown(f"**Usuário:** {nome} ({login_alvo})")

    novo_perfil = st.selectbox(
        "Novo perfil",
        options=PERFIS_DISPONIVEIS,
        index=PERFIS_DISPONIVEIS.index(perfil_atual) if perfil_atual in PERFIS_DISPONIVEIS else 0,
        format_func=lambda p: PERFIS_EXIBICAO.get(p, p),
        key=f"ep_perfil_{usuario_id}",
    )

    senha_admin = st.text_input(
        "Confirme sua senha de Admin para salvar",
        type="password",
        key=f"ep_senha_{usuario_id}",
    )

    col_s, col_c = st.columns(2)
    with col_s:
        salvar = st.button("Salvar", use_container_width=True, key=f"ep_salvar_{usuario_id}")
    with col_c:
        if st.button("Cancelar", use_container_width=True, key=f"ep_cancelar_{usuario_id}"):
            st.rerun()

    if salvar:
        if novo_perfil == perfil_atual:
            st.toast("Nenhuma alteração detectada.", icon="ℹ️")
            return
        if not senha_admin:
            st.toast("Digite sua senha para confirmar.", icon="⚠️")
            return

        try:
            resp = supabase.table("usuarios").select("senha").eq("login", usuario_logado).execute()
            if not resp.data or resp.data[0]["senha"] != senha_admin:
                st.toast("Senha incorreta.", icon="❌")
                return

            supabase.table("usuarios").update({"perfil": novo_perfil}).eq("id", usuario_id).execute()
            st.toast(f"Perfil de {nome} atualizado para {novo_perfil}.", icon="✅")
            st.rerun()
        except Exception as e:
            st.toast(f"Erro ao atualizar perfil: {e}", icon="❌")


@st.dialog("Excluir Usuário", width="small")
def _dialog_excluir_usuario(usuario_id: int, nome: str, login_alvo: str, usuario_logado: str):
    st.warning(f"Tem certeza que deseja excluir o usuário **{nome}** ({login_alvo})?")
    st.caption("Esta ação não pode ser desfeita.")

    senha_admin = st.text_input(
        "Confirme sua senha de Admin para excluir",
        type="password",
        key=f"exc_senha_{usuario_id}",
    )

    col_s, col_c = st.columns(2)
    with col_s:
        confirmar = st.button("Excluir definitivamente", use_container_width=True, key=f"exc_confirmar_{usuario_id}")
    with col_c:
        if st.button("Cancelar", use_container_width=True, key=f"exc_cancelar_{usuario_id}"):
            st.rerun()

    if confirmar:
        if login_alvo == usuario_logado:
            st.toast("Você não pode excluir o próprio usuário.", icon="⚠️")
            return
        if not senha_admin:
            st.toast("Digite sua senha para confirmar.", icon="⚠️")
            return

        try:
            resp = supabase.table("usuarios").select("senha").eq("login", usuario_logado).execute()
            if not resp.data or resp.data[0]["senha"] != senha_admin:
                st.toast("Senha incorreta.", icon="❌")
                return

            supabase.table("usuarios").delete().eq("id", usuario_id).execute()
            st.toast(f"Usuário {nome} excluído.", icon="✅")
            st.rerun()
        except Exception as e:
            st.toast(f"Erro ao excluir usuário: {e}", icon="❌")


def mostrar_tela():
    st.title("Configurações — Gestão de Usuários")

    usuario_logado = st.session_state.get("login", "")

    if st.button("Novo Usuário", key="btn_novo_usuario"):
        _dialog_novo_usuario()

    st.markdown("---")

    usuarios = _carregar_usuarios()

    if not usuarios:
        st.info("Nenhum usuário cadastrado.")
        return

    st.caption(f"{len(usuarios)} usuário(s) cadastrado(s)")

    COLS = [2, 2, 1.5, 0.8, 0.8]
    h = st.columns(COLS)
    for col_h, label in zip(h, ["Nome", "Login", "Perfil", "Editar", "Excluir"]):
        col_h.markdown(f"**{label}**")
    st.divider()

    for u in usuarios:
        c = st.columns(COLS)
        with c[0]:
            st.write(u["nome"])
        with c[1]:
            st.write(u["login"])
        with c[2]:
            st.write(PERFIS_EXIBICAO.get(u["perfil"], u["perfil"]))
        with c[3]:
            eh_proprio_usuario = u["login"] == usuario_logado
            if st.button(
                "✏️",
                key=f"btn_editar_{u['id']}",
                disabled=eh_proprio_usuario,
                help="Você não pode editar o próprio perfil" if eh_proprio_usuario else "Editar perfil",
            ):
                _dialog_editar_perfil(u["id"], u["nome"], u["login"], u["perfil"], usuario_logado)
        with c[4]:
            if st.button(
                "🗑️",
                key=f"btn_excluir_{u['id']}",
                disabled=eh_proprio_usuario,
                help="Você não pode excluir o próprio usuário" if eh_proprio_usuario else "Excluir usuário",
            ):
                _dialog_excluir_usuario(u["id"], u["nome"], u["login"], usuario_logado)