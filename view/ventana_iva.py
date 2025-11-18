from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QMessageBox

from report.report import reporte_iva_trimestre


class VentanaIVA(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("ventana_iva.ui", self)

        # Llenar combos
        self.cargar_anios()
        self.cargar_trimestres()

        # Conectar botones
        self.btn_generar.clicked.connect(self.generar_pdf)
        self.btn_cerrar.clicked.connect(self.close)

    # ===========================
    # Cargar años disponibles
    # ===========================
    def cargar_anios(self):
        """Carga un rango de años razonable para la DIAN"""
        from datetime import datetime
        anio_actual = datetime.now().year

        # Últimos 10 años
        for a in range(anio_actual, anio_actual - 10, -1):
            self.combo_anio.addItem(str(a))

    # ===========================
    # Cargar trimestres
    # ===========================
    def cargar_trimestres(self):
        self.combo_trimestre.addItem("1")
        self.combo_trimestre.addItem("2")
        self.combo_trimestre.addItem("3")
        self.combo_trimestre.addItem("4")

    # ===========================
    # Generar PDF
    # ===========================
    def generar_pdf(self):
        anio = self.combo_anio.currentText()
        trimestre = self.combo_trimestre.currentText()

        try:
            archivo = reporte_iva_trimestre(int(anio), int(trimestre))
            QMessageBox.information(
                self,
                "Reporte generado",
                f"El PDF del IVA Trimestral ha sido creado:\n\n{archivo}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
