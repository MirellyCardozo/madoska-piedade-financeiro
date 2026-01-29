import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from database import executar
from datetime import datetime
import io

def gerar_pdf(df, entradas, saidas, saldo):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Relatório Financeiro - Madoska Piedade", ln=True)

    pdf.set_font("Arial", size=10)
    pdf.cell(0, 8, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)

    pdf.ln(5)
    pdf.cell(0, 8, f"Entradas: R$ {entradas:.2f}", ln=True)
    pdf.cell(0, 8, f"Saídas: R$ {saidas:.2f}", ln=True)
    pdf.cell(0, 8, f"Saldo: R$ {saldo:.2f}", ln=True)

    pdf.ln(10)

    for _, row in df.iterrows():
        linha = f"{row['Data']} | {row['Descrição']} | {row['Categoria']} | R$ {row['Valor']:.2f}"
        pdf.multi_cell(0, 8, linha)

    buffer = io.BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()


def tela_dashboard(user):
    st.title("📊 Dashboard Financeiro")

    rows = executar(
        """
        SELECT data, descricao, categoria, tipo, valor
        FROM lancamentos
        WHERE usuario_id = :uid
        ORDER BY data DESC
        """,
        {"uid": user["id"]},
        fetchall=True
    )

    if not rows:
        st.info("Nenhum lançamento para exibir")
        return

    df = pd.DataFrame(
        rows,
        columns=["Data", "Descrição", "Categoria", "Tipo", "Valor"]
    )

    entradas = df[df["Tipo"] == "Entrada"]["Valor"].sum()
    saidas = df[df["Tipo"] == "Saída"]["Valor"].sum()
    saldo = entradas - saidas

    c1, c2, c3 = st.columns(3)
    c1.metric("Entradas", f"R$ {entradas:.2f}")
    c2.metric("Saídas", f"R$ {saidas:.2f}")
    c3.metric("Saldo", f"R$ {saldo:.2f}")

    st.divider()

    st.subheader("📊 Gastos por categoria")

    gastos = (
        df[df["Tipo"] == "Saída"]
        .groupby("Categoria")["Valor"]
        .sum()
    )

    if not gastos.empty:
        fig, ax = plt.subplots()
        gastos.plot(kind="bar", ax=ax)
        st.pyplot(fig)
    else:
        st.info("Sem gastos para exibir gráfico")

    st.divider()
    st.subheader("📄 Exportar relatório")

    if st.button("Gerar PDF"):
        pdf_bytes = gerar_pdf(df, entradas, saidas, saldo)

        st.download_button(
            "📥 Baixar relatório em PDF",
            data=pdf_bytes,
            file_name="relatorio_financeiro.pdf",
            mime="application/pdf"
        )
