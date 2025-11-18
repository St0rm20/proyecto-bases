"""
Clase para la gestión de auditoría de ingresos y salidas
Por: Juan David Ramirez Carmona y Miguel Ángel Vargas Peláez
Fecha: 2025-11
Licencia: GPLv3
"""
from modelo_base import BaseModel
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class AuditoriaData:
    """Representa un registro de auditoría"""
    id_auditoria: int
    fecha_ingreso: datetime
    usuario: int
    fecha_salida: Optional[datetime] = None

    def __str__(self):
        salida = f" - Salida: {self.fecha_salida}" if self.fecha_salida else " (Sesión Activa)"
        return f"Auditoria(id={self.id_auditoria}, usuario={self.usuario}, ingreso={self.fecha_ingreso}{salida})"

    def esta_activa(self) -> bool:
        """Retorna True si la sesión está activa (sin fecha de salida)"""
        return self.fecha_salida is None

    def duracion(self) -> Optional[str]:
        """Calcula la duración de la sesión"""
        if not self.fecha_salida:
            return "En curso"

        delta = self.fecha_salida - self.fecha_ingreso
        horas = delta.total_seconds() / 3600
        minutos = (delta.total_seconds() % 3600) / 60
        return f"{int(horas)}h {int(minutos)}m"


class Auditoria(BaseModel):
    """Gestión de auditoría de ingresos y salidas de usuarios"""

    def get_table_name(self):
        return "Auditoria"

    def get_primary_key(self):
        return "id_auditoria"

    def registrar_ingreso(self, codigo_usuario: int) -> bool:
        """
        Registra el ingreso de un usuario al sistema.
        Crea un nuevo registro de auditoría con la fecha/hora actual.

        Args:
            codigo_usuario: Código del cliente que ingresa

        Returns:
            bool: True si se registró exitosamente, False en caso contrario
        """
        sql = """
            INSERT INTO Auditoria (fecha_ingreso, usuario)
            VALUES (SYSDATE, :usuario)
        """
        try:
            self.db.execute_query(sql, {'usuario': codigo_usuario}, fetch=False)
            print(f"✓ Ingreso registrado para usuario {codigo_usuario}")
            return True
        except Exception as e:
            print(f"Error al registrar ingreso: {e}")
            return False

    def registrar_salida(self, codigo_usuario: int) -> bool:
        """
        Registra la salida de un usuario del sistema.
        Actualiza el registro de auditoría más reciente sin fecha de salida.

        Args:
            codigo_usuario: Código del cliente que sale

        Returns:
            bool: True si se registró exitosamente, False en caso contrario
        """
        # Buscar la sesión activa más reciente del usuario
        sql_buscar = """
            SELECT id_auditoria 
            FROM Auditoria 
            WHERE usuario = :usuario 
              AND fecha_salida IS NULL
            ORDER BY fecha_ingreso DESC
            FETCH FIRST 1 ROW ONLY
        """

        try:
            resultado = self.db.execute_query(sql_buscar, {'usuario': codigo_usuario})

            if not resultado:
                print(f"No se encontró sesión activa para el usuario {codigo_usuario}")
                return False

            id_auditoria = resultado[0][0]

            # Actualizar con la fecha de salida
            sql_actualizar = """
                UPDATE Auditoria 
                SET fecha_salida = SYSDATE
                WHERE id_auditoria = :id_auditoria
            """

            filas = self.db.execute_query(sql_actualizar, {'id_auditoria': id_auditoria}, fetch=False)

            if filas > 0:
                print(f"✓ Salida registrada para usuario {codigo_usuario}")
                return True
            else:
                return False

        except Exception as e:
            print(f"Error al registrar salida: {e}")
            return False

    def obtener_sesion_activa(self, codigo_usuario: int) -> Optional[AuditoriaData]:
        """
        Obtiene la sesión activa (sin fecha de salida) de un usuario.

        Args:
            codigo_usuario: Código del cliente

        Returns:
            AuditoriaData si hay sesión activa, None si no la hay
        """
        sql = """
            SELECT id_auditoria, fecha_ingreso, usuario, fecha_salida
            FROM Auditoria 
            WHERE usuario = :usuario 
              AND fecha_salida IS NULL
            ORDER BY fecha_ingreso DESC
            FETCH FIRST 1 ROW ONLY
        """
        try:
            resultado = self.db.execute_query(sql, {'usuario': codigo_usuario})
            return AuditoriaData(*resultado[0]) if resultado else None
        except Exception as e:
            print(f"Error al obtener sesión activa: {e}")
            return None

    def tiene_sesion_activa(self, codigo_usuario: int) -> bool:
        """
        Verifica si un usuario tiene una sesión activa.

        Args:
            codigo_usuario: Código del cliente

        Returns:
            bool: True si tiene sesión activa, False si no
        """
        return self.obtener_sesion_activa(codigo_usuario) is not None

    def obtener_todos_como_objetos(self) -> List[AuditoriaData]:
        """Obtiene todos los registros de auditoría como objetos"""
        resultados = self.obtener_todos()
        return [AuditoriaData(*r) for r in resultados]

    def obtener_por_usuario(self, codigo_usuario: int) -> List[AuditoriaData]:
        """
        Obtiene todos los registros de auditoría de un usuario específico.

        Args:
            codigo_usuario: Código del cliente

        Returns:
            Lista de registros de auditoría del usuario
        """
        sql = """
            SELECT id_auditoria, fecha_ingreso, usuario, fecha_salida
            FROM Auditoria 
            WHERE usuario = :usuario
            ORDER BY fecha_ingreso DESC
        """
        try:
            resultados = self.db.execute_query(sql, {'usuario': codigo_usuario})
            return [AuditoriaData(*r) for r in resultados]
        except Exception as e:
            print(f"Error al obtener registros por usuario: {e}")
            return []

    def obtener_con_nombres(self) -> List[tuple]:
        """
        Obtiene todos los registros de auditoría con el nombre del usuario.

        Returns:
            Lista de tuplas: (id_auditoria, fecha_ingreso, fecha_salida, codigo_usuario, nombre_usuario)
        """
        sql = """
            SELECT 
                a.id_auditoria,
                a.fecha_ingreso,
                a.fecha_salida,
                a.usuario,
                c.nombre
            FROM Auditoria a
            INNER JOIN Cliente c ON a.usuario = c.codigo_cliente
            ORDER BY a.fecha_ingreso DESC
        """
        try:
            return self.db.execute_query(sql)
        except Exception as e:
            print(f"Error al obtener registros con nombres: {e}")
            return []

    def obtener_sesiones_activas(self) -> List[tuple]:
        """
        Obtiene todas las sesiones activas con información del usuario.

        Returns:
            Lista de tuplas: (id_auditoria, fecha_ingreso, codigo_usuario, nombre_usuario)
        """
        sql = """
            SELECT 
                a.id_auditoria,
                a.fecha_ingreso,
                a.usuario,
                c.nombre
            FROM Auditoria a
            INNER JOIN Cliente c ON a.usuario = c.codigo_cliente
            WHERE a.fecha_salida IS NULL
            ORDER BY a.fecha_ingreso DESC
        """
        try:
            return self.db.execute_query(sql)
        except Exception as e:
            print(f"Error al obtener sesiones activas: {e}")
            return []

    def obtener_por_rango_fechas(self, fecha_inicio: datetime, fecha_fin: datetime) -> List[tuple]:
        """
        Obtiene registros de auditoría en un rango de fechas.

        Args:
            fecha_inicio: Fecha inicial del rango
            fecha_fin: Fecha final del rango

        Returns:
            Lista de tuplas con información de auditoría y usuario
        """
        sql = """
            SELECT 
                a.id_auditoria,
                a.fecha_ingreso,
                a.fecha_salida,
                a.usuario,
                c.nombre
            FROM Auditoria a
            INNER JOIN Cliente c ON a.usuario = c.codigo_cliente
            WHERE a.fecha_ingreso BETWEEN :fecha_inicio AND :fecha_fin
            ORDER BY a.fecha_ingreso DESC
        """
        try:
            return self.db.execute_query(sql, {
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin
            })
        except Exception as e:
            print(f"Error al obtener registros por rango de fechas: {e}")
            return []

    def obtener_estadisticas_usuario(self, codigo_usuario: int) -> dict:
        """
        Obtiene estadísticas de acceso de un usuario.

        Args:
            codigo_usuario: Código del cliente

        Returns:
            Diccionario con estadísticas del usuario
        """
        sql = """
            SELECT 
                COUNT(*) as total_sesiones,
                COUNT(fecha_salida) as sesiones_cerradas,
                COUNT(*) - COUNT(fecha_salida) as sesiones_activas,
                MIN(fecha_ingreso) as primer_ingreso,
                MAX(fecha_ingreso) as ultimo_ingreso
            FROM Auditoria
            WHERE usuario = :usuario
        """
        try:
            resultado = self.db.execute_query(sql, {'usuario': codigo_usuario})
            if resultado:
                row = resultado[0]
                return {
                    'total_sesiones': row[0],
                    'sesiones_cerradas': row[1],
                    'sesiones_activas': row[2],
                    'primer_ingreso': row[3],
                    'ultimo_ingreso': row[4]
                }
            return {}
        except Exception as e:
            print(f"Error al obtener estadísticas: {e}")
            return {}