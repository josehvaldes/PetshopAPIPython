import sqlite3

class SQLiteProfileMemory:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)


    def get_pet_summary(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT breed, age, name, temperament FROM questionnaire
            WHERE user_id = ?
            ORDER BY timestamp DESC LIMIT 1
        """, (user_id,))
        row = cursor.fetchone()
        if row:
            breed, age, name, temperament = row
            return [f"{user_id} has a {age}-year-old {breed} named {name}, described as {temperament}."]
        return "No dog profile found."
    
    def close(self):
        self.conn.close()
