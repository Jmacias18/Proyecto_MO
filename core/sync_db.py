import pyodbc

# Configuración de la conexión a la base de datos remota SPF_Info
remote_info_conn_info = {
    'driver': '{ODBC Driver 17 for SQL Server}',
    'server': r'192.168.0.5\SQLEXPRESS',
    'database': 'SPF_Info',
    'uid': 'IT',
    'pwd': 'sqlSPF#2024'
}

# Configuración de la conexión a la base de datos remota SPF_HRS_MO
remote_hrs_conn_info = {
    'driver': '{ODBC Driver 17 for SQL Server}',
    'server': r'192.168.0.5\SQLEXPRESS',
    'database': 'SPF_HRS_MO',
    'uid': 'IT',
    'pwd': 'sqlSPF#2024'
}

# Configuración de la conexión a la base de datos local SPF_HRS_MO
local_hrs_conn_info = {
    'driver': '{ODBC Driver 17 for SQL Server}',
    'server': 'localhost\\SQLEXPRESS',
    'database': 'SPF_HRS_MO',
    'trusted_connection': 'yes'
}

# Configuración de la conexión a la base de datos local SPF_Info
local_info_conn_info = {
    'driver': '{ODBC Driver 17 for SQL Server}',
    'server': 'localhost\\SQLEXPRESS',
    'database': 'SPF_Info',
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

def table_exists(conn, table_name):
    query = f"SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{table_name}'"
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchone() is not None

def has_identity_column(conn, table_name):
    query = f"""
    SELECT COLUMN_NAME 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME = '{table_name}' AND COLUMNPROPERTY(object_id(TABLE_NAME), COLUMN_NAME, 'IsIdentity') = 1
    """
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchone() is not None

def sync_table(remote_conn, local_conn, table_name, primary_key, where_clause=""):
    with remote_conn.cursor() as remote_cur, local_conn.cursor() as local_cur:
        # Obtener todos los datos de la tabla remota con la cláusula WHERE
        query = f"SELECT * FROM dbo.{table_name} {where_clause}"
        remote_cur.execute(query)
        remote_rows = remote_cur.fetchall()
        remote_columns = [desc[0] for desc in remote_cur.description]
        primary_key_index = remote_columns.index(primary_key)

        remote_data = {row[primary_key_index]: row for row in remote_rows}

        # Obtener todos los datos de la tabla local
        local_cur.execute(f"SELECT * FROM dbo.{table_name}")
        local_rows = local_cur.fetchall()
        local_columns = [desc[0] for desc in local_cur.description]
        primary_key_index_local = local_columns.index(primary_key)

        local_data = {row[primary_key_index_local]: row for row in local_rows}

        # Verificar si la tabla tiene una columna de identidad
        identity_column = has_identity_column(local_conn, table_name)

        # Insertar o actualizar registros que están en la tabla remota
        placeholders = ', '.join(['?'] * len(remote_columns))
        update_set = ', '.join([f"{col}=?" for col in remote_columns if col != primary_key])

        for key, remote_row in remote_data.items():
            if key in local_data:
                # Comparar y actualizar si los datos son diferentes
                local_row = local_data[key]
                if remote_row != local_row:
                    local_cur.execute(
                        f"UPDATE dbo.{table_name} SET {update_set} WHERE {primary_key} = ?",
                        [remote_row[remote_columns.index(col)] for col in remote_columns if col != primary_key] + [key]
                    )
            else:
                # Insertar nuevo registro
                if identity_column:
                    local_cur.execute(f"SET IDENTITY_INSERT dbo.{table_name} ON")
                local_cur.execute(
                    f"INSERT INTO dbo.{table_name} ({', '.join(remote_columns)}) VALUES ({placeholders})",
                    [remote_row[remote_columns.index(col)] for col in remote_columns]
                )
                if identity_column:
                    local_cur.execute(f"SET IDENTITY_INSERT dbo.{table_name} OFF")

        # Eliminar registros que están en la tabla local pero no en la tabla remota
        for key in local_data.keys():
            if key not in remote_data:
                local_cur.execute(f"DELETE FROM dbo.{table_name} WHERE {primary_key} = ?", key)

        # Confirmar los cambios en la base de datos local
        local_conn.commit()
def sync_databases():
    # Conectar a las bases de datos local y remota
    remote_hrs_conn = get_connection(remote_hrs_conn_info)
    remote_info_conn = get_connection(remote_info_conn_info)
    local_hrs_conn = get_connection(local_hrs_conn_info)
    local_info_conn = get_connection(local_info_conn_info)

    try:
        # Sincronizar tabla Procesos en SPF_HRS_MO
        print("Sincronizando tabla Procesos desde SPF_HRS_MO a SPF_HRS_MO local...")
        sync_table(remote_hrs_conn, local_hrs_conn, 'Procesos', 'ID_Pro')
        print("Tabla Procesos sincronizada con éxito en SPF_HRS_MO local.")
        
        # Sincronizar tabla Empleados con condiciones específicas
        print("Sincronizando tabla Empleados desde SPF_HRS_MO a SPF_HRS_MO local con condiciones específicas...")
        where_clause = "WHERE Estado = 'A' AND ID_Departamento IN (12, 16, 17, 18, 19, 20, 21, 22, 23)"
        sync_table(remote_hrs_conn, local_hrs_conn, 'Empleados', 'Codigo_Emp', where_clause)
        print("Tabla Empleados sincronizada con éxito en SPF_HRS_MO local con condiciones específicas.")

        # Sincronizar tablas en SPF_Info
        print("Sincronizando tabla Departamentos desde SPF_Info a SPF_Info local...")
        sync_table(remote_info_conn, local_info_conn, 'Departamentos', 'ID_Departamento')
        print("Tabla Departamentos sincronizada con éxito en SPF_Info local.")
        
        print("Sincronizando tabla Productos desde SPF_Info a SPF_Info local...")
        sync_table(remote_info_conn, local_info_conn, 'Productos', 'ID_Producto')
        print("Tabla Productos sincronizada con éxito en SPF_Info local.")
        
        print("Sincronizando tabla Tipo_Asist desde SPF_Info a SPF_Info local...")
        sync_table(remote_info_conn, local_info_conn, 'Tipo_Asist', 'ID_Asis')
        print("Tabla Tipo_Asist sincronizada con éxito en SPF_Info local.")
        
        print("Sincronizando tabla Turnos desde SPF_Info a SPF_Info local...")
        sync_table(remote_info_conn, local_info_conn, 'Turnos', 'ID_Turno')
        print("Tabla Turnos sincronizada con éxito en SPF_Info local.")
        
        # Sincronizar tabla Motivo en SPF_HRS_MO
        if table_exists(remote_hrs_conn, 'Motivo'):
            print("Sincronizando tabla Motivo desde SPF_HRS_MO a SPF_HRS_MO local...")
            sync_table(remote_hrs_conn, local_hrs_conn, 'Motivo', 'ID')
            print("Tabla Motivo sincronizada con éxito en SPF_HRS_MO local.")
        else:
            print("La tabla 'Motivo' no existe en la base de datos remota SPF_HRS_MO.")
        
    finally:
        # Cerrar las conexiones a las bases de datos
        remote_hrs_conn.close()
        remote_info_conn.close()
        local_hrs_conn.close()
        local_info_conn.close()

if __name__ == "__main__":
    sync_databases()