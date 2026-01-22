import os
import streamlit as st
from database import criar_tabelas
from auth import tela_login, criar_usuario, trocar_senha, autenticar
from estoque import tela_estoque
from backup import backup_automatico
import pandas as pd
from sqlalchemy import create_engine

# Caminho automático do banco
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "madoska.db")
engine = create_engine(f"sqlite:///{DB_FILE}")

# Inicialização
criar_tabelas()
backup_automatico()

# Sessão
if "usuario" not in st.session_state:
    st.session_state.usuario = None

# ---------------------------
# LOGIN / SETUP INICIAL
# ---------------------------
if not st.session_state.usuario:
    st.title("🔐 Login - Madoska Piedade")

    st.info("Se for o primeiro acesso na nuvem, crie o ADMIN abaixo. Depois faça login normalmente.")

    # --- SETUP ADMIN ---
    st.subheader("🛠️ Criar ADMIN inicial (apenas na primeira vez)")

    setup_nome = st.text_input("Nome (ADMIN inicial)")
    setup_user = st.text_input("Usuário (login ADMIN)")
    setup_senha = st.text_input("Senha ADMIN", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Criar ADMIN"):
            try:
                if setup_nome and setup_user and setup_senha:
                    criar_usuario(setup_nome, setup_user, setup_senha, "admin")
                    st.success("ADMIN criado com sucesso! Agora faça login abaixo.")
                else:
                    st.error("Preencha todos os campos do ADMIN.")
            except Exception:
                st.error("Erro ao criar usuário. Talvez esse login já exista.")

    st.markdown("---")

    # --- LOGIN NORMAL ---
    st.subheader("🔐 Entrar no sistema")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        user = autenticar(usuario, senha)
        if user:
            st.session_state.usuario = user
            st.success(f"Bem-vinda, {user['nome']}!")
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos")

    st.stop()

# ---------------------------
# SISTEMA PRINCIPAL
# ---------------------------
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
        try:
            criar_usuario(nome, usuario, senha, perfil)
            st.success("Usuário criado com sucesso!")
        except Exception:
            st.error("Erro ao criar usuário. Login pode já existir.")

# -------- FINANCEIRO --------
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
