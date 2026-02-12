import streamlit as st
from database import executar

def tela_estoque(user):
    st.header("📦 Estoque")

    with st.form("novo_produto"):
        nome = st.text_input("Produto")
        quantidade = st.number_input("Quantidade", min_value=0)
        preco = st.number_input("Preço", min_value=0.0)

        if st.form_submit_button("Cadastrar"):
            executar(
                """
                INSERT INTO estoque (nome, quantidade, preco, usuario_id)
                VALUES (:n, :q, :p, :uid)
                """,
                {"n": nome, "q": quantidade, "p": preco, "uid": user["id"]}
            )
            st.success("Produto cadastrado")
            st.rerun()

    rows = executar(
        "SELECT nome, quantidade, preco FROM estoque ORDER BY nome",
        fetchall=True
    )

    if rows:
        st.dataframe(rows, use_container_width=True)
