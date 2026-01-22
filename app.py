import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from database import criar_tabela
from fpdf import FPDF
import os
import base64
from pathlib import Path
from datetime import datetime

# ---------------- CONFIGURAÇÕES ----------------
SENHA_SISTEMA = "madoska123"  # 🔐 Troque por uma senha só sua

# ---------------- BANCO ----------------
engine = create_engine("sqlite:///madoska.db")
criar_tabela()

# ---------------- PÁGINA ----------------
st.set_page_config(
    page_title="Madoska Piedade - Financeiro",
    page_icon="🍨",
    layout="wide"
)

# ---------- Forçar ícone do app no iPhone/Android ----------
icon_path = Path("apple-touch-icon.png")

if icon_path.exists():
    with open(icon_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <link rel="apple-touch-icon" href="data:image/png;base64,{encoded}">
        <link rel="icon" href="data:image/png;base64,{encoded}">
        """,
        unsafe_allow_html=True
    )

# ---------------- FUNÇÕES ----------------
def gerar_pdf(df, mes, ano):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    if os.path.exists("logo.png"):
        pdf.image("logo.png", x=10, y=8, w=30)
        pdf.ln(25)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Relatório Financeiro - Madoska Piedade", ln=True, align="C")

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
    col_widths = [25, 20, 55, 35, 30, 20]

    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 8, header, border=1)
    pdf.ln()

    pdf.set_font("Arial", "", 8)
    for _, row in df.iterrows():
        pdf.cell(col_widths[0], 8, str(row["data"]), border=1)
        pdf.cell(col_widths[1], 8, str(row["tipo"]), border=1)
        pdf.cell(col_widths[2], 8, str(row["descricao"])[:35], border=1)
        pdf.cell(col_widths[3], 8, str(row["categoria"]), border=1)
        pdf.cell(col_widths[4], 8, str(row["pagamento"]), border=1)
        pdf.cell(col_widths[5], 8, f'R$ {row["valor"]:.2f}', border=1)
        pdf.ln()

    nome_arquivo = f"relatorio_{mes}_{ano}.pdf"
    pdf.output(nome_arquivo)
    return nome_arquivo


def preparar_dataframe(df):
    df["data_dt"] = pd.to_datetime(df["data"], format="%d/%m/%Y", errors="coerce")
    return df


def calcular_lucro(df):
    creditos = df[df["tipo"] == "Crédito"]["valor"].sum()
    gastos = df[df["tipo"] == "Gasto"]["valor"].sum()
    return creditos - gastos


def excluir_registro(registro_id):
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM registros WHERE id = :id"), {"id": registro_id})


# ---------------- LOGIN ----------------
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

menu = st.sidebar.selectbox(
    "Menu",
    ["Registrar Movimento", "Dashboard", "Lucro por Período", "Relatório PDF", "Excluir Registro"]
)

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
        df = preparar_dataframe(df)

        df["mes"] = df["data_dt"].dt.month
        df["ano"] = df["data_dt"].dt.year

        meses = sorted(df["mes"].dropna().unique())
        anos = sorted(df["ano"].dropna().unique())

        colf1, colf2 = st.columns(2)
        mes_sel = colf1.selectbox("📅 Mês", meses)
        ano_sel = colf2.selectbox("📆 Ano", anos)

        df_filtrado = df[(df["mes"] == mes_sel) & (df["ano"] == ano_sel)]

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
        st.dataframe(df_filtrado.drop(columns=["data_dt", "mes", "ano"]))

    else:
        st.info("Nenhum registro ainda.")

# ---------- LUCRO POR PERÍODO ----------
elif menu == "Lucro por Período":
    st.subheader("📈 Lucro por Dia, Semana e Mês")

    df = pd.read_sql("SELECT * FROM registros", engine)

    if not df.empty:
        df = preparar_dataframe(df)

        periodo = st.selectbox("Ver lucro por:", ["Dia", "Semana", "Mês"])

        if periodo == "Dia":
            df["periodo"] = df["data_dt"].dt.strftime("%d/%m/%Y")
        elif periodo == "Semana":
            df["periodo"] = df["data_dt"].dt.strftime("Semana %U - %Y")
        else:
            df["periodo"] = df["data_dt"].dt.strftime("%m/%Y")

        resultados = []
        for p in df["periodo"].dropna().unique():
            df_p = df[df["periodo"] == p]
            lucro = calcular_lucro(df_p)
            resultados.append({"Período": p, "Lucro (R$)": round(lucro, 2)})

        df_resultado = pd.DataFrame(resultados).sort_values("Período")

        st.subheader("📊 Tabela de Lucro")
        st.dataframe(df_resultado)

        st.subheader("📈 Gráfico de Lucro")
        st.line_chart(df_resultado.set_index("Período"))

    else:
        st.info("Nenhum registro ainda.")

# ---------- RELATÓRIO PDF ----------
elif menu == "Relatório PDF":
    st.subheader("📄 Gerar PDF Mensal")

    df = pd.read_sql("SELECT * FROM registros", engine)

    if not df.empty:
        df = preparar_dataframe(df)

        df["mes"] = df["data_dt"].dt.month
        df["ano"] = df["data_dt"].dt.year

        meses = sorted(df["mes"].dropna().unique())
        anos = sorted(df["ano"].dropna().unique())

        mes = st.selectbox("Mês", meses)
        ano = st.selectbox("Ano", anos)

        df_filtrado = df[(df["mes"] == mes) & (df["ano"] == ano)]

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

# ---------- EXCLUIR REGISTRO ----------
elif menu == "Excluir Registro":
    st.subheader("🗑️ Excluir Registro")

    df = pd.read_sql("SELECT id, data, tipo, descricao, valor FROM registros", engine)

    if not df.empty:
        df["label"] = df.apply(
            lambda x: f'#{x["id"]} | {x["data"]} | {x["tipo"]} | {x["descricao"]} | R$ {x["valor"]:.2f}',
            axis=1
        )

        escolha = st.selectbox("Selecione o registro para excluir:", df["label"])

        registro_id = int(escolha.split("|")[0].replace("#", "").strip())

        st.warning("⚠️ Essa ação NÃO pode ser desfeita!")

        if st.button("🗑️ Confirmar Exclusão"):
            excluir_registro(registro_id)
            st.success("Registro excluído com sucesso!")
            st.rerun()
    else:
        st.info("Nenhum registro para excluir.")
