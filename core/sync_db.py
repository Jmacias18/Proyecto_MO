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

def get_connection(conn_info):
    if 'trusted_connection' in conn_info and conn_info['trusted_connection'] == 'yes':
        return pyodbc.connect(
            driver=conn_info['driver'],
            server=conn_info['server'],
            database=conn_info['database'],
            trusted_connection='yes'
        )
    else:
        return pyodbc.connect(
            driver=conn_info['driver'],
            server=conn_info['server'],
            database=conn_info['database'],
            uid=conn_info['uid'],
            pwd=conn_info['pwd']
        )

def sync_table(remote_conn, local_conn, table_name):
    with remote_conn.cursor() as remote_cur, local_conn.cursor() as local_cur:
        # Obtener los datos de la tabla remota
        remote_cur.execute(f"SELECT * FROM {table_name}")
        rows = remote_cur.fetchall()
        columns = [desc[0] for desc in remote_cur.description]

        # Activar IDENTITY_INSERT para la tabla
        local_cur.execute(f"SET IDENTITY_INSERT {table_name} ON")

        # Insertar o actualizar los datos en la tabla local
        for row in rows:
            row_dict = dict(zip(columns, row))
            try:
                local_cur.execute(
                    f"INSERT INTO {table_name} (ID_Pro, Nombre_Pro, Estado_Pro) VALUES (?, ?, ?)",
                    row_dict['ID_Pro'], row_dict['Nombre_Pro'], row_dict['Estado_Pro']
                )
            except pyodbc.IntegrityError:
                local_cur.execute(
                    f"UPDATE {table_name} SET Nombre_Pro = ?, Estado_Pro = ? WHERE ID_Pro = ?",
                    row_dict['Nombre_Pro'], row_dict['Estado_Pro'], row_dict['ID_Pro']
                )

        # Desactivar IDENTITY_INSERT para la tabla
        local_cur.execute(f"SET IDENTITY_INSERT {table_name} OFF")

        # Confirmar los cambios en la base de datos local
        local_conn.commit()

def sync_databases():
    # Conectar a las bases de datos local y remota
    local_conn = get_connection(local_conn_info)
    remote_conn = get_connection(remote_conn_info)

    try:
        tables_to_sync = ['Procesos']  # Lista de tablas a sincronizar
        for table in tables_to_sync:
            print(f"Sincronizando tabla {table}...")
            sync_table(remote_conn, local_conn, table)
            print(f"Tabla {table} sincronizada con éxito.")
    finally:
        # Cerrar las conexiones a las bases de datos
        local_conn.close()
        remote_conn.close()

if __name__ == "__main__":
    sync_databases()