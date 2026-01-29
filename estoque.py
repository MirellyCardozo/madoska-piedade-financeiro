import streamlit as st
from database import executar

def tela_estoque(user):
    st.title("📦 Estoque")

    produto = st.text_input("Produto")
    quantidade = st.number_input("Quantidade", min_value=0, step=1)
    preco = st.number_input("Preço", min_value=0.0, step=0.01)

    if st.button("Cadastrar"):
        executar(
            """
            INSERT INTO estoque (produto, quantidade, preco)
            VALUES (:produto, :quantidade, :preco)
            """,
            {
                "produto": produto,
                "quantidade": quantidade,
                "preco": preco
            }
        )
        st.success("Produto cadastrado")
        st.rerun()

    st.subheader("📋 Produtos")

    produtos = executar(
        "SELECT id, produto, quantidade, preco FROM estoque ORDER BY produto",
        fetchall=True
    )

    for p in produtos:
        st.write(f"**{p['produto']}** | Qtd: {p['quantidade']} | R$ {p['preco']:.2f}")
