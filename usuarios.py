import streamlit as st
from passlib.context import CryptContext

from database import executar

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ==========================
# HASH SEGURO
# ==========================
def gerar_hash(senha: str) -> str:
    return pwd_context.hash(senha[:72])

def verificar_senha(senha_digitada, senha_hash):
    return pwd_context.verify(senha_digitada[:72], senha_hash)

# ==========================
# CRIAR USUÁRIO
# ==========================
def criar_usuario(nome, usuario, senha, perfil):
    sql = """
    INSERT INTO usuarios (nome, usuario, senha, perfil)
    VALUES (:nome, :usuario, :senha, :perfil)
    """
    executar(sql, {
        "nome": nome,
        "usuario": usuario,
        "senha": gerar_hash(senha),
        "perfil": perfil
    })

# ==========================
# BUSCAR USUÁRIOS
# ==========================
def listar_usuarios():
    sql = "SELECT id, nome, usuario, perfil FROM usuarios ORDER BY nome"
    return executar(sql).fetchall()

# ==========================
# ALTERAR SENHA
# ==========================
def alterar_senha(id_usuario, nova_senha):
    sql = """
    UPDATE usuarios
    SET senha = :senha
    WHERE id = :id
    """
    executar(sql, {
        "id": id_usuario,
        "senha": gerar_hash(nova_senha)
    })

# ==========================
# TELA
# ==========================
def tela_usuarios():
    st.title("👥 Gestão de Usuários")

    abas = st.tabs(["📋 Listar", "➕ Criar", "🔑 Alterar Senha"])

    usuarios = listar_usuarios()

    # =====================
    # LISTAR
    # =====================
    with abas[0]:
        if not usuarios:
            st.info("Nenhum usuário cadastrado.")
        else:
            for u in usuarios:
                st.write(f"👤 {u[1]} | Login: `{u[2]}` | Perfil: {u[3]}")

    # =====================
    # CRIAR
    # =====================
    with abas[1]:
        st.subheader("Novo Usuário")

        nome = st.text_input("Nome")
        usuario = st.text_input("Usuário (login)")
        senha = st.text_input("Senha", type="password")
        perfil = st.selectbox("Perfil", ["admin", "usuario"])

        if st.button("Criar Usuário"):
            if not nome or not usuario or not senha:
                st.error("Preencha todos os campos.")
            else:
                criar_usuario(nome, usuario, senha, perfil)
                st.success("Usuário criado com sucesso!")
                st.experimental_rerun()

    # =====================
    # ALTERAR SENHA
    # =====================
    with abas[2]:
        if not usuarios:
            st.info("Nenhum usuário cadastrado.")
        else:
            nomes = {f"{u[1]} ({u[2]})": u[0] for u in usuarios}

            escolha = st.selectbox("Selecione o usuário", list(nomes.keys()))
            nova_senha = st.text_input("Nova senha", type="password")

            if st.button("Alterar Senha"):
                if not nova_senha:
                    st.error("Digite a nova senha.")
                else:
                    alterar_senha(nomes[escolha], nova_senha)
                    st.success("Senha alterada com sucesso!")
