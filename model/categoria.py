"""
Clase para la gestión de categorías
Por: Juan David Ramirez Carmona y Miguel Ángel Vargas Peláez
Fecha: 2025-11
Licencia: GPLv3
"""
from modelo_base import BaseModel
from dataclasses import dataclass
from typing import List
from decimal import Decimal


@dataclass
class CategoriaData:
    """Representa una categoría de productos"""
    codigo_categoria: int
    iva: Decimal
    utilidad: Decimal
    nombre: str  # <-- AÑADIDO

    def __str__(self):
        return f"Categoria(codigo={self.codigo_categoria}, nombre='{self.nombre}', IVA={self.iva}, Utilidad={self.utilidad}%)"


class Categoria(BaseModel):
    """Gestión de categorías"""

    def get_table_name(self):
        return "Categoria"

    def get_primary_key(self):
        return "codigo_categoria"

    def crear(self, codigo_categoria: int, iva: Decimal, utilidad: Decimal, nombre: str) -> bool:
        """Crea una nueva categoría"""
        # Se añade 'nombre' a la consulta
        sql = """
            INSERT INTO Categoria (codigo_categoria, iva, utilidad, nombre)
            VALUES (:codigo_categoria, :iva, :utilidad, :nombre)
        """
        try:
            self.db.execute_query(sql, {
                'codigo_categoria': codigo_categoria,
                'iva': iva,
                'utilidad': utilidad,
                'nombre': nombre  # <-- AÑADIDO
            }, fetch=False)
            return True
        except Exception as e:
            print(f"Error al crear categoría: {e}")
            return False

    def actualizar(self, codigo_categoria: int, iva: Decimal = None, utilidad: Decimal = None, nombre: str = None) -> bool:
        """Actualiza una categoría existente"""
        campos = []
        params = {'codigo_categoria': codigo_categoria}

        if iva is not None:
            campos.append("iva = :iva")
            params['iva'] = iva
        if utilidad is not None:
            campos.append("utilidad = :utilidad")
            params['utilidad'] = utilidad
        if nombre is not None:  # <-- AÑADIDO
            campos.append("nombre = :nombre")
            params['nombre'] = nombre

        if not campos:
            return False

        sql = f"UPDATE Categoria SET {', '.join(campos)} WHERE codigo_categoria = :codigo_categoria"

        try:
            filas = self.db.execute_query(sql, params, fetch=False)
            return filas > 0
        except Exception as e:
            print(f"Error al actualizar categoría: {e}")
            return False

    def obtener_todos_como_objetos(self) -> List[CategoriaData]:
        """Obtiene todas las categorías como objetos"""
        resultados = self.obtener_todos()
        return [CategoriaData(*r) for r in resultados]

    def obtener_por_codigo(self, codigo_categoria: int) -> CategoriaData:
        """Obtiene una categoría por su código"""
        resultado = self.obtener_por_id(codigo_categoria)
        return CategoriaData(*resultado) if resultado else None