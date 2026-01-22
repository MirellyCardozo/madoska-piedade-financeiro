import streamlit as st
from database import criar_tabelas
from auth import tela_login, criar_usuario
from estoque import tela_estoque
from backup import backup_automatico
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("sqlite:///madoska.db")
criar_tabelas()
backup_automatico()

if "usuario" not in st.session_state:
    st.session_state.usuario = None

if not st.session_state.usuario:
    tela_login()
    st.stop()

user = st.session_state.usuario

st.set_page_config(page_title="Madoska Piedade", layout="wide")
st.title(f"🍨 Madoska Piedade — Bem-vinda, {user['nome']}")

if user["perfil"] == "admin":
    menu = st.sidebar.selectbox("Menu", ["📦 Estoque", "👥 Usuários", "📊 Financeiro"])
else:
    menu = st.sidebar.selectbox("Menu", ["📦 Estoque"])

if menu == "📦 Estoque":
    tela_estoque()

elif menu == "👥 Usuários":
    st.subheader("👥 Criar Usuários")

    nome = st.text_input("Nome")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    perfil = st.selectbox("Perfil", ["admin", "estoque"])

    if st.button("Criar"):
        criar_usuario(nome, usuario, senha, perfil)
        st.success("Usuário criado!")

elif menu == "📊 Financeiro":
    df = pd.read_sql("SELECT * FROM registros", engine)
    st.dataframe(df)
