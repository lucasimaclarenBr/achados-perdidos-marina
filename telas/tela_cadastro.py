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
    digitos = re.sub(r"\D", "", valor)[:11]
    if len(digitos) <= 2:
        return digitos
    if len(digitos) <= 7:
        return f"({digitos[:2]}) {digitos[2:]}"
    return f"({digitos[:2]}) {digitos[2:7]}-{digitos[7:]}"


def _validar_telefone(telefone: str) -> bool:
    return len(re.sub(r"\D", "", telefone)) == 11


def _gerar_todos_codigos(sigla: str, capacidade: int) -> list[str]:
    return [f"{str(i).zfill(3)}{sigla}" for i in range(1, capacidade + 1)]


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
        if not _validar_telefone(valor):
            digitos = len(re.sub(r"\D", "", valor))
            st.caption(f"⚠️ Número inválido ({digitos} dígitos). Use DDD + 9 dígitos.")
    return valor


def _limpar_estado(chaves: list[str]) -> None:
    for chave in chaves:
        st.session_state.pop(chave, None)


# =============================================================================
# TELA PRINCIPAL
# =============================================================================

def mostrar_tela():
    st.title("Gestão de Achados e Perdidos")

    aba_item, aba_dono = st.tabs(
        ["📦 Registrar Item Encontrado", "🔎 Registrar Busca Ativa (Dono)"]
    )

    # =========================================================================
    # ABA 1: REGISTRAR ITEM ENCONTRADO
    # =========================================================================
    with aba_item:

        col_cat, col_cod = st.columns(2)

        with col_cat:
            opcoes_categoria = ["Selecione uma categoria..."] + list(CATEGORIAS.keys())
            categoria_selecionada = st.selectbox(
                "Categoria *",
                options=opcoes_categoria,
                index=0,
                key="cat_item",
            )

        categoria_valida = categoria_selecionada != "Selecione uma categoria..."

        with col_cod:
            if not categoria_valida:
                st.selectbox(
                    "Código do Item *",
                    options=["Selecione a categoria primeiro..."],
                    disabled=True,
                    key="cod_placeholder",
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
                        key="cod_item",
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
            descricao_input = st.text_input("Descrição detalhada *", key="desc_item")
            local_input = st.text_input("Local onde foi achado", key="local_item")
            foto_input = st.file_uploader(
                "Foto do item", type=["png", "jpg", "jpeg"], key="foto_item"
            )
            caixa_azul_input = st.checkbox(
                "📦 Item está na Caixa Azul",
                key="caixa_azul_item",
                help="Marque se o item estiver fisicamente na Caixa Azul.",
            )

        with col2:
            st.markdown('<p class="section-header">Dados do Sócio (Opcional)</p>', unsafe_allow_html=True)
            nome_socio = st.text_input("Nome no item/documento", key="nome_socio_item")
            titulo_socio = st.text_input("Número do Título", key="titulo_socio_item")
            telefone_socio = _campo_telefone("Telefone de Contato", key="tel_socio_item")

            socio_identificado = bool(nome_socio or titulo_socio or telefone_socio)
            contatado_input = None
            if socio_identificado:
                contatado_input = st.radio(
                    "Sócio já foi contatado? *",
                    options=["Sim", "Não"],
                    index=None,
                    horizontal=True,
                    key="contatado_item",
                )

        st.write("")
        if st.button("Salvar Registro de Item", use_container_width=True, key="btn_salvar_item"):
            erros = []
            if not categoria_valida:
                erros.append("Selecione uma categoria.")
            if not codigo_selecionado:
                erros.append("Selecione um código de item.")
            if not descricao_input:
                erros.append("Preencha a descrição do item.")
            if telefone_socio and not _validar_telefone(telefone_socio):
                erros.append("Telefone inválido. Digite DDD + 9 dígitos.")
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
                    "status_atual": "Ativo AeP",
                    "foto_url": url_foto,
                }
                try:
                    supabase.table("itens").insert(dados_novo_item).execute()
                    _buscar_codigos_ocupados.clear()
                    _limpar_estado([
                        "cat_item", "cod_item", "cod_placeholder",
                        "desc_item", "local_item", "foto_item", "caixa_azul_item",
                        "nome_socio_item", "titulo_socio_item",
                        "tel_socio_item", "contatado_item",
                    ])
                    st.toast(f"Item {codigo_selecionado} registrado com sucesso!", icon="✅")
                    st.rerun()
                except Exception as e:
                    st.toast("Erro ao salvar. Verifique os dados e tente novamente.", icon="❌")
                    print(f"Erro na inserção: {e}")

    # =========================================================================
    # ABA 2: REGISTRAR BUSCA ATIVA
    # =========================================================================
    with aba_dono:
        st.write("Abra um ticket para um sócio que está procurando um item perdido.")

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown('<p class="section-header">Dados do Sócio</p>', unsafe_allow_html=True)
            nome_busca = st.text_input("Nome do Sócio *", key="nome_busca")
            titulo_busca = st.text_input("Número do Título *", key="titulo_busca")
            telefone_busca = _campo_telefone("Telefone *", key="tel_busca")

        with col_b:
            st.markdown('<p class="section-header">Dados do Item Perdido</p>', unsafe_allow_html=True)
            opcoes_cat_busca = ["Selecione uma categoria..."] + list(CATEGORIAS.keys())
            categoria_busca = st.selectbox(
                "Categoria *",
                options=opcoes_cat_busca,
                index=0,
                key="cat_busca",
            )
            descricao_busca = st.text_input(
                "Descrição do que foi perdido *", key="desc_busca"
            )
            data_sla = (datetime.now() + timedelta(days=10)).strftime("%d/%m/%Y")
            st.text_input(
                "Data Limite de Retorno (SLA 10 dias)",
                value=data_sla,
                disabled=True,
            )

        st.write("")
        if st.button("Abrir Ticket de Busca", use_container_width=True, key="btn_salvar_busca"):
            erros_busca = []
            if not nome_busca:
                erros_busca.append("Preencha o nome do sócio.")
            if not titulo_busca:
                erros_busca.append("Preencha o número do título.")
            if not telefone_busca:
                erros_busca.append("Preencha o telefone.")
            elif not _validar_telefone(telefone_busca):
                erros_busca.append("Telefone inválido. Digite DDD + 9 dígitos.")
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
                    _limpar_estado([
                        "nome_busca", "titulo_busca", "tel_busca",
                        "cat_busca", "desc_busca",
                    ])
                    st.toast("Ticket de busca ativa aberto com sucesso!", icon="✅")
                    st.rerun()
                except Exception as e:
                    st.toast("Erro ao abrir o ticket.", icon="❌")
                    print(f"Erro na inserção da busca: {e}")