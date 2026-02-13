import streamlit as st
import pandas as pd
from sqlalchemy import text
from datetime import datetime
from io import BytesIO
from fpdf import FPDF

from database import engine


# =========================
# PDF
# =========================
def gerar_pdf(df, periodo, saldo_anterior, entradas, saidas, saldo_final):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Relatório Financeiro - Madoska Piedade", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", "", 11)

    pdf.cell(0, 8, f"Período: {periodo}", ln=True)
    pdf.cell(0, 8, f"Saldo anterior: R$ {saldo_anterior:.2f}", ln=True)
    pdf.cell(0, 8, f"Total de entradas: R$ {entradas:.2f}", ln=True)
    pdf.cell(0, 8, f"Total de saídas: R$ {saidas:.2f}", ln=True)
    pdf.cell(0, 8, f"Saldo final: R$ {saldo_final:.2f}", ln=True)

    pdf.ln(8)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Lançamentos do mês:", ln=True)

    pdf.set_font("Arial", "", 9)
    largura_util = pdf.w - 2 * pdf.l_margin

    if df.empty:
        pdf.cell(0, 8, "Nenhum lançamento no período.", ln=True)
    else:
        for _, row in df.iterrows():
            linha = (
                f"{row['data']} | "
                f"{row['tipo']} | "
                f"{row['descricao']} | "
                f"{row['categoria']} | "
                f"{row['forma_pagamento']} | "
                f"R$ {float(row['valor']):.2f}"
            )

            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(largura_util, 6, linha)

    buffer = BytesIO()
    buffer.write(pdf.output(dest="S"))
    buffer.seek(0)

    return buffer


# =========================
# DASHBOARD
# =========================
def tela_dashboard(usuario):
    st.title("📊 Dashboard Financeiro")

    hoje = datetime.today()
    mes = st.selectbox("Mês", list(range(1, 13)), index=hoje.month - 1)
    ano = st.selectbox("Ano", list(range(2023, hoje.year + 1)), index=(hoje.year - 2023))

    periodo = f"{mes:02d}/{ano}"

    inicio_mes = f"{ano}-{mes:02d}-01"
    fim_mes = f"{ano + 1}-01-01" if mes == 12 else f"{ano}-{mes + 1:02d}-01"

    # =========================
    # SALDO ANTERIOR
    # =========================
    sql_saldo_anterior = """
        SELECT COALESCE(SUM(
            CASE
                WHEN UPPER(tipo) = 'ENTRADA' THEN valor
                WHEN UPPER(tipo) IN ('SAIDA', 'SAÍDA') THEN -valor
                ELSE 0
            END
        ), 0)
        FROM lancamentos
        WHERE data < :inicio
    """

    with engine.connect() as conn:
        saldo_anterior = conn.execute(
            text(sql_saldo_anterior),
            {"inicio": inicio_mes}
        ).scalar()

    saldo_anterior = float(saldo_anterior or 0)

    # =========================
    # LANÇAMENTOS DO MÊS
    # =========================
    sql_lancamentos = """
        SELECT 
            data,
            tipo,
            descricao,
            categoria,
            forma_pagamento,
            valor
        FROM lancamentos
        WHERE data >= :inicio AND data < :fim
        ORDER BY data
    """

    df = pd.read_sql(
        text(sql_lancamentos),
        engine,
        params={"inicio": inicio_mes, "fim": fim_mes}
    )

    if not df.empty:
        df["valor"] = df["valor"].astype(float)
        df["tipo_norm"] = df["tipo"].str.upper().str.strip()

        entradas = df.loc[df["tipo_norm"] == "ENTRADA", "valor"].sum()
        saidas = df.loc[df["tipo_norm"].isin(["SAIDA", "SAÍDA"]), "valor"].sum()
    else:
        entradas = 0.0
        saidas = 0.0

    saldo_final = saldo_anterior + entradas - saidas

    # =========================
    # MÉTRICAS
    # =========================
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Saldo Anterior", f"R$ {saldo_anterior:.2f}")
    col2.metric("Entradas", f"R$ {entradas:.2f}")
    col3.metric("Saídas", f"R$ {saidas:.2f}")
    col4.metric("Saldo Final", f"R$ {saldo_final:.2f}")

    st.divider()
    st.subheader("📋 Lançamentos do Mês")

    if df.empty:
        st.info("Nenhum lançamento neste período.")
    else:
        st.dataframe(
            df.drop(columns=["tipo_norm"], errors="ignore"),
            use_container_width=True
        )

    # =========================
    # PDF
    # =========================
    st.divider()
    if st.button("📄 Gerar Relatório PDF"):
        pdf_buffer = gerar_pdf(
            df,
            periodo,
            saldo_anterior,
            entradas,
            saidas,
            saldo_final
        )

        st.download_button(
            "⬇️ Baixar PDF",
            pdf_buffer,
            file_name=f"relatorio_{ano}_{mes:02d}.pdf",
            mime="application/pdf"
        )
