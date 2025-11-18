from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QMessageBox, QTableWidgetItem

from database.connection import get_connection
from report.report import reporte_inventario_por_categoria

# Importa tu modelo Producto
from model.producto import Producto


class VentanaInventario(QWidget):

    def __init__(self):
        super().__init__()
        uic.loadUi("inventario.ui", self)

        self.modelo_producto = Producto()   # <--- Tu modelo real

        self.btn_pdf.clicked.connect(self.generar_pdf)
        self.btn_cerrar.clicked.connect(self.close)
        self.btn_filtrar.clicked.connect(self.aplicar_filtro)

        self.cargar_categorias()
        self.cargar_inventario()

    # ============================
    # Cargar categorías en combo
    # ============================
    def cargar_categorias(self):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT codigo_categoria, nombre FROM categoria ORDER BY codigo_categoria")
        categorias = [fila[0] for fila in cursor.fetchall()]

        self.combo_categoria.addItem("TODAS")
        for c in categorias:
            self.combo_categoria.addItem(str(c))

    # ============================
    # Cargar inventario completo
    # ============================
    def cargar_inventario(self, categoria=None):
        self.tabla_inv.setRowCount(0)

        # Si es "TODAS" o None, mostrar todos
        if categoria is None or categoria == "TODAS":
            productos = self.modelo_producto.obtener_todos_como_objetos()
        else:
            # Pasar la categoría como string, sin convertir a int
            productos = self.modelo_producto.buscar_por_categoria(categoria)

        # Configurar tabla
        self.tabla_inv.setRowCount(len(productos))
        self.tabla_inv.setColumnCount(5)
        self.tabla_inv.setHorizontalHeaderLabels(
            ["Categoría", "Código", "Producto", "Costo", "Venta"]
        )

        # Llenar tabla
        for row, p in enumerate(productos):
            self.tabla_inv.setItem(row, 0, QTableWidgetItem(str(p.codigo_categoria)))
            self.tabla_inv.setItem(row, 1, QTableWidgetItem(str(p.codigo)))
            self.tabla_inv.setItem(row, 2, QTableWidgetItem(p.nombre))
            self.tabla_inv.setItem(row, 3, QTableWidgetItem(str(p.valor_adquisicion)))
            self.tabla_inv.setItem(row, 4, QTableWidgetItem(str(p.valor_venta)))
    # ============================
    # Aplicar filtro del ComboBox
    # ============================
    def aplicar_filtro(self):
        categoria = self.combo_categoria.currentText()
        self.cargar_inventario(categoria)

    # ============================
    # PDF
    # ============================
    def generar_pdf(self):
        try:
            archivo = reporte_inventario_por_categoria()
            QMessageBox.information(self, "PDF Generado", f"Archivo guardado:\n{archivo}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
