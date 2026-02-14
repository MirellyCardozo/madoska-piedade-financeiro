import streamlit as st
import pandas as pd
from sqlalchemy import text
from database import engine
from datetime import date


def tela_dashboard(usuario_id):
    st.title("Dashboard Financeiro")

    # ==============================
    # FILTRO DE MÊS
    # ==============================
    hoje = date.today()
    mes = st.selectbox(
        "Mês",
        list(range(1, 13)),
        index=hoje.month - 1
    )
    ano = st.selectbox(
        "Ano",
        list(range(2023, hoje.year + 1)),
        index=(hoje.year - 2023)
    )

    inicio_mes = date(ano, mes, 1)

    if mes == 12:
        fim_mes = date(ano + 1, 1, 1)
    else:
        fim_mes = date(ano, mes + 1, 1)

    # ==============================
    # SALDO ANTERIOR
    # ==============================
    sql_saldo_anterior = """
        SELECT
            COALESCE(SUM(
                CASE
                    WHEN tipo = 'Entrada' THEN valor
                    ELSE -valor
                END
            ), 0)
        FROM lancamentos
        WHERE usuario_id = :usuario_id
          AND data < :inicio_mes
    """

    saldo_anterior = pd.read_sql(
        text(sql_saldo_anterior),
        engine,
        params={"usuario_id": usuario_id, "inicio_mes": inicio_mes}
    ).iloc[0, 0]

    saldo_anterior = float(saldo_anterior or 0)

    # ==============================
    # LANÇAMENTOS DO MÊS
    # ==============================
    sql_lancamentos = """
        SELECT
            data,
            tipo,
            categoria,
            pagamento,
            descricao,
            valor
        FROM lancamentos
        WHERE usuario_id = :usuario_id
          AND data >= :inicio_mes
          AND data < :fim_mes
        ORDER BY data
    """

    df = pd.read_sql(
        text(sql_lancamentos),
        engine,
        params={
            "usuario_id": usuario_id,
            "inicio_mes": inicio_mes,
            "fim_mes": fim_mes
        }
    )

    if df.empty:
        st.info("Nenhum lançamento no período.")
        st.metric("Saldo anterior", f"R$ {saldo_anterior:,.2f}")
        return

    df["valor"] = df["valor"].astype(float)

    entradas = df[df["tipo"] == "Entrada"]["valor"].sum()
    saidas = df[df["tipo"] == "Saída"]["valor"].sum()

    saldo_final = saldo_anterior + entradas - saidas

    # ==============================
    # MÉTRICAS
    # ==============================
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Saldo anterior", f"R$ {saldo_anterior:,.2f}")
    col2.metric("Entradas", f"R$ {entradas:,.2f}")
    col3.metric("Saídas", f"R$ {saidas:,.2f}")
    col4.metric("Saldo final", f"R$ {saldo_final:,.2f}")

    # ==============================
    # GASTOS POR CATEGORIA
    # ==============================
    st.subheader("Gastos por categoria")

    df_saidas = df[df["tipo"] == "Saída"]

    if df_saidas.empty:
        st.info("Nenhuma saída no período.")
    else:
        resumo_categoria = (
            df_saidas
            .groupby("categoria")["valor"]
            .sum()
            .reset_index()
            .sort_values("valor", ascending=False)
        )

        st.dataframe(
            resumo_categoria,
            use_container_width=True,
            hide_index=True
        )

        st.bar_chart(
            resumo_categoria.set_index("categoria")
        )

    # ==============================
    # TABELA DE LANÇAMENTOS
    # ==============================
    st.subheader("Lançamentos do mês")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
