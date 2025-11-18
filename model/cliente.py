"""
Clase para la gestión de clientes
Por: Juan David Ramirez Carmona y
Miguel Ángel Vargas Peláez
Fecha: 2025-11
Licencia: GPLv3
"""

from modelo_base import BaseModel
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class ClienteData:
    """Representa un cliente (solo datos de contacto)"""
    codigo_cliente: int
    nombre: str
    telefono: Optional[str] = None
    departamento: Optional[str] = None
    municipio: Optional[str] = None
    calle: Optional[str] = None
    direccion: Optional[str] = None

    def __str__(self):
        return f"Cliente(codigo={self.codigo_cliente}, nombre='{self.nombre}')"

    def __repr__(self):
        return f"ClienteData(codigo_cliente={self.codigo_cliente!r}, nombre={self.nombre!r})"


class Cliente(BaseModel):
    """Gestión de clientes"""

    def get_table_name(self):
        return "Cliente"

    def get_primary_key(self):
        return "codigo_cliente"

    def crear(self, codigo_cliente: int, nombre: str, telefono: str = None,
              departamento: str = None, municipio: str = None, calle: str = None,
              direccion: str = None) -> bool:
        """Crea un nuevo cliente"""

        sql = """
            INSERT INTO Cliente (codigo_cliente, nombre, telefono, departamento, 
                                municipio, calle, direccion)
            VALUES (:codigo_cliente, :nombre, :telefono, :departamento, 
                    :municipio, :calle, :direccion)
        """
        try:
            self.db.execute_query(sql, {
                'codigo_cliente': codigo_cliente,
                'nombre': nombre,
                'telefono': telefono,
                'departamento': departamento,
                'municipio': municipio,
                'calle': calle,
                'direccion': direccion
            }, fetch=False)
            return True
        except Exception as e:
            print(f"Error al crear cliente: {e}")
            return False

    def actualizar(self, codigo_cliente: int, nombre: str = None, telefono: str = None,
                   departamento: str = None, municipio: str = None, calle: str = None,
                   direccion: str = None) -> bool:
        """Actualiza un cliente existente (solo los campos proporcionados)"""
        campos = []
        params = {'codigo_cliente': codigo_cliente}

        if nombre is not None:
            campos.append("nombre = :nombre")
            params['nombre'] = nombre
        if telefono is not None:
            campos.append("telefono = :telefono")
            params['telefono'] = telefono
        if departamento is not None:
            campos.append("departamento = :departamento")
            params['departamento'] = departamento
        if municipio is not None:
            campos.append("municipio = :municipio")
            params['municipio'] = municipio
        if calle is not None:
            campos.append("calle = :calle")
            params['calle'] = calle
        if direccion is not None:
            campos.append("direccion = :direccion")
            params['direccion'] = direccion

        if not campos:
            return False

        sql = f"UPDATE Cliente SET {', '.join(campos)} WHERE codigo_cliente = :codigo_cliente"

        try:
            filas = self.db.execute_query(sql, params, fetch=False)
            return filas > 0
        except Exception as e:
            print(f"Error al actualizar cliente: {e}")
            return False

    def obtener_todos_como_objetos(self) -> List[ClienteData]:
        """Obtiene todos los clientes como objetos"""
        resultados = self.obtener_todos()
        return [ClienteData(*r) for r in resultados]

    def buscar_por_nombre(self, nombre: str) -> List[ClienteData]:
        """Busca clientes por nombre"""
        sql = "SELECT * FROM Cliente WHERE UPPER(nombre) LIKE UPPER(:nombre)"
        resultados = self.db.execute_query(sql, {'nombre': f'%{nombre}%'})
        return [ClienteData(*r) for r in resultados]

    def buscar_por_municipio(self, municipio: str) -> List[ClienteData]:
        """Busca clientes por municipio"""
        sql = "SELECT * FROM Cliente WHERE UPPER(municipio) = UPPER(:municipio)"
        resultados = self.db.execute_query(sql, {'municipio': municipio})
        return [ClienteData(*r) for r in resultados]

    def eliminar(self, id_valor):
        """Elimina un cliente por su código"""
        sql = "DELETE FROM Cliente WHERE codigo_cliente = :id_valor"
        try:
            filas = self.db.execute_query(sql, {'id_valor': id_valor}, fetch=False)
            return filas > 0
        except Exception as e:
            print(f"Error al eliminar cliente: {e}")
            return False

    def obtener_por_codigo(self, codigo_cliente: int) -> ClienteData:
        """Obtiene un cliente por su código"""
        resultado = self.obtener_por_id(codigo_cliente)
        return ClienteData(*resultado) if resultado else None