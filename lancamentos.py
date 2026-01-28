import streamlit as st
from database import executar
from datetime import date

CATEGORIAS = ["Aluguel", "Fornecedor", "Energia", "Internet","Funcionários", "Impostos","Manutenção", "Outros"]
PAGAMENTOS = ["Pix", "Cartão", "Dinheiro", "Boleto","Transferência"]


def tela_lancamentos(user=None):
    st.title("💰 Lançamentos Financeiros")

    col1, col2 = st.columns(2)

    with col1:
        data = st.date_input("Data", value=date.today())
        categoria = st.selectbox("Categoria", CATEGORIAS)
        pagamento = st.selectbox("Forma de pagamento", PAGAMENTOS)

    with col2:
        descricao = st.text_input("Descrição")
        valor = st.number_input("Valor", min_value=0.0, format="%.2f")
        observacoes = st.text_area("Observações")

    if st.button("Salvar lançamento"):
        executar(
            """
            INSERT INTO registros
            (data, tipo, descricao, categoria, pagamento, valor, observacoes)
            VALUES
            (:data, 'saida', :descricao, :categoria, :pagamento, :valor, :obs)
            """,
            {
                "data": str(data),
                "descricao": descricao,
                "categoria": categoria,
                "pagamento": pagamento,
                "valor": valor,
                "obs": observacoes
            }
        )
        st.success("Lançamento salvo!")
        st.rerun()

    st.divider()
    st.subheader("Lançamentos registrados")

    registros = executar(
        "SELECT id, data, descricao, valor FROM registros ORDER BY data DESC",
        fetchall=True
    )

    for r in registros:
        with st.expander(f"{r.data} | {r.descricao} | R$ {float(r.valor):.2f}"):
            if st.button("🗑 Excluir", key=f"del_{r.id}"):
                executar(
                    "DELETE FROM registros WHERE id = :id",
                    {"id": r.id}
                )
                st.rerun()
