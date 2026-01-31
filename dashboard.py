import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
from database import executar


# ==========================
# GERAR PDF
# ==========================
def gerar_pdf(df, mes, ano, saldo):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # TÍTULO
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Relatório Financeiro - Madoska Piedade", ln=True, align="C")

    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 8, f"Mês: {mes} / Ano: {ano}", ln=True)
    pdf.cell(0, 8, f"Saldo atual: R$ {saldo:.2f}", ln=True)

    pdf.ln(5)

    # TABELA
    pdf.set_font("Arial", "B", 9)
    headers = ["Data", "Descrição", "Categoria", "Tipo", "Valor"]
    col_widths = [30, 60, 35, 20, 25]

    for h, w in zip(headers, col_widths):
        pdf.cell(w, 8, h, border=1)
    pdf.ln()

    pdf.set_font("Arial", "", 8)
    for _, row in df.iterrows():
        pdf.cell(col_widths[0], 8, str(row["data"]), border=1)
        pdf.cell(col_widths[1], 8, str(row["descricao"])[:30], border=1)
        pdf.cell(col_widths[2], 8, str(row["categoria"]), border=1)
        pdf.cell(col_widths[3], 8, str(row["tipo"]), border=1)
        pdf.cell(col_widths[4], 8, f'R$ {float(row["valor"]):.2f}', border=1)
        pdf.ln()

    # =======================
    # RESUMO POR CATEGORIA
    # =======================
    pdf.ln(10)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 10, "Resumo de Gastos por Categoria", ln=True)

    gastos = df[df["tipo"] == "Saída"]

    if not gastos.empty:
        resumo = gastos.groupby("categoria")["valor"].sum().reset_index()

        pdf.set_font("Arial", "B", 9)
        pdf.cell(80, 8, "Categoria", border=1)
        pdf.cell(40, 8, "Total (R$)", border=1)
        pdf.ln()

        pdf.set_font("Arial", "", 9)
        total_geral = 0

        for _, row in resumo.iterrows():
            pdf.cell(80, 8, str(row["categoria"]), border=1)
            pdf.cell(40, 8, f'R$ {row["valor"]:.2f}', border=1)
            pdf.ln()
            total_geral += row["valor"]

        pdf.ln(5)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(80, 8, "TOTAL GERAL", border=1)
        pdf.cell(40, 8, f"R$ {total_geral:.2f}", border=1)
    else:
        pdf.set_font("Arial", "", 9)
        pdf.cell(0, 8, "Nenhum gasto registrado.", ln=True)

    # Streamlit precisa de BYTES, não bytearray
    return bytes(pdf.output(dest="S"))


# ==========================
# DASHBOARD
# ==========================
def tela_dashboard(user):
    st.title("📊 Dashboard Financeiro")

    user_id = user["id"]

    # ==========================
    # FILTRO
    # ==========================
    col1, col2 = st.columns(2)

    with col1:
        mes = st.selectbox("Mês", list(range(1, 13)), index=datetime.now().month - 1)

    with col2:
        ano = st.selectbox(
            "Ano",
            list(range(2023, datetime.now().year + 2)),
            index=len(list(range(2023, datetime.now().year + 2))) - 2
        )

    # ==========================
    # QUERY CORRETA SQLALCHEMY
    # ==========================
    query = """
        SELECT data, descricao, categoria, tipo, valor
        FROM lancamentos
        WHERE usuario_id = :uid
          AND EXTRACT(MONTH FROM data) = :mes
          AND EXTRACT(YEAR FROM data) = :ano
        ORDER BY data DESC
    """

    rows = executar(
        query,
        {
            "uid": user_id,
            "mes": mes,
            "ano": ano
        },
        fetchall=True
    )

    df = pd.DataFrame(rows, columns=["data", "descricao", "categoria", "tipo", "valor"])

    # ==========================
    # CONVERSÕES
    # ==========================
    if not df.empty:
        df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0)
        df["data"] = pd.to_datetime(df["data"]).dt.date

    # ==========================
    # MÉTRICAS
    # ==========================
    entradas = df[df["tipo"] == "Entrada"]["valor"].sum() if not df.empty else 0
    saidas = df[df["tipo"] == "Saída"]["valor"].sum() if not df.empty else 0
    saldo = entradas - saidas

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Entradas", f"R$ {entradas:.2f}")
    col2.metric("💸 Saídas", f"R$ {saidas:.2f}")
    col3.metric("📊 Saldo", f"R$ {saldo:.2f}")

    st.divider()

    # ==========================
    # TABELA
    # ==========================
    st.subheader("📄 Lançamentos")

    if df.empty:
        st.info("Nenhum lançamento encontrado para este período.")
    else:
        st.dataframe(df, use_container_width=True)

    # ==========================
    # GRÁFICO
    # ==========================
    st.subheader("📊 Gastos por categoria")

    gastos = df[df["tipo"] == "Saída"]

    if not gastos.empty:
        resumo = gastos.groupby("categoria")["valor"].sum().reset_index()
        resumo = resumo.set_index("categoria")
        st.bar_chart(resumo)
    else:
        st.info("Nenhum gasto para exibir no gráfico.")

    st.divider()

    # ==========================
    # EXPORTAR PDF
    # ==========================
    st.subheader("📥 Exportar relatório")

    if not df.empty:
        if st.button("Gerar PDF"):
            pdf_bytes = gerar_pdf(df, mes, ano, saldo)

            st.download_button(
                label="📄 Baixar relatório em PDF",
                data=pdf_bytes,
                file_name=f"relatorio_{mes}_{ano}.pdf",
                mime="application/pdf"
            )
    else:
        st.info("Não há dados para gerar relatório.")
