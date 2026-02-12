import streamlit as st
import pandas as pd
from sqlalchemy import text
from fpdf import FPDF
from io import BytesIO

from database import engine
from backup import gerar_backup


# =========================
# PDF
# =========================
class RelatorioPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Relatório Financeiro", ln=True, align="C")
        self.ln(5)


def gerar_pdf(df, resumo):
    pdf = RelatorioPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=10)

    # ----- Resumo -----
    pdf.cell(0, 10, "Resumo por categoria:", ln=True)
    pdf.ln(3)

    for _, row in resumo.iterrows():
        texto = f"{row['categoria']}: R$ {row['total']:.2f}"
        pdf.cell(0, 8, texto, ln=True)

    pdf.ln(5)
    pdf.cell(0, 10, "Lançamentos:", ln=True)
    pdf.ln(3)

    largura_util = pdf.w - pdf.l_margin - pdf.r_margin

    for _, row in df.iterrows():
        linha = (
            f"{row['data']} | "
            f"{row['descricao']} | "
            f"{row['categoria']} | "
            f"R$ {row['valor']:.2f}"
        )

        # 🔧 FIX DEFINITIVO DO ERRO
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(largura_util, 7, linha)
        pdf.ln(1)

    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)

    return buffer.getvalue()


# =========================
# DASHBOARD
# =========================
def tela_dashboard(usuario):
    st.title("📊 Dashboard Financeiro")

    col1, col2 = st.columns(2)
    mes = col1.selectbox("Mês", list(range(1, 13)))
    ano = col2.selectbox("Ano", list(range(2024, 2031)))

    # -------------------------
    # BUSCA DADOS
    # -------------------------
    query = """
        SELECT id, data, descricao, categoria, tipo, valor
        FROM lancamentos
        WHERE usuario_id = :uid
          AND EXTRACT(MONTH FROM data) = :mes
          AND EXTRACT(YEAR FROM data) = :ano
        ORDER BY data DESC
    """

    with engine.connect() as conn:
        df = pd.read_sql(
            text(query),
            conn,
            params={"uid": usuario["id"], "mes": mes, "ano": ano}
        )

    if df.empty:
        st.info("Nenhum lançamento encontrado.")
        return

    # -------------------------
    # TABELA
    # -------------------------
    st.subheader("Lançamentos")
    st.dataframe(df, use_container_width=True)

    # -------------------------
    # RESUMO
    # -------------------------
    resumo = (
        df.groupby("categoria", as_index=False)["valor"]
        .sum()
        .rename(columns={"valor": "total"})
    )

    st.subheader("Resumo por categoria")
    st.dataframe(resumo, use_container_width=True)

    # -------------------------
    # PDF
    # -------------------------
    st.subheader("📄 Exportar relatório")

    if st.button("Gerar PDF"):
        pdf_bytes = gerar_pdf(df, resumo)

        st.download_button(
            label="⬇️ Baixar relatório em PDF",
            data=pdf_bytes,
            file_name=f"relatorio_{mes}_{ano}.pdf",
            mime="application/pdf"
        )

    # -------------------------
    # BACKUP
    # -------------------------
    st.divider()
    st.subheader("💾 Backup do banco")

    if st.button("Gerar backup agora"):
        caminho = gerar_backup()
        st.success(f"Backup gerado com sucesso: {caminho}")
