import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime
from sqlalchemy import text
from db import get_engine


# =============================
# PDF
# =============================
def gerar_pdf(df, mes, ano, saldo):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Relatório Financeiro", ln=True)

    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 8, f"Mês/Ano: {mes}/{ano}", ln=True)
    pdf.cell(0, 8, f"Saldo: R$ {saldo:,.2f}", ln=True)
    pdf.ln(5)

    # Cabeçalho
    pdf.set_font("Arial", "B", 9)
    headers = ["Data", "Descrição", "Categoria", "Tipo", "Valor"]
    col_widths = [30, 55, 35, 25, 25]

    for h, w in zip(headers, col_widths):
        pdf.cell(w, 8, h, border=1)
    pdf.ln()

    # Dados
    pdf.set_font("Arial", "", 9)
    for _, row in df.iterrows():
        pdf.cell(col_widths[0], 8, str(row["data"]), border=1)
        pdf.cell(col_widths[1], 8, str(row["descricao"])[:30], border=1)
        pdf.cell(col_widths[2], 8, str(row["categoria"])[:15], border=1)
        pdf.cell(col_widths[3], 8, str(row["tipo"]), border=1)
        pdf.cell(col_widths[4], 8, f'R$ {float(row["valor"]):.2f}', border=1)
        pdf.ln()

    # Retorna bytes (Streamlit precisa disso)
    return pdf.output(dest="S").encode("latin-1")


# =============================
# DASHBOARD
# =============================
def tela_dashboard(user):
    st.title("📊 Dashboard Financeiro")

    engine = get_engine()
    uid = user["id"]

    # =============================
    # FILTROS
    # =============================
    col1, col2 = st.columns(2)

    with col1:
        mes = st.selectbox("Mês", list(range(1, 13)), index=datetime.now().month - 1)
    with col2:
        ano = st.selectbox("Ano", list(range(2024, datetime.now().year + 1)), index=1)

    # =============================
    # BUSCA DADOS
    # =============================
    query = """
        SELECT data, descricao, categoria, tipo, valor, id
        FROM lancamentos
        WHERE usuario_id = :uid
          AND EXTRACT(MONTH FROM data) = :mes
          AND EXTRACT(YEAR FROM data) = :ano
        ORDER BY data DESC
    """

    with engine.connect() as conn:
        rows = conn.execute(
            text(query),
            {"uid": uid, "mes": mes, "ano": ano}
        ).fetchall()

    df = pd.DataFrame(rows, columns=["data", "descricao", "categoria", "tipo", "valor", "id"])

    if df.empty:
        st.info("Ainda não há lançamentos para este período.")
        return

    # =============================
    # GARANTE QUE VALOR É NUMÉRICO
    # =============================
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0)

    # =============================
    # TOTAIS
    # =============================
    entradas = df[df["tipo"] == "Entrada"]["valor"].sum()
    saidas = df[df["tipo"] == "Saída"]["valor"].sum()
    saldo = entradas - saidas

    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Entradas", f"R$ {entradas:,.2f}")
    c2.metric("💸 Saídas", f"R$ {saidas:,.2f}")
    c3.metric("📊 Saldo", f"R$ {saldo:,.2f}")

    st.divider()

    # =============================
    # GRÁFICO
    # =============================
    st.subheader("📉 Gastos por categoria")

    gastos = (
        df[df["tipo"] == "Saída"]
        .groupby("categoria")["valor"]
        .sum()
    )

    fig, ax = plt.subplots()

    if not gastos.empty and gastos.sum() > 0:
        gastos = gastos.astype(float)
        gastos.plot(kind="bar", ax=ax)
        ax.set_ylabel("Valor (R$)")
        ax.set_xlabel("Categoria")
        ax.set_title("Gastos por Categoria")
        st.pyplot(fig)
    else:
        st.info("Ainda não há gastos suficientes para gerar o gráfico.")

    st.divider()

    # =============================
    # TABELA
    # =============================
    st.subheader("📋 Lançamentos")
    st.dataframe(
        df[["data", "descricao", "categoria", "tipo", "valor"]],
        use_container_width=True
    )

    # =============================
    # EXCLUIR LANÇAMENTO
    # =============================
    st.subheader("🗑️ Excluir lançamento")

    lancamento_id = st.selectbox(
        "Selecione o lançamento para excluir",
        df["id"],
        format_func=lambda x: f"ID {x}"
    )

    if st.button("Excluir"):
        with engine.begin() as conn:
            conn.execute(
                text("DELETE FROM lancamentos WHERE id = :id AND usuario_id = :uid"),
                {"id": lancamento_id, "uid": uid}
            )
        st.success("Lançamento excluído com sucesso!")
        st.rerun()

    # =============================
    # PDF
    # =============================
    st.divider()
    st.subheader("📄 Exportar relatório")

    if st.button("Gerar PDF"):
        pdf_bytes = gerar_pdf(df, mes, ano, saldo)

        st.download_button(
            label="Baixar relatório em PDF",
            data=pdf_bytes,
            file_name=f"relatorio_{mes}_{ano}.pdf",
            mime="application/pdf"
        )
