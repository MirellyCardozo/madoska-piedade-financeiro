import streamlit as st
from datetime import datetime
import pytz

from database import criar_tabelas
from auth import criar_usuario, autenticar
from estoque import tela_estoque
from dashboard import tela_dashboard
from backup import backup_automatico

# ======================
# CONFIGURAÇÃO INICIAL
# ======================
st.set_page_config(page_title="Madoska Financeiro", layout="wide")

# Fuso horário Brasil
TZ = pytz.timezone("America/Sao_Paulo")

criar_tabelas()
backup_automatico()

# ======================
# TELA LOGIN
# ======================
def tela_login():
    st.title("🔐 Login - Madoska Piedade")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        user = autenticar(usuario, senha)
        if user:
            st.session_state["user"] = usuario
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos")

# ======================
# TELA PRINCIPAL
# ======================
def tela_principal():
    now = datetime.now(TZ).strftime("%d/%m/%Y %H:%M:%S")

    st.sidebar.markdown(f"👤 Usuário: **{st.session_state['user']}**")
    st.sidebar.markdown(f"🕒 Hora BR: **{now}**")

    menu = st.sidebar.radio(
        "Menu",
        ["📊 Dashboard", "📦 Estoque", "🚪 Sair"]
    )

    if menu == "📊 Dashboard":
        tela_dashboard(st.session_state["user"])

    elif menu == "📦 Estoque":
        tela_estoque()

    elif menu == "🚪 Sair":
        del st.session_state["user"]
        st.rerun()

# ======================
# CONTROLE SESSÃO
# ======================
if "user" not in st.session_state:
    tela_login()
else:
    tela_principal()
