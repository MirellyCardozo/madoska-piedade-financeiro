import streamlit as st
from auth import autenticar
from dashboard import tela_dashboard
from estoque import tela_estoque
from lancamentos import tela_lancamentos
from usuarios import tela_usuarios

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
            st.session_state["user"] = {
                "id": user["id"],
                "nome": user["nome"],
                "usuario": user["usuario"],
                "perfil": user["perfil"]
            }
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos")

# ==========================
# SISTEMA PRINCIPAL
# ==========================
def tela_principal():
    user = st.session_state["user"]

    # SIDEBAR
    st.sidebar.title("👤 Usuário")
    st.sidebar.write(f"**Nome:** {user['nome']}")
    st.sidebar.write(f"**Perfil:** {user['perfil']}")

    menu = st.sidebar.radio(
        "Menu",
        ["Dashboard", "Estoque", "Lançamentos", "Usuários", "Sair"]
    )

    # ROTAS
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

# ==========================
# CONTROLE DE SESSÃO
# ==========================
if "user" not in st.session_state:
    tela_login()
else:
    tela_principal()
