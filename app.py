import streamlit as st
from auth import autenticar
from dashboard import tela_dashboard
from lancamentos import tela_lancamentos
from estoque import tela_estoque
from usuarios import tela_usuarios

st.set_page_config(
    page_title="Madoska Piedade",
    layout="wide"
)

# =========================
# LOGIN
# =========================
def tela_login():
    st.title("🔐 Login - Madoska Piedade")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        user = autenticar(usuario, senha)

        if user:
            st.session_state["user"] = {
                "id": user.id,
                "nome": user.nome,
                "usuario": user.usuario,
                "perfil": user.perfil
            }
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos")

# =========================
# SISTEMA PRINCIPAL
# =========================
def tela_principal():
    user = st.session_state["user"]

    st.sidebar.markdown(f"👤 Usuário: **{user['nome']}**")
    st.sidebar.markdown(f"🛡 Perfil: **{user['perfil']}**")

    menu = st.sidebar.radio(
        "Menu",
        ["Dashboard", "Estoque", "Lançamentos", "Usuários", "Sair"]
    )

    if menu == "Dashboard":
        tela_dashboard()

    elif menu == "Estoque":
        tela_estoque()

    elif menu == "Lançamentos":
        tela_lancamentos()

    elif menu == "Usuários":
        tela_usuarios(user)

    elif menu == "Sair":
        st.session_state.clear()
        st.rerun()

# =========================
# CONTROLE DE SESSÃO
# =========================
if "user" not in st.session_state:
    tela_login()
else:
    tela_principal()
