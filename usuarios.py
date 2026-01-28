import streamlit as st
from database import executar
from auth import gerar_hash

def tela_usuarios(user):
    st.title("👥 Gerenciamento de Usuários")

    # ======================
    # CRIAR USUÁRIO
    # ======================
    st.subheader("Novo Usuário")

    nome = st.text_input("Nome")
    usuario = st.text_input("Usuário de login")
    senha = st.text_input("Senha", type="password")
    perfil = st.selectbox("Perfil", ["admin", "usuario"])

    if st.button("Criar usuário"):
        if nome and usuario and senha:
            executar(
                """
                INSERT INTO usuarios (nome, usuario, senha, perfil)
                VALUES (:nome, :usuario, :senha, :perfil)
                """,
                {
                    "nome": nome,
                    "usuario": usuario,
                    "senha": gerar_hash(senha),
                    "perfil": perfil
                }
            )
            st.success("Usuário criado com sucesso")
            st.rerun()
        else:
            st.warning("Preencha todos os campos")

    # ======================
    # LISTAGEM
    # ======================
    st.divider()
    st.subheader("Usuários cadastrados")

    usuarios = executar(
        "SELECT id, nome, usuario, perfil FROM usuarios ORDER BY nome",
        fetchall=True
    )

    if not usuarios:
        st.info("Nenhum usuário cadastrado")
        return

    for u in usuarios:
        with st.expander(f"{u['nome']} ({u['usuario']})"):
            st.write(f"Perfil: {u['perfil']}")

            # Impede que o usuário se delete
            if u["usuario"] != user["usuario"]:
                if st.button("🗑 Excluir", key=f"del_user_{u['id']}"):
                    executar(
                        "DELETE FROM usuarios WHERE id = :id",
                        {"id": u["id"]}
                    )
                    st.warning("Usuário removido")
                    st.rerun()
