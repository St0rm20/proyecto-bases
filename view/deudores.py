from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QMessageBox

from model.credito import Credito
from report.pdf_utils import crear_pdf   # <-- ESTE ES EL IMPORT CORRECTO


class VentanaMorosos(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("deudores.ui", self)

        self.modelo_credito = Credito()

        self.btn_generar_pdf.clicked.connect(self.exportar_pdf)
        self.btn_generar_pdf.clicked.connect(self.exportar_pdf)
        self.btn_cerrar.clicked.connect(self.close)

        self.cargar_morosos()

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
