import streamlit as st
import pandas as pd
from database import executar

def tela_estoque(user):
    st.title("📦 Estoque")

    produto = st.text_input("Produto")
    quantidade = st.number_input("Quantidade", min_value=0, step=1)
    preco = st.number_input("Preço", min_value=0.0, step=0.01)

    if st.button("Cadastrar"):
        executar("""
            INSERT INTO estoque (nome, quantidade, preco)
            VALUES (:n, :q, :p)
        """, {
            "n": produto,
            "q": quantidade,
            "p": preco
        })
        st.success("Produto cadastrado!")
        st.rerun()

    rows = executar("""
        SELECT id, nome, quantidade, preco
        FROM estoque
        ORDER BY nome
    """, fetchall=True)

    if rows:
        df = pd.DataFrame(rows, columns=[
            "ID", "Produto", "Quantidade", "Preço"
        ])
        st.dataframe(df, use_container_width=True)
