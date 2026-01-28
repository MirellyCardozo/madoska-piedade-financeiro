import streamlit as st
from auth import autenticar
from dashboard import tela_dashboard
from estoque import tela_estoque
from lancamentos import tela_lancamentos
from usuarios import tela_usuarios
from datetime import datetime

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="Madoska Piedade - Financeiro",
    page_icon="📊",
    layout="wide"
)

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
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos")


# =========================
# MENU LATERAL
# =========================
def menu_lateral(user):
    with st.sidebar:
        st.markdown(f"👤 **Usuário:** {user['nome']}")
        st.markdown(f"🛡️ **Perfil:** {user['perfil']}")
        st.markdown(f"🕒 **Hora BR:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

        st.divider()

        menu = st.radio(
            "Menu",
            ["Dashboard", "Estoque", "Lançamentos", "Usuários", "Sair"]
        )

    return menu


# =========================
# TELA PRINCIPAL
# =========================
def tela_principal():
    user = st.session_state["user"]

    menu = menu_lateral(user)

    if menu == "Dashboard":
        tela_dashboard(user)

    elif menu == "Estoque":
        tela_estoque(user)

    elif menu == "Lançamentos":
        tela_lancamentos(user)

    elif menu == "Usuários":
        tela_usuarios(user)

    elif menu == "Sair":
        del st.session_state["user"]
        st.rerun()


# =========================
# CONTROLE DE SESSÃO
# =========================
if "user" not in st.session_state:
    tela_login()
else:
    tela_principal()
