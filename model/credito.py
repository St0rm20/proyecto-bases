"""
Clase para la gestión de créditos asociados a ventas
Por: Juan David Ramirez Carmona y
Miguel Ángel Vargas Peláez
Fecha: 2025-11
Licencia: GPLv3
"""

from modelo_base import BaseModel
from dataclasses import dataclass
from typing import Optional, List
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


@dataclass
class CreditoData:
    """Representa un crédito asociado a una venta"""
    id_credito: int
    cuota_inicial: float
    saldo_financiado: float
    interes: float
    plazo_meses: int
    id_venta: int

    def __str__(self):
        return f"Credito(id={self.id_credito}, venta={self.id_venta})"


@dataclass
class CuotaData:
    """Estructura de datos para una cuota"""
    id_pago: int
    n_cuota: int
    fecha_vencimiento: date
    valor_cuota: float
    estado: str
    id_credito: int


def convertir_fecha_oracle(fecha_obj):
    """
    Convierte una fecha de Oracle (que puede venir como string o datetime) a objeto date
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


class Credito(BaseModel):

    def get_table_name(self):
        return "Credito"

    def get_primary_key(self):
        return "id_credito"

    # ---------------------------------------------------------
    # CREAR
    # ---------------------------------------------------------
    def crear(self, id_credito: int, cuota_inicial: float,
              saldo_financiado: float, interes: float,
              plazo_meses: int, id_venta: int) -> bool:
        """Crea un nuevo crédito"""

        sql = """
            INSERT INTO Credito (
                id_credito, cuota_inicial, saldo_financiado,
                interes, plazo_meses, id_venta
            )
            VALUES (
                :id_credito, :cuota_inicial, :saldo_financiado,
                :interes, :plazo_meses, :id_venta
            )
        """

        try:
            self.db.execute_query(sql, {
                'id_credito': id_credito,
                'cuota_inicial': cuota_inicial,
                'saldo_financiado': saldo_financiado,
                'interes': interes,
                'plazo_meses': plazo_meses,
                'id_venta': id_venta
            }, fetch=False)
            return True
        except Exception as e:
            print(f"Error al crear crédito: {e}")
            return False

    # ---------------------------------------------------------
    # ACTUALIZAR
    # ---------------------------------------------------------
    def actualizar(self, id_credito: int, cuota_inicial: float = None,
                   saldo_financiado: float = None, interes: float = None,
                   plazo_meses: int = None, id_venta: int = None) -> bool:
        """Actualiza un crédito"""

        campos = []
        params = {'id_credito': id_credito}

        if cuota_inicial is not None:
            campos.append("cuota_inicial = :cuota_inicial")
            params['cuota_inicial'] = cuota_inicial

        if saldo_financiado is not None:
            campos.append("saldo_financiado = :saldo_financiado")
            params['saldo_financiado'] = saldo_financiado

        if interes is not None:
            campos.append("interes = :interes")
            params['interes'] = interes

        if plazo_meses is not None:
            campos.append("plazo_meses = :plazo_meses")
            params['plazo_meses'] = plazo_meses

        if id_venta is not None:
            campos.append("id_venta = :id_venta")
            params['id_venta'] = id_venta

        if not campos:
            return False

        sql = f"""
            UPDATE Credito
            SET {', '.join(campos)}
            WHERE id_credito = :id_credito
        """

        try:
            filas = self.db.execute_query(sql, params, fetch=False)
            return filas > 0
        except Exception as e:
            print(f"Error al actualizar crédito: {e}")
            return False

    # ---------------------------------------------------------
    # OBTENER COMO OBJETOS
    # ---------------------------------------------------------
    def obtener_todos_como_objetos(self) -> List[CreditoData]:
        resultados = self.obtener_todos()
        return [CreditoData(*r) for r in resultados]

    # ---------------------------------------------------------
    # OBTENER POR ID
    # ---------------------------------------------------------
    def obtener_por_id_credito(self, id_credito: int) -> Optional[CreditoData]:
        resultado = self.obtener_por_id(id_credito)
        return CreditoData(*resultado) if resultado else None

    # ---------------------------------------------------------
    # OBTENER POR VENTA
    # ---------------------------------------------------------
    def obtener_por_venta(self, id_venta: int) -> Optional[CreditoData]:
        sql = "SELECT * FROM Credito WHERE id_venta = :id_venta"
        resultado = self.db.execute_query(sql, {'id_venta': id_venta})
        return CreditoData(*resultado[0]) if resultado else None

    # ---------------------------------------------------------
    # ELIMINAR
    # ---------------------------------------------------------
    def eliminar(self, id_credito: int) -> bool:
        sql = "DELETE FROM Credito WHERE id_credito = :id_credito"
        try:
            filas = self.db.execute_query(sql, {'id_credito': id_credito}, fetch=False)
            return filas > 0
        except Exception as e:
            print(f"Error al eliminar crédito: {e}")
            return False

    def obtener_creditos_activos(self) -> List[CreditoData]:
        """Obtiene todos los créditos con estado 'Activo' (que tengan cuotas pendientes)"""
        sql = """
            SELECT c.id_credito, c.cuota_inicial, c.saldo_financiado,
                   c.interes, c.plazo_meses, c.id_venta
            FROM Credito c
            INNER JOIN Venta v ON c.id_venta = v.id_venta
            WHERE v.estado_credito = 'Activo'
               OR (v.estado_credito IS NULL AND EXISTS (
                   SELECT 1 FROM Cuota cu 
                   WHERE cu.id_credito = c.id_credito 
                   AND cu.estado != 'Pagada'
               ))
            ORDER BY c.id_credito DESC
        """
        resultados = self.db.execute_query(sql)
        return [CreditoData(*r) for r in resultados]

    def obtener_info_credito_completa(self, id_credito: int) -> Optional[dict]:
        """
        Obtiene información completa del crédito incluyendo:
        - Datos del crédito
        - Datos del cliente (de la venta)
        - Total de cuotas
        - Cuotas pagadas
        - Total pagado
        - Saldo pendiente
        """
        sql = """
            SELECT c.id_credito,
                   c.cuota_inicial,
                   c.saldo_financiado,
                   c.interes,
                   c.plazo_meses,
                   c.id_venta,
                   v.codigo_venta,
                   v.codigo_cliente,
                   cl.nombre as nombre_cliente,
                   cl.telefono,
                   (SELECT COUNT(*) FROM Cuota WHERE id_credito = c.id_credito) as total_cuotas,
                   (SELECT COUNT(*) 
                    FROM Cuota 
                    WHERE id_credito = c.id_credito 
                      AND estado = 'Pagada') as cuotas_pagadas,
                   (SELECT COALESCE(SUM(p.valor), 0) 
                    FROM Pago p 
                    INNER JOIN Cuota cu ON p.id_pago = cu.id_pago 
                    WHERE cu.id_credito = c.id_credito) as total_pagado,
                   (c.saldo_financiado - 
                    COALESCE((SELECT SUM(p.valor) 
                              FROM Pago p 
                              INNER JOIN Cuota cu ON p.id_pago = cu.id_pago 
                              WHERE cu.id_credito = c.id_credito), 0)) as saldo_pendiente
            FROM Credito c
            INNER JOIN Venta v ON c.id_venta = v.id_venta
            INNER JOIN Cliente cl ON v.codigo_cliente = cl.codigo_cliente
            WHERE c.id_credito = :id_credito
        """

        resultado = self.db.execute_query(sql, {'id_credito': id_credito})

        if not resultado:
            return None

        r = resultado[0]
        return {
            'id_credito': r[0],
            'cuota_inicial': r[1],
            'saldo_financiado': r[2],
            'interes': r[3],
            'plazo_meses': r[4],
            'id_venta': r[5],
            'codigo_venta': r[6],
            'codigo_cliente': r[7],
            'nombre_cliente': r[8],
            'telefono': r[9],
            'total_cuotas': r[10],
            'cuotas_pagadas': r[11],
            'total_pagado': r[12],
            'saldo_pendiente': r[13]
        }

    def obtener_siguiente_cuota_pendiente(self, id_credito: int) -> Optional['CuotaData']:
        """Obtiene la siguiente cuota pendiente de pago"""
        sql = """
            SELECT id_pago, n_cuota, fecha_vencimiento, valor_cuota, estado, id_credito
            FROM Cuota
            WHERE id_credito = :id_credito
              AND estado = 'Pendiente'
            ORDER BY n_cuota ASC
            FETCH FIRST 1 ROWS ONLY
        """
        resultado = self.db.execute_query(sql, {'id_credito': id_credito})

        if resultado:
            try:
                # Convertir la tupla a lista
                datos = list(resultado[0])

                print(f"DEBUG - Datos originales de cuota: {datos}")
                print(f"DEBUG - Tipos: {[type(x).__name__ for x in datos]}")

                # Crear el objeto con el orden correcto del SELECT
                cuota = CuotaData(
                    id_pago=int(datos[0]),
                    n_cuota=int(datos[1]),
                    fecha_vencimiento=convertir_fecha_oracle(datos[2]),
                    valor_cuota=float(datos[3]),
                    estado=str(datos[4]),
                    id_credito=int(datos[5])
                )

                print(f"DEBUG - Cuota creada: {cuota}")
                return cuota

            except Exception as e:
                print(f"❌ Error al crear CuotaData: {e}")
                print(f"   Datos: {resultado[0]}")
                import traceback
                traceback.print_exc()
                return None

        return None

    def calcular_valor_cuota(self, saldo_financiado: float, interes: float, plazo_meses: int) -> float:
        """
        Calcula el valor de la cuota mensual usando la fórmula de amortización francesa
        Fórmula: Cuota = Saldo * (i * (1+i)^n) / ((1+i)^n - 1)
        Donde:
        - i = tasa de interés mensual (interes/100/12)
        - n = número de meses
        """
        if plazo_meses == 0:
            return 0

        if interes == 0:
            return saldo_financiado / plazo_meses

        # Convertir interés anual a mensual
        interes_mensual = (interes / 100) / 12

        # Aplicar fórmula de amortización
        numerador = interes_mensual * ((1 + interes_mensual) ** plazo_meses)
        denominador = ((1 + interes_mensual) ** plazo_meses) - 1

        cuota = saldo_financiado * (numerador / denominador)

        return round(cuota, 2)

    def generar_cuotas(self, id_credito: int) -> bool:
        """
        Genera automáticamente todas las cuotas para un crédito
        Retorna True si se crearon exitosamente
        """
        from model.cuota import Cuota
        from datetime import date, timedelta
        from dateutil.relativedelta import relativedelta

        # Obtener información del crédito
        credito = self.obtener_por_id_credito(id_credito)
        if not credito:
            print(f"Error: No se encontró el crédito {id_credito}")
            return False

        # Calcular valor de la cuota
        valor_cuota = self.calcular_valor_cuota(
            credito.saldo_financiado,
            credito.interes,
            credito.plazo_meses
        )

        if valor_cuota <= 0:
            print("Error: El valor de la cuota debe ser mayor a 0")
            return False

        # Crear controlador de cuotas
        cuota_controller = Cuota()

        # Fecha inicial (un mes después de hoy)
        fecha_actual = date.today()

        print(f"\n📄 Generando {credito.plazo_meses} cuotas para el crédito #{id_credito}")
        print(f"   Valor por cuota: ${valor_cuota:,.2f}")

        try:
            for i in range(1, credito.plazo_meses + 1):
                # Calcular fecha de vencimiento (i meses desde hoy)
                fecha_vencimiento = fecha_actual + relativedelta(months=i)

                # Generar ID único para la cuota
                id_pago = int(f"{id_credito}{i:03d}")  # Ej: 1763441304001

                # Crear la cuota
                exito = cuota_controller.crear(
                    id_pago=id_pago,
                    n_cuota=i,
                    fecha_vencimiento=fecha_vencimiento,
                    valor_cuota=valor_cuota,
                    estado="Pendiente",
                    id_credito=id_credito
                )

                if exito:
                    print(f"   ✅ Cuota {i}/{credito.plazo_meses} - Vence: {fecha_vencimiento.strftime('%d/%m/%Y')}")
                else:
                    print(f"   ❌ Error al crear cuota {i}")
                    return False

            print(f"\n✅ Se generaron exitosamente {credito.plazo_meses} cuotas\n")
            return True

        except Exception as e:
            print(f"❌ Error al generar cuotas: {e}")
            import traceback
            traceback.print_exc()
            return False

    def obtener_clientes_morosos(self):
        """
        Retorna una lista con tuplas:
        (nombre_cliente, codigo_venta, id_pago, fecha_vencimiento, estado_cuota)
        """
        sql = """
              SELECT cl.nombre,
                     v.codigo_venta,
                     cu.id_pago,
                     cu.fecha_vencimiento,
                     cu.estado
              FROM Cliente cl
                       JOIN Venta v ON v.codigo_cliente = cl.codigo_cliente
                       JOIN Credito cr ON cr.id_venta = v.id_venta
                       JOIN Cuota cu ON cu.id_credito = cr.id_credito
              WHERE cu.estado IN ('VENCIDA', 'PENDIENTE')
              ORDER BY cl.nombre \
              """

        try:
            return self.db.execute_query(sql)
        except Exception as e:
            print("Error al obtener morosos:", e)
            return []
