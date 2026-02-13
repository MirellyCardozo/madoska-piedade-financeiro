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
    largura = pdf.w - 2 * pdf.l_margin

    if df.empty:
        pdf.cell(0, 8, "Nenhum lançamento no período.", ln=True)
    else:
        for _, row in df.iterrows():
            linha = (
                f"{row['data']} | "
                f"{row['tipo']} | "
                f"{row['descricao']} | "
                f"{row['categoria']} | "
                f"{row.get('forma_pagamento', 'Não informado')} | "
                f"R$ {float(row['valor']):.2f}"
            )

            pdf.multi_cell(largura, 6, linha)

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
    mes = st.selectbox("Mês", range(1, 13), index=hoje.month - 1)
    ano = st.selectbox("Ano", range(2023, hoje.year + 1), index=hoje.year - 2023)

    periodo = f"{mes:02d}/{ano}"
    inicio = f"{ano}-{mes:02d}-01"
    fim = f"{ano + 1}-01-01" if mes == 12 else f"{ano}-{mes + 1:02d}-01"

    # =========================
    # SALDO ANTERIOR
    # =========================
    sql_saldo = """
        SELECT COALESCE(SUM(
            CASE
                WHEN UPPER(tipo) = 'ENTRADA' THEN valor
                WHEN UPPER(tipo) IN ('SAIDA','SAÍDA') THEN -valor
                ELSE 0
            END
        ), 0)
        FROM lancamentos
        WHERE data < :inicio
    """

    with engine.connect() as conn:
        saldo_anterior = float(conn.execute(text(sql_saldo), {"inicio": inicio}).scalar() or 0)

    # =========================
    # LANÇAMENTOS DO MÊS
    # =========================
    sql_lancamentos = """
        SELECT
            data,
            tipo,
            descricao,
            categoria,
            COALESCE(forma_pagamento, 'Não informado') AS forma_pagamento,
            valor
        FROM lancamentos
        WHERE data >= :inicio AND data < :fim
        ORDER BY data
    """

    df = pd.read_sql(
        text(sql_lancamentos),
        engine,
        params={"inicio": inicio, "fim": fim}
    )

    if not df.empty:
        df["valor"] = df["valor"].astype(float)
        tipo = df["tipo"].str.upper()

        entradas = df.loc[tipo == "ENTRADA", "valor"].sum()
        saidas = df.loc[tipo.isin(["SAIDA", "SAÍDA"]), "valor"].sum()
    else:
        entradas = 0.0
        saidas = 0.0

    saldo_final = saldo_anterior + entradas - saidas

    # =========================
    # MÉTRICAS
    # =========================
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Saldo Anterior", f"R$ {saldo_anterior:.2f}")
    c2.metric("Entradas", f"R$ {entradas:.2f}")
    c3.metric("Saídas", f"R$ {saidas:.2f}")
    c4.metric("Saldo Final", f"R$ {saldo_final:.2f}")

    st.divider()
    st.subheader("📋 Lançamentos")

    if df.empty:
        st.info("Nenhum lançamento no período.")
    else:
        st.dataframe(df, use_container_width=True)

    st.divider()
    if st.button("📄 Gerar Relatório PDF"):
        pdf = gerar_pdf(df, periodo, saldo_anterior, entradas, saidas, saldo_final)
        st.download_button(
            "⬇️ Baixar PDF",
            pdf,
            file_name=f"relatorio_{ano}_{mes:02d}.pdf",
            mime="application/pdf"
        )
