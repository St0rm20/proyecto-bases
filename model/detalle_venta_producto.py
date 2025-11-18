"""
Clase para la gestión de detalles de venta (productos vendidos en una venta)
Por: Juan David Ramirez Carmona y
Miguel Ángel Vargas Peláez
Fecha: 2025-11
Licencia: GPLv3
"""

from modelo_base import BaseModel
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class DetalleVentaProductoData:
    """Representa un detalle de venta (producto dentro de una venta)"""
    id_venta: int
    codigo_producto: int
    cantidad: int

    def __str__(self):
        return (f"DetalleVentaProducto(venta={self.id_venta}, "
                f"producto={self.codigo_producto}, cantidad={self.cantidad})")


class DetalleVentaProducto(BaseModel):
    """Gestión de detalles de venta con clave primaria compuesta"""

    def get_table_name(self):
        return "DetalleVentaProducto"

    def get_primary_key(self):
        # Clave primaria compuesta
        return ("id_venta", "codigo_producto")

    # ---------------------------------------------------------
    # CREAR
    # ---------------------------------------------------------
    def crear(self, id_venta: int, codigo_producto: int, cantidad: int = 1) -> bool:
        """Crea un nuevo detalle de venta"""

        sql = """
            INSERT INTO DetalleVentaProducto (id_venta, codigo_producto, cantidad)
            VALUES (:id_venta, :codigo_producto, :cantidad)
        """
        try:
            self.db.execute_query(sql, {
                'id_venta': id_venta,
                'codigo_producto': codigo_producto,
                'cantidad': cantidad
            }, fetch=False)
            return True
        except Exception as e:
            print(f"Error al crear detalle de venta: {e}")
            return False

    # ---------------------------------------------------------
    # ACTUALIZAR SOLO CANTIDAD
    # ---------------------------------------------------------
    def actualizar(self, id_venta: int, codigo_producto: int, cantidad: int) -> bool:
        """Actualiza la cantidad de un producto en una venta"""

        sql = """
            UPDATE DetalleVentaProducto
            SET cantidad = :cantidad
            WHERE id_venta = :id_venta AND codigo_producto = :codigo_producto
        """

        try:
            filas = self.db.execute_query(sql, {
                'cantidad': cantidad,
                'id_venta': id_venta,
                'codigo_producto': codigo_producto
            }, fetch=False)
            return filas > 0
        except Exception as e:
            print(f"Error al actualizar detalle venta: {e}")
            return False

    # ---------------------------------------------------------
    # OBTENER TODOS COMO OBJETOS
    # ---------------------------------------------------------
    def obtener_todos_como_objetos(self) -> List[DetalleVentaProductoData]:
        resultados = self.obtener_todos()
        return [DetalleVentaProductoData(*r) for r in resultados]

    # ---------------------------------------------------------
    # OBTENER DETALLES DE UNA VENTA
    # ---------------------------------------------------------
    def obtener_por_venta(self, id_venta: int) -> List[DetalleVentaProductoData]:
        sql = """
            SELECT * FROM DetalleVentaProducto
            WHERE id_venta = :id_venta
        """
        resultados = self.db.execute_query(sql, {'id_venta': id_venta})
        return [DetalleVentaProductoData(*r) for r in resultados]

    # ---------------------------------------------------------
    # ELIMINAR
    # ---------------------------------------------------------
    def eliminar(self, id_venta: int, codigo_producto: int) -> bool:
        """Elimina un producto de una venta"""

        sql = """
            DELETE FROM DetalleVentaProducto
            WHERE id_venta = :id_venta AND codigo_producto = :codigo_producto
        """

        try:
            filas = self.db.execute_query(sql, {
                'id_venta': id_venta,
                'codigo_producto': codigo_producto
            }, fetch=False)
            return filas > 0
        except Exception as e:
            print(f"Error al eliminar detalle venta: {e}")
            return False
