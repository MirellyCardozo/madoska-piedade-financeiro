import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime
from database import executar

# ==========================
# GERAR PDF
# ==========================
def gerar_pdf(df, mes, ano, total_mes):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Relatório Financeiro - Madoska Piedade", ln=True)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Mês/Ano: {mes}/{ano}", ln=True)
    pdf.cell(0, 8, f"Total do mês: R$ {total_mes:.2f}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 10)
    pdf.cell(30, 8, "Data", 1)
    pdf.cell(25, 8, "Tipo", 1)
    pdf.cell(40, 8, "Categoria", 1)
    pdf.cell(65, 8, "Descrição", 1)
    pdf.cell(25, 8, "Valor", 1, ln=True)

    pdf.set_font("Arial", "", 9)

    for _, row in df.iterrows():
        pdf.cell(30, 8, row["data"].strftime("%d/%m/%Y"), 1)
        pdf.cell(25, 8, row["tipo"], 1)
        pdf.cell(40, 8, row["categoria"], 1)
        pdf.cell(65, 8, str(row["descricao"])[:40], 1)
        pdf.cell(25, 8, f"R$ {float(row['valor']):.2f}", 1, ln=True)

    # fpdf2 retorna bytes direto
    return pdf.output(dest="S")


# ==========================
# DASHBOARD
# ==========================
def tela_dashboard(user):
    st.title("📊 Dashboard Financeiro")

    dados = executar(
        """
        SELECT data, tipo, categoria, descricao, valor
        FROM registros
        ORDER BY id ASC
        """,
        fetchall=True
    )

    if not dados:
        st.info("Nenhum lançamento encontrado")
        return

    df = pd.DataFrame(dados)

    # Datas em formato BR
    df["data"] = pd.to_datetime(df["data"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["data"])

    df["mes"] = df["data"].dt.month
    df["ano"] = df["data"].dt.year

    col1, col2 = st.columns(2)

    with col1:
        mes = st.selectbox("Mês", sorted(df["mes"].unique()))

    with col2:
        ano = st.selectbox("Ano", sorted(df["ano"].unique()))

    df_filtro = df[(df["mes"] == mes) & (df["ano"] == ano)]

    if df_filtro.empty:
        st.warning("Sem registros para esse período")
        return

    # ==========================
    # TOTAIS
    # ==========================
    total_entradas = df_filtro[df_filtro["tipo"] == "Entrada"]["valor"].sum()
    total_saidas = df_filtro[df_filtro["tipo"] == "Saída"]["valor"].sum()
    saldo = total_entradas - total_saidas

    colA, colB, colC = st.columns(3)
    colA.metric("💵 Entradas", f"R$ {total_entradas:.2f}")
    colB.metric("💸 Saídas", f"R$ {total_saidas:.2f}")
    colC.metric("📊 Saldo", f"R$ {saldo:.2f}")

    # ==========================
    # GRÁFICO POR CATEGORIA (SÓ SAÍDAS)
    # ==========================
    st.subheader("📊 Gastos por categoria")

    gastos = df_filtro[df_filtro["tipo"] == "Saída"]
    resumo = gastos.groupby("categoria")["valor"].sum()

    fig, ax = plt.subplots()
    resumo.plot(kind="bar", ax=ax)
    ax.set_ylabel("Valor (R$)")
    ax.set_xlabel("Categoria")
    ax.set_title("Distribuição de gastos")
    plt.xticks(rotation=45)

    st.pyplot(fig)

    # ==========================
    # EXPORTAR PDF
    # ==========================
    st.subheader("📄 Exportar relatório mensal")

    pdf_bytes = gerar_pdf(df_filtro, mes, ano, saldo)

    st.download_button(
        "📥 Baixar PDF mensal",
        data=pdf_bytes,
        file_name=f"relatorio_{mes}_{ano}.pdf",
        mime="application/pdf"
    )
