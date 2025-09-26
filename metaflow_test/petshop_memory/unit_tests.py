import sqlite3
import unittest
from conversation_memory import SQLiteConversationMemory
from profile_memory import SQLiteProfileMemory
from langchain_core.messages import HumanMessage, AIMessage
import os

class TestSQLiteMemory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_folder = "database"
        if not os.path.exists(cls.db_folder):
            os.makedirs(cls.db_folder)

        cls.db_path = os.path.join(cls.db_folder,"test_memory.db") 
        cls.user_id = "test_user"

        # Ensure the database file is fresh for each test run
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)
        
        # Initialize database and tables
        conn = sqlite3.connect(cls.db_path)
        cursor = conn.cursor()
        cursor.executescript("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            role TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS questionnaire (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            breed TEXT,
            age INTEGER,
            name TEXT,
            temperament TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.commit()
        print("Database and tables created.")
        conn.close()

    def setUp(self):
        self.conv_memory = SQLiteConversationMemory(self.db_path)
        self.profile_memory = SQLiteProfileMemory(self.db_path)

    def test_conversation_memory_save_and_load(self):
        print("Testing conversation memory save and load...")
        # Save some messages
        self.conv_memory.save_context(self.user_id,
            {"input": "Hello, how are you?"},
            {"output": "I'm fine, thank you!"}
        )
        self.conv_memory.save_context(self.user_id,
            {"input": "What is the best food for my dog?"},
            {"output": "The best food depends on your dog's breed and age."}
        )

        # Load messages and verify
        memory_vars = self.conv_memory.load_memory_variables(self.user_id)
        chat_history = memory_vars["chat_history"]
        
        self.assertEqual(len(chat_history), 4)
        self.assertIsInstance(chat_history[0], HumanMessage)
        self.assertIsInstance(chat_history[1], AIMessage)
        self.assertEqual(chat_history[0].content, "Hello, how are you?")
        self.assertEqual(chat_history[1].content, "I'm fine, thank you!")
        self.assertEqual(chat_history[2].content, "What is the best food for my dog?")
        self.assertEqual(chat_history[3].content, "The best food depends on your dog's breed and age.")

    def test_profile_memory_retrieval(self):
        # Insert a dog profile directly into the database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO questionnaire (user_id, breed, age, name, temperament)
            VALUES (?, ?, ?, ?, ?)
        """, (self.user_id, "Labrador", 3, "Buddy", "energetic"))
        conn.commit()
        conn.close()
        # Retrieve and verify the dog profile summary
        summary = self.profile_memory.get_pet_summary(self.user_id)
        expected_summary = f"{self.user_id} has a 3-year-old Labrador named Buddy, described as energetic."
        self.assertIsInstance(summary, list)
        self.assertGreater(len(summary), 0)
        self.assertEqual(summary[0], expected_summary)
        # Test retrieval for a user with no profile

    def test_profile_memory_retrieval_no_profile(self):
        summary = self.profile_memory.get_pet_summary("unknown_user")
        self.assertEqual(summary, "No dog profile found.")

if __name__ == '__main__':
    unittest.main()