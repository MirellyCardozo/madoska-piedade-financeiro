import streamlit as st
from dashboard import tela_dashboard
from lancamentos import tela_lancamentos
from estoque import tela_estoque
from usuarios import tela_usuarios


def tela_principal(usuario_id):
    st.sidebar.title("Menu")

    menu = st.sidebar.radio(
        "",
        [
            "Dashboard",
            "Lançamentos",
            "Estoque",
            "Usuários",
            "Sair"
        ]
    )

    if menu == "Dashboard":
        tela_dashboard(usuario_id)

    elif menu == "Lançamentos":
        tela_lancamentos(usuario_id)

    elif menu == "Estoque":
        tela_estoque(usuario_id)

    elif menu == "Usuários":
        tela_usuarios(usuario_id)

    elif menu == "Sair":
        st.session_state.clear()
        st.experimental_rerun()


# ========= APP =========
if "usuario_id" not in st.session_state:
    st.error("Usuário não autenticado")
else:
    tela_principal(st.session_state["usuario_id"])
