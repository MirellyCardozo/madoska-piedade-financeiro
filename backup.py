import os
import shutil
from datetime import datetime

def backup_automatico():
    if not os.path.exists("backups"):
        os.mkdir("backups")

    hoje = datetime.now().strftime("%Y-%m-%d")
    nome_backup = f"backups/backup_{hoje}.db"

    if not os.path.exists(nome_backup):
        shutil.copy("madoska.db", nome_backup)
