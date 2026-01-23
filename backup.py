import os
import shutil
from datetime import datetime

def backup_automatico():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_FILE = os.path.join(BASE_DIR, "madoska.db")
    BACKUP_DIR = os.path.join(BASE_DIR, "backups")

    if not os.path.exists(BACKUP_DIR):
        os.mkdir(BACKUP_DIR)

    hoje = datetime.now().strftime("%Y-%m-%d")
    nome_backup = os.path.join(BACKUP_DIR, f"backup_{hoje}.db")

    if not os.path.exists(nome_backup) and os.path.exists(DB_FILE):
        shutil.copy(DB_FILE, nome_backup)
