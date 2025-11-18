from PyQt5.QtWidgets import QApplication
from deudores import VentanaMorosos
import sys

app = QApplication(sys.argv)

ventana = VentanaMorosos()
ventana.show()

sys.exit(app.exec_())
