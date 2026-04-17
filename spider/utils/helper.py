
from .db import get_connection

def execute(query, data=None):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, data)
            conn.commit()   # important!
        print("Query executed successfully!")
    except Exception as e:
        print(f"DB Error: {e}")

def insert_into_doc_info(url, title, description):
    query = """
    INSERT INTO doc_info (url, title, description)
    VALUES (%s, %s, %s)
    ON CONFLICT (url) DO NOTHING;
    """
    
    data = (url, title, description)
    execute(query, data)


def insert_into_inverted_index(term, docs_ids):
    query = """
    INSERT INTO inverted_index (term, docs_ids)
    VALUES (%s, %s)
    ON CONFLICT (term)
    DO UPDATE SET docs_ids = inverted_index.docs_ids || EXCLUDED.docs_ids;
    """
    
    data = (term, docs_ids)
    execute(query, data)

def insert_many_doc_info(data_list):
    try:

        query = """
        INSERT INTO doc_info (url, title, description)
        VALUES (%s, %s, %s)
        ON CONFLICT (url) DO NOTHING;
        """

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.executemany(query, data_list)
            conn.commit()

    except Exception as e:
        print("error" , e)

def insert_many_inverted_index(data_list):
    try:

        query = """
        INSERT INTO inverted_index (term, docs_ids)
        VALUES (%s, %s)

        """

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.executemany(query, data_list)
            conn.commit()

    except Exception as e:
        print("error:", e)