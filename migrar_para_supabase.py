import sqlite3
import psycopg2

# ---------------------------
# CONFIGURAÇÕES
# ---------------------------
SQLITE_DB = "madoska.db"

POSTGRES_URI = "postgresql://postgres:Handebol09*@db.igcywmhrdpjmhbntjipa.supabase.co:5432/postgres"

# ---------------------------
# CONEXÕES
# ---------------------------
sqlite_conn = sqlite3.connect(SQLITE_DB)
sqlite_cur = sqlite_conn.cursor()

pg_conn = psycopg2.connect(POSTGRES_URI)
pg_cur = pg_conn.cursor()

# ---------------------------
# TABELAS PARA MIGRAR
# ---------------------------
TABELAS = [
    "registros",
    "usuarios",
    "estoque"
]

# ---------------------------
# MIGRAÇÃO
# ---------------------------
for tabela in TABELAS:
    print(f"Migrando tabela: {tabela}")

    sqlite_cur.execute(f"SELECT * FROM {tabela}")
    rows = sqlite_cur.fetchall()

    if not rows:
        print(f" - {tabela} vazia, pulando.")
        continue

    colunas = [desc[0] for desc in sqlite_cur.description]
    colunas_str = ", ".join(colunas)
    placeholders = ", ".join(["%s"] * len(colunas))

    insert_sql = f"INSERT INTO {tabela} ({colunas_str}) VALUES ({placeholders})"

    for row in rows:
        pg_cur.execute(insert_sql, row)

    pg_conn.commit()
    print(f" - {len(rows)} registros migrados.")

# ---------------------------
# FECHAR
# ---------------------------
sqlite_conn.close()
pg_cur.close()
pg_conn.close()

print("MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
