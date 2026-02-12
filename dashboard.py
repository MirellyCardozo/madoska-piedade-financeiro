import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import io
from datetime import datetime
from sqlalchemy import text
from database import engine


# =========================
# PDF
# =========================
def gerar_pdf(df, resumo):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    pdf.cell(0, 10, "Relatório Financeiro", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 8, "Resumo", ln=True)
    pdf.set_font("Arial", size=10)

    for k, v in resumo.items():
        pdf.cell(0, 8, f"{k}: R$ {v:.2f}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 8, "Lançamentos", ln=True)
    pdf.set_font("Arial", size=9)

    for _, row in df.iterrows():
        linha = f"{row['data']} | {row['descricao']} | {row['categoria']} | R$ {row['valor']:.2f}"
        pdf.multi_cell(0, 7, linha)

    buffer = io.BytesIO()
    buffer.write(pdf.output(dest="S"))  # ✔ SEM encode
    buffer.seek(0)
    return buffer


# =========================
# DASHBOARD
# =========================
def tela_dashboard(usuario):
    st.title("📊 Dashboard Financeiro")

    col1, col2 = st.columns(2)

    with col1:
        mes = st.selectbox("Mês", list(range(1, 13)), index=datetime.now().month - 1)

    with col2:
        ano = st.selectbox("Ano", list(range(2023, datetime.now().year + 1)), index=1)

    query = text("""
        SELECT data, descricao, categoria, tipo, valor
        FROM lancamentos
        WHERE usuario_id = :uid
          AND EXTRACT(MONTH FROM data) = :mes
          AND EXTRACT(YEAR FROM data) = :ano
        ORDER BY data
    """)

    with engine.connect() as conn:
        df = pd.read_sql(
            query,
            conn,
            params={"uid": usuario["id"], "mes": mes, "ano": ano}
        )

    if df.empty:
        st.warning("Nenhum lançamento encontrado para este período.")
        return

    df["valor"] = df["valor"].astype(float)

    entradas = df[df["tipo"] == "entrada"]["valor"].sum()
    saidas = df[df["tipo"] == "saida"]["valor"].sum()
    saldo = entradas - saidas

    resumo = {
        "Entradas": entradas,
        "Saídas": saidas,
        "Saldo": saldo
    }

    c1, c2, c3 = st.columns(3)
    c1.metric("Entradas", f"R$ {entradas:.2f}")
    c2.metric("Saídas", f"R$ {saidas:.2f}")
    c3.metric("Saldo", f"R$ {saldo:.2f}")

    # =========================
    # GRÁFICO
    # =========================
    fig, ax = plt.subplots()
    df.groupby("categoria")["valor"].sum().plot(kind="bar", ax=ax)
    ax.set_title("Gastos por Categoria")
    ax.set_ylabel("Valor (R$)")
    st.pyplot(fig)

    # =========================
    # EXPORTAR PDF
    # =========================
    st.subheader("📄 Exportar relatório")

    pdf_buffer = gerar_pdf(df, resumo)

    st.download_button(
        label="📥 Gerar PDF",
        data=pdf_buffer,
        file_name=f"relatorio_{mes}_{ano}.pdf",
        mime="application/pdf"
    )
from backup import gerar_backup

st.divider()
st.subheader("🧯 Backup do Sistema")

if st.button("📦 Gerar Backup do Banco"):
    try:
        caminho = gerar_backup()
        with open(caminho, "rb") as f:
            st.download_button(
                "⬇️ Baixar Backup",
                data=f,
                file_name=caminho.split("/")[-1],
                mime="application/octet-stream"
            )
        st.success("Backup gerado com sucesso!")
    except Exception as e:
        st.error(f"Erro ao gerar backup: {e}")
