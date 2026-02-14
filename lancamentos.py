import streamlit as st
import pandas as pd
from sqlalchemy import text
from database import engine


# ==============================
# CATEGORIAS FIXAS (COMO PEDIDO)
# ==============================
CATEGORIAS = [
    "Fornecedor",
    "Aluguel",
    "Funcionários",
    "Impostos",
    "Manutenção",
    "Marketing",
    "Outros"
]

PAGAMENTOS = [
    "Pix",
    "Cartão Débito",
    "Cartão Crédito",
    "Dinheiro",
    "Transferência",
    "Boleto"
]


def tela_lancamentos(usuario_id):
    st.title("Lançamentos")

    # ==============================
    # FORMULÁRIO
    # ==============================
    with st.form("form_lancamento"):
        col1, col2 = st.columns(2)

        with col1:
            data = st.date_input("Data")
            tipo = st.selectbox("Tipo", ["Entrada", "Saída"])
            categoria = st.selectbox("Categoria", CATEGORIAS)

        with col2:
            pagamento = st.selectbox("Forma de pagamento", PAGAMENTOS)
            valor = st.number_input("Valor", min_value=0.01, step=0.01)
            descricao = st.text_input("Descrição")

        salvar = st.form_submit_button("Salvar lançamento")

    # ==============================
    # SALVAR NO BANCO
    # ==============================
    if salvar:
        if not descricao:
            st.error("A descrição é obrigatória.")
            return

        sql = """
            INSERT INTO lancamentos
            (data, tipo, categoria, pagamento, valor, descricao, usuario_id)
            VALUES
            (:data, :tipo, :categoria, :pagamento, :valor, :descricao, :usuario_id)
        """

        with engine.begin() as conn:
            conn.execute(
                text(sql),
                {
                    "data": data,
                    "tipo": tipo,
                    "categoria": categoria,
                    "pagamento": pagamento,
                    "valor": valor,
                    "descricao": descricao,
                    "usuario_id": usuario_id
                }
            )

        st.success("Lançamento salvo com sucesso.")
        st.rerun()

    # ==============================
    # LISTAGEM DOS LANÇAMENTOS
    # ==============================
    st.divider()
    st.subheader("Lançamentos cadastrados")

    df = pd.read_sql(
    text("""
        SELECT
            id,
            data,
            tipo,
            categoria,
            pagamento,
            descricao,
            valor
        FROM lancamentos
        WHERE usuario_id = :usuario_id
        ORDER BY data DESC
    """),
    engine,
    params={"usuario_id": usuario_id}
)


    if df.empty:
        st.info("Nenhum lançamento cadastrado.")
        return

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
