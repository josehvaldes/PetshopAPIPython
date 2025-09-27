import sqlite3
from langchain_core.messages import HumanMessage, AIMessage

class SQLiteConversationMemory:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)

    def load_memory_variables(self, user_id: str):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT role, message FROM chat_history
            WHERE user_id = ?
            ORDER BY timestamp ASC
        """, (user_id,))
        messages = cursor.fetchall()
        print(f"Loaded {len(messages)} messages for user_id {user_id}")
        return {
            "chat_history": [
                HumanMessage(content=msg) if role == "human" else AIMessage(content=msg)
                for role, msg in messages
            ]
        }

    def close(self):
        self.conn.close()

    def save_context(self, user_id: str, input, output):
        cursor = self.conn.cursor()
        cursor.executemany("""
            INSERT INTO chat_history (user_id, role, message)
            VALUES (?, ?, ?)
        """, [
            (user_id, "human", input["input"]),
            (user_id, "ai", output["output"])
        ])
        self.conn.commit()
    
