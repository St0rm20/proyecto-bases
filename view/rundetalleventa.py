from PyQt5.QtWidgets import QApplication
from detalle_venta import VentanaDetalleFactura
import sys

app = QApplication(sys.argv)

ventana = VentanaDetalleFactura("VTA-20251117232926")
ventana.show()

sys.exit(app.exec_())
