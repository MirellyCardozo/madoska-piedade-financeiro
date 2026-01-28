import streamlit as st
from database import executar

def tela_estoque(user):
    st.title("📦 Controle de Estoque")

    # ======================
    # CADASTRO
    # ======================
    st.subheader("Cadastrar Produto")

    nome = st.text_input("Nome do produto")
    quantidade = st.number_input("Quantidade", min_value=0, step=1)
    preco = st.number_input("Preço", min_value=0.0, format="%.2f")

    if st.button("Salvar produto"):
        if nome:
            executar(
                """
                INSERT INTO estoque (nome, quantidade, preco)
                VALUES (:nome, :quantidade, :preco)
                """,
                {
                    "nome": nome,
                    "quantidade": quantidade,
                    "preco": preco
                }
            )
            st.success("Produto cadastrado com sucesso")
            st.rerun()
        else:
            st.warning("Informe o nome do produto")

    # ======================
    # LISTAGEM
    # ======================
    st.subheader("Estoque Atual")

    dados = executar(
        "SELECT id, nome, quantidade, preco FROM estoque ORDER BY nome",
        fetchall=True
    )

    if not dados:
        st.info("Nenhum produto cadastrado")
        return

    for item in dados:
        with st.expander(f"{item['nome']}"):
            col1, col2, col3 = st.columns(3)

            with col1:
                nova_qtd = st.number_input(
                    "Quantidade",
                    value=int(item["quantidade"]),
                    key=f"qtd_{item['id']}"
                )

            with col2:
                novo_preco = st.number_input(
                    "Preço",
                    value=float(item["preco"]),
                    format="%.2f",
                    key=f"preco_{item['id']}"
                )

            with col3:
                if st.button("💾 Atualizar", key=f"upd_{item['id']}"):
                    executar(
                        """
                        UPDATE estoque
                        SET quantidade=:qtd, preco=:preco
                        WHERE id=:id
                        """,
                        {
                            "qtd": nova_qtd,
                            "preco": novo_preco,
                            "id": item["id"]
                        }
                    )
                    st.success("Atualizado")
                    st.rerun()

                if st.button("🗑 Excluir", key=f"del_{item['id']}"):
                    executar(
                        "DELETE FROM estoque WHERE id=:id",
                        {"id": item["id"]}
                    )
                    st.warning("Produto excluído")
                    st.rerun()
