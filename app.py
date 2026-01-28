import streamlit as st
from datetime import datetime
import pytz

from database import criar_tabelas
from auth import autenticar
from dashboard import tela_dashboard
from lancamentos import tela_lancamentos
from usuarios import tela_usuarios


# =========================
# CONFIG STREAMLIT
# =========================
st.set_page_config(
    page_title="Madoska Piedade - Financeiro",
    page_icon="📊",
    layout="wide"
)

# =========================
# CRIA TABELAS SE NÃO EXISTIREM
# =========================
criar_tabelas()


# =========================
# FUNÇÃO HORA BRASIL
# =========================
def hora_br():
    tz = pytz.timezone("America/Sao_Paulo")
    return datetime.now(tz).strftime("%d/%m/%Y %H:%M:%S")


# =========================
# TELA DE LOGIN
# =========================
def tela_login():
    st.title("🔐 Login - Madoska Piedade")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        user = autenticar(usuario, senha)

        if user:
            st.session_state["user"] = {
                "id": user["id"],
                "nome": user["nome"],
                "usuario": user["usuario"],
                "perfil": user["perfil"]
            }
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha inválidos")


# =========================
# TELA PRINCIPAL
# =========================
def tela_principal():
    user = st.session_state["user"]

    # SIDEBAR
    st.sidebar.markdown(f"👤 **Usuário:** {user['nome']}")
    st.sidebar.markdown(f"🕒 **Hora BR:** {hora_br()}")
    st.sidebar.divider()

    menu = st.sidebar.radio("Menu", [
        "📊 Dashboard",
        "💰 Lançamentos",
        "👥 Usuários",
        "🚪 Sair"
    ])

    # CONTROLE DE PERMISSÃO
    if menu == "👥 Usuários" and user["perfil"] != "admin":
        st.warning("Apenas administradores podem acessar essa área.")
        return

    # ROTAS
    if menu == "📊 Dashboard":
        tela_dashboard(user)

    elif menu == "💰 Lançamentos":
        tela_lancamentos()

    elif menu == "👥 Usuários":
        tela_usuarios()

    elif menu == "🚪 Sair":
        st.session_state.clear()
        st.experimental_rerun()


# =========================
# CONTROLE DE SESSÃO
# =========================
if "user" not in st.session_state:
    tela_login()
else:
    tela_principal()
