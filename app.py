import streamlit as st
from datetime import datetime
import pytz

# IMPORTA SEUS MÓDULOS
from auth import autenticar
from dashboard import tela_dashboard
from estoque import tela_estoque
from lancamentos import tela_lancamentos
from usuarios import tela_usuarios

# =============================
# CONFIG
# =============================
st.set_page_config(
    page_title="Madoska Piedade - Sistema Financeiro",
    layout="wide"
)

TIMEZONE = pytz.timezone("America/Sao_Paulo")

# =============================
# LOGIN
# =============================
def tela_login():
    st.markdown("## 🔐 Login - Madoska Piedade")

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
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos")

# =============================
# APP PRINCIPAL
# =============================
def tela_principal():
    user = st.session_state["user"]

    agora = datetime.now(TIMEZONE).strftime("%d/%m/%Y %H:%M:%S")

    # SIDEBAR
    st.sidebar.markdown(f"👤 **Usuário:** {user['nome']}")
    st.sidebar.markdown(f"🕒 **Hora BR:** {agora}")
    st.sidebar.divider()

    menu = st.sidebar.radio(
        "Menu",
        [
            "📊 Dashboard",
            "📦 Estoque",
            "💰 Lançamentos",
            "👥 Usuários",
            "🚪 Sair"
        ]
    )

    # =============================
    # ROTAS
    # =============================
    if menu == "📊 Dashboard":
        tela_dashboard(user)

    elif menu == "📦 Estoque":
        tela_estoque(user)

    elif menu == "💰 Lançamentos":
        tela_lancamentos(user)

    elif menu == "👥 Usuários":
        if user["perfil"] != "admin":
            st.warning("Acesso restrito a administradores")
        else:
            tela_usuarios(user)

    elif menu == "🚪 Sair":
        st.session_state.clear()
        st.rerun()

# =============================
# CONTROLE DE SESSÃO
# =============================
if "user" not in st.session_state:
    tela_login()
else:
    tela_principal()
