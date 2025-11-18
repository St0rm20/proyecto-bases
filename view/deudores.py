from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QMessageBox, QPushButton
from PyQt5.QtCore import Qt

from model.credito import Credito
from report.pdf_utils import crear_pdf  # <-- ESTE ES EL IMPORT CORRECTO


class VentanaMorosos(QWidget):

    def __init__(self, parent=None):  # ✅ 1. Cambiar firma del __init__
        super().__init__(parent)

        # ✅ 2. Agregar después de super().__init__()
        self.lobby_window = parent

        uic.loadUi("deudores.ui", self)

        self.modelo_credito = Credito()

        # ✅ 4. Conectar botón refrescar (si existe en tu UI)
        # Si tienes un botón refrescar en deudores.ui, conéctalo así:
        # self.btn_refrescar.clicked.connect(self.actualizar_vista)

        self.btn_generar_pdf.clicked.connect(self.exportar_pdf)
        self.btn_cerrar.clicked.connect(self.close)

        self.cargar_morosos()

        # ✅ 3. Agregar botón de regreso
        self.crear_boton_regreso()

    # ------------------------------------------------------------
    # CARGA DE DATOS
    # ------------------------------------------------------------
    def cargar_morosos(self):
        """Carga la tabla usando los datos del modelo Credito"""
        filas = self.modelo_credito.obtener_clientes_morosos()

        self.tabla_morosos.setRowCount(len(filas))
        self.tabla_morosos.setColumnCount(5)

        for i, fila in enumerate(filas):
            nombre, codigo_venta, id_pago, fecha_vencimiento, estado = fila

            self.tabla_morosos.setItem(i, 0, QTableWidgetItem(str(nombre)))
            self.tabla_morosos.setItem(i, 1, QTableWidgetItem(str(codigo_venta)))
            self.tabla_morosos.setItem(i, 2, QTableWidgetItem(str(id_pago)))
            self.tabla_morosos.setItem(i, 3, QTableWidgetItem(str(fecha_vencimiento)))
            self.tabla_morosos.setItem(i, 4, QTableWidgetItem(str(estado)))

    # ------------------------------------------------------------
    # GENERAR PDF USANDO EL MODELO
    # ------------------------------------------------------------
    def generar_pdf_morosos(self):
        """
        Genera un PDF usando el MODELO Credito (no SQL directo)
        """
        filas = self.modelo_credito.obtener_clientes_morosos()

        headers = ["Cliente", "Venta", "Cuota", "Vencimiento", "Estado"]
        pdf_name = "reporte_morosos.pdf"

        crear_pdf(pdf_name, "Clientes Morosos", headers, filas)

        return pdf_name

    # ------------------------------------------------------------
    # BOTÓN EXPORTAR
    # ------------------------------------------------------------
    def exportar_pdf(self):
        """Acción del botón para exportar el PDF"""
        try:
            archivo = self.generar_pdf_morosos()
            QMessageBox.information(self, "PDF generado", f"Archivo creado:\n\n{archivo}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # ✅ 5. Agregar los 3 métodos del checklist
    def actualizar_vista(self):
        """Actualiza la vista recargando los datos de morosos"""
        self.cargar_morosos()

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

        # Agregar el botón a la interfaz
        # Dependiendo de tu diseño UI, puedes agregarlo a un layout existente
        # Por ejemplo, si tienes un layout vertical:
        # self.layout().addWidget(btn)

        # O si prefieres colocarlo en un lugar específico de tu UI
        # Esta implementación depende de cómo esté diseñado tu deudores.ui

    def regresar_al_lobby(self):
        """Regresa a la ventana principal del lobby"""
        if self.lobby_window:
            self.lobby_window.show()
            self.lobby_window.raise_()
            self.lobby_window.activateWindow()
        self.close()