import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import text
from database import engine
from datetime import datetime
from fpdf import FPDF


def gerar_pdf(df, mes):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"Relatório Financeiro - {mes}", ln=True)

    pdf.set_font("Arial", "", 10)
    pdf.ln(5)

    for _, row in df.iterrows():
        linha = f"{row['data']} | {row['tipo']} | {row['descricao']} | {row['categoria']} | R$ {row['valor']}"
        pdf.multi_cell(0, 6, linha)

    caminho = f"/tmp/relatorio_{mes}.pdf"
    pdf.output(caminho)

    return caminho


def tela_dashboard(usuario=None):
    st.title("📊 Dashboard Financeiro")

    mes = st.selectbox(
        "Selecione o mês",
        [f"{i:02d}/{datetime.now().year}" for i in range(1, 13)]
    )

    mes_num, ano = mes.split("/")
    mes_num = int(mes_num)

    with engine.begin() as conn:
        dados = conn.execute(
            text("""
                SELECT data, tipo, descricao, categoria, valor
                FROM registros
            """)
        ).fetchall()

    if not dados:
        st.info("Nenhum gasto registrado ainda.")
        return

    df = pd.DataFrame(dados, columns=["data", "tipo", "descricao", "categoria", "valor"])
    df["data"] = pd.to_datetime(df["data"], errors="coerce")

    df_mes = df[
        (df["data"].dt.month == mes_num) &
        (df["data"].dt.year == int(ano))
    ]

    if df_mes.empty:
        st.warning("Sem registros para este mês.")
        return

    st.subheader("📈 Gastos por Categoria")

    resumo = df_mes.groupby("categoria")["valor"].sum()

    fig, ax = plt.subplots()
    resumo.plot(kind="bar", ax=ax)
    ax.set_ylabel("Valor (R$)")
    ax.set_xlabel("Categoria")
    ax.set_title("Total por Categoria")

    st.pyplot(fig)

    st.divider()
    st.subheader("📄 Exportar Relatório")

    if st.button("Gerar PDF"):
        caminho = gerar_pdf(df_mes, mes)
        with open(caminho, "rb") as f:
            st.download_button(
                "⬇️ Baixar relatório em PDF",
                f,
                file_name=f"relatorio_{mes}.pdf",
                mime="application/pdf"
            )
