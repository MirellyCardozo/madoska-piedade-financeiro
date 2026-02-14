import streamlit as st
import pandas as pd
from sqlalchemy import text
from database import engine, executar


def tela_lancamentos(usuario_id):
    st.title("Lançamentos cadastrados")

    # ==========================
    # FORMULÁRIO DE CADASTRO
    # ==========================
    with st.form("form_lancamento"):
        col1, col2 = st.columns(2)

        with col1:
            data = st.date_input("Data")
            tipo = st.selectbox("Tipo", ["Entrada", "Saída"])
            categoria = st.selectbox(
                "Categoria",
                [
                    "Fornecedor",
                    "Aluguel",
                    "Funcionários",
                    "Impostos",
                    "Manutenção",
                    "Marketing",
                    "Outros",
                ],
            )

        with col2:
            pagamento = st.selectbox(
                "Forma de pagamento",
                [
                    "Pix",
                    "Cartão Débito",
                    "Cartão Crédito",
                    "Dinheiro",
                    "Transferência",
                    "Boleto",
                ],
            )
            valor = st.number_input("Valor", min_value=0.0, step=0.01)

        descricao = st.text_input("Descrição")

        salvar = st.form_submit_button("Salvar lançamento")

        if salvar:
            executar(
                """
                INSERT INTO lancamentos
                (data, tipo, categoria, pagamento, descricao, valor, usuario_id)
                VALUES (:data, :tipo, :categoria, :pagamento, :descricao, :valor, :usuario_id)
                """,
                {
                    "data": data,
                    "tipo": tipo,
                    "categoria": categoria,
                    "pagamento": pagamento,
                    "descricao": descricao,
                    "valor": valor,
                    "usuario_id": usuario_id,
                },
            )
            st.success("Lançamento salvo com sucesso")
            st.rerun()

    st.divider()

    # ==========================
    # LISTAGEM (ERRO CORRIGIDO AQUI)
    # ==========================
    df = pd.read_sql(
        text(
            """
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
            """
        ),
        engine,
        params={"usuario_id": usuario_id},
    )

    if df.empty:
        st.info("Nenhum lançamento cadastrado.")
        return

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    # ==========================
    # EXCLUIR LANÇAMENTO
    # ==========================
    st.subheader("Excluir lançamento")

    id_excluir = st.selectbox(
        "Selecione o ID do lançamento para excluir",
        df["id"].tolist(),
    )

    if st.button("Excluir"):
        executar(
            "DELETE FROM lancamentos WHERE id = :id AND usuario_id = :usuario_id",
            {"id": id_excluir, "usuario_id": usuario_id},
        )
        st.success("Lançamento excluído com sucesso")
        st.rerun()
