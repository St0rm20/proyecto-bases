"""
Sistema de Ventas con gestión de créditos
Por: Juan David Ramirez Carmona y Miguel Ángel Vargas Peláez
Fecha: 2025-11
Licencia: GPLv3
"""

import sys
from datetime import date, datetime
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QInputDialog
from PyQt5.QtCore import Qt
from decimal import Decimal

from model.cliente import Cliente, ClienteData
from model.producto import Producto, ProductoData
from model.venta import Venta
from model.credito import Credito
from model.detalle_venta_producto import DetalleVentaProducto


class VentasWindow(QtWidgets.QMainWindow):
    """Sistema completo de ventas con soporte para créditos"""

    def __init__(self):
        super().__init__()

        # Cargar UI
        try:
            uic.loadUi('ventas.ui', self)
        except FileNotFoundError:
            print("Error: Asegúrate de que 'ventas.ui' esté en el mismo directorio.")
            sys.exit(1)

        # Controladores
        self.cliente_controller = Cliente()
        self.producto_controller = Producto()
        self.venta_controller = Venta()
        self.credito_controller = Credito()
        self.detalle_controller = DetalleVentaProducto()

        # Variables de estado
        self.clientes = []
        self.productos = []
        self.carrito = []  # Lista de dict: {producto, cantidad, precio, subtotal}
        self.cliente_seleccionado = None
        self.producto_seleccionado = None

        # Configurar UI
        self.configurar_tabla()
        self.conectar_senales()

        # Cargar datos
        self.cargar_clientes()
        self.cargar_productos()

        self.statusBar().showMessage("Sistema de ventas listo. Seleccione un cliente para comenzar.")

    def conectar_senales(self):
        """Conecta todas las señales de la interfaz"""
        # Cliente
        self.comboBox_cliente.currentIndexChanged.connect(self.cliente_cambiado)

        # Producto
        self.comboBox_producto.currentIndexChanged.connect(self.producto_cambiado)
        self.pushButton_agregar_producto.clicked.connect(self.agregar_producto_carrito)

        # Tipo de pago
        self.radioButton_contado.toggled.connect(self.tipo_pago_cambiado)
        self.radioButton_credito.toggled.connect(self.tipo_pago_cambiado)
        self.comboBox_plazo.currentIndexChanged.connect(self.calcular_resumen)

        # Carrito
        self.tableWidget_carrito.itemSelectionChanged.connect(self.item_carrito_seleccionado)
        self.pushButton_editar_item.clicked.connect(self.editar_item_carrito)
        self.pushButton_eliminar_item.clicked.connect(self.eliminar_item_carrito)

        # Acciones finales
        self.pushButton_limpiar.clicked.connect(self.limpiar_todo)
        self.pushButton_finalizar.clicked.connect(self.finalizar_venta)

    def configurar_tabla(self):
        """Configura la tabla del carrito"""
        self.tableWidget_carrito.setColumnWidth(0, 80)  # Código
        self.tableWidget_carrito.setColumnWidth(1, 250)  # Producto
        self.tableWidget_carrito.setColumnWidth(2, 80)  # Cantidad
        self.tableWidget_carrito.setColumnWidth(3, 100)  # Precio
        self.tableWidget_carrito.setColumnWidth(4, 120)  # Subtotal

    def cargar_clientes(self):
        """Carga todos los clientes en el ComboBox"""
        try:
            self.clientes = self.cliente_controller.obtener_todos_como_objetos()

            self.comboBox_cliente.clear()
            self.comboBox_cliente.addItem("-- Seleccione un cliente --", None)

            for cliente in self.clientes:
                self.comboBox_cliente.addItem(
                    f"{cliente.codigo_cliente} - {cliente.nombre}",
                    cliente.codigo_cliente
                )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar clientes:\n{e}")

    def cargar_productos(self):
        """Carga todos los productos en el ComboBox"""
        try:
            self.productos = self.producto_controller.obtener_todos_como_objetos()

            self.comboBox_producto.clear()
            self.comboBox_producto.addItem("-- Seleccione un producto --", None)

            for producto in self.productos:
                self.comboBox_producto.addItem(
                    f"{producto.codigo} - {producto.nombre}",
                    producto.codigo
                )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar productos:\n{e}")

    def cliente_cambiado(self):
        """Se ejecuta cuando cambia la selección del cliente"""
        codigo_cliente = self.comboBox_cliente.currentData()

        if codigo_cliente is None:
            self.cliente_seleccionado = None
            self.label_info_cliente.setText("Información del cliente aparecerá aquí")
            return

        # Buscar cliente
        self.cliente_seleccionado = next(
            (c for c in self.clientes if c.codigo_cliente == codigo_cliente),
            None
        )

        if self.cliente_seleccionado:
            info = f"<b>Nombre:</b> {self.cliente_seleccionado.nombre}<br>"
            info += f"<b>Teléfono:</b> {self.cliente_seleccionado.telefono or 'N/A'}<br>"
            info += f"<b>Dirección:</b> {self.cliente_seleccionado.direccion or 'N/A'}"
            self.label_info_cliente.setText(info)

    def producto_cambiado(self):
        """Se ejecuta cuando cambia la selección del producto"""
        codigo_producto = self.comboBox_producto.currentData()

        if codigo_producto is None:
            self.producto_seleccionado = None
            self.label_cantidad_disponible.setText(
                '<html><body><p><span style="font-weight:600; color:#0066CC;">0 unidades</span></p></body></html>'
            )
            self.label_precio_producto.setText(
                '<html><body><p><span style="font-weight:600; color:#009900;">$0.00</span></p></body></html>'
            )
            self.spinBox_cantidad.setMaximum(1)
            return

        # Buscar producto
        self.producto_seleccionado = next(
            (p for p in self.productos if p.codigo == codigo_producto),
            None
        )

        if self.producto_seleccionado:
            # Mostrar cantidad disponible
            cantidad = self.producto_seleccionado.cantidad
            color = "#009900" if cantidad > 0 else "#CC0000"
            self.label_cantidad_disponible.setText(
                f'<html><body><p><span style="font-weight:600; color:{color};">{cantidad} unidades</span></p></body></html>'
            )

            # Mostrar precio
            precio = float(self.producto_seleccionado.valor_venta or 0)
            self.label_precio_producto.setText(
                f'<html><body><p><span style="font-weight:600; color:#009900;">${precio:,.2f}</span></p></body></html>'
            )

            # Configurar spinbox
            self.spinBox_cantidad.setMaximum(max(1, cantidad))
            self.spinBox_cantidad.setValue(1)

    def agregar_producto_carrito(self):
        """Agrega el producto seleccionado al carrito"""
        # Validaciones
        if not self.cliente_seleccionado:
            QMessageBox.warning(self, "Advertencia", "Debe seleccionar un cliente primero.")
            return

        if not self.producto_seleccionado:
            QMessageBox.warning(self, "Advertencia", "Debe seleccionar un producto.")
            return

        try:
            cantidad_solicitada = self.spinBox_cantidad.value()
            cantidad_disponible = self.producto_seleccionado.cantidad

            if cantidad_solicitada > cantidad_disponible:
                QMessageBox.warning(
                    self,
                    "Stock Insuficiente",
                    f"Solo hay {cantidad_disponible} unidades disponibles."
                )
                return

            # CREAR UNA COPIA DEL PRODUCTO PARA EVITAR REFERENCIAS
            from copy import copy
            producto_copia = copy(self.producto_seleccionado)

            # Verificar si el producto ya está en el carrito
            for item in self.carrito:
                if item['producto'].codigo == producto_copia.codigo:
                    # Actualizar cantidad
                    nueva_cantidad = item['cantidad'] + cantidad_solicitada
                    if nueva_cantidad > cantidad_disponible:
                        QMessageBox.warning(
                            self,
                            "Stock Insuficiente",
                            f"La cantidad total ({nueva_cantidad}) excede el stock disponible ({cantidad_disponible})."
                        )
                        return

                    item['cantidad'] = nueva_cantidad
                    item['subtotal'] = item['cantidad'] * item['precio']
                    self.actualizar_tabla_carrito()
                    self.calcular_resumen()
                    self.statusBar().showMessage(f"Cantidad actualizada: {producto_copia.nombre}")
                    return

            # Agregar nuevo producto al carrito
            precio = float(producto_copia.valor_venta or 0)
            subtotal = precio * cantidad_solicitada

            item = {
                'producto': producto_copia,  # Usar la copia en lugar del original
                'cantidad': cantidad_solicitada,
                'precio': precio,
                'subtotal': subtotal
            }

            self.carrito.append(item)
            self.actualizar_tabla_carrito()
            self.calcular_resumen()

            # Resetear selección
            self.comboBox_producto.setCurrentIndex(0)
            self.spinBox_cantidad.setValue(1)

            self.statusBar().showMessage(f"Producto agregado: {producto_copia.nombre}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al agregar producto al carrito:\n{e}")
            print(f"Error en agregar_producto_carrito: {e}")

    def actualizar_tabla_carrito(self):
        """Actualiza la tabla del carrito"""
        self.tableWidget_carrito.setRowCount(0)

        for item in self.carrito:
            fila = self.tableWidget_carrito.rowCount()
            self.tableWidget_carrito.insertRow(fila)

            self.tableWidget_carrito.setItem(fila, 0, QTableWidgetItem(str(item['producto'].codigo)))
            self.tableWidget_carrito.setItem(fila, 1, QTableWidgetItem(item['producto'].nombre))
            self.tableWidget_carrito.setItem(fila, 2, QTableWidgetItem(str(item['cantidad'])))
            self.tableWidget_carrito.setItem(fila, 3, QTableWidgetItem(f"${item['precio']:,.2f}"))
            self.tableWidget_carrito.setItem(fila, 4, QTableWidgetItem(f"${item['subtotal']:,.2f}"))

            # Guardar referencia al item
            self.tableWidget_carrito.item(fila, 0).setData(Qt.UserRole, item)

        # Habilitar botón finalizar si hay items
        self.pushButton_finalizar.setEnabled(len(self.carrito) > 0)

    def item_carrito_seleccionado(self):
        """Se ejecuta cuando se selecciona un item del carrito"""
        hay_seleccion = len(self.tableWidget_carrito.selectedItems()) > 0
        self.pushButton_editar_item.setEnabled(hay_seleccion)
        self.pushButton_eliminar_item.setEnabled(hay_seleccion)

    def editar_item_carrito(self):
        """Edita la cantidad de un producto en el carrito"""
        fila_actual = self.tableWidget_carrito.currentRow()
        if fila_actual < 0:
            return

        item = self.tableWidget_carrito.item(fila_actual, 0).data(Qt.UserRole)
        producto = item['producto']
        cantidad_actual = item['cantidad']

        # Diálogo para nueva cantidad
        nueva_cantidad, ok = QInputDialog.getInt(
            self,
            "Editar Cantidad",
            f"Nueva cantidad para {producto.nombre}:",
            cantidad_actual,
            1,
            producto.cantidad
        )

        if ok and nueva_cantidad != cantidad_actual:
            item['cantidad'] = nueva_cantidad
            item['subtotal'] = nueva_cantidad * item['precio']
            self.actualizar_tabla_carrito()
            self.calcular_resumen()
            self.statusBar().showMessage(f"Cantidad actualizada: {producto.nombre}")

    def eliminar_item_carrito(self):
        """Elimina un producto del carrito"""
        fila_actual = self.tableWidget_carrito.currentRow()
        if fila_actual < 0:
            return

        item = self.tableWidget_carrito.item(fila_actual, 0).data(Qt.UserRole)
        producto = item['producto']

        respuesta = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            f"¿Eliminar {producto.nombre} del carrito?",
            QMessageBox.Yes | QMessageBox.No
        )

        if respuesta == QMessageBox.Yes:
            self.carrito.remove(item)
            self.actualizar_tabla_carrito()
            self.calcular_resumen()
            self.statusBar().showMessage(f"Producto eliminado: {producto.nombre}")

    def tipo_pago_cambiado(self):
        """Se ejecuta cuando cambia el tipo de pago"""
        es_credito = self.radioButton_credito.isChecked()

        # Habilitar/deshabilitar opciones de crédito
        self.widget_opciones_credito.setEnabled(es_credito)
        self.widget_resumen_credito.setVisible(es_credito)

        if es_credito and self.cliente_seleccionado:
            # Verificar si el cliente tiene crédito activo
            credito_activo = self.verificar_credito_activo(self.cliente_seleccionado.codigo_cliente)

            if credito_activo:
                QMessageBox.warning(
                    self,
                    "Crédito Activo",
                    f"El cliente {self.cliente_seleccionado.nombre} ya tiene un crédito activo.\n\n"
                    "Debe completar el pago del crédito actual antes de solicitar uno nuevo."
                )
                self.radioButton_contado.setChecked(True)
                return

        self.calcular_resumen()

    def verificar_credito_activo(self, codigo_cliente: int) -> bool:
        """Verifica si un cliente tiene un crédito activo"""
        try:
            # Buscar ventas del cliente
            ventas = self.venta_controller.buscar_por_cliente(codigo_cliente)

            for venta in ventas:
                # Si la venta es a crédito y no está pagada
                if venta.tipo_venta == "Credito" and venta.estado_credito != "Pagado":
                    return True

            return False

        except Exception as e:
            print(f"Error al verificar crédito activo: {e}")
            return False

    def calcular_resumen(self):
        """Calcula y muestra el resumen de la venta"""
        if not self.carrito:
            self.label_subtotal.setText("Subtotal: $0.00")
            self.label_iva.setText("IVA: $0.00")
            self.label_total.setText(
                '<html><body><p><span style="font-size:14pt; font-weight:600;">TOTAL: $0.00</span></p></body></html>')
            return

        # Calcular subtotal (suma de todos los items)
        subtotal = sum(item['subtotal'] for item in self.carrito)

        # Calcular IVA (19% sobre el subtotal)
        iva = subtotal * 0.19

        # Total
        total = subtotal + iva

        # Actualizar labels
        self.label_subtotal.setText(f"Subtotal: ${subtotal:,.2f}")
        self.label_iva.setText(f"IVA (19%): ${iva:,.2f}")
        self.label_total.setText(
            f'<html><body><p><span style="font-size:14pt; font-weight:600;">TOTAL: ${total:,.2f}</span></p></body></html>'
        )

        # Si es crédito, calcular detalles
        if self.radioButton_credito.isChecked():
            self.calcular_resumen_credito(total)

    def calcular_resumen_credito(self, total: float):
        """Calcula y muestra el resumen para pago a crédito"""
        # Cuota inicial: 30%
        cuota_inicial = total * 0.30

        # Saldo a financiar: 70%
        saldo_financiar = total * 0.70

        # Interés: 5% sobre el saldo
        interes = saldo_financiar * 0.05

        # Total financiado
        total_financiado = saldo_financiar + interes

        # Plazo
        plazo_text = self.comboBox_plazo.currentText()
        plazo_meses = int(plazo_text.split()[0])

        # Cuota mensual
        cuota_mensual = total_financiado / plazo_meses

        # Actualizar labels
        self.label_cuota_inicial.setText(f"💰 Cuota Inicial (30%): ${cuota_inicial:,.2f}")
        self.label_saldo_financiar.setText(f"📊 Saldo a Financiar (70%): ${saldo_financiar:,.2f}")
        self.label_interes.setText(f"📈 Interés (5%): ${interes:,.2f}")
        self.label_total_financiado.setText(
            f'<html><body><p><span style="font-weight:600;">Total Financiado: ${total_financiado:,.2f}</span></p></body></html>'
        )
        self.label_cuota_mensual.setText(
            f'<html><body><p><span style="font-size:11pt; font-weight:600; color:#0066CC;">'
            f'💳 Cuota Mensual ({plazo_meses} meses): ${cuota_mensual:,.2f}</span></p></body></html>'
        )

    def limpiar_todo(self):
        """Limpia todo el formulario"""
        respuesta = QMessageBox.question(
            self,
            "Confirmar",
            "¿Está seguro de limpiar toda la venta actual?",
            QMessageBox.Yes | QMessageBox.No
        )

        if respuesta == QMessageBox.Yes:
            self.carrito = []
            self.actualizar_tabla_carrito()
            self.calcular_resumen()
            self.comboBox_cliente.setCurrentIndex(0)
            self.comboBox_producto.setCurrentIndex(0)
            self.radioButton_contado.setChecked(True)
            self.statusBar().showMessage("Venta limpiada. Puede comenzar una nueva.")

    def finalizar_venta(self):
        """Procesa y finaliza la venta"""
        # Validaciones finales
        if not self.cliente_seleccionado:
            QMessageBox.warning(self, "Error", "Debe seleccionar un cliente.")
            return

        if not self.carrito:
            QMessageBox.warning(self, "Error", "El carrito está vacío.")
            return

        es_credito = self.radioButton_credito.isChecked()

        # Si es crédito, verificar nuevamente
        if es_credito:
            if self.verificar_credito_activo(self.cliente_seleccionado.codigo_cliente):
                QMessageBox.warning(
                    self,
                    "Error",
                    "El cliente tiene un crédito activo. No se puede procesar la venta."
                )
                return

        # Confirmación
        tipo_pago = "CRÉDITO" if es_credito else "CONTADO"
        subtotal = sum(item['subtotal'] for item in self.carrito)
        iva = subtotal * 0.19
        total = subtotal + iva

        mensaje = f"¿Confirmar venta?\n\n"
        mensaje += f"Cliente: {self.cliente_seleccionado.nombre}\n"
        mensaje += f"Tipo de Pago: {tipo_pago}\n"
        mensaje += f"Total Items: {len(self.carrito)}\n"
        mensaje += f"Total a Pagar: ${total:,.2f}\n"

        if es_credito:
            cuota_inicial = total * 0.30
            mensaje += f"\nCuota Inicial: ${cuota_inicial:,.2f}\n"

        respuesta = QMessageBox.question(
            self,
            "Confirmar Venta",
            mensaje,
            QMessageBox.Yes | QMessageBox.No
        )

        if respuesta == QMessageBox.Yes:
            self.procesar_venta(es_credito, subtotal, iva, total)

    def procesar_venta(self, es_credito: bool, subtotal: float, iva: float, total: float):
        """Procesa la venta en la base de datos"""
        try:
            # Generar ID de venta (puedes mejorarlo con secuencias)
            id_venta = int(datetime.now().timestamp())
            codigo_venta = f"VTA-{datetime.now().strftime('%Y%m%d%H%M%S')}"

            # Crear venta
            tipo_venta = "Credito" if es_credito else "Contado"
            estado_credito = "Activo" if es_credito else None

            exito_venta = self.venta_controller.crear(
                id_venta=id_venta,
                codigo_venta=codigo_venta,
                estado_venta="Completada",
                fecha=date.today(),
                tipo_venta=tipo_venta,
                codigo_cliente=self.cliente_seleccionado.codigo_cliente,
                total_bruto=subtotal,
                iva_total=iva,
                total_neto=total,
                estado_credito=estado_credito
            )

            if not exito_venta:
                raise Exception("No se pudo crear la venta")

            # Agregar detalles de venta
            for item in self.carrito:
                self.detalle_controller.crear(
                    id_venta=id_venta,
                    codigo_producto=item['producto'].codigo,
                    cantidad=item['cantidad']
                )

                # Actualizar stock del producto
                nuevo_stock = item['producto'].cantidad - item['cantidad']
                self.producto_controller.actualizar(
                    codigo=item['producto'].codigo,
                    cantidad=nuevo_stock
                )

            # Si es crédito, crear el crédito
            if es_credito:
                self.crear_credito(id_venta, total)

            # Éxito
            QMessageBox.information(
                self,
                "Venta Exitosa",
                f"✅ Venta procesada exitosamente\n\n"
                f"Código: {codigo_venta}\n"
                f"Total: ${total:,.2f}"
            )

            # Limpiar
            self.carrito = []
            self.actualizar_tabla_carrito()
            self.calcular_resumen()
            self.comboBox_cliente.setCurrentIndex(0)
            self.comboBox_producto.setCurrentIndex(0)
            self.radioButton_contado.setChecked(True)

            # Recargar productos (para actualizar stock)
            self.cargar_productos()

            self.statusBar().showMessage("Venta finalizada exitosamente.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al procesar venta:\n{e}")

    def crear_credito(self, id_venta: int, total: float):
        """Crea el registro de crédito"""
        # Calcular valores
        cuota_inicial = total * 0.30
        saldo_financiar = total * 0.70
        interes_porcentaje = 5.0
        saldo_financiado = saldo_financiar + (saldo_financiar * 0.05)

        plazo_text = self.comboBox_plazo.currentText()
        plazo_meses = int(plazo_text.split()[0])

        # Generar ID de crédito
        id_credito = int(datetime.now().timestamp()) + 1000

        # Crear crédito
        self.credito_controller.crear(
            id_credito=id_credito,
            cuota_inicial=cuota_inicial,
            saldo_financiado=saldo_financiado,
            interes=interes_porcentaje,
            plazo_meses=plazo_meses,
            id_venta=id_venta
        )


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = VentasWindow()
    window.show()
    sys.exit(app.exec_())