import streamlit as st
from dashboard import tela_dashboard
from lancamentos import tela_lancamentos

def tela_principal():
    usuario_id = 3  # fixo como já estava
    menu = st.sidebar.radio(
        "Menu",
        ["Dashboard", "Lançamentos"]
    )

    if menu == "Dashboard":
        tela_dashboard(usuario_id)
    elif menu == "Lançamentos":
        tela_lancamentos(usuario_id)

tela_principal()
