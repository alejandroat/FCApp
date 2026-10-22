import sqlite3
from pathlib import Path

DB_PATH = Path("data/app.db")
DB_PATH.parent.mkdir(exist_ok=True)

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            contrasena TEXT NOT NULL
        )
    """)
    
    # cursor.execute("DROP TABLE IF EXISTS jugadores")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jugadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dorsal INTEGER,
            nombre TEXT NOT NULL,
            valoracion INTEGER NOT NULL,
            posicion_principal TEXT NOT NULL,
            posicion_secundaria TEXT,
            pais TEXT NOT NULL,
            equipo TEXT,
            equipacion TEXT,
            rango INTEGER CHECK (rango >= 0 AND rango <= 5),
            habilitado INTEGER DEFAULT 1,
            programa TEXT,
            imagen_url TEXT,
            usuario_id INTEGER NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS imagenes_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_busqueda TEXT NOT NULL UNIQUE,
            imagen_url TEXT NOT NULL,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            dias_validez INTEGER DEFAULT 30
        )
    """)
    
    
    conn.commit()
    conn.close()
