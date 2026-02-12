import os
from datetime import datetime
from sqlalchemy import text
from database import engine


def gerar_backup():
    pasta = "backups"
    os.makedirs(pasta, exist_ok=True)

    nome_arquivo = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    caminho = os.path.join(pasta, nome_arquivo)

    with engine.connect() as conn, open(caminho, "w", encoding="utf-8") as f:
        tabelas = ["usuarios", "lancamentos", "estoque"]

        for tabela in tabelas:
            f.write(f"\n-- Backup da tabela {tabela}\n")

            resultado = conn.execute(text(f"SELECT * FROM {tabela}"))
            colunas = resultado.keys()

            for linha in resultado.fetchall():
                valores = []

                for valor in linha:
                    if valor is None:
                        valores.append("NULL")
                    else:
                        valor_str = str(valor).replace("'", "''")
                        valores.append(f"'{valor_str}'")

                sql = (
                    f"INSERT INTO {tabela} ({', '.join(colunas)}) "
                    f"VALUES ({', '.join(valores)});\n"
                )

                f.write(sql)

    return caminho
