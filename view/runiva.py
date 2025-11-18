from PyQt5.QtWidgets import QApplication
import sys
from ventana_iva import VentanaIVA

app = QApplication(sys.argv)

ventana = VentanaIVA()
ventana.show()

sys.exit(app.exec_())
