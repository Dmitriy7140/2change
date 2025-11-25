import psycopg2

conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password="Vv189895344")

cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT ALREADY EXISTS
""")

conn.commit()
cur.close()
conn.close()