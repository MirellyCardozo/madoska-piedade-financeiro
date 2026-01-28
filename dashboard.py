import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime

from database import executar

# ==========================
# GERAR PDF
# ==========================
def gerar_pdf(df, mes, ano, total_mes):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Relatório Financeiro - Madoska Piedade", ln=True)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Mês/Ano: {mes}/{ano}", ln=True)
    pdf.cell(0, 8, f"Total do mês: R$ {total_mes:.2f}", ln=True)

    pdf.ln(5)

    pdf.set_font("Arial", "B", 10)
    pdf.cell(30, 8, "Data", 1)
    pdf.cell(30, 8, "Tipo", 1)
    pdf.cell(40, 8, "Categoria", 1)
    pdf.cell(60, 8, "Descrição", 1)
    pdf.cell(25, 8, "Valor", 1, ln=True)

    pdf.set_font("Arial", "", 9)

    for _, row in df.iterrows():
        pdf.cell(30, 8, str(row["data"]), 1)
        pdf.cell(30, 8, str(row["tipo"]), 1)
        pdf.cell(40, 8, str(row["categoria"]), 1)
        pdf.cell(60, 8, str(row["descricao"])[:30], 1)
        pdf.cell(25, 8, f'R$ {float(row["valor"]):.2f}', 1, ln=True)

    # FPDF2 retorna BYTES direto
    return pdf.output(dest="S")


# ==========================
# DASHBOARD
# ==========================
def tela_dashboard(user):
    st.title("📊 Dashboard Financeiro")

    registros = executar(
        """
        SELECT data, tipo, categoria, descricao, valor
        FROM registros
        ORDER BY data
        """,
        fetchall=True
    )

    if not registros:
        st.info("Nenhum lançamento encontrado")
        return

    df = pd.DataFrame(
        registros,
        columns=["data", "tipo", "categoria", "descricao", "valor"]
    )

    # Corrige problema de datas em formato brasileiro
    df["data"] = pd.to_datetime(df["data"], dayfirst=True, errors="coerce")

    df = df.dropna(subset=["data"])

    df["mes"] = df["data"].dt.month
    df["ano"] = df["data"].dt.year

    col1, col2 = st.columns(2)

    with col1:
        mes = st.selectbox("Mês", list(range(1, 13)), index=datetime.now().month - 1)

    with col2:
        ano = st.selectbox("Ano", sorted(df["ano"].unique()), index=len(df["ano"].unique()) - 1)

    df_filtro = df[(df["mes"] == mes) & (df["ano"] == ano)]

    if df_filtro.empty:
        st.warning("Sem registros para este mês")
        return

    total_mes = df_filtro["valor"].sum()

    st.metric("💰 Total do mês", f"R$ {total_mes:.2f}")

    st.subheader("📊 Total por categoria")

    resumo = df_filtro.groupby("categoria")["valor"].sum()

    fig, ax = plt.subplots()
    resumo.plot(kind="bar", ax=ax)
    ax.set_ylabel("Valor (R$)")
    ax.set_xlabel("Categoria")

    st.pyplot(fig)

    st.divider()
    st.subheader("📄 Exportar relatório")

    pdf_bytes = gerar_pdf(df_filtro, mes, ano, total_mes)

    st.download_button(
        "📥 Baixar PDF",
        data=pdf_bytes,
        file_name=f"relatorio_{mes}_{ano}.pdf",
        mime="application/pdf"
    )
