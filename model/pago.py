"""
Clase para la gestión de pagos realizados
Por: Juan David Ramirez Carmona y
Miguel Ángel Vargas Peláez
Fecha: 2025-11
Licencia: GPLv3
"""

from modelo_base import BaseModel
from dataclasses import dataclass
from typing import Optional, List
from datetime import date


@dataclass
class PagoData:
    """Representa un pago realizado a una cuota"""
    codigo_pago: int
    fecha_pago: date
    estado: str
    valor: float
    id_pago: int   # referencia a Cuota.id_pago

    def __str__(self):
        return f"Pago(codigo={self.codigo_pago}, cuota={self.id_pago}, valor={self.valor})"


class Pago(BaseModel):

    def get_table_name(self):
        return "Pago"

    def get_primary_key(self):
        return "codigo_pago"

    # ---------------------------------------------------------
    # CREAR
    # ---------------------------------------------------------
    def crear(self, codigo_pago: int, fecha_pago, estado: str,
              valor: float, id_pago: int) -> bool:
        """Crea un pago"""

        sql = """
            INSERT INTO Pago (codigo_pago, fecha_pago, estado, valor, id_pago)
            VALUES (:codigo_pago, :fecha_pago, :estado, :valor, :id_pago)
        """

        try:
            self.db.execute_query(sql, {
                'codigo_pago': codigo_pago,
                'fecha_pago': fecha_pago,
                'estado': estado,
                'valor': valor,
                'id_pago': id_pago
            }, fetch=False)
            return True
        except Exception as e:
            print(f"Error al crear pago: {e}")
            return False

    # ---------------------------------------------------------
    # ACTUALIZAR
    # ---------------------------------------------------------
    def actualizar(self, codigo_pago: int, fecha_pago=None, estado: str = None,
                   valor: float = None, id_pago: int = None) -> bool:
        """Actualiza un pago"""

        campos = []
        params = {'codigo_pago': codigo_pago}

        if fecha_pago is not None:
            campos.append("fecha_pago = :fecha_pago")
            params['fecha_pago'] = fecha_pago

        if estado is not None:
            campos.append("estado = :estado")
            params['estado'] = estado

        if valor is not None:
            campos.append("valor = :valor")
            params['valor'] = valor

        if id_pago is not None:
            campos.append("id_pago = :id_pago")
            params['id_pago'] = id_pago

        if not campos:
            return False

        sql = f"""
            UPDATE Pago
            SET {', '.join(campos)}
            WHERE codigo_pago = :codigo_pago
        """

        try:
            filas = self.db.execute_query(sql, params, fetch=False)
            return filas > 0
        except Exception as e:
            print(f"Error al actualizar pago: {e}")
            return False

    # ---------------------------------------------------------
    # OBTENER TODOS COMO OBJETOS
    # ---------------------------------------------------------
    def obtener_todos_como_objetos(self) -> List[PagoData]:
        resultados = self.obtener_todos()
        return [PagoData(*r) for r in resultados]

    # ---------------------------------------------------------
    # OBTENER POR CUOTA (1–1)
    # ---------------------------------------------------------
    def obtener_por_id_pago(self, id_pago: int) -> Optional[PagoData]:
        sql = "SELECT * FROM Pago WHERE id_pago = :id_pago"
        resultado = self.db.execute_query(sql, {'id_pago': id_pago})
        return PagoData(*resultado[0]) if resultado else None

    # ---------------------------------------------------------
    # OBTENER POR CÓDIGO
    # ---------------------------------------------------------
    def obtener_por_codigo_pago(self, codigo_pago: int) -> Optional[PagoData]:
        resultado = self.obtener_por_id(codigo_pago)
        return PagoData(*resultado) if resultado else None

    # ---------------------------------------------------------
    # ELIMINAR
    # ---------------------------------------------------------
    def eliminar(self, codigo_pago: int) -> bool:
        sql = "DELETE FROM Pago WHERE codigo_pago = :codigo_pago"
        try:
            filas = self.db.execute_query(sql, {'codigo_pago': codigo_pago}, fetch=False)
            return filas > 0
        except Exception as e:
            print(f"Error al eliminar pago: {e}")
            return False
