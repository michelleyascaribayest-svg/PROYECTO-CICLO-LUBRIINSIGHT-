import psycopg2

configs = [
    {"host": "localhost", "port": 5432, "dbname": "Lubricadora", "user": "postgres", "password": "isa123"},
    {"host": "127.0.0.1", "port": 5432, "dbname": "Lubricadora", "user": "postgres", "password": "isa123"},
]

for cfg in configs:
    print(f"\n--- Probando con host={cfg['host']} ---")
    try:
        conn = psycopg2.connect(connect_timeout=5, **cfg)
        print("¡CONEXIÓN EXITOSA!")
        conn.close()
    except Exception as e:
        print("Tipo de error:", type(e).__name__)
        print("repr(e):", repr(e))
        print("str(e):", str(e))
        print("args:", e.args)
        if hasattr(e, "pgcode"):
            print("pgcode:", e.pgcode)
        if hasattr(e, "pgerror"):
            print("pgerror:", e.pgerror)