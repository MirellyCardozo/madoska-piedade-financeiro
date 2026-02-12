import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def gerar_backup():
    """
    Gera backup do banco PostgreSQL (Neon) usando pg_dump
    Retorna o caminho do arquivo gerado
    """

    DATABASE_URL = os.getenv("DATABASE_URL")

    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL não encontrada no .env")

    data = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    pasta = "backups"
    os.makedirs(pasta, exist_ok=True)

    arquivo = f"{pasta}/backup_{data}.sql"

    comando = [
        "pg_dump",
        DATABASE_URL,
        "-f",
        arquivo
    ]

    subprocess.run(comando, check=True)

    return arquivo
