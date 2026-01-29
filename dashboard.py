import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime
from database import executar

def gerar_pdf(df, mes, ano, total):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"Relatório Financeiro - {mes}/{ano}", ln=True)

    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 10, f"Total do mês: R$ {total:.2f}", ln=True)
    pdf.ln(5)

    for _, row in df.iterrows():
        linha = f"{row['data']} | {row['descricao']} | R$ {row['valor']:.2f}"
        pdf.cell(0, 8, linha, ln=True)

    return pdf.output(dest="S").encode("latin-1")

def tela_dashboard():
    st.title("📊 Dashboard Financeiro")

    dados = executar(
        """
        SELECT data, descricao, valor, categoria
        FROM lancamentos
        ORDER BY data
        """,
        fetchall=True
    )

    if not dados:
        st.info("Nenhum lançamento encontrado")
        return

    df = pd.DataFrame(dados)
    df["data"] = pd.to_datetime(df["data"], dayfirst=True)

    mes = st.selectbox("Mês", sorted(df["data"].dt.month.unique()))
    ano = st.selectbox("Ano", sorted(df["data"].dt.year.unique()))

    df_filtro = df[
        (df["data"].dt.month == mes) &
        (df["data"].dt.year == ano)
    ]

    total = df_filtro["valor"].sum()

    st.metric("Total do mês", f"R$ {total:.2f}")

    grafico = df_filtro.groupby("categoria")["valor"].sum()

    fig, ax = plt.subplots()
    grafico.plot(kind="bar", ax=ax)
    st.pyplot(fig)

    st.subheader("📄 Exportar relatório")
    if st.button("Gerar PDF"):
        pdf_bytes = gerar_pdf(df_filtro, mes, ano, total)
        st.download_button(
            "Baixar PDF",
            pdf_bytes,
            file_name=f"relatorio_{mes}_{ano}.pdf"
        )
