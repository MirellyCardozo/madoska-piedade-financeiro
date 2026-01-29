import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime
from database import executar

# ==========================
# PDF
# ==========================
def gerar_pdf(df, mes, ano, total):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Relatório Financeiro - Madoska Piedade", ln=True)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Mês/Ano: {mes}/{ano}", ln=True)
    pdf.cell(0, 10, f"Total do mês: R$ {total:.2f}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 11)
    pdf.cell(40, 8, "Data")
    pdf.cell(60, 8, "Descrição")
    pdf.cell(40, 8, "Categoria")
    pdf.cell(40, 8, "Valor", ln=True)

    pdf.set_font("Arial", "", 10)
    for _, row in df.iterrows():
        pdf.cell(40, 8, str(row["data"]))
        pdf.cell(60, 8, str(row["descricao"])[:25])
        pdf.cell(40, 8, str(row["categoria"]))
        pdf.cell(40, 8, f'R$ {float(row["valor"]):.2f}', ln=True)

    return pdf.output(dest="S").encode("latin-1")

# ==========================
# DASHBOARD
# ==========================
def tela_dashboard(user):
    st.title("📊 Dashboard Financeiro")

    # ==========================
    # BUSCAR DADOS
    # ==========================
    registros = executar(
        """
        SELECT data, descricao, categoria, valor
        FROM lancamentos
        ORDER BY data DESC
        """,
        fetchall=True
    )

    if not registros:
        st.info("Ainda não existem lançamentos financeiros cadastrados.")
        return

    df = pd.DataFrame(registros, columns=["data", "descricao", "categoria", "valor"])

    # ==========================
    # LIMPEZA DE DADOS
    # ==========================
    df["data"] = pd.to_datetime(df["data"], errors="coerce", dayfirst=True)
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")

    df = df.dropna(subset=["data", "valor"])

    # ==========================
    # FILTROS
    # ==========================
    mes = st.selectbox("Mês", list(range(1, 13)), index=datetime.now().month - 1)
    ano = st.selectbox("Ano", sorted(df["data"].dt.year.unique(), reverse=True))

    df_filtro = df[
        (df["data"].dt.month == mes) &
        (df["data"].dt.year == ano)
    ]

    if df_filtro.empty:
        st.warning("Não existem lançamentos para este mês.")
        return

    # ==========================
    # TOTAIS
    # ==========================
    entradas = df_filtro[df_filtro["valor"] > 0]["valor"].sum()
    saidas = df_filtro[df_filtro["valor"] < 0]["valor"].sum()
    saldo = entradas + saidas

    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Entradas", f"R$ {entradas:.2f}")
    c2.metric("💸 Saídas", f"R$ {abs(saidas):.2f}")
    c3.metric("📊 Saldo", f"R$ {saldo:.2f}")

    # ==========================
    # GRÁFICO POR CATEGORIA
    # ==========================
    st.subheader("📌 Gastos por categoria")

    resumo = (
        df_filtro[df_filtro["valor"] < 0]
        .groupby("categoria")["valor"]
        .sum()
        .abs()
        .reset_index()
    )

    if resumo.empty:
        st.info("Ainda não há gastos para gerar gráfico neste mês.")
    else:
        fig, ax = plt.subplots()
        ax.bar(resumo["categoria"], resumo["valor"])
        ax.set_ylabel("Valor (R$)")
        ax.set_xlabel("Categoria")
        ax.set_title("Gastos por Categoria")
        plt.xticks(rotation=45)

        st.pyplot(fig)

    # ==========================
    # TABELA
    # ==========================
    st.subheader("📄 Lançamentos do mês")
    st.dataframe(df_filtro.sort_values("data", ascending=False), use_container_width=True)

    # ==========================
    # EXPORTAR PDF
    # ==========================
    st.subheader("📥 Exportar relatório")

    if st.button("Gerar PDF"):
        pdf_bytes = gerar_pdf(df_filtro, mes, ano, saldo)

        st.download_button(
            label="Baixar relatório em PDF",
            data=pdf_bytes,
            file_name=f"relatorio_{mes}_{ano}.pdf",
            mime="application/pdf"
        )
