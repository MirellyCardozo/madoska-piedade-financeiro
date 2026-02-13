import streamlit as st
import pandas as pd
from sqlalchemy import text
from datetime import date

from database import engine


FORMAS_PAGAMENTO = [
    "Pix",
    "Cartão Débito",
    "Cartão Crédito",
    "Dinheiro",
    "Boleto",
    "Transferência"
]


def tela_lancamentos(usuario):
    st.title("💰 Lançamentos Financeiros")

    st.subheader("➕ Novo lançamento")

    with st.form("form_lancamento", clear_on_submit=True):
        data = st.date_input("Data", value=date.today())

        tipo = st.selectbox(
            "Tipo",
            ["Entrada", "Saída"]
        )

        descricao = st.text_input("Descrição")

        categoria = st.text_input("Categoria")

        pagamento = st.selectbox(
            "Forma de pagamento",
            FORMAS_PAGAMENTO
        )

        valor = st.number_input(
            "Valor (R$)",
            min_value=0.01,
            step=0.01,
            format="%.2f"
        )

        salvar = st.form_submit_button("Salvar lançamento")

    if salvar:
        sql = """
            INSERT INTO lancamentos
            (data, tipo, descricao, categoria, pagamento, valor, usuario_id)
            VALUES
            (:data, :tipo, :descricao, :categoria, :pagamento, :valor, :usuario_id)
        """

        with engine.begin() as conn:
            conn.execute(
                text(sql),
                {
                    "data": data,
                    "tipo": tipo,
                    "descricao": descricao,
                    "categoria": categoria,
                    "pagamento": pagamento,
                    "valor": valor,
                    "usuario_id": usuario["id"]
                }
            )

        st.success("✅ Lançamento cadastrado com sucesso")
        st.rerun()

    st.divider()
    st.subheader("📋 Lançamentos cadastrados")

    df = pd.read_sql(
        """
        SELECT
            id,
            data,
            tipo,
            descricao,
            categoria,
            pagamento,
            valor
        FROM lancamentos
        ORDER BY data DESC, id DESC
        """,
        engine
    )

    if df.empty:
        st.info("Nenhum lançamento cadastrado.")
        return

    df["valor"] = df["valor"].astype(float)

    for _, row in df.iterrows():
        with st.container(border=True):
            cols = st.columns([2, 2, 2, 2, 2, 1, 1])

            cols[0].write(row["data"])
            cols[1].write(row["tipo"])
            cols[2].write(row["descricao"])
            cols[3].write(row["categoria"])
            cols[4].write(row["pagamento"])
            cols[5].write(f"R$ {row['valor']:.2f}")

            editar = cols[6].button("✏️", key=f"edit_{row['id']}")
            excluir = cols[6].button("🗑️", key=f"del_{row['id']}")

            # 🗑️ EXCLUIR
            if excluir:
                with engine.begin() as conn:
                    conn.execute(
                        text("DELETE FROM lancamentos WHERE id = :id"),
                        {"id": row["id"]}
                    )
                st.success("🗑️ Lançamento excluído")
                st.rerun()

            # ✏️ EDITAR
            if editar:
                st.subheader("✏️ Editar lançamento")

                with st.form(f"form_edit_{row['id']}"):
                    nova_data = st.date_input("Data", value=row["data"])
                    novo_tipo = st.selectbox(
                        "Tipo",
                        ["Entrada", "Saída"],
                        index=0 if row["tipo"] == "Entrada" else 1
                    )
                    nova_descricao = st.text_input(
                        "Descrição",
                        value=row["descricao"]
                    )
                    nova_categoria = st.text_input(
                        "Categoria",
                        value=row["categoria"]
                    )
                    novo_pagamento = st.selectbox(
                        "Forma de pagamento",
                        FORMAS_PAGAMENTO,
                        index=FORMAS_PAGAMENTO.index(row["pagamento"])
                    )
                    novo_valor = st.number_input(
                        "Valor",
                        min_value=0.01,
                        value=float(row["valor"]),
                        step=0.01,
                        format="%.2f"
                    )

                    atualizar = st.form_submit_button("Atualizar")

                if atualizar:
                    with engine.begin() as conn:
                        conn.execute(
                            text("""
                                UPDATE lancamentos
                                SET
                                    data = :data,
                                    tipo = :tipo,
                                    descricao = :descricao,
                                    categoria = :categoria,
                                    pagamento = :pagamento,
                                    valor = :valor
                                WHERE id = :id
                            """),
                            {
                                "id": row["id"],
                                "data": nova_data,
                                "tipo": novo_tipo,
                                "descricao": nova_descricao,
                                "categoria": nova_categoria,
                                "pagamento": novo_pagamento,
                                "valor": novo_valor
                            }
                        )

                    st.success("✅ Lançamento atualizado")
                    st.rerun()
