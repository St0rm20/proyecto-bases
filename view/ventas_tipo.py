from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QMessageBox, QTableWidgetItem, QPushButton
from PyQt5.QtCore import QDate

from report.report import reporte_ventas_por_tipo
from model.venta import Venta
from database.connection import get_connection


class VentanaVentasTipo(QWidget):

    def __init__(self, parent=None):  # ✅ 1. Cambiar firma del __init__
        super().__init__(parent)

        # ✅ 2. Agregar después de super().__init__()
        self.lobby_window = parent

        uic.loadUi("ventas_tipo.ui", self)

        # Inicializar el modelo de ventas
        self.modelo_venta = Venta()

        # Conectar señales
        self.btn_buscar.clicked.connect(self.buscar)
        self.btn_pdf.clicked.connect(self.generar_pdf)
        self.btn_cerrar.clicked.connect(self.close)

        # Configurar fecha actual por defecto para QLineEdit
        self._configurar_fechas_por_defecto()

        # ✅ 3. Agregar botón de regreso
        self.crear_boton_regreso()

    def _configurar_fechas_por_defecto(self):
        """Configura fechas por defecto para QLineEdit"""
        fecha_actual = QDate.currentDate().toString("yyyy-MM-dd")
        fecha_inicio = QDate.currentDate().addDays(-30).toString("yyyy-MM-dd")  # Últimos 30 días

        self.txt_inicio.setText(fecha_inicio)
        self.txt_fin.setText(fecha_actual)

        # Agregar placeholders para ayudar al usuario
        self.txt_inicio.setPlaceholderText("YYYY-MM-DD")
        self.txt_fin.setPlaceholderText("YYYY-MM-DD")

    def _validar_fechas(self):
        """Valida que las fechas tengan formato correcto"""
        inicio = self.txt_inicio.text().strip()
        fin = self.txt_fin.text().strip()

        # Validar que no estén vacías
        if not inicio or not fin:
            return False, "Debe ingresar ambas fechas.", None, None

        # Validar formato YYYY-MM-DD
        try:
            fecha_inicio = QDate.fromString(inicio, "yyyy-MM-dd")
            fecha_fin = QDate.fromString(fin, "yyyy-MM-dd")

            if not fecha_inicio.isValid():
                return False, "Fecha inicial inválida. Use formato YYYY-MM-DD", None, None
            if not fecha_fin.isValid():
                return False, "Fecha final inválida. Use formato YYYY-MM-DD", None, None

            if fecha_inicio > fecha_fin:
                return False, "La fecha inicial no puede ser mayor que la fecha final", None, None

            return True, "", inicio, fin

        except Exception:
            return False, "Error en el formato de fechas. Use YYYY-MM-DD", None, None

    # ---------------------------------------
    # Buscar ventas por tipo usando el modelo
    # ---------------------------------------
    def buscar(self):
        # Validar fechas primero
        valido, mensaje, inicio, fin = self._validar_fechas()
        if not valido:
            QMessageBox.warning(self, "Error", mensaje)
            return

        try:
            # Usar el modelo para buscar ventas por fecha
            ventas = self.modelo_venta.buscar_por_fecha_(inicio, fin)

            # Agrupar por tipo de venta
            resumen = self._agrupar_por_tipo(ventas)

            # Mostrar en la tabla
            self._mostrar_resumen(resumen)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al buscar ventas: {str(e)}")

    def _agrupar_por_tipo(self, ventas):
        """Agrupa las ventas por tipo y cuenta la cantidad"""
        resumen = {}
        for venta in ventas:
            tipo = venta.tipo_venta or "Sin tipo"  # Manejar casos None
            if tipo in resumen:
                resumen[tipo] += 1
            else:
                resumen[tipo] = 1
        return resumen

    def _mostrar_resumen(self, resumen):
        """Muestra el resumen en la tabla"""
        if not resumen:
            self.tabla_resumen.setRowCount(1)
            self.tabla_resumen.setItem(0, 0, QTableWidgetItem("No hay datos"))
            self.tabla_resumen.setItem(0, 1, QTableWidgetItem("0"))
            return

        tipos = list(resumen.keys())
        self.tabla_resumen.setRowCount(len(tipos))
        self.tabla_resumen.setColumnCount(2)
        self.tabla_resumen.setHorizontalHeaderLabels(["Tipo Venta", "Cantidad"])

        for i, tipo in enumerate(tipos):
            cantidad = resumen[tipo]
            self.tabla_resumen.setItem(i, 0, QTableWidgetItem(str(tipo)))
            self.tabla_resumen.setItem(i, 1, QTableWidgetItem(str(cantidad)))

        # Ajustar el tamaño de las columnas al contenido
        self.tabla_resumen.resizeColumnsToContents()

    # ---------------------------------------
    # Generar PDF
    # ---------------------------------------
    def generar_pdf(self):
        # Validar fechas primero
        valido, mensaje, inicio, fin = self._validar_fechas()
        if not valido:
            QMessageBox.warning(self, "Error", mensaje)
            return

        try:
            # Verificar que hay datos para generar el reporte
            ventas = self.modelo_venta.buscar_por_fecha_(inicio, fin)
            if not ventas:
                QMessageBox.warning(self, "Sin datos",
                                    "No hay ventas en el rango de fechas seleccionado.")
                return

            # Generar PDF usando la función existente
            archivo = reporte_ventas_por_tipo(inicio, fin)
            QMessageBox.information(self, "Éxito", f"PDF generado:\n{archivo}")

        except Exception as e:
            QMessageBox.critical(self, "Error al generar PDF", str(e))

    # ---------------------------------------
    # Métodos adicionales útiles
    # ---------------------------------------
    def limpiar_campos(self):
        """Limpia todos los campos"""
        self.txt_inicio.clear()
        self.txt_fin.clear()
        self.tabla_resumen.setRowCount(0)

    def obtener_resumen_actual(self):
        """Retorna el resumen actual mostrado en la tabla"""
        resumen = {}
        for row in range(self.tabla_resumen.rowCount()):
            tipo_item = self.tabla_resumen.item(row, 0)
            cantidad_item = self.tabla_resumen.item(row, 1)
            if tipo_item and cantidad_item:
                resumen[tipo_item.text()] = int(cantidad_item.text())
        return resumen

    # ✅ 4. Agregar los 3 métodos del checklist
    def actualizar_vista(self):
        """Actualiza la vista ejecutando la búsqueda actual"""
        self.buscar()

    def crear_boton_regreso(self):
        """Crea el botón para regresar al menú principal"""
        btn = QPushButton("← Regresar al Menú")
        btn.setStyleSheet("""
            QPushButton {
                background-color: #6C757D; color: white; border: none;
                border-radius: 5px; padding: 10px 20px; font-size: 14px; font-weight: bold;
            }
            QPushButton:hover { background-color: #5A6268; }
        """)
        btn.clicked.connect(self.regresar_al_lobby)

        # Agregar el botón a la interfaz - dependiendo de cómo esté diseñado tu UI
        # Si tienes un layout vertical o horizontal, agrégalo ahí
        # Por ejemplo:
        # self.layout().addWidget(btn)  # Si usas QVBoxLayout o QHBoxLayout

        # O si prefieres en una barra de herramientas o en un grupo específico
        # Esta implementación depende de tu diseño UI específico

    def regresar_al_lobby(self):
        """Regresa a la ventana principal del lobby"""
        if self.lobby_window:
            self.lobby_window.show()
            self.lobby_window.raise_()
            self.lobby_window.activateWindow()
        self.close()