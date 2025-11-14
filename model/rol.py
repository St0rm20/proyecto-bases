"""
Clase para la gestión de roles
Por: Juan David Ramirez Carmona y
Miguel Ángel Vargas Peláez
Fecha: 2025-11
Licencia: GPLv3
"""
from modelo_base import BaseModel
from dataclasses import dataclass
from typing import List

"""
Realmente esto nunca lo vamos a usar JSAJAJJSASJSJSJ
Ahí está por si acaso :v
"""

@dataclass
class RolData:
    """Representa un rol en el sistema"""
    id_rol: int
    nombre: str

    def __str__(self):
        return f"Rol(id={self.id_rol}, nombre='{self.nombre}')"


class Rol(BaseModel):
    """Gestión de roles"""

    def get_table_name(self):
        return "Rol"

    def get_primary_key(self):
        return "id_rol"

    def crear(self, id_rol: int, nombre: str) -> bool:
        """Crea un nuevo rol"""
        sql = """
            INSERT INTO Rol (id_rol, nombre)
            VALUES (:id_rol, :nombre)
        """
        try:
            self.db.execute_query(sql, {
                'id_rol': id_rol,
                'nombre': nombre
            }, fetch=False)
            return True
        except Exception as e:
            print(f"Error al crear rol: {e}")
            return False

    def actualizar(self, id_rol: int, nombre: str) -> bool:
        """Actualiza un rol existente"""
        sql = """
            UPDATE Rol 
            SET nombre = :nombre
            WHERE id_rol = :id_rol
        """
        try:
            filas = self.db.execute_query(sql, {
                'id_rol': id_rol,
                'nombre': nombre
            }, fetch=False)
            return filas > 0
        except Exception as e:
            print(f"Error al actualizar rol: {e}")
            return False

    def obtener_todos_como_objetos(self) -> List[RolData]:
        """Obtiene todos los roles como objetos"""
        resultados = self.obtener_todos()
        return [RolData(id_rol=r[0], nombre=r[1]) for r in resultados]

    def buscar_por_nombre(self, nombre: str) -> List[RolData]:
        """Busca roles por nombre (búsqueda parcial)"""
        sql = "SELECT * FROM Rol WHERE UPPER(nombre) LIKE UPPER(:nombre)"
        resultados = self.db.execute_query(sql, {'nombre': f'%{nombre}%'})
        return [RolData(id_rol=r[0], nombre=r[1]) for r in resultados]