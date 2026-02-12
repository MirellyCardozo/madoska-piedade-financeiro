import streamlit as st
import pandas as pd
from sqlalchemy import text
from database import engine

def tela_lancamentos(usuario):
    st.title("📋 Lançamentos")

    # =========================
    # FORMULÁRIO NOVO LANÇAMENTO
    # =========================
    with st.form("novo_lancamento"):
        data = st.date_input("Data")
        descricao = st.text_input("Descrição")
        categoria = st.selectbox("Categoria", ["Fornecedor", "Aluguel", "Energia", "Manutenção", "Funcionários", "Impostos","Outros"])
        tipo = st.selectbox("Tipo", ["Entrada", "Saída"])
        valor = st.number_input("Valor", min_value=0.01, step=0.01)

        salvar = st.form_submit_button("Salvar")

        if salvar:
            with engine.begin() as conn:
                conn.execute(
                    text("""
                        INSERT INTO lancamentos (usuario_id, data, descricao, categoria, tipo, valor)
                        VALUES (:usuario_id, :data, :descricao, :categoria, :tipo, :valor)
                    """),
                    {
                        "usuario_id": usuario["id"],
                        "data": data,
                        "descricao": descricao,
                        "categoria": categoria,
                        "tipo": tipo,
                        "valor": valor
                    }
                )
            st.success("✅ Lançamento cadastrado com sucesso")
            st.rerun()

    st.divider()

    # =========================
    # LISTAR LANÇAMENTOS
    # =========================
    with engine.connect() as conn:
        df = pd.read_sql(
            text("""
                SELECT id, data, descricao, categoria, tipo, valor
                FROM lancamentos
                WHERE usuario_id = :uid
                ORDER BY data DESC
            """),
            conn,
            params={"uid": usuario["id"]}
        )

    if df.empty:
        st.info("Nenhum lançamento cadastrado.")
        return

    st.subheader("📄 Lançamentos cadastrados")
    st.dataframe(df, use_container_width=True)

    # =========================
    # SELECIONAR LANÇAMENTO
    # =========================
    st.subheader("✏️ Editar ou 🗑️ Excluir")

    lancamento_id = st.selectbox(
        "Selecione um lançamento pelo ID",
        df["id"]
    )

    lancamento = df[df["id"] == lancamento_id].iloc[0]

    # =========================
    # FORMULÁRIO DE EDIÇÃO
    # =========================
    with st.form("editar_lancamento"):
        nova_data = st.date_input("Data", lancamento["data"])
        nova_descricao = st.text_input("Descrição", lancamento["descricao"])
        nova_categoria = st.selectbox(
            "Categoria",
        ["Fornecedor", "Aluguel", "Energia", "Manutenção", "Funcionários", "Impostos","Outros"],
            index=["Fornecedor", "Aluguel", "Energia", "Manutenção", "Funcionários", "Impostos","Outros"].index(lancamento["categoria"])
        )
        novo_tipo = st.selectbox(
            "Tipo",
            ["Entrada", "Saída"],
            index=["Entrada", "Saída"].index(lancamento["tipo"])
        )
        novo_valor = st.number_input("Valor", value=float(lancamento["valor"]), step=0.01)

        col1, col2 = st.columns(2)

        with col1:
            atualizar = st.form_submit_button("💾 Atualizar")

        with col2:
            excluir = st.form_submit_button("🗑️ Excluir")

        # ATUALIZAR
        if atualizar:
            with engine.begin() as conn:
                conn.execute(
                    text("""
                        UPDATE lancamentos
                        SET data = :data,
                            descricao = :descricao,
                            categoria = :categoria,
                            tipo = :tipo,
                            valor = :valor
                        WHERE id = :id
                    """),
                    {
                        "data": nova_data,
                        "descricao": nova_descricao,
                        "categoria": nova_categoria,
                        "tipo": novo_tipo,
                        "valor": novo_valor,
                        "id": lancamento_id
                    }
                )
            st.success("✅ Lançamento atualizado")
            st.rerun()

        # EXCLUIR
        if excluir:
            with engine.begin() as conn:
                conn.execute(
                    text("DELETE FROM lancamentos WHERE id = :id"),
                    {"id": lancamento_id}
                )
            st.success("🗑️ Lançamento excluído")
            st.rerun()
