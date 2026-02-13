import streamlit as st
import pandas as pd
from sqlalchemy import text
from database import engine
from fpdf import FPDF
from io import BytesIO
from decimal import Decimal


# ================= PDF =================
def gerar_pdf(df, periodo, saldo_anterior, entradas, saidas, saldo_final):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=10)

    pdf.cell(0, 8, "Relatório Financeiro - Madoska Piedade", ln=True)
    pdf.ln(3)

    pdf.cell(0, 6, f"Período: {periodo}", ln=True)
    pdf.cell(0, 6, f"Saldo anterior: R$ {saldo_anterior:.2f}", ln=True)
    pdf.cell(0, 6, f"Total de entradas: R$ {entradas:.2f}", ln=True)
    pdf.cell(0, 6, f"Total de saídas: R$ {saidas:.2f}", ln=True)
    pdf.cell(0, 6, f"Saldo final: R$ {saldo_final:.2f}", ln=True)

    pdf.ln(5)
    pdf.cell(0, 6, "Lançamentos do mês:", ln=True)
    pdf.ln(2)

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


# ================= DASHBOARD =================
def tela_dashboard(usuario_id):
    st.title("Dashboard")

    mes_ref = st.date_input("Mês de referência")
    inicio_mes = mes_ref.replace(day=1)
    fim_mes = (inicio_mes + pd.offsets.MonthBegin(1)).date()

    # -------- SALDO ANTERIOR (MESES PASSADOS) --------
    saldo_anterior = pd.read_sql(
        text("""
            SELECT COALESCE(
                SUM(
                    CASE
                        WHEN tipo = 'Entrada' THEN valor
                        ELSE -valor
                    END
                ), 0
            ) AS saldo
            FROM lancamentos
            WHERE data < :inicio
        """),
        engine,
        params={"inicio": inicio_mes}
    ).iloc[0]["saldo"]

    saldo_anterior = float(saldo_anterior or 0)

    # -------- LANÇAMENTOS DO MÊS --------
    df = pd.read_sql(
        text("""
            SELECT
                data,
                tipo,
                categoria,
                pagamento,
                valor
            FROM lancamentos
            WHERE data >= :inicio
              AND data < :fim
            ORDER BY data
        """),
        engine,
        params={
            "inicio": inicio_mes,
            "fim": fim_mes
        }
    )

    entradas = float(df[df["tipo"] == "Entrada"]["valor"].sum() or 0)
    saidas = float(df[df["tipo"] == "Saída"]["valor"].sum() or 0)

    saldo_final = saldo_anterior + entradas - saidas

    # -------- MÉTRICAS --------
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Saldo anterior", f"R$ {saldo_anterior:.2f}")
    col2.metric("Entradas", f"R$ {entradas:.2f}")
    col3.metric("Saídas", f"R$ {saidas:.2f}")
    col4.metric("Saldo final", f"R$ {saldo_final:.2f}")

    st.divider()

    st.dataframe(df, use_container_width=True)

    # -------- PDF --------
    if st.button("Gerar Relatório PDF"):
        pdf = gerar_pdf(
            df,
            inicio_mes.strftime("%m/%Y"),
            saldo_anterior,
            entradas,
            saidas,
            saldo_final
        )

        st.download_button(
            "Baixar PDF",
            data=pdf,
            file_name=f"relatorio_{inicio_mes.strftime('%m_%Y')}.pdf",
            mime="application/pdf"
        )
