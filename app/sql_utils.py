import sqlite3

# Path to your SQLite database
DB_PATH = "db/ecommerce.db"  # Change if needed

def run_query(sql: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Allows access by column name
        cursor = conn.cursor()

        cursor.execute(sql)
        if sql.strip().lower().startswith("select"):
            rows = cursor.fetchall()
            result = [dict(row) for row in rows]
        else:
            conn.commit()
            result = {"status": "Query executed successfully."}

        cursor.close()
        conn.close()
        return result

    except Exception as e:
        return f"Error: {str(e)}"
