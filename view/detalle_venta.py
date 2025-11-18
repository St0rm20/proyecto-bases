from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QMessageBox, QTableWidgetItem, QPushButton
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont, QColor

from report.report import generar_factura_pdf
from model.venta import Venta
from model.cliente import Cliente
from model.detalle_venta_producto import DetalleVentaProducto
import os


class VentanaDetalleFactura(QWidget):

    def __init__(self, codigo_venta, parent=None):  # ✅ 1. Cambiar firma del __init__
        super().__init__(parent)

        # ✅ 2. Agregar después de super().__init__()
        self.lobby_window = parent

        ruta_ui = os.path.join(os.path.dirname(__file__), "detalle_venta.ui")
        uic.loadUi(ruta_ui, self)

        self.codigo_venta = codigo_venta

        # Inicializar modelos
        self.modelo_venta = Venta()
        self.modelo_cliente = Cliente()
        self.modelo_detalle = DetalleVentaProducto()

        # Cache de datos
        self.datos_venta = None
        self.datos_cliente = None
        self.detalles_completos = []  # Lista de tuplas (detalle, nombre_producto, precio, subtotal)

        # Conectar botones
        self.btn_generar_pdf.clicked.connect(self.exportar_pdf)
        self.btn_cerrar.clicked.connect(self.close)

        # ✅ 4. Conectar botón refrescar (si existe en tu UI)
        # Si tienes un botón refrescar en detalle_venta.ui, conéctalo así:
        # self.btn_refrescar.clicked.connect(self.actualizar_vista)

        # Cargar datos
        self.cargar_datos()

        # ✅ 3. Agregar botón de regreso
        self.crear_boton_regreso()

    def cargar_datos(self):
        """Inicia la carga de datos de la factura"""
        try:
            self._mostrar_estado("Cargando datos de la factura...")
            QTimer.singleShot(50, self._procesar_carga_datos)

        except Exception as e:
            self._mostrar_error(f"Error al iniciar carga: {str(e)}")

    def _procesar_carga_datos(self):
        """Procesa la carga de datos en secuencia"""
        try:
            # 1. Obtener datos de la venta por código
            self.datos_venta = self._obtener_venta_por_codigo()
            if not self.datos_venta:
                raise Exception(f"No se encontró la venta con código: {self.codigo_venta}")

            # 2. Obtener datos del cliente
            self.datos_cliente = self._obtener_datos_cliente()
            if not self.datos_cliente:
                raise Exception("No se encontró el cliente asociado a esta venta")

            # 3. Obtener detalles completos de la venta
            self.detalles_completos = self._obtener_detalles_completos()

            # 4. Actualizar interfaz
            self._actualizar_interfaz_completa()

            self._mostrar_estado("Factura cargada correctamente")

        except Exception as e:
            self._mostrar_error(str(e))

    def _obtener_venta_por_codigo(self):
        """Obtiene los datos de la venta usando el código de venta.
           Si no la encuentra, muestra todas las ventas disponibles."""
        try:
            ventas = self.modelo_venta.obtener_todos_como_objetos()

            # Buscar venta por código
            for venta in ventas:
                if venta.codigo_venta == self.codigo_venta:
                    return venta

            # Si no se encontró → mostrar todas las ventas existentes
            lista = "\n".join(
                f"- Código: {v.codigo_venta} | Cliente: {v.codigo_cliente} | Fecha: {v.fecha.strftime('%d/%m/%Y')}"
                for v in ventas
            )

            QMessageBox.warning(
                self,
                "Venta no encontrada",
                (
                    f"No se encontró la venta con código: {self.codigo_venta}\n\n"
                    "Estas son las ventas disponibles:\n\n"
                    f"{lista if lista else 'No hay ventas registradas.'}"
                )
            )

            return None

        except Exception as e:
            print(f"Error obteniendo venta por código: {e}")
            return None

    def _obtener_datos_cliente(self):
        """Obtiene los datos del cliente usando el modelo Cliente"""
        try:
            return self.modelo_cliente.obtener_por_codigo(self.datos_venta.codigo_cliente)
        except Exception as e:
            print(f"Error obteniendo datos del cliente: {e}")
            return None

    def _obtener_detalles_completos(self):
        """Obtiene los detalles completos de la venta usando los modelos"""
        try:
            # Obtener detalles básicos del modelo DetalleVentaProducto
            detalles_basicos = self.modelo_detalle.obtener_por_venta(self.datos_venta.id_venta)

            # Obtener información completa de cada producto
            detalles_completos = []
            for detalle in detalles_basicos:
                producto_info = self._obtener_info_producto(detalle.codigo_producto)
                if producto_info:
                    nombre_producto, precio_unitario = producto_info
                    subtotal = precio_unitario * detalle.cantidad
                    detalles_completos.append((detalle, nombre_producto, precio_unitario, subtotal))

            return detalles_completos

        except Exception as e:
            print(f"Error obteniendo detalles completos: {e}")
            return []

    def _obtener_info_producto(self, codigo_producto):
        """Obtiene información del producto (nombre y precio) usando consulta directa"""
        try:
            from database.connection import get_connection
            conn = get_connection()
            cursor = conn.cursor()

            # CORREGIDO: Usar "PRODUCTO" en lugar de "producto" o "Producto"
            sql = "SELECT nombre, valor_venta FROM PRODUCTO WHERE codigo = :codigo"
            cursor.execute(sql, {"codigo": codigo_producto})
            resultado = cursor.fetchone()

            if resultado:
                return resultado[0], float(resultado[1])
            return None

        except Exception as e:
            print(f"Error obteniendo información del producto {codigo_producto}: {e}")
            return None

    def _actualizar_interfaz_completa(self):
        """Actualiza toda la interfaz con los datos obtenidos"""
        self._actualizar_cabecera_factura()
        self._actualizar_seccion_totales()
        self._actualizar_tabla_detalles()

    def _actualizar_cabecera_factura(self):
        """Actualiza la cabecera de la factura"""
        self.lbl_numero_factura.setText(f"Factura: {self.datos_venta.codigo_venta}")
        self.lbl_fecha.setText(f"Fecha: {self.datos_venta.fecha.strftime('%d/%m/%Y')}")
        self.lbl_cliente.setText(f"Cliente: {self.datos_cliente.nombre}")

        # Información adicional del cliente
        if hasattr(self, 'lbl_info_cliente'):
            info_cliente = self._formatear_info_cliente()
            self.lbl_info_cliente.setText(info_cliente)

    def _formatear_info_cliente(self):
        """Formatea la información adicional del cliente"""
        info_parts = []
        if self.datos_cliente.telefono:
            info_parts.append(f"Tel: {self.datos_cliente.telefono}")
        if self.datos_cliente.municipio:
            info_parts.append(f"Ciudad: {self.datos_cliente.municipio}")
        if self.datos_cliente.departamento:
            info_parts.append(f"Depto: {self.datos_cliente.departamento}")

        return " | ".join(info_parts) if info_parts else "Sin información adicional"

    def _actualizar_seccion_totales(self):
        """Actualiza la sección de totales"""
        # Totales principales
        if self.datos_venta.total_bruto is not None:
            self.lbl_bruto.setText(f"${self.datos_venta.total_bruto:,.2f}")
        else:
            self.lbl_bruto.setText("$0.00")

        if self.datos_venta.iva_total is not None:
            self.lbl_iva.setText(f"${self.datos_venta.iva_total:,.2f}")
        else:
            self.lbl_iva.setText("$0.00")

        if self.datos_venta.total_neto is not None:
            self.lbl_total.setText(f"${self.datos_venta.total_neto:,.2f}")
        else:
            self.lbl_total.setText("$0.00")

        # Información de estado
        if hasattr(self, 'lbl_estado_venta'):
            estado = self.datos_venta.estado_venta or "Pendiente"
            tipo = self.datos_venta.tipo_venta or "No especificado"
            self.lbl_estado_venta.setText(f"Estado: {estado} | Tipo: {tipo}")

    def _actualizar_tabla_detalles(self):
        """Actualiza la tabla de detalles de productos"""
        if not self.detalles_completos:
            self._mostrar_tabla_vacia()
            return

        # Configurar tabla
        self.tabla_detalle.setRowCount(len(self.detalles_completos))
        self.tabla_detalle.setColumnCount(4)
        self.tabla_detalle.setHorizontalHeaderLabels([
            "Producto", "Cantidad", "Precio Unitario", "Subtotal"
        ])

        # Llenar tabla con datos
        total_general = 0.0

        for i, (detalle, nombre_producto, precio_unitario, subtotal) in enumerate(self.detalles_completos):
            self.tabla_detalle.setItem(i, 0, QTableWidgetItem(nombre_producto))
            self.tabla_detalle.setItem(i, 1, QTableWidgetItem(str(detalle.cantidad)))
            self.tabla_detalle.setItem(i, 2, QTableWidgetItem(f"${precio_unitario:,.2f}"))
            self.tabla_detalle.setItem(i, 3, QTableWidgetItem(f"${subtotal:,.2f}"))

            total_general += subtotal

        # Agregar fila de total
        self._agregar_fila_total(total_general)

        # Ajustar columnas
        self.tabla_detalle.resizeColumnsToContents()

    def _mostrar_tabla_vacia(self):
        """Muestra mensaje cuando no hay detalles"""
        self.tabla_detalle.setRowCount(1)
        self.tabla_detalle.setColumnCount(1)
        self.tabla_detalle.setHorizontalHeaderLabels(["Información"])

        item = QTableWidgetItem("No hay productos registrados en esta venta")
        self.tabla_detalle.setItem(0, 0, item)

    def _agregar_fila_total(self, total):
        """Agrega la fila de total con formato especial"""
        fila_total = self.tabla_detalle.rowCount()
        self.tabla_detalle.setRowCount(fila_total + 1)

        # Celda de "TOTAL" (combinada)
        item_total = QTableWidgetItem("TOTAL")
        item_total.setFont(QFont("Arial", 10, QFont.Bold))
        item_total.setBackground(QColor(240, 240, 240))
        self.tabla_detalle.setItem(fila_total, 0, item_total)
        self.tabla_detalle.setSpan(fila_total, 0, 1, 3)  # Combinar primeras 3 columnas

        # Celda de valor total
        item_valor = QTableWidgetItem(f"${total:,.2f}")
        item_valor.setFont(QFont("Arial", 10, QFont.Bold))
        item_valor.setForeground(QColor(0, 100, 0))  # Verde oscuro
        item_valor.setBackground(QColor(240, 240, 240))
        self.tabla_detalle.setItem(fila_total, 3, item_valor)

    def _mostrar_estado(self, mensaje):
        """Muestra mensaje de estado en la interfaz"""
        if hasattr(self, 'lbl_estado'):
            self.lbl_estado.setText(mensaje)

    def _mostrar_error(self, mensaje):
        """Muestra mensaje de error y cierra la ventana"""
        QMessageBox.critical(self, "Error al cargar factura", mensaje)
        self.close()

    def exportar_pdf(self):
        """Exporta la factura a PDF"""
        if not self.datos_venta:
            QMessageBox.warning(self, "Error", "No hay datos de venta para exportar.")
            return

        try:
            self.btn_generar_pdf.setEnabled(False)
            self.btn_generar_pdf.setText("Generando PDF...")

            # Ejecutar en segundo plano
            QTimer.singleShot(100, self._ejecutar_exportacion_pdf)

        except Exception as e:
            self._restaurar_boton_pdf()
            QMessageBox.critical(self, "Error", f"Error al iniciar exportación: {str(e)}")

    def _ejecutar_exportacion_pdf(self):
        """Ejecuta la exportación a PDF en segundo plano"""
        try:
            archivo = generar_factura_pdf(self.codigo_venta)

            QMessageBox.information(
                self,
                "PDF Generado Exitosamente",
                f"La factura ha sido exportada correctamente:\n\n{archivo}"
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error al Generar PDF",
                f"No se pudo generar el archivo PDF:\n\n{str(e)}"
            )
        finally:
            self._restaurar_boton_pdf()

    def _restaurar_boton_pdf(self):
        """Restaura el botón de PDF a su estado normal"""
        self.btn_generar_pdf.setEnabled(True)
        self.btn_generar_pdf.setText("Exportar a PDF")

    def obtener_resumen_venta(self):
        """Retorna un resumen de la venta para posibles usos externos"""
        if not self.datos_venta or not self.detalles_completos:
            return None

        return {
            'codigo_venta': self.datos_venta.codigo_venta,
            'fecha': self.datos_venta.fecha,
            'cliente': self.datos_cliente.nombre,
            'total_productos': len(self.detalles_completos),
            'total_neto': self.datos_venta.total_neto,
            'estado': self.datos_venta.estado_venta
        }

    def closeEvent(self, event):
        """Maneja el evento de cierre de la ventana"""
        # Limpiar recursos
        self.datos_venta = None
        self.datos_cliente = None
        self.detalles_completos = []
        event.accept()

    # ✅ 5. Agregar los 3 métodos del checklist
    def actualizar_vista(self):
        """Actualiza la vista recargando los datos de la factura"""
        try:
            self._mostrar_estado("Actualizando datos...")
            # Limpiar cache
            self.datos_venta = None
            self.datos_cliente = None
            self.detalles_completos = []

            # Recargar datos
            QTimer.singleShot(50, self._procesar_carga_datos)

        except Exception as e:
            self._mostrar_error(f"Error al actualizar vista: {str(e)}")

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
        # Esta implementación depende de cómo esté diseñado tu detalle_venta.ui

    def regresar_al_lobby(self):
        """Regresa a la ventana principal del lobby"""
        if self.lobby_window:
            self.lobby_window.show()
            self.lobby_window.raise_()
            self.lobby_window.activateWindow()
        self.close()