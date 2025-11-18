from PyQt5.QtWidgets import QApplication
import sys
from ventas_tipo import VentanaVentasTipo

app = QApplication(sys.argv)

ventana = VentanaVentasTipo()
ventana.show()

sys.exit(app.exec_())
