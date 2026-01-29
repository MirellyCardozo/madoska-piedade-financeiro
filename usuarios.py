import streamlit as st
from auth import criar_usuario
from database import executar

def tela_usuarios(user):
    if user["perfil"] != "admin":
        st.warning("Acesso restrito ao administrador")
        return

    st.title("👥 Usuários")

    nome = st.text_input("Nome")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    perfil = st.selectbox("Perfil", ["admin", "usuario"])

    if st.button("Criar usuário"):
        criar_usuario(nome, usuario, senha, perfil)
        st.success("Usuário criado")
        st.rerun()

    st.subheader("📋 Usuários cadastrados")

    usuarios = executar(
        "SELECT nome, usuario, perfil FROM usuarios ORDER BY nome",
        fetchall=True
    )

    for u in usuarios:
        st.write(f"**{u['nome']}** | {u['usuario']} | {u['perfil']}")
