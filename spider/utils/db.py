import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

def get_connection():
    try:
        conn =  psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_DATABASE"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT")
        )
        print('connnected successfully')

        return conn
    except Exception as e:
        raise Exception(f"DB Connection Error: {e}")
    
get_connection()