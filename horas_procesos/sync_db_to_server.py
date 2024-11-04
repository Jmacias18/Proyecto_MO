import pyodbc

# Configuración de la conexión a la base de datos remota
remote_conn_info = {
    'driver': '{ODBC Driver 17 for SQL Server}',
    'server': r'QBSERVER\SQLEXPRESS',
    'database': 'SPF_HRS_MO',
    'uid': 'IT',
    'pwd': 'sqlSPF#2024'
}

# Configuración de la conexión a la base de datos local
local_conn_info = {
    'driver': '{ODBC Driver 17 for SQL Server}',
    'server': 'localhost\\SQLEXPRESS',
    'database': 'SPF_HRS_MO',
    'trusted_connection': 'yes'
}

# Lista de tablas a sincronizar
tables_to_sync = ['HorasProcesos']

def sync_table(local_conn, remote_conn, table_name):
    with local_conn.cursor() as local_cur, remote_conn.cursor() as remote_cur:
        # Obtener los datos de la tabla local
        local_cur.execute(f"SELECT * FROM {table_name}")
        rows = local_cur.fetchall()
        columns = [desc[0] for desc in local_cur.description]

        # Limpiar la tabla remota
        remote_cur.execute(f"DELETE FROM {table_name}")

        # Insertar los datos en la tabla remota
        placeholders = ', '.join(['?'] * len(columns))
        insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        remote_cur.executemany(insert_query, rows)

        # Confirmar los cambios en la base de datos remota
        remote_conn.commit()

        # Actualizar el campo SYNC a 1 en la tabla local
        local_cur.execute(f"UPDATE {table_name} SET SYNC = 1")
        local_conn.commit()

        # Actualizar el campo SYNC a 1 en la tabla remota
        remote_cur.execute(f"UPDATE {table_name} SET SYNC = 1")
        remote_conn.commit()

def sync_databases():
    # Conectar a las bases de datos local y remota
    local_conn = pyodbc.connect(**local_conn_info)
    remote_conn = pyodbc.connect(**remote_conn_info)

    try:
        for table in tables_to_sync:
            print(f"Sincronizando tabla {table}...")
            sync_table(local_conn, remote_conn, table)
            print(f"Tabla {table} sincronizada con éxito.")
    finally:
        # Cerrar las conexiones a las bases de datos
        local_conn.close()
        remote_conn.close()

if __name__ == "__main__":
    sync_databases()