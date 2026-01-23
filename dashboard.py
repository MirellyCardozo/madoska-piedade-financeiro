import streamlit as st
from datetime import datetime
import pytz

from database import criar_tabelas
from auth import criar_usuario, autenticar
from estoque import tela_estoque
from dashboard import tela_dashboard
from backup import backup_automatico

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(
    page_title="Madoska Piedade - Financeiro",
    layout="wide"
)

# -----------------------------
# TIMEZONE BRASIL
# -----------------------------
TZ = pytz.timezone("America/Sao_Paulo")

def agora_br():
    return datetime.now(TZ)

# -----------------------------
# INIT
# -----------------------------
criar_tabelas()
backup_automatico()

# -----------------------------
# LOGIN
# -----------------------------
def tela_login():
    st.title("🔐 Login - Madoska Piedade")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        user = autenticar(usuario, senha)
        if user:
            st.session_state["user"] = user
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos")

# -----------------------------
# MENU PRINCIPAL
# -----------------------------
def tela_principal():
    user = st.session_state.get("user")

    st.sidebar.markdown(f"👤 **Usuário:** {user['nome']}")
    st.sidebar.markdown(f"🕒 **Hora BR:** {agora_br().strftime('%d/%m/%Y %H:%M:%S')}")

    menu = st.sidebar.radio(
        "Menu",
        ["📊 Dashboard", "📦 Estoque", "🚪 Sair"]
    )

    if menu == "📊 Dashboard":
        tela_dashboard()

    elif menu == "📦 Estoque":
        tela_estoque()

    elif menu == "🚪 Sair":
        st.session_state.clear()
        st.rerun()

# -----------------------------
# ROTEAMENTO
# -----------------------------
if "user" not in st.session_state:
    tela_login()
else:
    tela_principal()
