import os
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import date, timedelta

from database import criar_tabelas
from auth import criar_usuario, trocar_senha, autenticar
from estoque import tela_estoque
from backup import backup_automatico

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "madoska.db")
engine = create_engine(f"sqlite:///{DB_FILE}")

criar_tabelas()
backup_automatico()

# -------- AUTO ADMIN --------
def garantir_admin():
    with engine.begin() as conn:
        total = conn.execute(text("SELECT COUNT(*) FROM usuarios")).fetchone()[0]
        if total == 0:
            criar_usuario("Admin", "admin", "admin123", "admin")

garantir_admin()

# -------- SESSÃO --------
if "usuario" not in st.session_state:
    st.session_state.usuario = None

# -------- LOGIN --------
if not st.session_state.usuario:
    st.title("🔐 Login - Madoska Piedade")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        user = autenticar(usuario, senha)
        if user:
            st.session_state.usuario = user
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos")

    st.stop()

user = st.session_state.usuario

# -------- TOPO COM LOGOUT --------
st.set_page_config(page_title="Madoska Piedade", layout="wide")

col1, col2 = st.columns([6, 1])
with col1:
    st.title(f"🍨 Madoska Piedade — {user['nome']}")
with col2:
    if st.button("🚪 Sair"):
        st.session_state.usuario = None
        st.rerun()

# -------- MENU --------
if user["perfil"] == "admin":
    menu = st.sidebar.selectbox("Menu", [
        "📊 Dashboard",
        "➕ Lançar Financeiro",
        "📋 Registros Financeiros",
        "📦 Estoque",
        "👥 Usuários",
        "🔐 Trocar Senha"
    ])
else:
    menu = st.sidebar.selectbox("Menu", [
        "📦 Estoque",
        "🔐 Trocar Senha"
    ])

CATEGORIAS = [
    "Insumos", "Energia", "Vendas", "Fornecedores",
    "Impostos", "Aluguel", "Funcionários",
    "Manutenção", "Outros"
]

FORMAS_PAGAMENTO = ["Dinheiro", "PIX", "Cartão", "Transferência", "Boleto"]

# -------- DASHBOARD --------
if menu == "📊 Dashboard":
    st.subheader("📊 Dashboard Financeiro")

    df = pd.read_sql("SELECT * FROM registros", engine)

    if df.empty:
        st.info("Nenhum lançamento ainda.")
    else:
        df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")

        hoje = date.today()
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        inicio_mes = hoje.replace(day=1)

        def resumo(df_temp):
            creditos = df_temp[df_temp["tipo"] == "Crédito"]["valor"].sum()
            debitos = df_temp[df_temp["tipo"] == "Gasto"]["valor"].sum()
            return creditos, debitos, creditos - debitos

        df_dia = df[df["data"].dt.date == hoje]
        df_semana = df[df["data"].dt.date >= inicio_semana]
        df_mes = df[df["data"].dt.date >= inicio_mes]

        c1, d1, l1 = resumo(df_dia)
        c2, d2, l2 = resumo(df_semana)
        c3, d3, l3 = resumo(df_mes)

        col1, col2, col3 = st.columns(3)
        col1.metric("📅 Hoje", f"Lucro R$ {l1:.2f}", f"Créditos R$ {c1:.2f} | Débitos R$ {d1:.2f}")
        col2.metric("📆 Semana", f"Lucro R$ {l2:.2f}", f"Créditos R$ {c2:.2f} | Débitos R$ {d2:.2f}")
        col3.metric("🗓️ Mês", f"Lucro R$ {l3:.2f}", f"Créditos R$ {c3:.2f} | Débitos R$ {d3:.2f}")

# -------- LANÇAR --------
elif menu == "➕ Lançar Financeiro":
    data = st.date_input("Data", value=date.today())
    tipo = st.selectbox("Tipo", ["Crédito", "Gasto"])
    descricao = st.text_input("Descrição")
    categoria = st.selectbox("Categoria", CATEGORIAS)
    pagamento = st.selectbox("Forma de pagamento", FORMAS_PAGAMENTO)
    valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
    obs = st.text_area("Observações")

    if st.button("Salvar"):
        with engine.begin() as conn:
            conn.execute(text("""
            INSERT INTO registros
            (data, tipo, descricao, categoria, pagamento, valor, observacoes)
            VALUES (:d,:t,:desc,:c,:p,:v,:o)
            """), {
                "d": data.strftime("%d/%m/%Y"),
                "t": tipo,
                "desc": descricao,
                "c": categoria,
                "p": pagamento,
                "v": valor,
                "o": obs
            })
        st.success("Registro salvo!")
        st.rerun()

# -------- REGISTROS --------
elif menu == "📋 Registros Financeiros":
    df = pd.read_sql("SELECT * FROM registros ORDER BY id DESC", engine)
    st.dataframe(df, use_container_width=True)

# -------- ESTOQUE --------
elif menu == "📦 Estoque":
    tela_estoque()

# -------- USUÁRIOS --------
elif menu == "👥 Usuários":
    nome = st.text_input("Nome")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    perfil = st.selectbox("Perfil", ["admin", "estoque"])

    if st.button("Criar Usuário"):
        criar_usuario(nome, usuario, senha, perfil)
        st.success("Usuário criado!")

# -------- SENHA --------
elif menu == "🔐 Trocar Senha":
    atual = st.text_input("Senha atual", type="password")
    nova = st.text_input("Nova senha", type="password")
    conf = st.text_input("Confirmar nova senha", type="password")

    if st.button("Atualizar"):
        ok, msg = trocar_senha(user["usuario"], atual, nova)
        if ok:
            st.success(msg)
        else:
            st.error(msg)
