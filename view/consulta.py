"""
Ventana para consultar ventas recientes
Por: Juan David Ramirez Carmona y Miguel Ángel Vargas Peláez
Fecha: 2025-11
Licencia: GPLv3
"""

import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QPushButton
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor

from model.venta import Venta
from view.detalle_venta import VentanaDetalleFactura


class VentasWindow(QtWidgets.QMainWindow):
    """Ventana para consultar ventas recientes"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Referencia al lobby
        self.lobby_window = parent

        # Cargar UI
        try:
            uic.loadUi('ventas_window.ui', self)
        except FileNotFoundError:
            # Si no existe el UI, creamos uno básico
            self.crear_interfaz_rapida()

        # Controlador de ventas
        self.venta_controller = Venta()

        # Conectar señales
        self.conectar_senales()

        # Cargar datos iniciales
        self.cargar_ventas_recientes()

        # Agregar botón de regreso
        self.crear_boton_regreso()

        self.statusBar().showMessage(f"Cargadas {self.tableWidget_ventas.rowCount()} ventas recientes")

    def crear_interfaz_rapida(self):
        """Crea una interfaz rápida si no existe el archivo .ui"""
        self.setWindowTitle("Consultar Ventas - Sistema de Gestión")
        self.setGeometry(100, 100, 1000, 600)

        # Widget central
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        layout = QtWidgets.QVBoxLayout(central_widget)

        # Título
        titulo = QtWidgets.QLabel("📊 VENTAS RECIENTES")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(titulo)

        # Frame de controles
        frame_controles = QtWidgets.QFrame()
        layout_controles = QtWidgets.QHBoxLayout(frame_controles)

        # Botón cargar
        self.btn_cargar = QPushButton("🔄 Cargar Ventas Recientes")
        self.btn_cargar.setMinimumHeight(35)
        layout_controles.addWidget(self.btn_cargar)

        # Botón limpiar
        self.btn_limpiar = QPushButton("🗑️ Limpiar")
        self.btn_limpiar.setMinimumHeight(35)
        layout_controles.addWidget(self.btn_limpiar)

        layout_controles.addStretch()

        layout.addWidget(frame_controles)

        # Tabla de ventas
        self.tableWidget_ventas = QtWidgets.QTableWidget()
        layout.addWidget(self.tableWidget_ventas)

        # Configurar tabla
        self.configurar_tabla()

    def configurar_tabla(self):
        """Configura la tabla de ventas"""
        # Definir columnas
        columnas = [
            "Código Venta", "Fecha", "Cliente", "Tipo",
            "Total", "Estado", "Acciones"
        ]

        self.tableWidget_ventas.setColumnCount(len(columnas))
        self.tableWidget_ventas.setHorizontalHeaderLabels(columnas)

        # Ajustar anchos de columnas
        self.tableWidget_ventas.setColumnWidth(0, 120)  # Código
        self.tableWidget_ventas.setColumnWidth(1, 100)  # Fecha
        self.tableWidget_ventas.setColumnWidth(2, 200)  # Cliente
        self.tableWidget_ventas.setColumnWidth(3, 80)  # Tipo
        self.tableWidget_ventas.setColumnWidth(4, 100)  # Total
        self.tableWidget_ventas.setColumnWidth(5, 100)  # Estado
        self.tableWidget_ventas.setColumnWidth(6, 100)  # Acciones

        # Habilitar sorting
        self.tableWidget_ventas.setSortingEnabled(True)

    def conectar_senales(self):
        """Conecta todas las señales de la interfaz"""
        if hasattr(self, 'btn_cargar'):
            self.btn_cargar.clicked.connect(self.cargar_ventas_recientes)
        if hasattr(self, 'btn_limpiar'):
            self.btn_limpiar.clicked.connect(self.limpiar_tabla)

        # Si tienes otros botones en tu UI, conéctalos aquí
        # Por ejemplo:
        # self.pushButton_buscar.clicked.connect(self.buscar_ventas)
        # self.pushButton_exportar.clicked.connect(self.exportar_reporte)

    def cargar_ventas_recientes(self):
        """Carga las ventas más recientes en la tabla"""
        try:
            # Obtener todas las ventas
            ventas = self.venta_controller.obtener_todos_como_objetos()

            # Ordenar por fecha (más recientes primero) y tomar las últimas 50
            ventas_ordenadas = sorted(
                ventas,
                key=lambda x: x.fecha if hasattr(x, 'fecha') and x.fecha else QDate.currentDate(),
                reverse=True
            )[:50]  # Últimas 50 ventas

            self.mostrar_ventas_en_tabla(ventas_ordenadas)

            self.statusBar().showMessage(f"✅ Se cargaron {len(ventas_ordenadas)} ventas recientes")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar ventas:\n{e}")
            self.statusBar().showMessage("❌ Error al cargar ventas")

    def mostrar_ventas_en_tabla(self, ventas):
        """Muestra las ventas en la tabla"""
        self.tableWidget_ventas.setRowCount(0)

        if not ventas:
            self.tableWidget_ventas.setRowCount(1)
            self.tableWidget_ventas.setItem(0, 0, QtWidgets.QTableWidgetItem("No hay ventas registradas"))
            return

        for i, venta in enumerate(ventas):
            self.tableWidget_ventas.insertRow(i)

            # Código de venta
            self.tableWidget_ventas.setItem(i, 0, QtWidgets.QTableWidgetItem(
                venta.codigo_venta if hasattr(venta, 'codigo_venta') else "N/A"
            ))

            # Fecha
            fecha_str = ""
            if hasattr(venta, 'fecha') and venta.fecha:
                if isinstance(venta.fecha, str):
                    fecha_str = venta.fecha
                else:
                    fecha_str = venta.fecha.strftime("%d/%m/%Y")
            self.tableWidget_ventas.setItem(i, 1, QtWidgets.QTableWidgetItem(fecha_str))

            # Cliente (solo ID por ahora)
            cliente_str = str(venta.codigo_cliente) if hasattr(venta, 'codigo_cliente') else "N/A"
            self.tableWidget_ventas.setItem(i, 2, QtWidgets.QTableWidgetItem(cliente_str))

            # Tipo de venta
            tipo_str = venta.tipo_venta if hasattr(venta, 'tipo_venta') else "N/A"
            self.tableWidget_ventas.setItem(i, 3, QtWidgets.QTableWidgetItem(tipo_str))

            # Total
            total_str = f"${venta.total_neto:,.2f}" if hasattr(venta, 'total_neto') and venta.total_neto else "$0.00"
            self.tableWidget_ventas.setItem(i, 4, QtWidgets.QTableWidgetItem(total_str))

            # Estado
            estado_str = venta.estado_venta if hasattr(venta, 'estado_venta') else "N/A"
            estado_item = QtWidgets.QTableWidgetItem(estado_str)

            # Color según estado
            if estado_str == "Completada":
                estado_item.setForeground(QColor(0, 128, 0))  # Verde
            elif estado_str == "Cancelada":
                estado_item.setForeground(QColor(255, 0, 0))  # Rojo
            elif estado_str == "Pendiente":
                estado_item.setForeground(QColor(255, 165, 0))  # Naranja

            self.tableWidget_ventas.setItem(i, 5, estado_item)

            # Botón de acciones
            btn_ver = QPushButton("👁️ Ver")
            btn_ver.setStyleSheet("""
                QPushButton {
                    background-color: #0078D7;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 5px 10px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #005A9E;
                }
            """)
            btn_ver.clicked.connect(lambda checked, codigo=venta.codigo_venta: self.ver_detalle_venta(codigo))

            self.tableWidget_ventas.setCellWidget(i, 6, btn_ver)

            # Guardar objeto venta para referencia
            self.tableWidget_ventas.item(i, 0).setData(Qt.UserRole, venta)

    def ver_detalle_venta(self, codigo_venta):
        """Abre la ventana de detalle de la venta seleccionada"""
        try:
            self.ventana_detalle = VentanaDetalleFactura(codigo_venta, parent=self.lobby_window)
            self.ventana_detalle.show()
            self.statusBar().showMessage(f"✅ Abriendo detalle de venta: {codigo_venta}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir el detalle:\n{e}")

    def limpiar_tabla(self):
        """Limpia la tabla de ventas"""
        self.tableWidget_ventas.setRowCount(0)
        self.statusBar().showMessage("Tabla limpiada")

    def buscar_ventas(self):
        """Busca ventas por criterios específicos"""
        # Puedes implementar búsqueda por fecha, cliente, etc.
        QMessageBox.information(self, "Búsqueda", "Funcionalidad de búsqueda en desarrollo")

    def exportar_reporte(self):
        """Exporta el reporte de ventas a PDF"""
        # Puedes implementar exportación a PDF
        QMessageBox.information(self, "Exportar", "Funcionalidad de exportación en desarrollo")

    def crear_boton_regreso(self):
        """Crea el botón para regresar al menú principal"""
        btn = QPushButton("← Regresar al Menú")
        btn.setStyleSheet("""
            QPushButton {
                background-color: #6C757D;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5A6268;
            }
        """)
        btn.clicked.connect(self.regresar_al_lobby)
        self.statusBar().addPermanentWidget(btn)

    def regresar_al_lobby(self):
        """Regresa a la ventana principal del lobby"""
        if self.lobby_window:
            self.lobby_window.show()
            self.lobby_window.raise_()
            self.lobby_window.activateWindow()
        self.close()

    # ✅ Métodos del checklist
    def actualizar_vista(self):
        """Actualiza la vista recargando las ventas"""
        self.cargar_ventas_recientes()
        self.statusBar().showMessage("Vista actualizada correctamente")


if __name__ == "__main__":
    # Para pruebas
    app = QtWidgets.QApplication(sys.argv)
    window = VentasWindow()
    window.show()
    sys.exit(app.exec_())