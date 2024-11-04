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
tables_to_sync = ['Empleados', 'Asistencias']

def sync_table(remote_conn, local_conn, table_name):
    with remote_conn.cursor() as remote_cur, local_conn.cursor() as local_cur:
        # Obtener los datos de la tabla remota
        remote_cur.execute(f"SELECT * FROM {table_name}")
        rows = remote_cur.fetchall()
        columns = [desc[0] for desc in remote_cur.description]

        # Limpiar la tabla local
        local_cur.execute(f"DELETE FROM {table_name}")

        # Insertar los datos en la tabla local
        placeholders = ', '.join(['?'] * len(columns))
        insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        local_cur.executemany(insert_query, rows)

        # Confirmar los cambios en la base de datos local
        local_conn.commit()

def sync_databases():
    # Conectar a las bases de datos remota y local
    remote_conn = pyodbc.connect(**remote_conn_info)
    local_conn = pyodbc.connect(**local_conn_info)

    try:
        for table in tables_to_sync:
            print(f"Sincronizando tabla {table}...")
            sync_table(remote_conn, local_conn, table)
            print(f"Tabla {table} sincronizada con éxito.")
    finally:
        # Cerrar las conexiones a las bases de datos
        remote_conn.close()
        local_conn.close()

if __name__ == "__main__":
    sync_databases()