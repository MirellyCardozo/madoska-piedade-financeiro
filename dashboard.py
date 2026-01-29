import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from database import executar
from datetime import datetime

def carregar_lancamentos(user_id):
    return executar("""
        SELECT data, descricao, categoria, valor, tipo
        FROM lancamentos
        WHERE user_id = :u
        ORDER BY data DESC
    """, {"u": user_id}, fetchall=True)

def gerar_pdf(df, entradas, saidas, saldo):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Relatório Financeiro - Madoska", ln=True)

    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, f"Entradas: R$ {entradas:.2f}", ln=True)
    pdf.cell(0, 10, f"Saídas: R$ {saidas:.2f}", ln=True)
    pdf.cell(0, 10, f"Saldo: R$ {saldo:.2f}", ln=True)

    pdf.ln(5)

    for _, row in df.iterrows():
        linha = f"{row['Data']} | {row['Categoria']} | {row['Tipo']} | R$ {row['Valor']}"
        pdf.multi_cell(0, 8, linha)

    return pdf.output(dest="S").encode("latin-1")

def tela_dashboard(user):
    st.title("📊 Dashboard Financeiro")

    rows = carregar_lancamentos(user["id"])

    if not rows:
        st.info("Nenhum dado financeiro ainda")
        return

    df = pd.DataFrame(rows, columns=[
        "Data", "Descrição", "Categoria", "Valor", "Tipo"
    ])

    df["Valor"] = pd.to_numeric(df["Valor"])

    entradas = df[df["Tipo"] == "Entrada"]["Valor"].sum()
    saidas = df[df["Tipo"] == "Saída"]["Valor"].sum()
    saldo = entradas - saidas

    col1, col2, col3 = st.columns(3)
    col1.metric("Entradas", f"R$ {entradas:.2f}")
    col2.metric("Saídas", f"R$ {saidas:.2f}")
    col3.metric("Saldo", f"R$ {saldo:.2f}")

    st.subheader("📈 Gastos por Categoria")
    resumo = df[df["Tipo"] == "Saída"].groupby("Categoria")["Valor"].sum()

    if not resumo.empty:
        fig, ax = plt.subplots()
        resumo.plot(kind="bar", ax=ax)
        st.pyplot(fig)

    st.subheader("📄 Exportar relatório")

    pdf_bytes = gerar_pdf(df, entradas, saidas, saldo)

    st.download_button(
        label="Baixar relatório em PDF",
        data=pdf_bytes,
        file_name=f"relatorio_{datetime.now().date()}.pdf",
        mime="application/pdf"
    )
