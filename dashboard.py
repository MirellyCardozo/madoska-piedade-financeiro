import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime
import pytz

from database import executar

# Fuso horário Brasil
TZ = pytz.timezone("America/Sao_Paulo")

# ======================
# BUSCAR DADOS
# ======================
def carregar_gastos():
    sql = """
    SELECT
        data,
        categoria,
        valor
    FROM registros
    WHERE tipo = 'Débito'
    """
    result = executar(sql).fetchall()

    if not result:
        return pd.DataFrame(columns=["data", "categoria", "valor"])

    df = pd.DataFrame(result, columns=["data", "categoria", "valor"])
    df["data"] = pd.to_datetime(df["data"])
    df["valor"] = df["valor"].astype(float)

    return df

# ======================
# GERAR PDF
# ======================
def gerar_pdf(df, mes, ano, usuario):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Relatório Financeiro Mensal", ln=True)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Usuário: {usuario}", ln=True)
    pdf.cell(0, 10, f"Mês/Ano: {mes}/{ano}", ln=True)
    pdf.cell(0, 10, f"Gerado em: {datetime.now(TZ).strftime('%d/%m/%Y %H:%M:%S')}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(80, 10, "Categoria")
    pdf.cell(40, 10, "Total (R$)")
    pdf.ln()

    resumo = df.groupby("categoria")["valor"].sum()

    pdf.set_font("Arial", "", 12)
    for cat, total in resumo.items():
        pdf.cell(80, 10, str(cat))
        pdf.cell(40, 10, f"{total:.2f}")
        pdf.ln()

    file_name = f"relatorio_{mes}_{ano}.pdf"
    pdf.output(file_name)

    return file_name

# ======================
# TELA DASHBOARD
# ======================
def tela_dashboard(usuario):
    st.title("📊 Dashboard Financeiro")

    df = carregar_gastos()

    if df.empty:
        st.info("Nenhum gasto registrado ainda.")
        return

    # ======================
    # FILTRO MÊS / ANO
    # ======================
    col1, col2 = st.columns(2)

    with col1:
        mes = st.selectbox("Mês", list(range(1, 13)), index=datetime.now().month - 1)

    with col2:
        ano = st.selectbox("Ano", sorted(df["data"].dt.year.unique(), reverse=True))

    df_filtrado = df[
        (df["data"].dt.month == mes) &
        (df["data"].dt.year == ano)
    ]

    if df_filtrado.empty:
        st.warning("Sem dados para este mês.")
        return

    # ======================
    # RESUMO
    # ======================
    total = df_filtrado["valor"].sum()
    st.metric("💰 Total de Gastos no Mês", f"R$ {total:.2f}")

    # ======================
    # GRÁFICO
    # ======================
    resumo = df_filtrado.groupby("categoria")["valor"].sum()

    fig, ax = plt.subplots()
    resumo.plot(kind="bar", ax=ax)
    ax.set_title("Gastos por Categoria")
    ax.set_ylabel("Valor (R$)")
    ax.set_xlabel("Categoria")

    st.pyplot(fig)

    # ======================
    # TABELA
    # ======================
    st.subheader("📋 Lançamentos do Mês")
    st.dataframe(df_filtrado.sort_values("data", ascending=False))

    # ======================
    # PDF
    # ======================
    if st.button("📄 Exportar Relatório em PDF"):
        arquivo = gerar_pdf(df_filtrado, mes, ano, usuario)

        with open(arquivo, "rb") as f:
            st.download_button(
                label="⬇️ Baixar PDF",
                data=f,
                file_name=arquivo,
                mime="application/pdf"
            )
