import os
from sqlalchemy import create_engine, text

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "madoska.db")

engine = create_engine(f"sqlite:///{DB_FILE}")

def criar_tabelas():
    with engine.begin() as conn:
        # Financeiro
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            tipo TEXT,
            descricao TEXT,
            categoria TEXT,
            pagamento TEXT,
            valor REAL,
            observacoes TEXT
        )
        """))

        # Usuários
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            usuario TEXT UNIQUE,
            senha TEXT,
            perfil TEXT
        )
        """))

        # Estoque atual
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS estoque (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto TEXT,
            categoria TEXT,
            quantidade REAL,
            unidade TEXT,
            minimo REAL,
            ultima_atualizacao TEXT
        )
        """))

        # Histórico do estoque
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS estoque_historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER,
            data TEXT,
            tipo TEXT,
            quantidade REAL,
            observacao TEXT
        )
        """))
