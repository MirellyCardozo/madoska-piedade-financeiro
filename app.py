import streamlit as st
from database import criar_tabelas
from auth import tela_login, criar_usuario, trocar_senha
from estoque import tela_estoque
from backup import backup_automatico
import pandas as pd
from sqlalchemy import create_engine

DB_PATH = r"sqlite:///C:/Users/mirel/OneDrive/Área de Trabalho/madoska_financeiro/madoska.db"
engine = create_engine(DB_PATH)

criar_tabelas()
backup_automatico()

if "usuario" not in st.session_state:
    st.session_state.usuario = None

# LOGIN
if not st.session_state.usuario:
    tela_login()
    st.stop()

user = st.session_state.usuario

st.set_page_config(page_title="Madoska Piedade", layout="wide")
st.title(f"🍨 Madoska Piedade — Bem-vinda, {user['nome']}")

# MENU POR PERFIL
if user["perfil"] == "admin":
    menu = st.sidebar.selectbox("Menu", [
        "📦 Estoque",
        "👥 Usuários",
        "📊 Financeiro",
        "🔐 Trocar Senha"
    ])
else:
    menu = st.sidebar.selectbox("Menu", [
        "📦 Estoque",
        "🔐 Trocar Senha"
    ])

# -------- ESTOQUE --------
if menu == "📦 Estoque":
    tela_estoque()

# -------- USUÁRIOS (ADMIN) --------
elif menu == "👥 Usuários":
    st.subheader("👥 Criar Usuários")

    nome = st.text_input("Nome")
    usuario = st.text_input("Usuário (login)")
    senha = st.text_input("Senha", type="password")
    perfil = st.selectbox("Perfil", ["admin", "estoque"])

    if st.button("Criar"):
        criar_usuario(nome, usuario, senha, perfil)
        st.success("Usuário criado com sucesso!")

# -------- FINANCEIRO (VISUALIZAÇÃO) --------
elif menu == "📊 Financeiro":
    st.subheader("📊 Financeiro")
    df = pd.read_sql("SELECT * FROM registros", engine)
    st.dataframe(df)

# -------- TROCAR SENHA --------
elif menu == "🔐 Trocar Senha":
    st.subheader("🔐 Trocar Minha Senha")

    senha_atual = st.text_input("Senha atual", type="password")
    nova_senha = st.text_input("Nova senha", type="password")
    confirmar = st.text_input("Confirmar nova senha", type="password")

    if st.button("Atualizar Senha"):
        if nova_senha != confirmar:
            st.error("A nova senha e a confirmação não coincidem.")
        elif len(nova_senha) < 4:
            st.error("A senha deve ter pelo menos 4 caracteres.")
        else:
            sucesso, msg = trocar_senha(
                user["usuario"],
                senha_atual,
                nova_senha
            )
            if sucesso:
                st.success(msg)
            else:
                st.error(msg)
