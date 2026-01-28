import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from database import executar
from datetime import datetime

def tela_dashboard():
    st.title("📊 Dashboard Financeiro")

    dados = executar(
        "SELECT data, categoria, valor FROM registros ORDER BY data",
        fetchall=True
    )

    if not dados:
        st.info("Nenhum lançamento registrado.")
        return

    df = pd.DataFrame(dados, columns=["Data", "Categoria", "Valor"])
    df["Data"] = pd.to_datetime(df["Data"])
    df["Mes"] = df["Data"].dt.to_period("M")

    resumo = df.groupby("Mes")["Valor"].sum()

    st.subheader("Resumo mensal")
    st.dataframe(resumo)

    st.subheader("Gráfico")
    fig, ax = plt.subplots()
    resumo.plot(kind="bar", ax=ax)
    st.pyplot(fig)

    if st.button("📄 Exportar PDF Mensal"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, "Relatório Financeiro Mensal", ln=True)

        for mes, total in resumo.items():
            pdf.cell(200, 10, f"{mes}: R$ {float(total):.2f}", ln=True)

        nome_arquivo = f"relatorio_{datetime.now().strftime('%Y_%m')}.pdf"
        pdf.output(nome_arquivo)

        with open(nome_arquivo, "rb") as f:
            st.download_button(
                "Baixar PDF",
                f,
                file_name=nome_arquivo
            )
