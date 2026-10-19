from pathlib import Path
import sqlite3

DB_DIR = Path.home() / 'GestionCabras'
DB_PATH = DB_DIR / 'rebanio.db'

def connect():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA foreign_keys = ON')
    return con

def init_db():
    with connect() as con:
        con.executescript('''
        CREATE TABLE IF NOT EXISTS goats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL, name TEXT NOT NULL,
            sex TEXT NOT NULL DEFAULT 'Hembra', breed TEXT DEFAULT '',
            birth_date TEXT DEFAULT '', color TEXT DEFAULT '', weight_kg REAL,
            status TEXT NOT NULL DEFAULT 'Activa', mother_id INTEGER, father_id INTEGER,
            notes TEXT DEFAULT '',
            FOREIGN KEY(mother_id) REFERENCES goats(id) ON DELETE SET NULL,
            FOREIGN KEY(father_id) REFERENCES goats(id) ON DELETE SET NULL
        );
        CREATE TABLE IF NOT EXISTS milk (
            id INTEGER PRIMARY KEY AUTOINCREMENT, goat_id INTEGER NOT NULL,
            record_date TEXT NOT NULL, morning_l REAL NOT NULL DEFAULT 0,
            evening_l REAL NOT NULL DEFAULT 0, notes TEXT DEFAULT '',
            UNIQUE(goat_id, record_date),
            FOREIGN KEY(goat_id) REFERENCES goats(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS births (
            id INTEGER PRIMARY KEY AUTOINCREMENT, mother_id INTEGER NOT NULL,
            birth_date TEXT NOT NULL, kids_count INTEGER NOT NULL DEFAULT 1,
            notes TEXT DEFAULT '',
            FOREIGN KEY(mother_id) REFERENCES goats(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS birth_kids (
            id INTEGER PRIMARY KEY AUTOINCREMENT, birth_id INTEGER NOT NULL,
            goat_id INTEGER, sex TEXT DEFAULT '', notes TEXT DEFAULT '',
            FOREIGN KEY(birth_id) REFERENCES births(id) ON DELETE CASCADE,
            FOREIGN KEY(goat_id) REFERENCES goats(id) ON DELETE SET NULL
        );
        ''')
