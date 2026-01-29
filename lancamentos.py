import streamlit as st
import pandas as pd
from database import executar
from datetime import date

CATEGORIAS = [
    "Aluguel", "Fornecedor", "Energia", "Internet",
    "Funcionários", "Impostos", "Manutenção", "Outros"
]

PAGAMENTOS = ["Pix", "Cartão", "Dinheiro", "Boleto", "Transferência"]

def tela_lancamentos(user):
    st.title("💰 Lançamentos Financeiros")

    col1, col2 = st.columns(2)

    with col1:
        data = st.date_input("Data", value=date.today())
        descricao = st.text_input("Descrição")
        categoria = st.selectbox("Categoria", CATEGORIAS)

    with col2:
        valor = st.number_input("Valor", min_value=0.0, step=0.01)
        tipo = st.selectbox("Tipo", ["Entrada", "Saída"])
        pagamento = st.selectbox("Forma de pagamento", PAGAMENTOS)

    if st.button("Salvar lançamento"):
        executar("""
            INSERT INTO lancamentos
            (user_id, data, descricao, categoria, valor, tipo, pagamento)
            VALUES (:u, :d, :desc, :cat, :v, :t, :p)
        """, {
            "u": user["id"],
            "d": data,
            "desc": descricao,
            "cat": categoria,
            "v": valor,
            "t": tipo,
            "p": pagamento
        })
        st.success("Lançamento salvo!")
        st.rerun()

    st.divider()
    st.subheader("📋 Registros")

    rows = executar("""
        SELECT id, data, descricao, categoria, valor, tipo, pagamento
        FROM lancamentos
        WHERE user_id = :u
        ORDER BY data DESC
    """, {"u": user["id"]}, fetchall=True)

    if not rows:
        st.info("Nenhum lançamento registrado")
        return

    df = pd.DataFrame(rows, columns=[
        "ID", "Data", "Descrição", "Categoria",
        "Valor", "Tipo", "Pagamento"
    ])

    st.dataframe(df, use_container_width=True)

    excluir_id = st.number_input("ID para excluir", min_value=1, step=1)

    if st.button("Excluir lançamento"):
        executar("DELETE FROM lancamentos WHERE id = :id", {"id": excluir_id})
        st.success("Lançamento excluído")
        st.rerun()
