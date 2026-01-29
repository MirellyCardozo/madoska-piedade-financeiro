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

    col1, col2, col3 = st.columns(3)

    with col1:
        data = st.date_input("Data", value=date.today())
        descricao = st.text_input("Descrição")

    with col2:
        categoria = st.selectbox("Categoria", CATEGORIAS)
        pagamento = st.selectbox("Forma de pagamento", PAGAMENTOS)

    with col3:
        tipo = st.selectbox("Tipo", ["Entrada", "Saída"])
        valor = st.number_input("Valor", min_value=0.0, step=0.01)

    if st.button("Salvar lançamento"):
        executar(
            """
            INSERT INTO lancamentos (data, descricao, categoria, tipo, valor, pagamento, usuario_id)
            VALUES (:data, :descricao, :categoria, :tipo, :valor, :pagamento, :usuario_id)
            """,
            {
                "data": data,
                "descricao": descricao,
                "categoria": categoria,
                "tipo": tipo,
                "valor": valor,
                "pagamento": pagamento,
                "usuario_id": user["id"]
            }
        )
        st.success("Lançamento salvo com sucesso")
        st.rerun()

    st.divider()
    st.subheader("📋 Lançamentos registrados")

    rows = executar(
        """
        SELECT id, data, descricao, categoria, tipo, valor, pagamento
        FROM lancamentos
        WHERE usuario_id = :uid
        ORDER BY data DESC
        """,
        {"uid": user["id"]},
        fetchall=True
    )

    if not rows:
        st.info("Nenhum lançamento encontrado")
        return

    df = pd.DataFrame(
        rows,
        columns=["ID", "Data", "Descrição", "Categoria", "Tipo", "Valor", "Pagamento"]
    )

    st.dataframe(df, use_container_width=True)

    excluir = st.selectbox("Excluir lançamento (ID)", df["ID"])

    if st.button("🗑️ Excluir"):
        executar(
            "DELETE FROM lancamentos WHERE id = :id AND usuario_id = :uid",
            {"id": excluir, "uid": user["id"]}
        )
        st.success("Lançamento excluído")
        st.rerun()
