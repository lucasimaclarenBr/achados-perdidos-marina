import streamlit as st
from infra.banco_dados import supabase
from datetime import datetime, timedelta

def mostrar_tela():
    st.title("Gestão de Achados e Perdidos")
    
    # Criando as Abas para separar as funções
    aba_item, aba_dono = st.tabs(["📦 Registrar Item Encontrado", "🔎 Registrar Busca Ativa (Dono)"])
    
    # ==========================================
    # ABA 1: REGISTRAR ITEM ENCONTRADO
    # ==========================================
    with aba_item:
        st.write("Preencha os dados abaixo para dar entrada num item encontrado.")
        
        with st.form("form_novo_item", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                categoria_input = st.selectbox("Categoria *", ["Roupas", "Eletrônicos", "Documentos", "Acessórios", "Cartões", "Outros"])
                
                # Mantido como texto livre até aplicarmos a regra de vagas
                codigo_input = st.text_input("Código do Item (Ex: 0042R, 0092AC) *")
                
                descricao_input = st.text_input("Descrição detalhada do item *")
                local_input = st.text_input("Local onde foi achado")
                
                st.caption("Upload de Imagem")
                foto_input = st.file_uploader("Anexar foto do item", type=['png', 'jpg', 'jpeg'])
                
            with col2:
                st.caption("Identificação do Sócio (Opcional)")
                nome_socio_input = st.text_input("Nome no item/documento")
                titulo_socio_input = st.text_input("Número do Título")
                telefone_socio_input = st.text_input("Telefone de Contato")
                
                # Lógica Condicional: Só mostra o rádio se algum campo do sócio tiver texto
                socio_identificado = bool(nome_socio_input or titulo_socio_input or telefone_socio_input)
                contatado_input = "Não" # Variável invisível padrão
                
                if socio_identificado:
                    contatado_input = st.radio("Sócio já foi contatado?", ["Não", "Sim"], horizontal=True)
            
                # Espaçamento para empurrar o botão para baixo, alinhando com o upload de foto
                st.write("") 
                st.write("")
                st.write("")
                st.markdown("*Campos obrigatórios*")
                botao_salvar = st.form_submit_button("Salvar Registro de Item")
            
            if botao_salvar:
                if not codigo_input or not descricao_input:
                    # Substituição para Toast
                    st.toast("Preencha o Código do Item e a Descrição.", icon="⚠️")
                else:
                    foi_contatado = True if contatado_input == "Sim" else False
                    
                    dados_novo_item = {
                        "codigo_item": codigo_input,
                        "categoria": categoria_input,
                        "descricao": descricao_input,
                        "local_achado": local_input,
                        "nome_socio_identificado": nome_socio_input,
                        "titulo_socio": titulo_socio_input,
                        "telefone_socio": telefone_socio_input,
                        "contatado": foi_contatado
                    }
                    try:
                        supabase.table("itens").insert(dados_novo_item).execute()
                        st.toast(f"Item {codigo_input} registrado com sucesso!", icon="✅")
                    except Exception as e:
                        st.toast("Erro ao salvar. Verifique se o código já existe no sistema.", icon="❌")
                        print(f"Erro na inserção: {e}")

    # ==========================================
    # ABA 2: REGISTRAR BUSCA ATIVA (DONO PROCURANDO)
    # ==========================================
    with aba_dono:
        st.write("Abra um ticket para um sócio que está procurando um item perdido.")
        
        with st.form("form_busca_ativa", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            
            with col_a:
                nome_busca = st.text_input("Nome do Sócio *")
                titulo_busca = st.text_input("Número do Título *")
                telefone_busca = st.text_input("Telefone *")
                
            with col_b:
                categoria_busca = st.selectbox("Categoria do Item *", ["Roupas", "Eletrônicos", "Documentos", "Acessórios", "Cartões", "Outros"])
                
                # Cálculo automático do SLA (Hoje + 10 dias) com bloqueio visual
                data_sla = (datetime.now() + timedelta(days=10)).strftime("%d/%m/%Y")
                st.text_input("Data Limite de Retorno (SLA 10 dias)", value=data_sla, disabled=True)
                
            descricao_busca = st.text_area("Descrição detalhada do que foi perdido *")
            
            botao_salvar_busca = st.form_submit_button("Abrir Ticket de Busca")
            
            if botao_salvar_busca:
                if not nome_busca or not telefone_busca or not descricao_busca:
                    st.toast("Preencha os campos obrigatórios (Nome, Telefone e Descrição).", icon="⚠️")
                else:
                    dados_busca = {
                        "nome_socio": nome_busca,
                        "titulo_socio": titulo_busca,
                        "telefone": telefone_busca,
                        "categoria": categoria_busca,
                        "descricao_perdido": descricao_busca,
                        # Salvando no banco no formato padrão do banco de dados YYYY-MM-DD
                        "data_limite_retorno": (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
                    }
                    try:
                        supabase.table("busca_ativa").insert(dados_busca).execute()
                        st.toast("Ticket de busca ativa aberto com sucesso!", icon="✅")
                    except Exception as e:
                        st.toast("Erro ao abrir o ticket.", icon="❌")
                        print(f"Erro na inserção da busca: {e}")