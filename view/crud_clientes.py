"""
Ventana CRUD para Gestión de Clientes
Por: Juan David Ramirez Carmona y Miguel Ángel Vargas Peláez
Fecha: 2025-11
Licencia: GPLv3
"""

import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QPushButton
from PyQt5.QtCore import Qt
from model.cliente import Cliente, ClienteData


class CrudClientesWindow(QtWidgets.QMainWindow):
    """
    Ventana CRUD completa para gestionar clientes
    """

    def __init__(self, parent=None):  # ← CAMBIO 1: Agregar parent
        super().__init__()

        self.lobby_window = parent  # ← CAMBIO 2: Guardar referencia al lobby

        # Cargar el archivo .ui
        try:
            uic.loadUi('crud_clientes.ui', self)
        except FileNotFoundError:
            print("Error: Asegúrate de que 'crud_clientes.ui' esté en el mismo directorio.")
            sys.exit(1)

        # Instanciar el controlador de Cliente
        try:
            self.cliente_controller = Cliente()
        except Exception as e:
            QMessageBox.critical(self, "Error de Base de Datos",
                                 f"No se pudo conectar a la base de datos.\nError: {e}")
            sys.exit(1)

        # Variables de estado
        self.modo_actual = "visualizacion"
        self.cliente_seleccionado = None

        # Conectar señales
        self.conectar_senales()

        # Configurar tabla
        self.configurar_tabla()

        # Cargar datos iniciales
        self.cargar_todos_clientes()

        # Inicializar estado
        self.limpiar_formulario()

        # ← CAMBIO 3: Crear botón de regreso
        self.crear_boton_regreso()

        self.statusBar().showMessage("Listo. Seleccione un cliente o cree uno nuevo.")

    def conectar_senales(self):
        """Conecta todos los eventos de la interfaz"""
        # Botones de búsqueda y lista
        self.pushButton_buscar.clicked.connect(self.buscar_clientes)
        self.pushButton_refrescar.clicked.connect(self.actualizar_vista)  # ← CAMBIO 4
        self.pushButton_nuevo.clicked.connect(self.modo_nuevo_cliente)
        self.lineEdit_buscar.returnPressed.connect(self.buscar_clientes)

        # Botones de acción
        self.pushButton_guardar.clicked.connect(self.guardar_cliente)
        self.pushButton_editar.clicked.connect(self.modo_edicion)
        self.pushButton_eliminar.clicked.connect(self.eliminar_cliente)
        self.pushButton_cancelar.clicked.connect(self.cancelar_operacion)

        # Tabla
        self.tableWidget_clientes.itemSelectionChanged.connect(self.cliente_seleccionado_cambio)

    def configurar_tabla(self):
        """Configura las propiedades de la tabla"""
        self.tableWidget_clientes.setColumnWidth(0, 100)
        self.tableWidget_clientes.setColumnWidth(1, 200)
        self.tableWidget_clientes.setColumnWidth(2, 120)
        self.tableWidget_clientes.setColumnWidth(3, 150)
        self.tableWidget_clientes.setColumnWidth(4, 150)
        self.tableWidget_clientes.setSortingEnabled(True)

    def cargar_todos_clientes(self):
        """Carga todos los clientes en la tabla"""
        try:
            clientes = self.cliente_controller.obtener_todos_como_objetos()
            self.llenar_tabla(clientes)
            self.statusBar().showMessage(f"Se cargaron {len(clientes)} clientes.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar clientes:\n{e}")
            self.statusBar().showMessage("Error al cargar clientes.")

    def buscar_clientes(self):
        """Busca clientes según el texto ingresado"""
        texto_busqueda = self.lineEdit_buscar.text().strip()

        if not texto_busqueda:
            self.cargar_todos_clientes()
            return

        try:
            if texto_busqueda.isdigit():
                cliente = self.cliente_controller.obtener_por_id(int(texto_busqueda))
                clientes = [cliente] if cliente else []
                if clientes and not isinstance(clientes[0], ClienteData):
                    clientes = [ClienteData(*clientes[0])]
            else:
                clientes = self.cliente_controller.buscar_por_nombre(texto_busqueda)

            self.llenar_tabla(clientes)
            self.statusBar().showMessage(f"Se encontraron {len(clientes)} clientes.")

        except Exception as e:
            QMessageBox.warning(self, "Error de Búsqueda", f"Error al buscar:\n{e}")
            self.statusBar().showMessage("Error en la búsqueda.")

    def llenar_tabla(self, clientes):
        """Llena la tabla con los clientes proporcionados"""
        self.tableWidget_clientes.setRowCount(0)

        for cliente in clientes:
            if isinstance(cliente, tuple):
                cliente = ClienteData(*cliente)

            fila = self.tableWidget_clientes.rowCount()
            self.tableWidget_clientes.insertRow(fila)

            self.tableWidget_clientes.setItem(fila, 0, QTableWidgetItem(str(cliente.codigo_cliente)))
            self.tableWidget_clientes.setItem(fila, 1, QTableWidgetItem(cliente.nombre))
            self.tableWidget_clientes.setItem(fila, 2, QTableWidgetItem(cliente.telefono or ""))
            self.tableWidget_clientes.setItem(fila, 3, QTableWidgetItem(cliente.departamento or ""))
            self.tableWidget_clientes.setItem(fila, 4, QTableWidgetItem(cliente.municipio or ""))

            self.tableWidget_clientes.item(fila, 0).setData(Qt.UserRole, cliente)

        self.label_total.setText(f"Total: {len(clientes)} clientes")

    def cliente_seleccionado_cambio(self):
        """Se ejecuta cuando se selecciona un cliente en la tabla"""
        seleccion = self.tableWidget_clientes.selectedItems()

        if not seleccion:
            return

        fila = self.tableWidget_clientes.currentRow()
        item = self.tableWidget_clientes.item(fila, 0)
        self.cliente_seleccionado = item.data(Qt.UserRole)

        self.mostrar_detalles_cliente(self.cliente_seleccionado)
        self.cambiar_modo("visualizacion")

    def mostrar_detalles_cliente(self, cliente: ClienteData):
        """Muestra los detalles del cliente en el formulario"""
        self.lineEdit_codigo.setText(str(cliente.codigo_cliente))
        self.lineEdit_nombre.setText(cliente.nombre)
        self.lineEdit_telefono.setText(cliente.telefono or "")
        self.lineEdit_departamento.setText(cliente.departamento or "")
        self.lineEdit_municipio.setText(cliente.municipio or "")
        self.lineEdit_calle.setText(cliente.calle or "")
        self.lineEdit_direccion.setText(cliente.direccion or "")

    def limpiar_formulario(self):
        """Limpia todos los campos del formulario"""
        self.lineEdit_codigo.clear()
        self.lineEdit_nombre.clear()
        self.lineEdit_telefono.clear()
        self.lineEdit_departamento.clear()
        self.lineEdit_municipio.clear()
        self.lineEdit_calle.clear()
        self.lineEdit_direccion.clear()
        self.cliente_seleccionado = None

    def cambiar_modo(self, modo):
        """Cambia el modo de operación de la ventana"""
        self.modo_actual = modo

        if modo == "visualizacion":
            self.label_modo.setText('<html><body><p align="center"><span style="font-weight:600;">Modo: Visualización</span></p></body></html>')
            self.habilitar_formulario(False)
            self.pushButton_editar.setEnabled(True)
            self.pushButton_eliminar.setEnabled(True)
            self.pushButton_guardar.setEnabled(False)
            self.pushButton_cancelar.setEnabled(False)
            self.lineEdit_codigo.setEnabled(False)

        elif modo == "edicion":
            self.label_modo.setText('<html><body><p align="center"><span style="font-weight:600; color:#FF8C00;">Modo: Editando</span></p></body></html>')
            self.habilitar_formulario(True)
            self.pushButton_editar.setEnabled(False)
            self.pushButton_eliminar.setEnabled(False)
            self.pushButton_guardar.setEnabled(True)
            self.pushButton_cancelar.setEnabled(True)
            self.lineEdit_codigo.setEnabled(False)

        elif modo == "nuevo":
            self.label_modo.setText('<html><body><p align="center"><span style="font-weight:600; color:#28A745;">Modo: Nuevo Cliente</span></p></body></html>')
            self.habilitar_formulario(True)
            self.pushButton_editar.setEnabled(False)
            self.pushButton_eliminar.setEnabled(False)
            self.pushButton_guardar.setEnabled(True)
            self.pushButton_cancelar.setEnabled(True)
            self.lineEdit_codigo.setEnabled(True)

    def habilitar_formulario(self, habilitar):
        """Habilita o deshabilita los campos del formulario"""
        self.lineEdit_nombre.setEnabled(habilitar)
        self.lineEdit_telefono.setEnabled(habilitar)
        self.lineEdit_departamento.setEnabled(habilitar)
        self.lineEdit_municipio.setEnabled(habilitar)
        self.lineEdit_calle.setEnabled(habilitar)
        self.lineEdit_direccion.setEnabled(habilitar)

    def modo_nuevo_cliente(self):
        """Activa el modo para crear un nuevo cliente"""
        self.limpiar_formulario()
        self.cambiar_modo("nuevo")
        self.lineEdit_codigo.setFocus()
        self.statusBar().showMessage("Ingrese los datos del nuevo cliente.")

    def modo_edicion(self):
        """Activa el modo de edición"""
        if not self.cliente_seleccionado:
            QMessageBox.warning(self, "Advertencia", "Debe seleccionar un cliente primero.")
            return

        self.cambiar_modo("edicion")
        self.lineEdit_nombre.setFocus()
        self.statusBar().showMessage("Editando cliente. Realice los cambios y guarde.")

    def validar_formulario(self):
        """Valida que los campos obligatorios estén llenos"""
        if not self.lineEdit_codigo.text().strip():
            QMessageBox.warning(self, "Validación", "El código es obligatorio.")
            self.lineEdit_codigo.setFocus()
            return False

        if not self.lineEdit_nombre.text().strip():
            QMessageBox.warning(self, "Validación", "El nombre es obligatorio.")
            self.lineEdit_nombre.setFocus()
            return False

        return True

    def guardar_cliente(self):
        """Guarda el cliente (nuevo o editado)"""
        if not self.validar_formulario():
            return

        try:
            codigo = int(self.lineEdit_codigo.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Error", "El código debe ser un número válido.")
            return

        nombre = self.lineEdit_nombre.text().strip()
        telefono = self.lineEdit_telefono.text().strip() or None
        departamento = self.lineEdit_departamento.text().strip() or None
        municipio = self.lineEdit_municipio.text().strip() or None
        calle = self.lineEdit_calle.text().strip() or None
        direccion = self.lineEdit_direccion.text().strip() or None

        try:
            if self.modo_actual == "nuevo":
                exito = self.cliente_controller.crear(
                    codigo_cliente=codigo, nombre=nombre, telefono=telefono,
                    departamento=departamento, municipio=municipio,
                    calle=calle, direccion=direccion
                )

                if exito:
                    QMessageBox.information(self, "Éxito", "Cliente creado exitosamente.")
                    self.actualizar_vista()  # ← CAMBIO 5
                    self.limpiar_formulario()
                    self.cambiar_modo("visualizacion")
                else:
                    QMessageBox.warning(self, "Error", "No se pudo crear el cliente.")

            elif self.modo_actual == "edicion":
                exito = self.cliente_controller.actualizar(
                    codigo_cliente=codigo, nombre=nombre, telefono=telefono,
                    departamento=departamento, municipio=municipio,
                    calle=calle, direccion=direccion
                )

                if exito:
                    QMessageBox.information(self, "Éxito", "Cliente actualizado exitosamente.")
                    self.actualizar_vista()  # ← CAMBIO 6
                    self.cambiar_modo("visualizacion")
                else:
                    QMessageBox.warning(self, "Error", "No se pudo actualizar el cliente.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar:\n{e}")

    def eliminar_cliente(self):
        """Elimina el cliente seleccionado"""
        if not self.cliente_seleccionado:
            QMessageBox.warning(self, "Advertencia", "Debe seleccionar un cliente primero.")
            return

        respuesta = QMessageBox.question(
            self, "Confirmar Eliminación",
            f"¿Está seguro de eliminar al cliente '{self.cliente_seleccionado.nombre}'?\n\n"
            "Esta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if respuesta == QMessageBox.Yes:
            try:
                exito = self.cliente_controller.eliminar(self.cliente_seleccionado.codigo_cliente)

                if exito:
                    QMessageBox.information(self, "Éxito", "Cliente eliminado exitosamente.")
                    self.actualizar_vista()  # ← CAMBIO 7
                    self.limpiar_formulario()
                    self.cambiar_modo("visualizacion")
                else:
                    QMessageBox.warning(self, "Error", "No se pudo eliminar el cliente.")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al eliminar:\n{e}")

    def cancelar_operacion(self):
        """Cancela la operación actual"""
        if self.modo_actual == "nuevo":
            self.limpiar_formulario()
            self.cambiar_modo("visualizacion")
        elif self.modo_actual == "edicion":
            if self.cliente_seleccionado:
                self.mostrar_detalles_cliente(self.cliente_seleccionado)
            self.cambiar_modo("visualizacion")

        self.statusBar().showMessage("Operación cancelada.")

    # ========================================
    # ← CAMBIOS 8, 9, 10: NUEVOS MÉTODOS
    # ========================================

    def actualizar_vista(self):
        """Actualiza los datos de la vista"""
        self.cargar_todos_clientes()
        self.statusBar().showMessage("Vista actualizada")

    def crear_boton_regreso(self):
        """Crea el botón de regreso al lobby"""
        btn_regresar = QPushButton("← Regresar al Menú")
        btn_regresar.setStyleSheet("""
            QPushButton {
                background-color: #6C757D;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5A6268;
            }
        """)
        btn_regresar.clicked.connect(self.regresar_al_lobby)
        self.statusBar().addPermanentWidget(btn_regresar)

    def regresar_al_lobby(self):
        """Regresa a la ventana del lobby"""
        if self.lobby_window:
            self.lobby_window.show()
            self.lobby_window.raise_()
            self.lobby_window.activateWindow()
        self.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = CrudClientesWindow()
    window.show()
    sys.exit(app.exec_())