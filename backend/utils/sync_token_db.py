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

def get_calendar_color(calendar_id: str) -> Optional[Dict[str, any]]:
    """Get calendar color information from database.
    
    Returns:
        Dict with 'color_index' and 'color_class' keys, or None if not found
    """
    ensure_tables_exist()
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute('SELECT color_index, color_class FROM calendar_colors WHERE calendar_id = ?', (calendar_id,))
        row = cur.fetchone()
        if row:
            return {'color_index': row[0], 'color_class': row[1]}
        return None

def set_calendar_color(calendar_id: str, color_index: int, color_class: str) -> None:
    """Set calendar color in database.
    
    Args:
        calendar_id: The calendar ID
        color_index: Numeric index for color ordering
        color_class: CSS class string for the color
    """
    ensure_tables_exist()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('REPLACE INTO calendar_colors (calendar_id, color_index, color_class) VALUES (?, ?, ?)', 
                    (calendar_id, color_index, color_class))
        conn.commit()

def get_all_calendar_colors() -> Dict[str, Dict[str, any]]:
    """Get all calendar colors from database.
    
    Returns:
        Dict mapping calendar_id to color info
    """
    ensure_tables_exist()
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute('SELECT calendar_id, color_index, color_class FROM calendar_colors ORDER BY color_index')
        colors = {}
        for row in cur.fetchall():
            colors[row[0]] = {'color_index': row[1], 'color_class': row[2]}
        return colors 