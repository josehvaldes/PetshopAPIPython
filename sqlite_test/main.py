import sqlite3
import os
import traceback
import sys
database_dir = "petshopdb"
database_name = "petshop_database.db"

if not os.path.exists(database_dir):
        os.makedirs(database_dir)
db_path_absolute = os.path.join(os.getcwd(), database_dir, database_name)
print(f"DB Path: {db_path_absolute}")

def initialize_db():
    print("Initializing database...")
    try:
        conn_absolute = sqlite3.connect(db_path_absolute, check_same_thread=False)
        cursor = conn_absolute.cursor()
        cursor.executescript(open("./dbscripts/chat_history.sql").read())
        conn_absolute.commit()
        conn_absolute.close()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
        traceback.print_exc()
    finally:
        if conn_absolute:
            conn_absolute.close()

def test_db()-> bool:
    try:
         
        tablename = "chat_history" 
        conn_absolute = sqlite3.connect(db_path_absolute, check_same_thread=False)
        cursor = conn_absolute.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name ='{tablename}';")
        result = cursor.fetchone()
        return result is not None
    except Exception as e:
        print(f"Error testing database: {e}")
    finally:
        if conn_absolute:
            conn_absolute.close()

def load_data()->bool:
    try:
        conn_absolute = sqlite3.connect(db_path_absolute, check_same_thread=False)
        cursor = conn_absolute.cursor()
        cursor.executescript(open("./dbscripts/insert_sample_data.sql").read())
        conn_absolute.commit()
        conn_absolute.close()
        print("Sample data loaded successfully.")
        return True
    except Exception as e:
        print(f"Error loading sample data: {e}")
        traceback.print_exc()
        return False
    finally:
        if conn_absolute:
            conn_absolute.close()

if __name__ == "__main__":
    #initialize_db()
    if test_db() == False:
        initialize_db()
        load_data()
    else:
        print("DB already initialized.")

    # print("Arguments:", sys.argv)
    # if len(sys.argv) > 1 and sys.argv[1] == "load":
        
