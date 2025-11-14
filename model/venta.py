"""
Clase para la gestión de ventas
Por: Juan David Ramirez Carmona y
Miguel Ángel Vargas Peláez
Fecha: 2025-11
Licencia: GPLv3
"""

from modelo_base import BaseModel
from dataclasses import dataclass
from typing import Optional, List
from decimal import Decimal
from datetime import date


@dataclass
class VentaData:
    """Representa una venta"""
    id_venta: int
    codigo_venta: str
    estado_venta: str
    fecha: date
    total_neto: Optional[Decimal]
    estado_credito: Optional[str]
    tipo_venta: str
    total_bruto: Optional[Decimal]
    iva_total: Optional[Decimal]
    codigo_cliente: int

    def __str__(self):
        return f"Venta(id={self.id_venta}, codigo='{self.codigo_venta}', total=${self.total_neto})"


class Venta(BaseModel):
    """Gestión de ventas"""

    def get_table_name(self):
        return "Venta"

    def get_primary_key(self):
        return "id_venta"

    def crear(self, id_venta: int, codigo_venta: str, estado_venta: str,
              fecha: date, tipo_venta: str, codigo_cliente: int,
              total_neto: float = None, estado_credito: str = None,
              total_bruto: float = None, iva_total: float = None) -> bool:
        """Crea una nueva venta"""
        sql = """
            INSERT INTO Venta (id_venta, codigo_venta, estado_venta, fecha, 
                              total_neto, estado_credito, tipo_venta, 
                              total_bruto, iva_total, codigo_cliente)
            VALUES (:id_venta, :codigo_venta, :estado_venta, :fecha, 
                    :total_neto, :estado_credito, :tipo_venta, 
                    :total_bruto, :iva_total, :codigo_cliente)
        """
        try:
            self.db.execute_query(sql, {
                'id_venta': id_venta,
                'codigo_venta': codigo_venta,
                'estado_venta': estado_venta,
                'fecha': fecha,
                'total_neto': total_neto,
                'estado_credito': estado_credito,
                'tipo_venta': tipo_venta,
                'total_bruto': total_bruto,
                'iva_total': iva_total,
                'codigo_cliente': codigo_cliente
            }, fetch=False)
            return True
        except Exception as e:
            print(f"Error al crear venta: {e}")
            return False

    def actualizar_estado(self, id_venta: int, estado_venta: str) -> bool:
        """Actualiza el estado de una venta"""
        sql = "UPDATE Venta SET estado_venta = :estado WHERE id_venta = :id"
        try:
            filas = self.db.execute_query(sql, {
                'estado': estado_venta,
                'id': id_venta
            }, fetch=False)
            return filas > 0
        except Exception as e:
            print(f"Error al actualizar estado: {e}")
            return False

    def actualizar_totales(self, id_venta: int, total_neto: float = None,
                           total_bruto: float = None, iva_total: float = None) -> bool:
        """Actualiza los totales de una venta"""
        campos = []
        params = {'id_venta': id_venta}

        if total_neto is not None:
            campos.append("total_neto = :total_neto")
            params['total_neto'] = total_neto
        if total_bruto is not None:
            campos.append("total_bruto = :total_bruto")
            params['total_bruto'] = total_bruto
        if iva_total is not None:
            campos.append("iva_total = :iva_total")
            params['iva_total'] = iva_total

        if not campos:
            return False

        sql = f"UPDATE Venta SET {', '.join(campos)} WHERE id_venta = :id_venta"

        try:
            filas = self.db.execute_query(sql, params, fetch=False)
            return filas > 0
        except Exception as e:
            print(f"Error al actualizar totales: {e}")
            return False

    def obtener_todos_como_objetos(self) -> List[VentaData]:
        """Obtiene todas las ventas como objetos"""
        resultados = self.obtener_todos()
        return [VentaData(*r) for r in resultados]

    def buscar_por_cliente(self, codigo_cliente: int) -> List[VentaData]:
        """Obtiene todas las ventas de un cliente"""
        sql = "SELECT * FROM Venta WHERE codigo_cliente = :cliente ORDER BY fecha DESC"
        resultados = self.db.execute_query(sql, {'cliente': codigo_cliente})
        return [VentaData(*r) for r in resultados]

    def buscar_por_fecha(self, fecha_inicio: date, fecha_fin: date) -> List[VentaData]:
        """Busca ventas en un rango de fechas"""
        sql = """
            SELECT * FROM Venta 
            WHERE fecha BETWEEN :fecha_inicio AND :fecha_fin
            ORDER BY fecha DESC
        """
        resultados = self.db.execute_query(sql, {
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin
        })
        return [VentaData(*r) for r in resultados]

    def buscar_por_tipo(self, tipo_venta: str) -> List[VentaData]:
        """Busca ventas por tipo"""
        sql = "SELECT * FROM Venta WHERE tipo_venta = :tipo ORDER BY fecha DESC"
        resultados = self.db.execute_query(sql, {'tipo': tipo_venta})
        return [VentaData(*r) for r in resultados]

    def agregar_producto(self, id_venta: int, codigo_producto: int) -> bool:
        """Agrega un producto a una venta"""
        sql = """
            INSERT INTO DetalleVentaProducto (id_venta, codigo_producto)
            VALUES (:id_venta, :codigo_producto)
        """
        try:
            self.db.execute_query(sql, {
                'id_venta': id_venta,
                'codigo_producto': codigo_producto
            }, fetch=False)
            return True
        except Exception as e:
            print(f"Error al agregar producto: {e}")
            return False

    def obtener_productos(self, id_venta: int) -> List[int]:
        """Obtiene los códigos de productos de una venta"""
        sql = "SELECT codigo_producto FROM DetalleVentaProducto WHERE id_venta = :id"
        resultados = self.db.execute_query(sql, {'id': id_venta})
        return [r[0] for r in resultados]