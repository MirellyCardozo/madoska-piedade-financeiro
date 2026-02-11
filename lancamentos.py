import streamlit as st
from database import executar
from datetime import date

CATEGORIAS = ["Aluguel", "Fornecedor", "Energia", "Internet", "Funcionários", "Impostos", "Manutenção", "Marketing", "Outros"]
PAGAMENTOS = ["Pix", "Cartão Débito","Cartão Crédito", "Dinheiro", "Boleto", "Transferência"]

def tela_lancamentos(user):
    st.header("📋 Lançamentos Financeiros")

    with st.form("novo_lancamento"):
        data = st.date_input("Data", value=date.today())
        descricao = st.text_input("Descrição")
        categoria = st.selectbox("Categoria", CATEGORIAS)
        tipo = st.selectbox("Tipo", ["Entrada", "Saída"])
        valor = st.number_input("Valor", min_value=0.01)
        pagamento = st.selectbox("Forma de pagamento", PAGAMENTOS)

        if st.form_submit_button("Salvar"):
            executar(
                """
                INSERT INTO lancamentos
                (data, descricao, categoria, tipo, valor, pagamento, usuario_id)
                VALUES (:d, :desc, :cat, :tipo, :val, :pag, :uid)
                """,
                {
                    "d": data,
                    "desc": descricao,
                    "cat": categoria,
                    "tipo": tipo,
                    "val": valor,
                    "pag": pagamento,
                    "uid": user["id"]
                }
            )
            st.success("Lançamento salvo")
            st.rerun()

    st.subheader("Lançamentos cadastrados")

    rows = executar(
        "SELECT id, data, descricao, categoria, tipo, valor FROM lancamentos ORDER BY data DESC",
        fetchall=True
    )

    if rows:
        st.dataframe(rows, use_container_width=True)
