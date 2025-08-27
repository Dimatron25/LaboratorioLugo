import sqlite3
import os

DB_PATH = "data/laboratorio.db"

def conectar():
    if not os.path.exists("data"):
        os.makedirs("data")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            curp TEXT UNIQUE,
            edad INTEGER,
            telefono TEXT,
            direccion TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS examenes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER,
            tipo TEXT NOT NULL,
            fecha TEXT NOT NULL,
            precio REAL,
            pagado REAL DEFAULT 0,
            estado_pago TEXT DEFAULT 'pendiente',
            FOREIGN KEY(paciente_id) REFERENCES pacientes(id)
        )
    ''')
    conn.commit()
    return conn