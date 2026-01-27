import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

from database import executar

# ==========================
# HORA BR
# ==========================
def agora_br():
    tz = pytz.timezone("America/Sao_Paulo")
    return datetime.now(tz)

# ==========================
# BUSCAR GASTOS
# ==========================
def buscar_gastos():
    sql = """
    SELECT id, data, categoria, descricao, valor
    FROM gastos
    ORDER BY data DESC
    """
    result = executar(sql).fetchall()
    return pd.DataFrame(result, columns=["ID", "Data", "Categoria", "Descrição", "Valor"])

# ==========================
# INSERIR
# ==========================
def inserir_gasto(data, categoria, descricao, valor):
    sql = """
    INSERT INTO gastos (data, categoria, descricao, valor)
    VALUES (:data, :categoria, :descricao, :valor)
    """
    executar(sql, {
        "data": data,
        "categoria": categoria,
        "descricao": descricao,
        "valor": valor
    })

# ==========================
# ATUALIZAR
# ==========================
def atualizar_gasto(id_gasto, data, categoria, descricao, valor):
    sql = """
    UPDATE gastos
    SET data = :data,
        categoria = :categoria,
        descricao = :descricao,
        valor = :valor
    WHERE id = :id
    """
    executar(sql, {
        "id": id_gasto,
        "data": data,
        "categoria": categoria,
        "descricao": descricao,
        "valor": valor
    })

# ==========================
# EXCLUIR
# ==========================
def excluir_gasto(id_gasto):
    sql = "DELETE FROM gastos WHERE id = :id"
    executar(sql, {"id": id_gasto})

# ==========================
# TELA PRINCIPAL
# ==========================
def tela_lancamentos():
    st.title("💰 Lançamentos Financeiros")
    st.caption(f"Hora BR: {agora_br().strftime('%d/%m/%Y %H:%M:%S')}")

    abas = st.tabs(["📋 Listar", "➕ Cadastrar", "✏️ Editar", "🗑️ Excluir"])

    df = buscar_gastos()

    # =====================
    # LISTAR
    # =====================
    with abas[0]:
        if df.empty:
            st.info("Nenhum gasto registrado.")
        else:
            st.dataframe(df, use_container_width=True)

    # =====================
    # CADASTRAR
    # =====================
    with abas[1]:
        st.subheader("Novo Gasto")

        data = st.date_input("Data", value=agora_br().date())
        categoria = st.text_input("Categoria")
        descricao = st.text_input("Descrição")
        valor = st.number_input("Valor (R$)", min_value=0.0, step=0.01)

        if st.button("Salvar Gasto"):
            if not categoria or not descricao or valor <= 0:
                st.error("Preencha todos os campos corretamente.")
            else:
                inserir_gasto(data, categoria, descricao, valor)
                st.success("Gasto cadastrado com sucesso!")
                st.experimental_rerun()

    # =====================
    # EDITAR
    # =====================
    with abas[2]:
        if df.empty:
            st.info("Nada para editar.")
        else:
            gasto_id = st.selectbox("Selecione o gasto", df["ID"])

            gasto = df[df["ID"] == gasto_id].iloc[0]

            data = st.date_input("Data", gasto["Data"])
            categoria = st.text_input("Categoria", gasto["Categoria"])
            descricao = st.text_input("Descrição", gasto["Descrição"])
            valor = st.number_input("Valor (R$)", value=float(gasto["Valor"]), min_value=0.0, step=0.01)

            if st.button("Atualizar Gasto"):
                atualizar_gasto(gasto_id, data, categoria, descricao, valor)
                st.success("Gasto atualizado!")
                st.experimental_rerun()

    # =====================
    # EXCLUIR
    # =====================
    with abas[3]:
        if df.empty:
            st.info("Nada para excluir.")
        else:
            gasto_id = st.selectbox("Selecione o gasto para excluir", df["ID"])
            st.warning("Essa ação NÃO pode ser desfeita.")

            if st.button("Excluir Gasto"):
                excluir_gasto(gasto_id)
                st.success("Gasto excluído!")
                st.experimental_rerun()
