import pyodbc

# Configuración de la conexión a la base de datos remota
remote_conn_info = {
    'driver': '{ODBC Driver 17 for SQL Server}',
    'server': r'192.168.0.5\SQLEXPRESS',
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
tables_to_sync = ['HorasProcesos', 'Procesos']

def sync_table(local_conn, remote_conn, table_name):
    with local_conn.cursor() as local_cur, remote_conn.cursor() as remote_cur:
        # Obtener los datos de la tabla local
        local_cur.execute(f"SELECT * FROM {table_name}")
        rows = local_cur.fetchall()
        columns = [desc[0] for desc in local_cur.description]

        # Determinar la clave primaria y preparar la consulta de inserción o actualización
        if table_name == 'HorasProcesos':
            primary_key = 'ID_HrsProcesos'
            # Asegurarse de que el campo SYNC se actualice a 1
            update_columns = ', '.join([f"{col}=source.{col}" for col in columns if col != primary_key and col != 'SYNC']) + ", SYNC=1"
        elif table_name == 'Procesos':
            primary_key = 'ID_Pro'
            update_columns = ', '.join([f"{col}=source.{col}" for col in columns if col != primary_key])
        else:
            raise ValueError(f"Clave primaria no definida para la tabla {table_name}")

        placeholders = ', '.join(['?'] * len(columns))
        insert_query = f"""
            MERGE INTO {table_name} AS target
            USING (VALUES ({placeholders})) AS source ({', '.join(columns)})
            ON target.{primary_key} = source.{primary_key}
            WHEN MATCHED THEN
                UPDATE SET {update_columns}
            WHEN NOT MATCHED THEN
                INSERT ({', '.join(columns)}) VALUES ({placeholders});
        """

        # Activar IDENTITY_INSERT para la tabla si es necesario
        if table_name == 'Procesos':
            remote_cur.execute(f"SET IDENTITY_INSERT {table_name} ON")

        # Insertar o actualizar los datos en la tabla remota
        for row in rows:
            row_data = tuple(row)  # Convertir la fila a una tupla
            remote_cur.execute(insert_query, row_data + row_data)  # Duplicar los parámetros para la cláusula INSERT

        # Desactivar IDENTITY_INSERT para la tabla si es necesario
        if table_name == 'Procesos':
            remote_cur.execute(f"SET IDENTITY_INSERT {table_name} OFF")

        # Confirmar los cambios en la base de datos remota
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