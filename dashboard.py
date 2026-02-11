import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from database import executar
from fpdf import FPDF
from io import BytesIO
from datetime import datetime

def gerar_pdf(df, resumo):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Relatório Financeiro", ln=True)

    pdf.set_font("Arial", size=10)
    pdf.ln(5)

    for _, row in resumo.iterrows():
        pdf.cell(0, 8, f"{row['categoria']}: R$ {row['valor']:.2f}", ln=True)

    pdf.ln(5)

    for _, row in df.iterrows():
        pdf.cell(0, 8, f"{row['data']} - {row['descricao']} - R$ {row['valor']}", ln=True)

    buffer = BytesIO()
    buffer.write(pdf.output(dest="S").encode("latin-1"))
    buffer.seek(0)
    return buffer

def tela_dashboard(user):
    st.header("📊 Dashboard Financeiro")

    rows = executar(
        "SELECT data, descricao, categoria, tipo, valor FROM lancamentos",
        fetchall=True
    )

    if not rows:
        st.info("Nenhum lançamento encontrado")
        return

    df = pd.DataFrame(rows, columns=["data", "descricao", "categoria", "tipo", "valor"])

    entradas = df[df["tipo"] == "Entrada"]["valor"].sum()
    saidas = df[df["tipo"] == "Saída"]["valor"].sum()
    saldo = entradas - saidas

    c1, c2, c3 = st.columns(3)
    c1.metric("Entradas", f"R$ {entradas:.2f}")
    c2.metric("Saídas", f"R$ {saidas:.2f}")
    c3.metric("Saldo", f"R$ {saldo:.2f}")

    resumo = df[df["tipo"] == "Saída"].groupby("categoria")["valor"].sum().reset_index()

    if not resumo.empty:
        fig, ax = plt.subplots()
        ax.bar(resumo["categoria"], resumo["valor"])
        plt.xticks(rotation=45)
        st.pyplot(fig)

    st.subheader("📄 Exportar relatório")
    if st.button("Gerar PDF"):
        pdf = gerar_pdf(df, resumo)
        st.download_button(
            "Baixar PDF",
            data=pdf,
            file_name="relatorio_financeiro.pdf",
            mime="application/pdf"
        )
