import streamlit as st
import pandas as pd
from sqlalchemy import text
from fpdf import FPDF
from io import BytesIO
from datetime import date

from database import engine
from backup import gerar_backup


# =====================================================
# PDF
# =====================================================
class RelatorioPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Relatório Financeiro - Madoska Piedade", ln=True, align="C")
        self.ln(5)


def gerar_pdf(df, saldo_anterior, entradas, saidas, saldo_final, mes, ano):
    pdf = RelatorioPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=10)

    pdf.cell(0, 8, f"Período: {mes:02d}/{ano}", ln=True)
    pdf.ln(2)

    pdf.cell(0, 8, f"Saldo anterior: R$ {saldo_anterior:.2f}", ln=True)
    pdf.cell(0, 8, f"Total de entradas: R$ {entradas:.2f}", ln=True)
    pdf.cell(0, 8, f"Total de saídas: R$ {saidas:.2f}", ln=True)
    pdf.cell(0, 8, f"Saldo final: R$ {saldo_final:.2f}", ln=True)

    pdf.ln(6)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 8, "Lançamentos do mês:", ln=True)
    pdf.set_font("Arial", size=9)

    largura = pdf.w - pdf.l_margin - pdf.r_margin

    for _, row in df.iterrows():
        linha = (
            f"{row['data']} | "
            f"{row['tipo'].upper()} | "
            f"{row['descricao']} | "
            f"{row['categoria']} | "
            f"R$ {float(row['valor']):.2f}"
        )
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(largura, 6, linha)

    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer.getvalue()


# =====================================================
# DASHBOARD
# =====================================================
def tela_dashboard(usuario):
    st.title("📊 Dashboard Financeiro")

    col1, col2 = st.columns(2)
    mes = col1.selectbox("Mês", list(range(1, 13)), index=date.today().month - 1)
    ano = col2.selectbox("Ano", list(range(2023, date.today().year + 1)))

    # -------------------------------------------------
    # SALDO ANTERIOR (tudo antes do mês selecionado)
    # -------------------------------------------------
    query_saldo_anterior = text("""
        SELECT
            COALESCE(SUM(
                CASE
                    WHEN tipo = 'entrada' THEN valor
                    ELSE -valor
                END
            ), 0)
        FROM lancamentos
        WHERE usuario_id = :uid
          AND data < DATE(:ano || '-' || :mes || '-01')
    """)

    with engine.connect() as conn:
        saldo_anterior = conn.execute(
            query_saldo_anterior,
            {"uid": usuario["id"], "mes": mes, "ano": ano}
        ).scalar()

    # -------------------------------------------------
    # LANÇAMENTOS DO MÊS
    # -------------------------------------------------
    query_mes = text("""
        SELECT
            data,
            descricao,
            categoria,
            tipo,
            valor
        FROM lancamentos
        WHERE usuario_id = :uid
          AND EXTRACT(MONTH FROM data) = :mes
          AND EXTRACT(YEAR FROM data) = :ano
        ORDER BY data
    """)

    with engine.connect() as conn:
        df = pd.read_sql(
            query_mes,
            conn,
            params={"uid": usuario["id"], "mes": mes, "ano": ano}
        )

    # -------------------------------------------------
    # CÁLCULOS (CORRIGIDOS DEFINITIVAMENTE)
    # -------------------------------------------------
    if df.empty:
        entradas = 0.0
        saidas = 0.0
    else:
        entradas = df.loc[df["tipo"] == "entrada", "valor"].sum()
        saidas = df.loc[df["tipo"] == "saida", "valor"].sum()

    saldo_anterior = float(saldo_anterior or 0)
    entradas = float(entradas or 0)
    saidas = float(saidas or 0)

    saldo_final = saldo_anterior + entradas - saidas

    # -------------------------------------------------
    # INDICADORES
    # -------------------------------------------------
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Saldo anterior", f"R$ {saldo_anterior:.2f}")
    c2.metric("Entradas", f"R$ {entradas:.2f}")
    c3.metric("Saídas", f"R$ {saidas:.2f}")
    c4.metric("Saldo final", f"R$ {saldo_final:.2f}")

    # -------------------------------------------------
    # TABELA
    # -------------------------------------------------
    st.subheader("Lançamentos do mês")

    if df.empty:
        st.info("Nenhum lançamento neste mês.")
    else:
        st.dataframe(df, use_container_width=True)

    # -------------------------------------------------
    # PDF
    # -------------------------------------------------
    st.subheader("📄 Relatório mensal")

    if not df.empty and st.button("Gerar PDF"):
        pdf = gerar_pdf(
            df,
            saldo_anterior,
            entradas,
            saidas,
            saldo_final,
            mes,
            ano
        )

        st.download_button(
            label="⬇️ Baixar PDF",
            data=pdf,
            file_name=f"relatorio_{mes:02d}_{ano}.pdf",
            mime="application/pdf"
        )

    # -------------------------------------------------
    # BACKUP
    # -------------------------------------------------
    st.divider()
    if st.button("💾 Gerar backup"):
        caminho = gerar_backup()
        st.success(f"Backup gerado com sucesso: {caminho}")
