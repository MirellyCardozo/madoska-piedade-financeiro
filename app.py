import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from database import criar_tabela
from datetime import datetime
from fpdf import FPDF
import os

# ---------------- CONFIGURAÇÕES ----------------
SENHA_SISTEMA = "Piedade161246"  # <-- Você pode mudar essa senha depois

# ---------------- BANCO ----------------
engine = create_engine("sqlite:///madoska.db")
criar_tabela()

# ---------------- FUNÇÕES ----------------
def gerar_pdf(df, mes, ano):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Logo
    if os.path.exists("logo.png"):
        pdf.image("logo.png", x=10, y=8, w=30)
        pdf.ln(25)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"Relatório Financeiro - Madoska Piedade", ln=True, align="C")

    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 8, f"Mês/Ano: {mes}/{ano}", ln=True, align="C")
    pdf.ln(5)

    total_creditos = df[df["tipo"] == "Crédito"]["valor"].sum()
    total_gastos = df[df["tipo"] == "Gasto"]["valor"].sum()
    saldo = total_creditos - total_gastos

    pdf.cell(0, 8, f"Total Créditos: R$ {total_creditos:,.2f}", ln=True)
    pdf.cell(0, 8, f"Total Gastos: R$ {total_gastos:,.2f}", ln=True)
    pdf.cell(0, 8, f"Saldo: R$ {saldo:,.2f}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 9)

    headers = ["Data", "Tipo", "Descrição", "Categoria", "Pagamento", "Valor"]
    col_widths = [25, 20, 50, 35, 30, 20]

    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 8, header, border=1)
    pdf.ln()

    pdf.set_font("Arial", "", 8)
    for _, row in df.iterrows():
        pdf.cell(col_widths[0], 8, str(row["data"]), border=1)
        pdf.cell(col_widths[1], 8, str(row["tipo"]), border=1)
        pdf.cell(col_widths[2], 8, str(row["descricao"])[:30], border=1)
        pdf.cell(col_widths[3], 8, str(row["categoria"]), border=1)
        pdf.cell(col_widths[4], 8, str(row["pagamento"]), border=1)
        pdf.cell(col_widths[5], 8, f'R$ {row["valor"]:.2f}', border=1)
        pdf.ln()

    nome_arquivo = f"relatorio_{mes}_{ano}.pdf"
    pdf.output(nome_arquivo)
    return nome_arquivo


# ---------------- LOGIN ----------------
st.set_page_config(
    page_title="Madoska Piedade - Financeiro",
    layout="wide"
)

if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🔐 Acesso Restrito - Madoska Piedade")
    senha = st.text_input("Digite a senha", type="password")

    if st.button("Entrar"):
        if senha == SENHA_SISTEMA:
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("Senha incorreta")
    st.stop()

# ---------------- SISTEMA ----------------
st.title("🍨 Sistema Financeiro - Madoska Piedade")

menu = st.sidebar.selectbox("Menu", ["Registrar Movimento", "Dashboard", "Relatório PDF"])

# ---------- REGISTRAR MOVIMENTO ----------
if menu == "Registrar Movimento":
    st.subheader("📱 Registrar Gasto ou Crédito")

    data = st.date_input("Data")
    tipo = st.selectbox("Tipo", ["Gasto", "Crédito"])
    desc = st.text_input("Descrição")

    categoria = st.selectbox("Categoria", [
        "Vendas",
        "Aluguel",
        "Energia Elétrica",
        "Água",
        "Funcionários",
        "Insumos",
        "Embalagens",
        "Marketing",
        "Manutenção",
        "Outros"
    ])

    pagamento = st.selectbox("Forma de Pagamento", [
        "Pix",
        "Crédito",
        "Débito",
        "Dinheiro"
    ])

    valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
    obs = st.text_area("Observações")

    if st.button("💾 Salvar"):
        data_formatada = f"{data.day:02d}/{data.month:02d}/{data.year}"

        df = pd.DataFrame([{
            "data": data_formatada,
            "tipo": tipo,
            "descricao": desc,
            "categoria": categoria,
            "pagamento": pagamento,
            "valor": valor,
            "observacoes": obs
        }])

        df.to_sql("registros", engine, if_exists="append", index=False)
        st.success(f"{tipo} registrado com sucesso 🍦")

# ---------- DASHBOARD ----------
elif menu == "Dashboard":
    st.subheader("📊 Painel Financeiro")

    df = pd.read_sql("SELECT * FROM registros", engine)

    if not df.empty:
        df["data"] = df["data"].astype(str)

        # Filtro por mês e ano
        meses = sorted(df["data"].str[3:5].unique())
        anos = sorted(df["data"].str[6:10].unique())

        colf1, colf2 = st.columns(2)
        mes_sel = colf1.selectbox("📅 Mês", meses)
        ano_sel = colf2.selectbox("📆 Ano", anos)

        df_filtrado = df[
            (df["data"].str[3:5] == mes_sel) &
            (df["data"].str[6:10] == ano_sel)
        ]

        total_creditos = df_filtrado[df_filtrado["tipo"] == "Crédito"]["valor"].sum()
        total_gastos = df_filtrado[df_filtrado["tipo"] == "Gasto"]["valor"].sum()
        saldo = total_creditos - total_gastos

        col1, col2, col3 = st.columns(3)
        col1.metric("💰 Total Créditos", f"R$ {total_creditos:,.2f}")
        col2.metric("💸 Total Gastos", f"R$ {total_gastos:,.2f}")
        col3.metric("🏦 Saldo", f"R$ {saldo:,.2f}")

        st.subheader("📊 Por Categoria")
        por_categoria = df_filtrado.groupby("categoria")["valor"].sum()
        st.bar_chart(por_categoria)

        st.subheader("📋 Registros do Mês")
        st.dataframe(df_filtrado)

    else:
        st.info("Nenhum registro ainda.")

# ---------- RELATÓRIO PDF ----------
elif menu == "Relatório PDF":
    st.subheader("📄 Gerar PDF Mensal")

    df = pd.read_sql("SELECT * FROM registros", engine)

    if not df.empty:
        df["data"] = df["data"].astype(str)

        meses = sorted(df["data"].str[3:5].unique())
        anos = sorted(df["data"].str[6:10].unique())

        mes = st.selectbox("Mês", meses)
        ano = st.selectbox("Ano", anos)

        df_filtrado = df[
            (df["data"].str[3:5] == mes) &
            (df["data"].str[6:10] == ano)
        ]

        if st.button("📄 Gerar PDF"):
            nome_arquivo = gerar_pdf(df_filtrado, mes, ano)

            with open(nome_arquivo, "rb") as f:
                st.download_button(
                    label="⬇️ Baixar Relatório PDF",
                    data=f,
                    file_name=nome_arquivo,
                    mime="application/pdf"
                )
    else:
        st.info("Nenhum registro ainda.")
