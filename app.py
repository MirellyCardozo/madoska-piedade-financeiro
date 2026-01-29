import streamlit as st
from auth import autenticar
from dashboard import tela_dashboard
from estoque import tela_estoque
from lancamentos import tela_lancamentos
from usuarios import tela_usuarios

st.set_page_config("Madoska Financeiro", layout="wide")

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
            st.error("Usuário ou senha inválidos")

def tela_principal():
    user = st.session_state["user"]

    with st.sidebar:
        st.subheader("Usuário")
        st.write(f"Nome: {user['nome']}")
        st.write(f"Perfil: {user['perfil']}")

        menu = st.radio("Menu", [
            "Dashboard",
            "Estoque",
            "Lançamentos",
            "Usuários",
            "Sair"
        ])

    if menu == "Dashboard":
        tela_dashboard(user)

    elif menu == "Estoque":
        tela_estoque(user)

    elif menu == "Lançamentos":
        tela_lancamentos(user)

    elif menu == "Usuários":
        tela_usuarios(user)

    elif menu == "Sair":
        st.session_state.clear()
        st.rerun()

if "user" not in st.session_state:
    tela_login()
else:
    tela_principal()
