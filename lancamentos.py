import streamlit as st
import pandas as pd
from sqlalchemy import text
from database import engine, executar

FORMAS_PAGAMENTO = [
    "Pix",
    "Cartão Débito",
    "Cartão Crédito",
    "Dinheiro",
    "Boleto",
    "Transferência"
]

def tela_lancamentos(usuario_id):
    st.title("Lançamentos")

    categorias = pd.read_sql(
        "SELECT DISTINCT categoria FROM lancamentos ORDER BY categoria",
        engine
    )["categoria"].tolist()

    with st.form("novo_lancamento"):
        data = st.date_input("Data")
        tipo = st.selectbox("Tipo", ["Entrada", "Saída"])
        categoria = st.selectbox("Categoria", categorias)
        pagamento = st.selectbox("Forma de pagamento", FORMAS_PAGAMENTO)
        descricao = st.text_input("Descrição")
        valor = st.number_input("Valor", min_value=0.01, step=0.01)

        salvar = st.form_submit_button("Salvar")

        if salvar:
            executar("""
                INSERT INTO lancamentos
                (data, tipo, categoria, pagamento, descricao, valor, usuario_id)
                VALUES
                (:data, :tipo, :categoria, :pagamento, :descricao, :valor, :usuario)
            """, {
                "data": data,
                "tipo": tipo,
                "categoria": categoria,
                "pagamento": pagamento,
                "descricao": descricao,
                "valor": valor,
                "usuario": usuario_id
            })
            st.success("Lançamento salvo")

    st.divider()

    df = pd.read_sql("""
        SELECT id, data, tipo, categoria, pagamento, descricao, valor
        FROM lancamentos
        ORDER BY data DESC
    """, engine)

    st.dataframe(df, use_container_width=True)

    excluir_id = st.number_input("ID para excluir", min_value=1, step=1)
    if st.button("Excluir lançamento"):
        executar("DELETE FROM lancamentos WHERE id = :id", {"id": excluir_id})
        st.success("Lançamento excluído")
