import pyodbc
from datetime import datetime, timedelta

# Configuración de la conexión a la base de datos remota TempusAccesos
remote_conn_info = {
    'driver': '{ODBC Driver 17 for SQL Server}',
    'server': r'192.168.0.9\SPFSQLSERVER',
    'database': 'TempusAccesos',
    'uid': 'IT',
    'pwd': 'sqlSPF#2024'
}

# Configuración de la conexión a la base de datos local TempusAccesos
local_conn_info = {
    'driver': '{ODBC Driver 17 for SQL Server}',
    'server': 'localhost\\SQLEXPRESS',
    'database': 'TempusAccesos',
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

def sync_checkinout_table(remote_conn, local_conn):
    with remote_conn.cursor() as remote_cur, local_conn.cursor() as local_cur:
        # Calcular las fechas de hoy y de ayer
        today = datetime.today()
        yesterday = today - timedelta(days=1)

        # Formatear las fechas
        today_str = today.strftime('%Y-%m-%d')
        yesterday_str = yesterday.strftime('%Y-%m-%d')

        # Obtener datos de la tabla remota para hoy y ayer
        query = f"""
        SELECT [USERID], [CHECKTIME], [CHECKTYPE], [VERIFYCODE], [SENSORID], [LOGID], 
               [MachineId], [UserExtFmt], [WorkCode], [Memoinfo], [sn]
        FROM [dbo].[CHECKINOUT]
        WHERE CONVERT(date, [CHECKTIME]) IN ('{today_str}', '{yesterday_str}')
        """
        remote_cur.execute(query)
        remote_rows = remote_cur.fetchall()
        remote_columns = [desc[0] for desc in remote_cur.description]

        # Borrar datos existentes en la tabla local para hoy y ayer
        delete_query = f"""
        DELETE FROM [dbo].[CHECKINOUT]
        WHERE CONVERT(date, [CHECKTIME]) IN ('{today_str}', '{yesterday_str}')
        """
        local_cur.execute(delete_query)

        # Habilitar IDENTITY_INSERT para la tabla CHECKINOUT
        local_cur.execute("SET IDENTITY_INSERT [dbo].[CHECKINOUT] ON")

        # Insertar datos remotos en la tabla local
        placeholders = ', '.join(['?'] * len(remote_columns))
        insert_query = f"INSERT INTO [dbo].[CHECKINOUT] ({', '.join(remote_columns)}) VALUES ({placeholders})"
        for row in remote_rows:
            local_cur.execute(insert_query, row)

        # Deshabilitar IDENTITY_INSERT después de la inserción
        local_cur.execute("SET IDENTITY_INSERT [dbo].[CHECKINOUT] OFF")

        # Confirmar los cambios en la base de datos local
        local_conn.commit()

def sync_userinfo_table(remote_conn, local_conn):
    with remote_conn.cursor() as remote_cur, local_conn.cursor() as local_cur:
        # Obtener usuarios cuyo Badgenumber comienza con '13'
        query = """
        SELECT [USERID], [Badgenumber], [SSN], [Name], [Gender], [TITLE], [PAGER], [BIRTHDAY], [HIREDDAY], 
               [street], [CITY], [STATE], [ZIP], [OPHONE], [FPHONE], [VERIFICATIONMETHOD], [DEFAULTDEPTID], 
               [SECURITYFLAGS], [ATT], [INLATE], [OUTEARLY], [OVERTIME], [SEP], [HOLIDAY], [MINZU], [PASSWORD], 
               [LUNCHDURATION], [PHOTO], [mverifypass], [Notes], [privilege], [InheritDeptSch], [InheritDeptSchClass], 
               [AutoSchPlan], [MinAutoSchInterval], [RegisterOT], [InheritDeptRule], [EMPRIVILEGE], [CardNo], 
               [change_operator], [change_time], [create_operator], [create_time], [delete_operator], [delete_time], 
               [status], [lastname], [AccGroup], [TimeZones], [identitycard], [UTime], [Education], [OffDuty], 
               [DelTag], [morecard_group_id], [set_valid_time], [acc_startdate], [acc_enddate], [birthplace], 
               [Political], [contry], [hiretype], [email], [firedate], [isatt], [homeaddress], [emptype], [bankcode1], 
               [bankcode2], [isblacklist], [Iuser1], [Iuser2], [Iuser3], [Iuser4], [Iuser5], [Cuser1], [Cuser2], 
               [Cuser3], [Cuser4], [Cuser5], [Duser1], [Duser2], [Duser3], [Duser4], [Duser5], [OfflineBeginDate], 
               [OfflineEndDate], [carNo], [carType], [carBrand], [carColor], [ID_GrupoSincronizacion], [Conexion], 
               [CreadoEn]
        FROM [dbo].[USERINFO]
        WHERE [Badgenumber] LIKE '13%'
        """
        remote_cur.execute(query)
        remote_rows = remote_cur.fetchall()
        remote_columns = [desc[0] for desc in remote_cur.description]

        # Borrar datos existentes en la tabla local para esos usuarios
        delete_query = """
        DELETE FROM [dbo].[USERINFO]
        WHERE [Badgenumber] LIKE '13%'
        """
        local_cur.execute(delete_query)

        # Habilitar IDENTITY_INSERT para la tabla USERINFO
        local_cur.execute("SET IDENTITY_INSERT [dbo].[USERINFO] ON")

        # Insertar datos remotos en la tabla local
        placeholders = ', '.join(['?'] * len(remote_columns))
        insert_query = f"INSERT INTO [dbo].[USERINFO] ({', '.join(remote_columns)}) VALUES ({placeholders})"
        for row in remote_rows:
            local_cur.execute(insert_query, row)

        # Deshabilitar IDENTITY_INSERT después de la inserción
        local_cur.execute("SET IDENTITY_INSERT [dbo].[USERINFO] OFF")

        # Confirmar los cambios en la base de datos local
        local_conn.commit()

def sync_databases():
    # Conectar a las bases de datos local y remota
    remote_conn = get_connection(remote_conn_info)
    local_conn = get_connection(local_conn_info)

    try:
        # Sincronizar la tabla CHECKINOUT
        print("Sincronizando tabla CHECKINOUT desde TempusAccesos remota a TempusAccesos local...")
        sync_checkinout_table(remote_conn, local_conn)
        print("Tabla CHECKINOUT sincronizada con éxito en TempusAccesos local.")

        # Sincronizar la tabla USERINFO
        print("Sincronizando tabla USERINFO desde TempusAccesos remota a TempusAccesos local...")
        sync_userinfo_table(remote_conn, local_conn)
        print("Tabla USERINFO sincronizada con éxito en TempusAccesos local.")
    finally:
        # Cerrar las conexiones a las bases de datos
        remote_conn.close()
        local_conn.close()

if __name__ == "__main__":
    sync_databases()