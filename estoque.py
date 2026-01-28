import streamlit as st
from database import executar

# ==========================
# TELA DE ESTOQUE
# ==========================
def tela_estoque(user):
    st.title("📦 Estoque")

    st.subheader("Cadastrar produto")

    produto = st.text_input("Produto")
    quantidade = st.number_input("Quantidade", min_value=0, step=1)
    preco = st.number_input("Preço", min_value=0.0, step=0.01, format="%.2f")

    if st.button("Cadastrar"):
        if not produto.strip():
            st.error("Informe o nome do produto")
        else:
            executar(
                """
                INSERT INTO estoque (produto, quantidade, preco)
                VALUES (:produto, :quantidade, :preco)
                """,
                {
                    "produto": produto.strip(),
                    "quantidade": quantidade,
                    "preco": preco
                }
            )
            st.success("Produto cadastrado com sucesso")
            st.rerun()

    st.divider()
    st.subheader("Produtos cadastrados")

    produtos = executar(
        """
        SELECT id, produto, quantidade, preco
        FROM estoque
        ORDER BY produto
        """,
        fetchall=True
    )

    if not produtos:
        st.info("Nenhum produto cadastrado")
        return

    for p in produtos:
        id_produto = p[0]
        nome_produto = p[1]
        qtd_produto = p[2]
        preco_produto = float(p[3])

        with st.expander(f"📦 {nome_produto} | Qtd: {qtd_produto} | R$ {preco_produto:.2f}"):
            col1, col2 = st.columns(2)

            with col1:
                novo_produto = st.text_input(
                    "Produto",
                    value=nome_produto,
                    key=f"produto_{id_produto}"
                )

                nova_qtd = st.number_input(
                    "Quantidade",
                    min_value=0,
                    step=1,
                    value=int(qtd_produto),
                    key=f"qtd_{id_produto}"
                )

                novo_preco = st.number_input(
                    "Preço",
                    min_value=0.0,
                    step=0.01,
                    format="%.2f",
                    value=float(preco_produto),
                    key=f"preco_{id_produto}"
                )

                if st.button("💾 Salvar alterações", key=f"salvar_{id_produto}"):
                    if not novo_produto.strip():
                        st.error("O nome do produto não pode ficar vazio")
                    else:
                        executar(
                            """
                            UPDATE estoque
                            SET produto = :produto,
                                quantidade = :quantidade,
                                preco = :preco
                            WHERE id = :id
                            """,
                            {
                                "produto": novo_produto.strip(),
                                "quantidade": nova_qtd,
                                "preco": novo_preco,
                                "id": id_produto
                            }
                        )
                        st.success("Produto atualizado")
                        st.rerun()

            with col2:
                st.warning("Atenção: essa ação não pode ser desfeita")

                if st.button("🗑 Excluir produto", key=f"excluir_{id_produto}"):
                    executar(
                        "DELETE FROM estoque WHERE id = :id",
                        {"id": id_produto}
                    )
                    st.success("Produto excluído")
                    st.rerun()
