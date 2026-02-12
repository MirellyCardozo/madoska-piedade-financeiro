import streamlit as st
import pandas as pd
from sqlalchemy import text
from database import engine
from datetime import date


def tela_lancamentos(usuario):
    st.title("🧾 Lançamentos Financeiros")

    # =========================
    # FORMULÁRIO NOVO LANÇAMENTO
    # =========================
    with st.expander("➕ Novo lançamento"):
        with st.form("form_novo_lancamento"):
            data = st.date_input("Data", value=date.today())
            descricao = st.text_input("Descrição")
            categoria = st.text_input("Categoria")
            tipo = st.selectbox("Tipo", ["entrada", "saida"])
            valor = st.number_input("Valor", min_value=0.0, step=0.01)

            salvar = st.form_submit_button("Salvar")

            if salvar:
                sql = text("""
                    INSERT INTO lancamentos (usuario_id, data, descricao, categoria, tipo, valor)
                    VALUES (:uid, :data, :descricao, :categoria, :tipo, :valor)
                """)
                with engine.begin() as conn:
                    conn.execute(sql, {
                        "uid": usuario["id"],
                        "data": data,
                        "descricao": descricao,
                        "categoria": categoria,
                        "tipo": tipo,
                        "valor": valor
                    })

                st.success("Lançamento salvo com sucesso!")
                st.rerun()

    # =========================
    # LISTAR LANÇAMENTOS
    # =========================
    query = text("""
        SELECT id, data, descricao, categoria, tipo, valor
        FROM lancamentos
        WHERE usuario_id = :uid
        ORDER BY data DESC
    """)

    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"uid": usuario["id"]})

    if df.empty:
        st.info("Nenhum lançamento cadastrado.")
        return

    # =========================
    # EDIÇÃO / EXCLUSÃO
    # =========================
    for _, row in df.iterrows():
        with st.expander(
            f"📌 {row['data']} | {row['descricao']} | R$ {row['valor']:.2f}"
        ):
            col1, col2 = st.columns(2)

            with col1:
                data_edit = st.date_input(
                    "Data", value=row["data"], key=f"data_{row['id']}"
                )
                descricao_edit = st.text_input(
                    "Descrição", value=row["descricao"], key=f"desc_{row['id']}"
                )
                categoria_edit = st.text_input(
                    "Categoria", value=row["categoria"], key=f"cat_{row['id']}"
                )

            with col2:
                tipo_edit = st.selectbox(
                    "Tipo", ["entrada", "saida"],
                    index=0 if row["tipo"] == "entrada" else 1,
                    key=f"tipo_{row['id']}"
                )
                valor_edit = st.number_input(
                    "Valor",
                    min_value=0.0,
                    step=0.01,
                    value=float(row["valor"]),
                    key=f"valor_{row['id']}"
                )

            col_save, col_delete = st.columns(2)

            # =========================
            # ATUALIZAR
            # =========================
            if col_save.button("💾 Atualizar", key=f"save_{row['id']}"):
                sql = text("""
                    UPDATE lancamentos
                    SET data = :data,
                        descricao = :descricao,
                        categoria = :categoria,
                        tipo = :tipo,
                        valor = :valor
                    WHERE id = :id AND usuario_id = :uid
                """)
                with engine.begin() as conn:
                    conn.execute(sql, {
                        "data": data_edit,
                        "descricao": descricao_edit,
                        "categoria": categoria_edit,
                        "tipo": tipo_edit,
                        "valor": valor_edit,
                        "id": row["id"],
                        "uid": usuario["id"]
                    })

                st.success("Lançamento atualizado!")
                st.rerun()

            # =========================
            # EXCLUIR
            # =========================
            if col_delete.button("🗑️ Excluir", key=f"del_{row['id']}"):
                sql = text("""
                    DELETE FROM lancamentos
                    WHERE id = :id AND usuario_id = :uid
                """)
                with engine.begin() as conn:
                    conn.execute(sql, {
                        "id": row["id"],
                        "uid": usuario["id"]
                    })

                st.warning("Lançamento excluído!")
                st.rerun()
