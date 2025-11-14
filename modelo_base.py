from abc import ABC, abstractmethod
from database.connection import DatabaseConfig


"""
Básicamente todo hace lo mismo, recibe self de parametro
define la Query de lo que va a hacer y la ejecuta con la conexión a la DB
y si es necesario retorna el resultado
Y ya, facilito el tutorial
"""
class BaseModel(ABC):
    """Clase base para todos los modelos con operaciones CRUD genéricas
    Contiene metodos de obtener todos, obtener por ID, eliminar y verificar existencia.
    Es abstracta y debe ser extendida por modelos específicos."""

    def __init__(self):
        self.db = DatabaseConfig()

    @abstractmethod
    def get_table_name(self):
        """Debe retornar el nombre de la tabla en la base de datos"""
        pass
    """El pass es necesario para que la clase abstracta funcione correctamente."""
    #No sabia para qué era XD

    @abstractmethod
    def get_primary_key(self):
        """Debe retornar el nombre de la clave primaria"""
        pass

    def obtener_todos(self):
        """Obtiene todos los registros de la tabla"""
        sql = f"SELECT * FROM {self.get_table_name()}"
        return self.db.execute_query(sql)

    #self es la instancia de la clase actual que extiende BaseModel
    """Por ejemplo, si tenemos una clase Cliente que extiende BaseModel, 
    al llamar a self.get_table_name() dentro de Cliente, se ejecutará el 
    método get_table_name() definido en Cliente, devolviendo "Cliente"."""



    def obtener_por_id(self, id_valor):
        """Obtiene un registro por su ID"""
        sql = f"SELECT * FROM {self.get_table_name()} WHERE {self.get_primary_key()} = :id"
        resultado = self.db.execute_query(sql, {'id': id_valor})
        return resultado[0] if resultado else None

    def eliminar(self, id_valor):
        """Elimina un registro por su ID"""
        sql = f"DELETE FROM {self.get_table_name()} WHERE {self.get_primary_key()} = :id"
        filas_afectadas = self.db.execute_query(sql, {'id': id_valor}, fetch=False)
        return filas_afectadas > 0

    def existe(self, id_valor):
        """Verifica si un registro existe"""
        sql = f"SELECT COUNT(*) FROM {self.get_table_name()} WHERE {self.get_primary_key()} = :id"
        resultado = self.db.execute_query(sql, {'id': id_valor})
        return resultado[0][0] > 0