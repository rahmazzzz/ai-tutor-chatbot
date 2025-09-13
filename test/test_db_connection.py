# test/test_sqlalchemy_connection.py
from sqlalchemy import text
from app.clients.supabase_client import engine

def test_sqlalchemy_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()
            print("✅ SQLAlchemy connected to database!")
            print("Postgres version:", version[0])
    except Exception as e:
        print("❌ SQLAlchemy connection failed:", e)

if __name__ == "__main__":
    test_sqlalchemy_connection()
