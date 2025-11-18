from PyQt5.QtWidgets import QApplication
import sys
from inventario import VentanaInventario
from database.connection import get_connection
app = QApplication(sys.argv)
conn = get_connection()
cur = conn.cursor()

cur.execute("SELECT USER FROM dual")
print("Usuario en Python:", cur.fetchone())

cur.execute("SELECT table_name FROM user_tables")
print("Tablas en Python:", cur.fetchall())
ventana = VentanaInventario()
ventana.show()

sys.exit(app.exec_())
