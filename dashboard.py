import streamlit as st
import pandas as pd
from sqlalchemy import text
from fpdf import FPDF
from datetime import datetime

from db import get_engine

# ==============================
# PDF
# ==============================
def gerar_pdf(df, mes, ano, saldo):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Título
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Relatório Financeiro - Madoska Piedade", ln=True)

    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 8, f"Mês/Ano: {mes}/{ano}", ln=True)
    pdf.cell(0, 8, f"Saldo Final: R$ {saldo:.2f}", ln=True)
    pdf.ln(5)

    # Cabeçalho tabela
    pdf.set_font("Arial", "B", 9)
    headers = ["Data", "Descrição", "Categoria", "Tipo", "Valor"]
    col_widths = [28, 55, 35, 25, 25]

    for h, w in zip(headers, col_widths):
        pdf.cell(w, 8, h, border=1)
    pdf.ln()

    # Linhas
    pdf.set_font("Arial", "", 9)
    for _, row in df.iterrows():
        pdf.cell(col_widths[0], 8, str(row["data"]), border=1)
        pdf.cell(col_widths[1], 8, str(row["descricao"])[:30], border=1)
        pdf.cell(col_widths[2], 8, str(row["categoria"]), border=1)
        pdf.cell(col_widths[3], 8, str(row["tipo"]), border=1)
        pdf.cell(col_widths[4], 8, f'R$ {float(row["valor"]):.2f}', border=1)
        pdf.ln()

    # fpdf2 retorna bytearray → NÃO usar encode()
    return bytes(pdf.output(dest="S"))


# ==============================
# DASHBOARD
# ==============================
def tela_dashboard(user):
    st.title("📊 Dashboard Financeiro")

    engine = get_engine()

    # ==============================
    # FILTROS
    # ==============================
    col1, col2 = st.columns(2)

    with col1:
        mes = st.selectbox("Mês", list(range(1, 13)), index=datetime.now().month - 1)

    with col2:
        ano = st.selectbox("Ano", [2024, 2025, 2026], index=1)

    # ==============================
    # BUSCA DADOS
    # ==============================
    query = """
        SELECT id, data, descricao, categoria, tipo, valor
        FROM lancamentos
        WHERE usuario_id = :uid
          AND EXTRACT(MONTH FROM data) = :mes
          AND EXTRACT(YEAR FROM data) = :ano
        ORDER BY data DESC
    """

    with engine.connect() as conn:
        result = conn.execute(
            text(query),
            {"uid": user["id"], "mes": mes, "ano": ano}
        ).fetchall()

    df = pd.DataFrame(result, columns=["id", "data", "descricao", "categoria", "tipo", "valor"])

    # ==============================
    # MÉTRICAS
    # ==============================
    entradas = df[df["tipo"] == "Entrada"]["valor"].sum() if not df.empty else 0
    saidas = df[df["tipo"] == "Saída"]["valor"].sum() if not df.empty else 0
    saldo = entradas - saidas

    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Entradas", f"R$ {entradas:.2f}")
    c2.metric("💸 Saídas", f"R$ {saidas:.2f}")
    c3.metric("📊 Saldo", f"R$ {saldo:.2f}")

    st.divider()

    # ==============================
    # GRÁFICO
    # ==============================
    st.subheader("📊 Gastos por categoria")

    if not df.empty:
        gastos = (
            df[df["tipo"] == "Saída"]
            .groupby("categoria")["valor"]
            .sum()
            .reset_index()
        )

        if not gastos.empty:
            st.bar_chart(gastos.set_index("categoria"))
        else:
            st.info("Ainda não há saídas para gerar o gráfico.")
    else:
        st.info("Nenhum lançamento encontrado para este período.")

    # ==============================
    # TABELA
    # ==============================
    st.subheader("📋 Lançamentos")
    st.dataframe(df.drop(columns=["id"]), use_container_width=True)

    # ==============================
    # EXCLUSÃO
    # ==============================
    st.subheader("🗑️ Excluir lançamento")

    if not df.empty:
        selecionado = st.selectbox(
            "Selecione o lançamento para excluir",
            df["id"],
            format_func=lambda x: f"ID {x}"
        )

        if st.button("Excluir"):
            with engine.begin() as conn:
                conn.execute(
                    text("DELETE FROM lancamentos WHERE id = :id AND usuario_id = :uid"),
                    {"id": selecionado, "uid": user["id"]}
                )

            st.success("Lançamento excluído com sucesso!")
            st.rerun()
    else:
        st.info("Nenhum lançamento para excluir.")

    st.divider()

    # ==============================
    # PDF
    # ==============================
    st.subheader("📄 Exportar relatório")

    if not df.empty:
        if st.button("Gerar PDF"):
            pdf_bytes = gerar_pdf(df, mes, ano, saldo)

            st.download_button(
                label="📥 Baixar relatório em PDF",
                data=pdf_bytes,
                file_name=f"relatorio_{mes}_{ano}.pdf",
                mime="application/pdf"
            )
    else:
        st.info("Não há dados para exportar.")
