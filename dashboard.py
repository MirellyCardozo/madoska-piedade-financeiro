import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime
import pytz

from database import executar

# ==========================
# CONFIG
# ==========================
TZ_BR = pytz.timezone("America/Sao_Paulo")

# ==========================
# PDF EXPORT
# ==========================
def gerar_pdf(df, mes, ano, total):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Relatório Financeiro Mensal", ln=True, align="C")

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Mês/Ano: {mes}/{ano}", ln=True)
    pdf.cell(0, 8, f"Gerado em: {datetime.now(TZ_BR).strftime('%d/%m/%Y %H:%M')}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 11)
    pdf.cell(35, 8, "Data", 1)
    pdf.cell(40, 8, "Categoria", 1)
    pdf.cell(60, 8, "Descrição", 1)
    pdf.cell(25, 8, "Valor (R$)", 1)
    pdf.ln()

    pdf.set_font("Arial", "", 10)
    for _, row in df.iterrows():
        pdf.cell(35, 8, str(row["Data"]), 1)
        pdf.cell(40, 8, str(row["Categoria"]), 1)
        pdf.cell(60, 8, str(row["Descricao"])[:30], 1)
        pdf.cell(25, 8, f"{row['Valor']:.2f}", 1)
        pdf.ln()

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"TOTAL DO MÊS: R$ {total:.2f}", ln=True)

    return pdf.output(dest="S").encode("latin-1")


# ==========================
# DASHBOARD PRINCIPAL
# ==========================
def tela_dashboard(usuario=None):
    st.title("📊 Dashboard Financeiro")

    # ==========================
    # BUSCAR DADOS
    # ==========================
    rows = executar(
        """
        SELECT data, categoria, descricao, valor
        FROM registros
        ORDER BY data ASC
        """,
        fetchall=True
    )

    if not rows:
        st.info("Nenhum gasto registrado ainda.")
        return

    df = pd.DataFrame(rows, columns=["Data", "Categoria", "Descricao", "Valor"])

    # ==========================
    # TRATAR DATAS (BR)
    # ==========================
    df["Data"] = pd.to_datetime(df["Data"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["Data"])

    df["Mes"] = df["Data"].dt.month
    df["Ano"] = df["Data"].dt.year

    # ==========================
    # FILTRO MENSAL
    # ==========================
    col1, col2 = st.columns(2)

    with col1:
        mes = st.selectbox(
            "Mês",
            sorted(df["Mes"].unique()),
            format_func=lambda x: datetime(1900, x, 1).strftime("%B").capitalize()
        )

    with col2:
        ano = st.selectbox("Ano", sorted(df["Ano"].unique()))

    df_filtro = df[(df["Mes"] == mes) & (df["Ano"] == ano)]

    if df_filtro.empty:
        st.warning("Nenhum registro para esse mês.")
        return

    # ==========================
    # TOTAIS
    # ==========================
    total_mes = df_filtro["Valor"].sum()

    st.metric("💰 Total do mês", f"R$ {total_mes:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    # ==========================
    # TABELA
    # ==========================
    st.subheader("📋 Registros do mês")
    st.dataframe(
        df_filtro[["Data", "Categoria", "Descricao", "Valor"]]
        .sort_values("Data"),
        use_container_width=True
    )

    # ==========================
    # GRÁFICO POR CATEGORIA
    # ==========================
    st.subheader("📊 Gastos por categoria")

    cat_group = df_filtro.groupby("Categoria")["Valor"].sum().reset_index()

    fig, ax = plt.subplots()
    ax.bar(cat_group["Categoria"], cat_group["Valor"])
    ax.set_ylabel("Valor (R$)")
    ax.set_xlabel("Categoria")
    ax.set_title("Distribuição de gastos por categoria")
    plt.xticks(rotation=45)

    st.pyplot(fig)

    # ==========================
    # EXPORTAR PDF
    # ==========================
    st.subheader("📄 Exportar relatório")

    pdf_bytes = gerar_pdf(df_filtro, mes, ano, total_mes)

    st.download_button(
        "📥 Baixar PDF mensal",
        data=pdf_bytes,
        file_name=f"relatorio_{mes}_{ano}.pdf",
        mime="application/pdf"
    )
