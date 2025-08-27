import shutil
import datetime
import os

def hacer_backup():
    if not os.path.exists("backups"):
        os.makedirs("backups")
    fecha = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = f"backups/backup_{fecha}.db"
    try:
        shutil.copy("data/laboratorio.db", destino)
        print(f"Backup guardado: {destino}")
    except Exception as e:
        print(f"Error en backup: {e}")