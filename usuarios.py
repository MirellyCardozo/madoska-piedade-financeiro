import streamlit as st
from database import executar

def tela_usuarios(user):
    st.title("👥 Usuários")

    if user["perfil"] != "admin":
        st.warning("Apenas administradores podem gerenciar usuários.")
        return

    nome = st.text_input("Nome")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    perfil = st.selectbox("Perfil", ["admin", "usuario"])

    if st.button("Criar usuário"):
        executar(
            """
            INSERT INTO usuarios (nome, usuario, senha, perfil)
            VALUES (:n, :u, :s, :p)
            """,
            {
                "n": nome,
                "u": usuario,
                "s": senha,
                "p": perfil
            }
        )
        st.success("Usuário criado!")
        st.rerun()

    st.divider()
    st.subheader("Usuários cadastrados")

    usuarios = executar(
        "SELECT id, nome, usuario, perfil FROM usuarios ORDER BY nome",
        fetchall=True
    )

    for u in usuarios:
        with st.expander(f"{u.nome} ({u.usuario}) - {u.perfil}"):
            if st.button("🗑 Excluir", key=f"u{u.id}"):
                executar(
                    "DELETE FROM usuarios WHERE id = :id",
                    {"id": u.id}
                )
                st.rerun()
