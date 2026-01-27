import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime
import pytz

from database import executar

TIMEZONE = pytz.timezone("America/Sao_Paulo")

# ==========================
# TABELA NO BANCO (EXECUTA UMA VEZ)
# ==========================
def criar_tabela_lancamentos():
    executar("""
    CREATE TABLE IF NOT EXISTS lancamentos (
        id SERIAL PRIMARY KEY,
        data DATE NOT NULL,
        categoria TEXT NOT NULL,
        descricao TEXT NOT NULL,
        valor NUMERIC(10,2) NOT NULL,
        usuario TEXT NOT NULL
    )
    """)

# ==========================
# BUSCAR DADOS
# ==========================
def buscar_lancamentos(usuario):
    result = executar("""
        SELECT id, data, categoria, descricao, valor
        FROM lancamentos
        WHERE usuario = :usuario
        ORDER BY data DESC
    """, {"usuario": usuario}).fetchall()

    return pd.DataFrame(result, columns=["id", "data", "categoria", "descricao", "valor"])

# ==========================
# INSERIR
# ==========================
def inserir_lancamento(data, categoria, descricao, valor, usuario):
    executar("""
        INSERT INTO lancamentos (data, categoria, descricao, valor, usuario)
        VALUES (:data, :categoria, :descricao, :valor, :usuario)
    """, {
        "data": data,
        "categoria": categoria,
        "descricao": descricao,
        "valor": valor,
        "usuario": usuario
    })

# ==========================
# EXCLUIR
# ==========================
def excluir_lancamento(lancamento_id):
    executar("""
        DELETE FROM lancamentos
        WHERE id = :id
    """, {"id": lancamento_id})

# ==========================
# GERAR PDF
# ==========================
def gerar_pdf(df, mes, ano, usuario):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"Relatório Financeiro - {usuario}", ln=True)
    pdf.cell(0, 10, f"Mês: {mes}/{ano}", ln=True)

    pdf.set_font("Arial", size=10)
    pdf.ln(5)

    for _, row in df.iterrows():
        linha = f"{row['data']} | {row['categoria']} | {row['descricao']} | R$ {row['valor']}"
        pdf.multi_cell(0, 8, linha)

    nome_arquivo = f"relatorio_{usuario}_{mes}_{ano}.pdf"
    pdf.output(nome_arquivo)

    return nome_arquivo

# ==========================
# DASHBOARD PRINCIPAL
# ==========================
def tela_dashboard(usuario):
    criar_tabela_lancamentos()

    st.title("📊 Dashboard Financeiro")

    agora = datetime.now(TIMEZONE).strftime("%d/%m/%Y %H:%M:%S")
    st.caption(f"Usuário: {usuario} | Hora BR: {agora}")

    # ==========================
    # FORMULÁRIO DE LANÇAMENTO
    # ==========================
    st.subheader("➕ Novo Lançamento")

    col1, col2 = st.columns(2)

    with col1:
        data = st.date_input("Data", datetime.now(TIMEZONE))
        categoria = st.text_input("Categoria")

    with col2:
        descricao = st.text_input("Descrição")
        valor = st.number_input("Valor (R$)", min_value=0.0, step=0.01)

    if st.button("Salvar Lançamento"):
        if categoria and descricao and valor > 0:
            inserir_lancamento(data, categoria, descricao, valor, usuario)
            st.success("Lançamento salvo com sucesso!")
            st.rerun()
        else:
            st.warning("Preencha todos os campos corretamente.")

    # ==========================
    # TABELA
    # ==========================
    df = buscar_lancamentos(usuario)

    if df.empty:
        st.info("Nenhum gasto registrado ainda.")
        return

    st.subheader("📋 Lançamentos")
    st.dataframe(df, use_container_width=True)

    # ==========================
    # EXCLUIR
    # ==========================
    st.subheader("🗑 Excluir Lançamento")
    lancamento_id = st.selectbox(
        "Selecione o ID para excluir",
        df["id"].tolist()
    )

    if st.button("Excluir"):
        excluir_lancamento(lancamento_id)
        st.success("Lançamento excluído!")
        st.rerun()

    # ==========================
    # GRÁFICO
    # ==========================
    st.subheader("📈 Gastos por Categoria")

    grafico_df = df.groupby("categoria")["valor"].sum()

    fig, ax = plt.subplots()
    grafico_df.plot(kind="bar", ax=ax)
    ax.set_ylabel("Total R$")
    ax.set_xlabel("Categoria")
    ax.set_title("Gastos por Categoria")

    st.pyplot(fig)

    # ==========================
    # EXPORTAÇÃO PDF
    # ==========================
    st.subheader("📄 Exportar Relatório Mensal")

    colm1, colm2 = st.columns(2)

    with colm1:
        mes = st.selectbox("Mês", list(range(1, 13)))

    with colm2:
        ano = st.selectbox("Ano", list(range(2023, 2031)))

    if st.button("Gerar PDF"):
        df_filtrado = df[
            (pd.to_datetime(df["data"]).dt.month == mes) &
            (pd.to_datetime(df["data"]).dt.year == ano)
        ]

        if df_filtrado.empty:
            st.warning("Nenhum lançamento nesse mês.")
        else:
            arquivo = gerar_pdf(df_filtrado, mes, ano, usuario)
            with open(arquivo, "rb") as f:
                st.download_button(
                    "📥 Baixar PDF",
                    f,
                    file_name=arquivo,
                    mime="application/pdf"
                )
