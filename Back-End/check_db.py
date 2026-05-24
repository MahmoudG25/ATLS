import psycopg2

try:
    conn = psycopg2.connect(
        dbname="erp_db",
        user="postgres",
        host="localhost",
        password="postgres",
        port=5432,
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'reports_dailytaskreport'
    """)
    rows = cur.fetchall()
    for row in rows:
        print(f"Column: {row[0]}, Type: {row[1]}")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
