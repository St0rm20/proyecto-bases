"""
Clase para la gestión de cuotas (pagos programados de un crédito)
Por: Juan David Ramirez Carmona y
Miguel Ángel Vargas Peláez
Fecha: 2025-11
Licencia: GPLv3
"""

from modelo_base import BaseModel
from dataclasses import dataclass
from typing import Optional, List
from datetime import date, datetime


def convertir_fecha_oracle(fecha_obj):
    """
    Convierte una fecha de Oracle (que puede venir como string) a objeto date
    """
    if fecha_obj is None:
        return date.today()

    if isinstance(fecha_obj, date):
        return fecha_obj

    if isinstance(fecha_obj, datetime):
        return fecha_obj.date()

    if isinstance(fecha_obj, str):
        # Intentar diferentes formatos de Oracle
        formatos = [
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%Y-%m-%d %H:%M:%S',
            '%d-%m-%Y',
        ]

        for fmt in formatos:
            try:
                return datetime.strptime(fecha_obj, fmt).date()
            except ValueError:
                continue

        print(f"⚠️ Formato de fecha no reconocido: {fecha_obj}")
        return date.today()

    return date.today()


@dataclass
class CuotaData:
    """Representa una cuota programada de un crédito"""
    id_pago: int
    n_cuota: int
    estado: str
    valor_cuota: float
    fecha_vencimiento: date
    id_credito: int

    def __str__(self):
        return f"Cuota(id_pago={self.id_pago}, cuota={self.n_cuota}, credito={self.id_credito})"


class Cuota(BaseModel):

    def get_table_name(self):
        return "Cuota"

    def get_primary_key(self):
        return "id_pago"

    # ---------------------------------------------------------
    # CREAR
    # ---------------------------------------------------------
    def crear(self, id_pago: int, n_cuota: int, estado: str,
              valor_cuota: float, fecha_vencimiento, id_credito: int) -> bool:
        """Crea una cuota"""

        sql = """
            INSERT INTO Cuota (id_pago, n_cuota, estado, valor_cuota, fecha_vencimiento, id_credito)
            VALUES (:id_pago, :n_cuota, :estado, :valor_cuota, :fecha_vencimiento, :id_credito)
        """
        try:
            self.db.execute_query(sql, {
                'id_pago': id_pago,
                'n_cuota': n_cuota,
                'estado': estado,
                'valor_cuota': valor_cuota,
                'fecha_vencimiento': fecha_vencimiento,
                'id_credito': id_credito
            }, fetch=False)
            return True
        except Exception as e:
            print(f"Error al crear cuota: {e}")
            return False

    # ---------------------------------------------------------
    # ACTUALIZAR
    # ---------------------------------------------------------
    def actualizar(self, id_pago: int, n_cuota: int = None, estado: str = None,
                   valor_cuota: float = None, fecha_vencimiento=None,
                   id_credito: int = None) -> bool:
        """Actualiza una cuota (solo campos proporcionados)"""

        campos = []
        params = {'id_pago': id_pago}

        if n_cuota is not None:
            campos.append("n_cuota = :n_cuota")
            params['n_cuota'] = n_cuota

        if estado is not None:
            campos.append("estado = :estado")
            params['estado'] = estado

        if valor_cuota is not None:
            campos.append("valor_cuota = :valor_cuota")
            params['valor_cuota'] = valor_cuota

        if fecha_vencimiento is not None:
            campos.append("fecha_vencimiento = :fecha_vencimiento")
            params['fecha_vencimiento'] = fecha_vencimiento

        if id_credito is not None:
            campos.append("id_credito = :id_credito")
            params['id_credito'] = id_credito

        if not campos:
            return False

        sql = f"UPDATE Cuota SET {', '.join(campos)} WHERE id_pago = :id_pago"

        try:
            filas = self.db.execute_query(sql, params, fetch=False)
            return filas > 0
        except Exception as e:
            print(f"Error al actualizar cuota: {e}")
            return False

    # ---------------------------------------------------------
    # OBTENER TODOS COMO OBJETOS
    # ---------------------------------------------------------
    def obtener_todos_como_objetos(self) -> List[CuotaData]:
        resultados = self.obtener_todos()
        return self._convertir_resultados_a_objetos(resultados)

    # ---------------------------------------------------------
    # OBTENER POR CRÉDITO
    # ---------------------------------------------------------
    def obtener_por_credito(self, id_credito: int) -> List[CuotaData]:
        sql = "SELECT * FROM Cuota WHERE id_credito = :id_credito ORDER BY n_cuota"
        resultados = self.db.execute_query(sql, {'id_credito': id_credito})
        return self._convertir_resultados_a_objetos(resultados)

    # ---------------------------------------------------------
    # OBTENER POR ID
    # ---------------------------------------------------------
    def obtener_por_id_pago(self, id_pago: int) -> Optional[CuotaData]:
        resultado = self.obtener_por_id(id_pago)
        if resultado:
            return self._convertir_fila_a_objeto(resultado)
        return None

    # ---------------------------------------------------------
    # ELIMINAR
    # ---------------------------------------------------------
    def eliminar(self, id_pago: int) -> bool:
        sql = "DELETE FROM Cuota WHERE id_pago = :id_pago"
        try:
            filas = self.db.execute_query(sql, {'id_pago': id_pago}, fetch=False)
            return filas > 0
        except Exception as e:
            print(f"Error al eliminar cuota: {e}")
            return False

    # ---------------------------------------------------------
    # MÉTODOS AUXILIARES PARA CONVERSIÓN
    # ---------------------------------------------------------
    def _convertir_resultados_a_objetos(self, resultados) -> List[CuotaData]:
        """Convierte una lista de tuplas en objetos CuotaData"""
        cuotas = []
        for fila in resultados:
            cuota = self._convertir_fila_a_objeto(fila)
            if cuota:
                cuotas.append(cuota)
        return cuotas

    def _convertir_fila_a_objeto(self, fila) -> Optional[CuotaData]:
        """Convierte una fila de la BD en un objeto CuotaData"""
        try:
            # Convertir a lista para poder modificar
            datos = list(fila)

            # Imprimir para debug
            print(f"DEBUG - Fila original: {datos}")
            print(f"DEBUG - Tipos: {[type(x).__name__ for x in datos]}")

            # Identificar qué campo es la fecha (buscar datetime o date)
            for i, valor in enumerate(datos):
                if isinstance(valor, (date, datetime)):
                    print(f"DEBUG - Fecha encontrada en índice {i}: {valor}")
                    datos[i] = convertir_fecha_oracle(valor)

            # Crear el objeto
            cuota = CuotaData(
                id_pago=int(datos[0]),
                n_cuota=int(datos[1]),
                estado=str(datos[2]),
                valor_cuota=float(datos[3]),
                fecha_vencimiento=convertir_fecha_oracle(datos[4]),
                id_credito=int(datos[5])
            )

            print(f"DEBUG - Cuota creada: {cuota}")
            return cuota

        except Exception as e:
            print(f"❌ Error al convertir fila a objeto: {e}")
            print(f"   Fila: {fila}")
            import traceback
            traceback.print_exc()
            return None