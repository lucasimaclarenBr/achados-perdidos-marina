import re
import streamlit as st
from infra.banco_dados import supabase
from datetime import datetime, timedelta


# =============================================================================
# CONFIGURAÇÃO DE CATEGORIAS
# =============================================================================
CATEGORIAS = {
    "Acessórios":         {"sigla": "AC",  "capacidade": 100},
    "Bolas":              {"sigla": "B",   "capacidade": 100},
    "Bolsas":             {"sigla": "BOL", "capacidade": 100},
    "Brinquedos":         {"sigla": "BR",  "capacidade": 50},
    "Calçados":           {"sigla": "C",   "capacidade": 150},
    "Cosméticos":         {"sigla": "CO",  "capacidade": 50},
    "Garrafas":           {"sigla": "G",   "capacidade": 150},
    "Material Esportivo": {"sigla": "ME",  "capacidade": 100},
    "Objetos":            {"sigla": "OB",  "capacidade": 50},
    "Óculos":             {"sigla": "OC",  "capacidade": 50},
    "Roupas":             {"sigla": "R",   "capacidade": 300},
    "Toalhas":            {"sigla": "T",   "capacidade": 100},
}


# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def _formatar_telefone(valor: str) -> str:
    digitos = re.sub(r"\D", "", valor)
    d = digitos[:11]
    if len(digitos) <= 2:
        return digitos
    if len(digitos) <= 7:
        return f"({d[:2]}) {d[2:]}"
    formatted = f"({d[:2]}) {d[2:7]}-{d[7:11]}"
    # Mantém dígitos excedentes visíveis para o usuário poder apagá-los
    if len(digitos) > 11:
        formatted += digitos[11:]
    return formatted


def _validar_telefone(telefone: str) -> bool:
    return len(re.sub(r"\D", "", telefone)) == 11


def _formatar_titulo(valor: str) -> str:
    digitos = re.sub(r"\D", "", valor)
    if len(digitos) <= 4:
        return digitos
    formatted = f"{digitos[:4]}-{digitos[4:6]}"
    if len(digitos) > 6:
        formatted += digitos[6:]  # excesso visível para o usuário apagar
    return formatted


def _validar_titulo(titulo: str) -> bool:
    return bool(re.fullmatch(r"\d{4}-\d{2}", titulo))


def _gerar_todos_codigos(sigla: str, capacidade: int) -> list[str]:
    return [f"{str(i).zfill(4)} {sigla}" for i in range(1, capacidade + 1)]


@st.cache_data(ttl=30)
def _buscar_codigos_ocupados(sigla: str) -> set[str]:
    try:
        resposta = (
            supabase.table("itens")
            .select("codigo_item")
            .neq("status_atual", "Devolvidos")
            .like("codigo_item", f"%{sigla}")
            .execute()
        )
        return {row["codigo_item"] for row in resposta.data}
    except Exception as e:
        st.warning(f"Não foi possível consultar vagas ocupadas: {e}")
        return set()


def _buscar_codigos_livres(categoria_nome: str) -> list[str]:
    config = CATEGORIAS[categoria_nome]
    todos = _gerar_todos_codigos(config["sigla"], config["capacidade"])
    ocupados = _buscar_codigos_ocupados(config["sigla"])
    return [c for c in todos if c not in ocupados]


def _upload_foto(foto, codigo_item: str) -> str | None:
    try:
        extensao = foto.name.split(".")[-1]
        caminho = f"itens/{codigo_item}.{extensao}"
        supabase.storage.from_("fotos-itens").upload(
            caminho,
            foto.read(),
            {"content-type": foto.type, "upsert": "true"},
        )
        return supabase.storage.from_("fotos-itens").get_public_url(caminho)
    except Exception as e:
        st.warning(f"Foto não salva (item registrado sem imagem): {e}")
        return None


def _campo_telefone(label: str, key: str) -> str:
    def _ao_alterar():
        st.session_state[key] = _formatar_telefone(st.session_state[key])

    valor = st.text_input(
        label,
        key=key,
        on_change=_ao_alterar,
        placeholder="(21) 99999-9999",
    )
    if valor:
        digitos = len(re.sub(r"\D", "", valor))
        if digitos > 11:
            st.caption(
                f"⚠️ Número muito longo ({digitos} dígitos). "
                "Use o padrão (21) 99999-9999."
            )
        elif digitos < 11:
            st.caption(
                f"⚠️ Número incompleto ({digitos} dígitos). "
                "Use o padrão (21) 99999-9999."
            )
    return valor


def _campo_descricao(label: str, key: str) -> str:
    def _ao_alterar():
        st.session_state[key] = st.session_state[key].upper()

    return st.text_input(label, key=key, on_change=_ao_alterar)


def _campo_titulo(label: str, key: str) -> str:
    def _ao_alterar():
        st.session_state[key] = _formatar_titulo(st.session_state[key])

    valor = st.text_input(
        label,
        key=key,
        on_change=_ao_alterar,
        placeholder="1234-10",
    )
    if valor:
        digitos = len(re.sub(r"\D", "", valor))
        if not _validar_titulo(valor):
            if digitos > 6:
                st.caption(f"⚠️ Título muito longo ({digitos} dígitos). Use o padrão 1234-10.")
            else:
                st.caption(f"⚠️ Título incompleto ({digitos} dígitos). Use o padrão 1234-10.")
    return valor


# =============================================================================
# TELA PRINCIPAL
# =============================================================================

def mostrar_tela():
    st.title("Gestão de Achados e Perdidos")

    aba_item, aba_dono = st.tabs(
        ["📦 Registrar Item Encontrado", "🔎 Registrar Busca Ativa (Dono)"]
    )

    # Contadores de versão: incrementar no sucesso força reset completo do formulário
    v_item = st.session_state.get("_v_item", 0)
    v_busca = st.session_state.get("_v_busca", 0)

    # =========================================================================
    # ABA 1: REGISTRAR ITEM ENCONTRADO
    # =========================================================================
    with aba_item:
        # Toast de sucesso exibido APÓS o rerun (evita ser apagado imediatamente)
        if "_msg_item" in st.session_state:
            st.toast(st.session_state.pop("_msg_item"), icon="✅")

        col_cat, col_cod = st.columns(2)

        with col_cat:
            opcoes_categoria = ["Selecione uma categoria..."] + list(CATEGORIAS.keys())
            categoria_selecionada = st.selectbox(
                "Categoria *",
                options=opcoes_categoria,
                index=0,
                key=f"cat_item_{v_item}",
            )

        categoria_valida = categoria_selecionada != "Selecione uma categoria..."

        with col_cod:
            if not categoria_valida:
                st.selectbox(
                    "Código do Item *",
                    options=["Selecione a categoria primeiro..."],
                    disabled=True,
                    key=f"cod_placeholder_{v_item}",
                )
                codigo_selecionado = None
            else:
                codigos_livres = _buscar_codigos_livres(categoria_selecionada)
                vagas_restantes = len(codigos_livres)
                if codigos_livres:
                    opcoes_codigo = ["Selecione um código..."] + codigos_livres
                    codigo_escolhido = st.selectbox(
                        f"Código do Item * ({vagas_restantes} vagas livres)",
                        options=opcoes_codigo,
                        index=0,
                        key=f"cod_item_{v_item}",
                    )
                    codigo_selecionado = (
                        None if codigo_escolhido == "Selecione um código..."
                        else codigo_escolhido
                    )
                else:
                    st.error(f"Sem vagas em '{categoria_selecionada}'. Devolva itens antes de cadastrar novos.")
                    codigo_selecionado = None

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<p class="section-header">Dados do Item</p>', unsafe_allow_html=True)
            descricao_input = _campo_descricao("Descrição detalhada *", key=f"desc_item_{v_item}")
            local_input = _campo_descricao("Local onde foi achado", key=f"local_item_{v_item}")
            foto_input = st.file_uploader(
                "Foto do item", type=["png", "jpg", "jpeg"], key=f"foto_item_{v_item}"
            )
            caixa_azul_input = st.checkbox(
                "📦 Item está na Caixa Azul",
                key=f"caixa_azul_item_{v_item}",
            )

        with col2:
            st.markdown('<p class="section-header">Dados do Sócio (Opcional)</p>', unsafe_allow_html=True)
            nome_socio = _campo_descricao("Nome no item", key=f"nome_socio_item_{v_item}")
            titulo_socio = _campo_titulo("Número do Título", key=f"titulo_socio_item_{v_item}")
            telefone_socio = _campo_telefone("Telefone de Contato", key=f"tel_socio_item_{v_item}")

            socio_identificado = bool(nome_socio or titulo_socio or telefone_socio)
            contatado_input = None
            if socio_identificado:
                contatado_input = st.radio(
                    "Sócio já foi contatado? *",
                    options=["Sim", "Não"],
                    index=None,
                    horizontal=True,
                    key=f"contatado_item_{v_item}",
                )

        st.write("")
        if st.button("Salvar Registro de Item", use_container_width=True, key=f"btn_salvar_item_{v_item}"):
            erros = []
            if not categoria_valida:
                erros.append("Selecione uma categoria.")
            if not codigo_selecionado:
                erros.append("Selecione um código de item.")
            if not descricao_input:
                erros.append("Preencha a descrição do item.")
            if titulo_socio and not _validar_titulo(titulo_socio):
                erros.append("Título inválido. Use o formato 1234-10.")
            if telefone_socio and not _validar_telefone(telefone_socio):
                erros.append("Telefone inválido. Use o padrão (21) 99999-9999.")
            if socio_identificado and contatado_input is None:
                erros.append("Informe se o sócio já foi contatado.")

            if erros:
                for erro in erros:
                    st.toast(erro, icon="⚠️")
            else:
                url_foto = _upload_foto(foto_input, codigo_selecionado) if foto_input else None
                dados_novo_item = {
                    "codigo_item": codigo_selecionado,
                    "categoria": categoria_selecionada,
                    "descricao": descricao_input,
                    "local_achado": local_input,
                    "caixa_azul": caixa_azul_input,
                    "nome_socio_identificado": nome_socio,
                    "titulo_socio": titulo_socio,
                    "telefone_socio": telefone_socio,
                    "contatado": contatado_input == "Sim",
                    "status_atual": "Armazenado",
                    "foto_url": url_foto,
                }
                try:
                    supabase.table("itens").insert(dados_novo_item).execute()
                    _buscar_codigos_ocupados.clear()
                    st.session_state["_msg_item"] = f"Item {codigo_selecionado} registrado com sucesso!"
                    st.session_state["_v_item"] = v_item + 1
                    st.rerun()
                except Exception as e:
                    st.toast("Erro ao salvar. Verifique os dados e tente novamente.", icon="❌")
                    print(f"Erro na inserção: {e}")

    # =========================================================================
    # ABA 2: REGISTRAR BUSCA ATIVA
    # =========================================================================
    with aba_dono:
        if "_msg_busca" in st.session_state:
            st.toast(st.session_state.pop("_msg_busca"), icon="✅")

        st.write("Abra um ticket para um sócio que está procurando um item perdido.")

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown('<p class="section-header">Dados do Sócio</p>', unsafe_allow_html=True)
            nome_busca = _campo_descricao("Nome do Sócio *", key=f"nome_busca_{v_busca}")
            titulo_busca = _campo_titulo("Número do Título *", key=f"titulo_busca_{v_busca}")
            telefone_busca = _campo_telefone("Telefone *", key=f"tel_busca_{v_busca}")

        with col_b:
            st.markdown('<p class="section-header">Dados do Item Perdido</p>', unsafe_allow_html=True)
            opcoes_cat_busca = ["Selecione uma categoria..."] + list(CATEGORIAS.keys())
            categoria_busca = st.selectbox(
                "Categoria *",
                options=opcoes_cat_busca,
                index=0,
                key=f"cat_busca_{v_busca}",
            )
            descricao_busca = _campo_descricao(
                "Descrição do que foi perdido *", key=f"desc_busca_{v_busca}"
            )
            data_sla = (datetime.now() + timedelta(days=10)).strftime("%d/%m/%Y")
            st.text_input(
                "Data Limite de Retorno (SLA 10 dias)",
                value=data_sla,
                disabled=True,
            )

        st.write("")
        if st.button("Abrir Ticket de Busca", use_container_width=True, key=f"btn_salvar_busca_{v_busca}"):
            erros_busca = []
            if not nome_busca:
                erros_busca.append("Preencha o nome do sócio.")
            if not titulo_busca:
                erros_busca.append("Preencha o número do título.")
            elif not _validar_titulo(titulo_busca):
                erros_busca.append("Título inválido. Use o formato 1234-10.")
            if not telefone_busca:
                erros_busca.append("Preencha o telefone.")
            elif not _validar_telefone(telefone_busca):
                erros_busca.append("Telefone inválido. Use o padrão (21) 99999-9999 — 11 dígitos.")
            if categoria_busca == "Selecione uma categoria...":
                erros_busca.append("Selecione uma categoria.")
            if not descricao_busca:
                erros_busca.append("Preencha a descrição do item perdido.")

            if erros_busca:
                for erro in erros_busca:
                    st.toast(erro, icon="⚠️")
            else:
                dados_busca = {
                    "nome_socio": nome_busca,
                    "titulo_socio": titulo_busca,
                    "telefone": telefone_busca,
                    "categoria": categoria_busca,
                    "descricao_perdido": descricao_busca,
                    "data_limite_retorno": (
                        datetime.now() + timedelta(days=10)
                    ).strftime("%Y-%m-%d"),
                    "status_busca": "Aberto",
                }
                try:
                    supabase.table("busca_ativa").insert(dados_busca).execute()
                    st.session_state["_msg_busca"] = "Ticket de busca ativa aberto com sucesso!"
                    st.session_state["_v_busca"] = v_busca + 1
                    st.rerun()
                except Exception as e:
                    st.toast("Erro ao abrir o ticket.", icon="❌")
                    print(f"Erro na inserção da busca: {e}")
