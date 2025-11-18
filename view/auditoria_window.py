"""
Ventana de visualización de auditoría de ingresos y salidas
Por: Juan David Ramirez Carmona y Miguel Ángel Vargas Peláez
Fecha: 2025-11
Licencia: GPLv3
"""

import sys
import csv
from datetime import datetime, timedelta
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QFileDialog
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor
from model.auditoria import Auditoria


class AuditoriaWindow(QtWidgets.QMainWindow):
    """
    Ventana para visualizar el historial de ingresos y salidas de usuarios
    """

    def __init__(self):
        super().__init__()

        # Cargar el archivo .ui
        try:
            uic.loadUi('auditoria.ui', self)
        except FileNotFoundError:
            print("Error: Asegúrate de que 'auditoria.ui' esté en el mismo directorio.")
            sys.exit(1)

        # Instanciar el controlador
        try:
            self.auditoria_controller = Auditoria()
        except Exception as e:
            QMessageBox.critical(self, "Error de Base de Datos",
                                 f"No se pudo conectar a la base de datos.\nError: {e}")
            sys.exit(1)

        # Variables de estado
        self.registros_actuales = []
        self.registro_seleccionado = None

        # Conectar señales
        self.conectar_senales()

        # Configurar tabla
        self.configurar_tabla()

        # Configurar fechas por defecto (última semana)
        self.configurar_fechas_default()

        # Cargar datos iniciales
        self.cargar_todos_registros()

        self.statusBar().showMessage("Listo. Mostrando todos los registros de auditoría.")

    def conectar_senales(self):
        """Conecta todos los eventos de la interfaz"""
        # Botones principales
        self.pushButton_refrescar.clicked.connect(self.cargar_todos_registros)
        self.pushButton_aplicar_filtro.clicked.connect(self.aplicar_filtros)
        self.pushButton_buscar.clicked.connect(self.buscar_usuario)
        self.pushButton_exportar.clicked.connect(self.exportar_csv)
        self.pushButton_ver_detalles.clicked.connect(self.ver_detalles_usuario)

        # Filtro rápido
        self.comboBox_filtro.currentIndexChanged.connect(self.aplicar_filtro_rapido)

        # Tabla
        self.tableWidget_auditoria.itemSelectionChanged.connect(self.registro_seleccionado_cambio)

        # Enter en búsqueda
        self.lineEdit_buscar_usuario.returnPressed.connect(self.buscar_usuario)

    def configurar_tabla(self):
        """Configura las propiedades de la tabla"""
        self.tableWidget_auditoria.setColumnWidth(0, 100)  # ID Registro
        self.tableWidget_auditoria.setColumnWidth(1, 180)  # Fecha Ingreso
        self.tableWidget_auditoria.setColumnWidth(2, 180)  # Fecha Salida
        self.tableWidget_auditoria.setColumnWidth(3, 120)  # Duración
        self.tableWidget_auditoria.setColumnWidth(4, 100)  # ID Usuario
        self.tableWidget_auditoria.setColumnWidth(5, 250)  # Nombre Usuario
        self.tableWidget_auditoria.setColumnWidth(6, 120)  # Estado

        self.tableWidget_auditoria.setSortingEnabled(True)

    def configurar_fechas_default(self):
        """Configura las fechas por defecto (última semana)"""
        fecha_fin = QDate.currentDate()
        fecha_inicio = fecha_fin.addDays(-7)

        self.dateEdit_inicio.setDate(fecha_inicio)
        self.dateEdit_fin.setDate(fecha_fin)

    def cargar_todos_registros(self):
        """Carga todos los registros de auditoría"""
        try:
            registros = self.auditoria_controller.obtener_con_nombres()
            self.registros_actuales = registros
            self.llenar_tabla(registros)
            self.actualizar_estadisticas(registros)
            self.statusBar().showMessage(f"Se cargaron {len(registros)} registros.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar registros:\n{e}")
            self.statusBar().showMessage("Error al cargar registros.")

    def aplicar_filtro_rapido(self):
        """Aplica el filtro rápido seleccionado en el ComboBox"""
        filtro = self.comboBox_filtro.currentText()

        try:
            if filtro == "Solo sesiones activas":
                registros = self.auditoria_controller.obtener_sesiones_activas()
                # Agregar None como fecha_salida para compatibilidad
                registros = [(r[0], r[1], None, r[2], r[3]) for r in registros]
            elif filtro == "Solo sesiones cerradas":
                todos = self.auditoria_controller.obtener_con_nombres()
                registros = [r for r in todos if r[2] is not None]
            else:  # Todos los registros
                registros = self.auditoria_controller.obtener_con_nombres()

            self.registros_actuales = registros
            self.llenar_tabla(registros)
            self.actualizar_estadisticas(registros)
            self.statusBar().showMessage(f"Filtro aplicado: {len(registros)} registros.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al aplicar filtro:\n{e}")

    def aplicar_filtros(self):
        """Aplica los filtros de fecha"""
        try:
            fecha_inicio = self.dateEdit_inicio.date().toPyDate()
            fecha_fin = self.dateEdit_fin.date().toPyDate()

            # Convertir a datetime para la consulta
            fecha_inicio_dt = datetime.combine(fecha_inicio, datetime.min.time())
            fecha_fin_dt = datetime.combine(fecha_fin, datetime.max.time())

            registros = self.auditoria_controller.obtener_por_rango_fechas(
                fecha_inicio_dt,
                fecha_fin_dt
            )

            self.registros_actuales = registros
            self.llenar_tabla(registros)
            self.actualizar_estadisticas(registros)

            self.statusBar().showMessage(
                f"Filtro aplicado: {len(registros)} registros entre "
                f"{fecha_inicio.strftime('%d/%m/%Y')} y {fecha_fin.strftime('%d/%m/%Y')}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al aplicar filtro de fechas:\n{e}")

    def buscar_usuario(self):
        """Busca registros por ID o nombre de usuario"""
        texto_busqueda = self.lineEdit_buscar_usuario.text().strip()

        if not texto_busqueda:
            self.cargar_todos_registros()
            return

        try:
            todos_registros = self.auditoria_controller.obtener_con_nombres()

            # Filtrar por ID o nombre
            if texto_busqueda.isdigit():
                # Buscar por ID de usuario
                registros = [r for r in todos_registros if str(r[3]) == texto_busqueda]
            else:
                # Buscar por nombre (case insensitive)
                texto_upper = texto_busqueda.upper()
                registros = [r for r in todos_registros if texto_upper in r[4].upper()]

            self.registros_actuales = registros
            self.llenar_tabla(registros)
            self.actualizar_estadisticas(registros)
            self.statusBar().showMessage(f"Búsqueda: {len(registros)} registros encontrados.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al buscar:\n{e}")

    def llenar_tabla(self, registros):
        """
        Llena la tabla con los registros proporcionados.

        Formato de registros:
        (id_auditoria, fecha_ingreso, fecha_salida, codigo_usuario, nombre_usuario)
        """
        self.tableWidget_auditoria.setRowCount(0)

        for registro in registros:
            id_audit = registro[0]
            fecha_ingreso = registro[1]
            fecha_salida = registro[2]
            codigo_usuario = registro[3]
            nombre_usuario = registro[4]

            fila = self.tableWidget_auditoria.rowCount()
            self.tableWidget_auditoria.insertRow(fila)

            # Calcular duración
            duracion = "En curso"
            if fecha_salida:
                delta = fecha_salida - fecha_ingreso
                horas = int(delta.total_seconds() / 3600)
                minutos = int((delta.total_seconds() % 3600) / 60)
                duracion = f"{horas}h {minutos}m"

            # Estado
            estado = "🟢 Activa" if fecha_salida is None else "🔴 Cerrada"

            # Formatear fechas
            fecha_ingreso_str = fecha_ingreso.strftime('%d/%m/%Y %H:%M:%S')
            fecha_salida_str = fecha_salida.strftime('%d/%m/%Y %H:%M:%S') if fecha_salida else "-"

            # Agregar datos a las columnas
            self.tableWidget_auditoria.setItem(fila, 0, QTableWidgetItem(str(id_audit)))
            self.tableWidget_auditoria.setItem(fila, 1, QTableWidgetItem(fecha_ingreso_str))
            self.tableWidget_auditoria.setItem(fila, 2, QTableWidgetItem(fecha_salida_str))
            self.tableWidget_auditoria.setItem(fila, 3, QTableWidgetItem(duracion))
            self.tableWidget_auditoria.setItem(fila, 4, QTableWidgetItem(str(codigo_usuario)))
            self.tableWidget_auditoria.setItem(fila, 5, QTableWidgetItem(nombre_usuario))
            self.tableWidget_auditoria.setItem(fila, 6, QTableWidgetItem(estado))

            # Colorear filas según estado
            if fecha_salida is None:
                # Sesión activa - verde claro
                for col in range(7):
                    self.tableWidget_auditoria.item(fila, col).setBackground(
                        QColor(200, 255, 200)
                    )

            # Guardar registro completo en la primera celda
            self.tableWidget_auditoria.item(fila, 0).setData(Qt.UserRole, registro)

    def actualizar_estadisticas(self, registros):
        """Actualiza las etiquetas de estadísticas"""
        total = len(registros)
        activas = sum(1 for r in registros if r[2] is None)
        cerradas = total - activas

        self.label_total_registros.setText(f"📊 Total Registros: {total}")
        self.label_sesiones_activas.setText(f"🟢 Sesiones Activas: {activas}")
        self.label_sesiones_cerradas.setText(f"🔴 Sesiones Cerradas: {cerradas}")

    def registro_seleccionado_cambio(self):
        """Se ejecuta cuando se selecciona un registro en la tabla"""
        seleccion = self.tableWidget_auditoria.selectedItems()

        if not seleccion:
            self.pushButton_ver_detalles.setEnabled(False)
            return

        fila = self.tableWidget_auditoria.currentRow()
        item = self.tableWidget_auditoria.item(fila, 0)
        self.registro_seleccionado = item.data(Qt.UserRole)

        # Habilitar botón de detalles
        self.pushButton_ver_detalles.setEnabled(True)

        # Mostrar info en statusbar
        codigo_usuario = self.registro_seleccionado[3]
        nombre_usuario = self.registro_seleccionado[4]
        self.label_info.setText(f"Registro seleccionado - Usuario: {nombre_usuario} (ID: {codigo_usuario})")

    def ver_detalles_usuario(self):
        """Muestra detalles y estadísticas del usuario seleccionado"""
        if not self.registro_seleccionado:
            return

        codigo_usuario = self.registro_seleccionado[3]
        nombre_usuario = self.registro_seleccionado[4]

        try:
            # Obtener estadísticas del usuario
            stats = self.auditoria_controller.obtener_estadisticas_usuario(codigo_usuario)

            # Obtener todos los registros del usuario
            registros_usuario = self.auditoria_controller.obtener_por_usuario(codigo_usuario)

            mensaje = f"""
<h2>Detalles de {nombre_usuario}</h2>
<p><b>ID Usuario:</b> {codigo_usuario}</p>

<h3>Estadísticas Generales:</h3>
<ul>
    <li><b>Total de Sesiones:</b> {stats.get('total_sesiones', 0)}</li>
    <li><b>Sesiones Cerradas:</b> {stats.get('sesiones_cerradas', 0)}</li>
    <li><b>Sesiones Activas:</b> {stats.get('sesiones_activas', 0)}</li>
    <li><b>Primer Ingreso:</b> {stats.get('primer_ingreso', 'N/A')}</li>
    <li><b>Último Ingreso:</b> {stats.get('ultimo_ingreso', 'N/A')}</li>
</ul>

<h3>Últimas 5 Sesiones:</h3>
"""
            for i, reg in enumerate(registros_usuario[:5], 1):
                estado = "Activa" if reg.esta_activa() else "Cerrada"
                duracion = reg.duracion()
                mensaje += f"<p>{i}. {reg.fecha_ingreso.strftime('%d/%m/%Y %H:%M')} - "
                mensaje += f"Estado: {estado} - Duración: {duracion}</p>"

            # Crear diálogo personalizado
            dialog = QMessageBox(self)
            dialog.setWindowTitle("Detalles del Usuario")
            dialog.setTextFormat(Qt.RichText)
            dialog.setText(mensaje)
            dialog.setIcon(QMessageBox.Information)
            dialog.exec_()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al obtener detalles:\n{e}")

    def exportar_csv(self):
        """Exporta los registros actuales a un archivo CSV"""
        if not self.registros_actuales:
            QMessageBox.warning(self, "Advertencia", "No hay registros para exportar.")
            return

        # Diálogo para seleccionar ubicación del archivo
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Auditoría a CSV",
            f"auditoria_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv)"
        )

        if not filename:
            return

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)

                # Escribir encabezados
                writer.writerow([
                    'ID Registro',
                    'Fecha Ingreso',
                    'Fecha Salida',
                    'Duración (minutos)',
                    'ID Usuario',
                    'Nombre Usuario',
                    'Estado'
                ])

                # Escribir datos
                for registro in self.registros_actuales:
                    id_audit = registro[0]
                    fecha_ingreso = registro[1]
                    fecha_salida = registro[2]
                    codigo_usuario = registro[3]
                    nombre_usuario = registro[4]

                    # Calcular duración en minutos
                    duracion_min = ""
                    if fecha_salida:
                        delta = fecha_salida - fecha_ingreso
                        duracion_min = int(delta.total_seconds() / 60)

                    estado = "Activa" if fecha_salida is None else "Cerrada"

                    writer.writerow([
                        id_audit,
                        fecha_ingreso.strftime('%Y-%m-%d %H:%M:%S'),
                        fecha_salida.strftime('%Y-%m-%d %H:%M:%S') if fecha_salida else '',
                        duracion_min,
                        codigo_usuario,
                        nombre_usuario,
                        estado
                    ])

            QMessageBox.information(
                self,
                "Éxito",
                f"Datos exportados exitosamente a:\n{filename}"
            )
            self.statusBar().showMessage(f"Datos exportados a {filename}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al exportar:\n{e}")


# Para pruebas independientes
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = AuditoriaWindow()
    window.show()
    sys.exit(app.exec_())