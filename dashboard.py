import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import pytz
from fpdf import FPDF

from database import executar

# ==========================
# CONFIG FUSO HORÁRIO
# ==========================
FUSO_BR = pytz.timezone("America/Sao_Paulo")


def agora_br():
    return datetime.now(FUSO_BR)


# ==========================
# BUSCA DADOS
# ==========================
def carregar_registros():
    result = executar("""
        SELECT data, descricao, categoria, pagamento, valor
        FROM registros
        ORDER BY data
    """).fetchall()

    return pd.DataFrame(result, columns=[
        "Data", "Descrição", "Categoria", "Pagamento", "Valor"
    ])


# ==========================
# GERAR PDF
# ==========================
def gerar_pdf(df, mes, ano):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"Relatório Financeiro - {mes}/{ano}", ln=True)

    pdf.set_font("Arial", size=10)
    pdf.ln(5)

    total = 0

    for _, row in df.iterrows():
        linha = f"{row['Data']} | {row['Categoria']} | {row['Descrição']} | R$ {row['Valor']:.2f}"
        pdf.multi_cell(0, 8, linha)
        total += float(row["Valor"])

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"TOTAL DO MÊS: R$ {total:.2f}", ln=True)

    nome_arquivo = f"relatorio_{mes}_{ano}.pdf"
    pdf.output(nome_arquivo)

    return nome_arquivo


# ==========================
# TELA DASHBOARD
# ==========================
def tela_dashboard(usuario):
    st.title("📊 Dashboard Financeiro - Madoska Piedade")

    agora = agora_br()
    st.caption(f"🕒 Horário atual: {agora.strftime('%d/%m/%Y %H:%M:%S')}")

    df = carregar_registros()

    if df.empty:
        st.warning("Nenhum dado encontrado")
        return

    df["Data"] = pd.to_datetime(df["Data"], dayfirst=True)

    # ==========================
    # FILTRO MÊS / ANO
    # ==========================
    col1, col2 = st.columns(2)

    with col1:
        mes = st.selectbox("Mês", list(range(1, 13)), index=agora.month - 1)

    with col2:
        ano = st.selectbox("Ano", sorted(df["Data"].dt.year.unique()), index=0)

    df_filtrado = df[
        (df["Data"].dt.month == mes) &
        (df["Data"].dt.year == ano)
    ]

    st.subheader("📈 Gastos por Categoria")

    if df_filtrado.empty:
        st.info("Nenhum dado para este período")
        return

    grafico = df_filtrado.groupby("Categoria")["Valor"].sum()

    fig, ax = plt.subplots()
    grafico.plot(kind="bar", ax=ax)
    ax.set_ylabel("Valor (R$)")
    ax.set_xlabel("Categoria")
    ax.set_title("Total por Categoria")

    st.pyplot(fig)

    # ==========================
    # TABELA
    # ==========================
    st.subheader("📋 Registros do Mês")
    st.dataframe(df_filtrado, use_container_width=True)

    # ==========================
    # EXPORTAR PDF
    # ==========================
    if st.button("📄 Exportar Relatório em PDF"):
        arquivo = gerar_pdf(df_filtrado, mes, ano)

        with open(arquivo, "rb") as f:
            st.download_button(
                "⬇️ Baixar PDF",
                f,
                file_name=arquivo,
                mime="application/pdf"
            )