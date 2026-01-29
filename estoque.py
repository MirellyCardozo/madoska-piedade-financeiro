import streamlit as st
import pandas as pd
from database import executar

def tela_estoque(user):
    st.title("📦 Estoque")

    nome = st.text_input("Produto")
    quantidade = st.number_input("Quantidade", min_value=0, step=1)
    preco = st.number_input("Preço", min_value=0.0, step=0.01)

    if st.button("Cadastrar"):
        executar(
            """
            INSERT INTO estoque (nome, quantidade, preco, usuario_id)
            VALUES (:nome, :quantidade, :preco, :uid)
            """,
            {
                "nome": nome,
                "quantidade": quantidade,
                "preco": preco,
                "uid": user["id"]
            }
        )
        st.success("Produto cadastrado")
        st.rerun()

    st.divider()

    produtos = executar(
        """
        SELECT id, nome, quantidade, preco
        FROM estoque
        WHERE usuario_id = :uid
        ORDER BY nome
        """,
        {"uid": user["id"]},
        fetchall=True
    )

    if not produtos:
        st.info("Estoque vazio")
        return

    df = pd.DataFrame(produtos, columns=["ID", "Nome", "Quantidade", "Preço"])
    st.dataframe(df, use_container_width=True)

    apagar = st.selectbox("Excluir produto (ID)", df["ID"])

    if st.button("🗑️ Excluir produto"):
        executar(
            "DELETE FROM estoque WHERE id = :id AND usuario_id = :uid",
            {"id": apagar, "uid": user["id"]}
        )
        st.success("Produto excluído")
        st.rerun()
