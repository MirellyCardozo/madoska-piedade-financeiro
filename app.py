import streamlit as st
from datetime import datetime
import pytz

from database import criar_tabelas
from auth import criar_usuario, autenticar
from estoque import tela_estoque
from dashboard import tela_dashboard
from backup import backup_automatico

# ==========================
# CONFIG
# ==========================
st.set_page_config(page_title="Madoska Financeiro", layout="wide")

criar_tabelas()
backup_automatico()

TIMEZONE = pytz.timezone("America/Sao_Paulo")

# ==========================
# LOGIN
# ==========================
def tela_login():
    st.title("🔐 Login - Madoska Piedade")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        user = autenticar(usuario, senha)

        if user:
            # OPÇÃO 3 → salva só string
            st.session_state["user"] = user
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos")

# ==========================
# MENU PRINCIPAL
# ==========================
def tela_principal():
    agora = datetime.now(TIMEZONE).strftime("%d/%m/%Y %H:%M:%S")

    st.sidebar.markdown(f"👤 Usuário: {st.session_state['user']}")
    st.sidebar.markdown(f"🕒 Hora BR: {agora}")

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

# ==========================
# MAIN
# ==========================
if "user" not in st.session_state:
    tela_login()
else:
    tela_principal()
