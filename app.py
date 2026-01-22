import os
import streamlit as st
from database import criar_tabelas
from auth import criar_usuario, trocar_senha, autenticar
from estoque import tela_estoque
from backup import backup_automatico
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import date, timedelta

# -----------------------------
# BANCO AUTOMÁTICO
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "madoska.db")
engine = create_engine(f"sqlite:///{DB_FILE}")

# -----------------------------
# INICIALIZAÇÃO
# -----------------------------
criar_tabelas()
backup_automatico()

# -----------------------------
# AUTO ADMIN SE VAZIO
# -----------------------------
def garantir_admin():
    with engine.begin() as conn:
        total = conn.execute(text("SELECT COUNT(*) FROM usuarios")).fetchone()[0]
        if total == 0:
            criar_usuario("Admin", "admin", "admin123", "admin")

garantir_admin()

# -----------------------------
# SESSÃO
# -----------------------------
if "usuario" not in st.session_state:
    st.session_state.usuario = None

# -----------------------------
# LOGIN
# -----------------------------
if not st.session_state.usuario:
    st.title("🔐 Login - Madoska Piedade")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        user = autenticar(usuario, senha)
        if user:
            st.session_state.usuario = user
            st.success(f"Bem-vinda, {user['nome']}!")
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos")

    st.stop()

user = st.session_state.usuario

# -----------------------------
# TELA PRINCIPAL
# -----------------------------
st.set_page_config(page_title="Madoska Piedade", layout="wide")
st.title(f"🍨 Madoska Piedade — Bem-vinda, {user['nome']}")

# -----------------------------
# MENU
# -----------------------------
if user["perfil"] == "admin":
    menu = st.sidebar.selectbox("Menu", [
        "📊 Dashboard",
        "➕ Lançar Financeiro",
        "📋 Registros Financeiros",
        "📦 Estoque",
        "👥 Usuários",
        "🔐 Trocar Senha"
    ])
else:
    menu = st.sidebar.selectbox("Menu", [
        "📦 Estoque",
        "🔐 Trocar Senha"
    ])

# -----------------------------
# CATEGORIAS FIXAS
# -----------------------------
CATEGORIAS = [
    "Insumos",
    "Energia",
    "Vendas",
    "Fornecedores",
    "Impostos",
    "Aluguel",
    "Funcionários",
    "Manutenção",
    "Outros"
]

FORMAS_PAGAMENTO = [
    "Dinheiro",
    "PIX",
    "Cartão",
    "Transferência",
    "Boleto"
]

# -----------------------------
# DASHBOARD
# -----------------------------
if menu == "📊 Dashboard":
    st.subheader("📊 Dashboard Financeiro")

    df = pd.read_sql("SELECT * FROM registros", engine)

    if df.empty:
        st.info("Nenhum lançamento financeiro ainda.")
    else:
        df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")

        hoje = date.today()
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        inicio_mes = hoje.replace(day=1)

        df_dia = df[df["data"].dt.date == hoje]
        df_semana = df[df["data"].dt.date >= inicio_semana]
        df_mes = df[df["data"].dt.date >= inicio_mes]

        def resumo(df_temp):
            creditos = df_temp[df_temp["tipo"] == "Crédito"]["valor"].sum()
            gastos = df_temp[df_temp["tipo"] == "Gasto"]["valor"].sum()
            lucro = creditos - gastos
            return creditos, gastos, lucro

        c1, g1, l1 = resumo(df_dia)
        c2, g2, l2 = resumo(df_semana)
        c3, g3, l3 = resumo(df_mes)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("📅 Hoje - Lucro", f"R$ {l1:.2f}", f"Créditos: R$ {c1:.2f}")
        with col2:
            st.metric("📆 Semana - Lucro", f"R$ {l2:.2f}", f"Gastos: R$ {g2:.2f}")
        with col3:
            st.metric("🗓️ Mês - Lucro", f"R$ {l3:.2f}", f"Créditos: R$ {c3:.2f}")

# -----------------------------
# LANÇAR FINANCEIRO
# -----------------------------
elif menu == "➕ Lançar Financeiro":
    st.subheader("➕ Novo Lançamento")

    data = st.date_input("Data", value=date.today())
    tipo = st.selectbox("Tipo", ["Crédito", "Gasto"])
    descricao = st.text_input("Descrição")

    categoria = st.selectbox("Categoria", CATEGORIAS)
    pagamento = st.selectbox("Forma de pagamento", FORMAS_PAGAMENTO)

    valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
    observacoes = st.text_area("Observações")

    if st.button("Salvar Lançamento"):
        with engine.begin() as conn:
            conn.execute(text("""
            INSERT INTO registros
            (data, tipo, descricao, categoria, pagamento, valor, observacoes)
            VALUES (:d, :t, :desc, :cat, :pag, :v, :obs)
            """), {
                "d": data.strftime("%d/%m/%Y"),
                "t": tipo,
                "desc": descricao,
                "cat": categoria,
                "pag": pagamento,
                "v": valor,
                "obs": observacoes
            })
        st.success("Lançamento salvo com sucesso!")

# -----------------------------
# REGISTROS (EDITAR / EXCLUIR)
# -----------------------------
elif menu == "📋 Registros Financeiros":
    st.subheader("📋 Registros Financeiros")

    df = pd.read_sql("SELECT * FROM registros ORDER BY id DESC", engine)

    if df.empty:
        st.info("Nenhum registro encontrado.")
    else:
        st.dataframe(df, use_container_width=True)

        st.markdown("### ✏️ Editar ou 🗑️ Excluir Registro")

        registro_id = st.number_input("ID do registro", min_value=1, step=1)

        with engine.connect() as conn:
            registro = conn.execute(
                text("SELECT * FROM registros WHERE id = :id"),
                {"id": registro_id}
            ).fetchone()

        if registro:
            data_edit = st.date_input("Data", value=pd.to_datetime(registro[1], format="%d/%m/%Y").date())
            tipo_edit = st.selectbox("Tipo", ["Crédito", "Gasto"], index=0 if registro[2] == "Crédito" else 1)
            descricao_edit = st.text_input("Descrição", value=registro[3])
            categoria_edit = st.selectbox("Categoria", CATEGORIAS, index=CATEGORIAS.index(registro[4]) if registro[4] in CATEGORIAS else 0)
            pagamento_edit = st.selectbox("Forma de pagamento", FORMAS_PAGAMENTO, index=FORMAS_PAGAMENTO.index(registro[5]) if registro[5] in FORMAS_PAGAMENTO else 0)
            valor_edit = st.number_input("Valor (R$)", min_value=0.0, value=float(registro[6]), format="%.2f")
            observacoes_edit = st.text_area("Observações", value=registro[7])

            col1, col2 = st.columns(2)

            with col1:
                if st.button("💾 Salvar Alterações"):
                    with engine.begin() as conn:
                        conn.execute(text("""
                        UPDATE registros
                        SET data = :d,
                            tipo = :t,
                            descricao = :desc,
                            categoria = :cat,
                            pagamento = :pag,
                            valor = :v,
                            observacoes = :obs
                        WHERE id = :id
                        """), {
                            "d": data_edit.strftime("%d/%m/%Y"),
                            "t": tipo_edit,
                            "desc": descricao_edit,
                            "cat": categoria_edit,
                            "pag": pagamento_edit,
                            "v": valor_edit,
                            "obs": observacoes_edit,
                            "id": registro_id
                        })
                    st.success("Registro atualizado com sucesso!")
                    st.rerun()

            with col2:
                if st.button("🗑️ Excluir Registro"):
                    with engine.begin() as conn:
                        conn.execute(text("DELETE FROM registros WHERE id = :id"), {"id": registro_id})
                    st.warning("Registro excluído!")
                    st.rerun()
        else:
            st.info("Digite um ID válido para editar ou excluir.")

# -----------------------------
# ESTOQUE
# -----------------------------
elif menu == "📦 Estoque":
    tela_estoque()

# -----------------------------
# USUÁRIOS
# -----------------------------
elif menu == "👥 Usuários":
    st.subheader("👥 Criar Usuários")

    nome = st.text_input("Nome")
    usuario = st.text_input("Usuário (login)")
    senha = st.text_input("Senha", type="password")
    perfil = st.selectbox("Perfil", ["admin", "estoque"])

    if st.button("Criar Usuário"):
        try:
            criar_usuario(nome, usuario, senha, perfil)
            st.success("Usuário criado com sucesso!")
        except Exception:
            st.error("Erro ao criar usuário. Login pode já existir.")

# -----------------------------
# TROCAR SENHA
# -----------------------------
elif menu == "🔐 Trocar Senha":
    st.subheader("🔐 Trocar Minha Senha")

    senha_atual = st.text_input("Senha atual", type="password")
    nova_senha = st.text_input("Nova senha", type="password")
    confirmar = st.text_input("Confirmar nova senha", type="password")

    if st.button("Atualizar Senha"):
        if nova_senha != confirmar:
            st.error("A nova senha e a confirmação não coincidem.")
        elif len(nova_senha) < 4:
            st.error("A senha deve ter pelo menos 4 caracteres.")
        else:
            sucesso, msg = trocar_senha(
                user["usuario"],
                senha_atual,
                nova_senha
            )
            if sucesso:
                st.success(msg)
            else:
                st.error(msg)
