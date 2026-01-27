import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime
import pytz

from database import executar

# ==========================
# HORA BR
# ==========================
def agora_br():
    tz = pytz.timezone("America/Sao_Paulo")
    return datetime.now(tz)

# ==========================
# BUSCAR GASTOS
# ==========================
def buscar_gastos():
    sql = """
    SELECT 
        data,
        categoria,
        descricao,
        valor
    FROM gastos
    ORDER BY data DESC
    """
    result = executar(sql).fetchall()

    return pd.DataFrame(result, columns=["Data", "Categoria", "Descrição", "Valor"])

# ==========================
# GERAR PDF
# ==========================
def gerar_pdf(df, mes, ano):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Relatório Financeiro - {mes}/{ano}", ln=True)

    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 10, f"Gerado em: {agora_br().strftime('%d/%m/%Y %H:%M:%S')}", ln=True)

    pdf.ln(5)

    total = 0

    for _, row in df.iterrows():
        linha = f"{row['Data']} | {row['Categoria']} | {row['Descrição']} | R$ {row['Valor']:.2f}"
        pdf.cell(0, 8, linha, ln=True)
        total += row["Valor"]

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"TOTAL DO MÊS: R$ {total:.2f}", ln=True)

    arquivo = f"relatorio_{mes}_{ano}.pdf"
    pdf.output(arquivo)

    return arquivo

# ==========================
# TELA DASHBOARD
# ==========================
def tela_dashboard(usuario):
    st.title("📊 Dashboard Financeiro")

    st.info(f"Usuário: {usuario}")
    st.caption(f"Hora BR: {agora_br().strftime('%d/%m/%Y %H:%M:%S')}")

    df = buscar_gastos()

    if df.empty:
        st.warning("Nenhum gasto registrado ainda.")
        return

    # =====================
    # FILTRO MÊS / ANO
    # =====================
    col1, col2 = st.columns(2)

    with col1:
        mes = st.selectbox("Mês", list(range(1, 13)), index=agora_br().month - 1)

    with col2:
        ano = st.selectbox("Ano", [agora_br().year - 1, agora_br().year, agora_br().year + 1])

    df["Data"] = pd.to_datetime(df["Data"])
    df_filtrado = df[
        (df["Data"].dt.month == mes) &
        (df["Data"].dt.year == ano)
    ]

    # =====================
    # TABELA
    # =====================
    st.subheader("📋 Lançamentos do mês")
    st.dataframe(df_filtrado, use_container_width=True)

    # =====================
    # GRÁFICO
    # =====================
    st.subheader("📈 Gastos por Categoria")

    resumo = df_filtrado.groupby("Categoria")["Valor"].sum()

    if not resumo.empty:
        fig, ax = plt.subplots()
        resumo.plot(kind="bar", ax=ax)
        ax.set_ylabel("Valor (R$)")
        ax.set_xlabel("Categoria")
        ax.set_title("Total por Categoria")

        st.pyplot(fig)
    else:
        st.info("Nenhum gasto neste mês.")

    # =====================
    # PDF
    # =====================
    st.subheader("📄 Exportar Relatório")

    if st.button("Gerar PDF do Mês"):
        arquivo = gerar_pdf(df_filtrado, mes, ano)
        with open(arquivo, "rb") as f:
            st.download_button(
                label="📥 Baixar PDF",
                data=f,
                file_name=arquivo,
                mime="application/pdf"
            )
