from database import executar

SQL = """
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    usuario TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL,
    perfil TEXT NOT NULL DEFAULT 'user',
    criado_em TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS estoque (
    id SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    quantidade INTEGER NOT NULL,
    preco NUMERIC(10,2) NOT NULL,
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS lancamentos (
    id SERIAL PRIMARY KEY,
    data DATE NOT NULL,
    descricao TEXT NOT NULL,
    categoria TEXT NOT NULL,
    tipo TEXT NOT NULL,
    valor NUMERIC(10,2) NOT NULL,
    pagamento TEXT NOT NULL,
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE
);
"""

executar(SQL)
print("✅ Tabelas criadas com sucesso")