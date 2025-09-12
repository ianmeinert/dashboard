import os
import sqlite3
from typing import Dict, Optional

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
DB_PATH = os.path.join(DATA_DIR, 'calendar_sync.db')

CREATE_SYNC_TABLE_SQL = '''
CREATE TABLE IF NOT EXISTS calendar_sync_tokens (
    calendar_id TEXT PRIMARY KEY,
    sync_token TEXT
);
'''

CREATE_COLORS_TABLE_SQL = '''
CREATE TABLE IF NOT EXISTS calendar_colors (
    calendar_id TEXT PRIMARY KEY,
    color_index INTEGER NOT NULL,
    color_class TEXT NOT NULL
);
'''

def ensure_tables_exist():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(CREATE_SYNC_TABLE_SQL)
        conn.execute(CREATE_COLORS_TABLE_SQL)
        conn.commit()

def get_sync_token(calendar_id: str) -> Optional[str]:
    ensure_tables_exist()
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute('SELECT sync_token FROM calendar_sync_tokens WHERE calendar_id = ?', (calendar_id,))
        row = cur.fetchone()
        return row[0] if row else None

def set_sync_token(calendar_id: str, sync_token: str) -> None:
    ensure_tables_exist()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('REPLACE INTO calendar_sync_tokens (calendar_id, sync_token) VALUES (?, ?)', (calendar_id, sync_token))
        conn.commit()
