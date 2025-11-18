import oracledb
from contextlib import contextmanager


class DatabaseConfig:
    """Configuración centralizada de la base de datos"""

    DB_USER = "system"
    DB_PASSWORD = "password"
    DB_HOST = "localhost"
    DB_PORT = 1521
    DB_SID = "xe"

    @classmethod
    @contextmanager
    def get_connection(cls):
        """Context manager para manejar conexiones de forma segura,
        Utiliza oracledb para conectarse a Oracle DB. XE no sirve XD
        Simplemente usa este método para obtener una conexión."""
        connection = None
        try:
            connection = oracledb.connect(
                user=cls.DB_USER,
                password=cls.DB_PASSWORD,
                host=cls.DB_HOST,
                port=cls.DB_PORT,
                sid=cls.DB_SID
            )
            yield connection
        except oracledb.DatabaseError as e:
            print(f"Error de base de datos: {e}")
            raise
        finally:
            if connection:
                connection.close()

    @classmethod
    def execute_query(cls, sql, params=None, fetch=True):
        """Ejecuta una consulta SQL y retorna los resultados
        with opciones para parámetros y fetch de resultados."""
        with cls.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, params or {})

                if fetch:
                    return cursor.fetchall()
                else:
                    conn.commit()
                    return cursor.rowcount

    @classmethod
    def execute_many(cls, sql, data_list):
        """Ejecuta múltiples inserciones
        Esperemos no usar esto :c"""
        with cls.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.executemany(sql, data_list)
                conn.commit()
                return cursor.rowcount


def get_connection():
    """Función auxiliar para obtener una conexión directa"""
    return oracledb.connect(
        user=DatabaseConfig.DB_USER,
        password=DatabaseConfig.DB_PASSWORD,
        host=DatabaseConfig.DB_HOST,
        port=DatabaseConfig.DB_PORT,
        sid=DatabaseConfig.DB_SID
    )