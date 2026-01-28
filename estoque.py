import streamlit as st
from database import executar

def tela_estoque():
    st.title("📦 Estoque")

    nome = st.text_input("Produto")
    quantidade = st.number_input("Quantidade", min_value=0)
    preco = st.number_input("Preço", min_value=0.0, format="%.2f")

    if st.button("Cadastrar"):
        executar(
            """
            INSERT INTO estoque (nome, quantidade, preco)
            VALUES (:n, :q, :p)
            """,
            {"n": nome, "q": quantidade, "p": preco}
        )
        st.success("Produto cadastrado!")
        st.rerun()

    st.divider()

    produtos = executar(
        "SELECT id, nome, quantidade, preco FROM estoque ORDER BY nome",
        fetchall=True
    )

    for p in produtos:
        with st.expander(f"{p.nome} | Qtd: {p.quantidade} | R$ {float(p.preco):.2f}"):
            if st.button("🗑 Excluir", key=f"e{p.id}"):
                executar(
                    "DELETE FROM estoque WHERE id = :id",
                    {"id": p.id}
                )
                st.rerun()
