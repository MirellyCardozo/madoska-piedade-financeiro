import streamlit as st
import pandas as pd
from sqlalchemy import text
from database import engine
from fpdf import FPDF
from io import BytesIO
from decimal import Decimal

def gerar_pdf(df, periodo, saldo_anterior, entradas, saidas, saldo_final):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    pdf.cell(0, 8, "Relatório Financeiro - Madoska Piedade", ln=True)
    pdf.ln(3)

    pdf.cell(0, 6, f"Período: {periodo}", ln=True)
    pdf.cell(0, 6, f"Saldo anterior: R$ {saldo_anterior:.2f}", ln=True)
    pdf.cell(0, 6, f"Entradas: R$ {entradas:.2f}", ln=True)
    pdf.cell(0, 6, f"Saídas: R$ {saidas:.2f}", ln=True)
    pdf.cell(0, 6, f"Saldo final: R$ {saldo_final:.2f}", ln=True)

    pdf.ln(5)
    pdf.cell(0, 6, "Lançamentos:", ln=True)

    for _, row in df.iterrows():
        linha = (
            f"{row['data']} | {row['tipo'].upper()} | "
            f"{row['categoria']} | {row['pagamento']} | "
            f"R$ {row['valor']:.2f}"
        )
        pdf.multi_cell(0, 6, linha)

    buffer = BytesIO()
    buffer.write(pdf.output(dest="S").encode("latin-1"))
    buffer.seek(0)
    return buffer


def tela_dashboard(usuario):
    st.title("Dashboard")

    mes = st.date_input("Mês de referência").replace(day=1)
    inicio = mes
    fim = (mes + pd.offsets.MonthBegin(1)).date()

    saldo_anterior = pd.read_sql("""
        SELECT COALESCE(SUM(
            CASE WHEN tipo = 'Entrada' THEN valor ELSE -valor END
        ),0) AS saldo
        FROM lancamentos
        WHERE data < :inicio
    """, engine, params={"inicio": inicio}).iloc[0]["saldo"]

    df = pd.read_sql("""
        SELECT data, tipo, categoria, pagamento, valor
        FROM lancamentos
        WHERE data >= :inicio AND data < :fim
        ORDER BY data
    """, engine, params={"inicio": inicio, "fim": fim})

    entradas = df[df["tipo"] == "Entrada"]["valor"].sum()
    saidas = df[df["tipo"] == "Saída"]["valor"].sum()

    entradas = float(entradas or 0)
    saidas = float(saidas or 0)
    saldo_anterior = float(saldo_anterior or 0)

    saldo_final = saldo_anterior + entradas - saidas

    st.metric("Saldo anterior", f"R$ {saldo_anterior:.2f}")
    st.metric("Entradas", f"R$ {entradas:.2f}")
    st.metric("Saídas", f"R$ {saidas:.2f}")
    st.metric("Saldo final", f"R$ {saldo_final:.2f}")

    if st.button("Gerar Relatório PDF"):
        pdf = gerar_pdf(
            df,
            mes.strftime("%m/%Y"),
            saldo_anterior,
            entradas,
            saidas,
            saldo_final
        )
        st.download_button(
            "Baixar PDF",
            data=pdf,
            file_name=f"relatorio_{mes.strftime('%m_%Y')}.pdf"
        )
