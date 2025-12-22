import sqlite3

class Database:
    def __init__(self, db_name='users.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_table()
    
    def _create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_tag TEXT,
                chat_id INTEGER PRIMARY KEY,
                subscribe BOOLEAN
            )
        ''')
        self.conn.commit()
    
    def add_user(self, user_tag: str, chat_id: int, subscribe: bool):
        self.cursor.execute('''
            INSERT OR REPLACE INTO users (user_tag, chat_id, subscribe)
            VALUES (?, ?, ?)
        ''', (user_tag, chat_id, subscribe))
        self.conn.commit()
    
    def get_user_by_sub(self, sub: bool):
        self.cursor.execute('''
            SELECT user_tag, chat_id FROM users WHERE subscribe = ?
        ''', (sub,))
        rows = self.cursor.fetchall()
        # Возвращаем список словарей для всех пользователей
        return [{"user_tag": row[0], "chat_id": row[1]} for row in rows]
    
    def get_user_by_chat_id(self, chat_id: int):
        self.cursor.execute('''
            SELECT user_tag, subscribe FROM users WHERE chat_id = ?
        ''', (chat_id,))
        row = self.cursor.fetchone()
        if row:
            return {"user_tag": row[0], "subscribe": row[1]}
        return None
    
    def update_subscribe(self, chat_id: int, subscribe: bool):
        self.cursor.execute('''
            UPDATE users SET subscribe = ? WHERE chat_id = ?
        ''', (subscribe, chat_id))
        self.conn.commit()
        return self.cursor.rowcount > 0  # Возвращает True если запись была обновлена
    
    def get_all_users(self):
        self.cursor.execute('SELECT user_tag, chat_id, subscribe FROM users')
        rows = self.cursor.fetchall()
        return [{"user_tag": row[0], "chat_id": row[1], "subscribe": row[2]} for row in rows]
    
    def user_exists(self, chat_id: int):
        self.cursor.execute('SELECT 1 FROM users WHERE chat_id = ?', (chat_id,))
        return self.cursor.fetchone() is not None
    
    def close(self):
        self.conn.close()