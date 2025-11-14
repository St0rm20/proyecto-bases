"""
Ventana CRUD para Gestión de Clientes
Por: Juan David Ramirez Carmona y Miguel Ángel Vargas Peláez
Fecha: 2025-11
Licencia: GPLv3
"""

import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
from PyQt5.QtCore import Qt
from model.cliente import Cliente, ClienteData


class CRUDClientesWindow(QtWidgets.QMainWindow):
    """
    Ventana CRUD completa para gestionar clientes
    """

    def __init__(self):
        super().__init__()

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
        self.modo_actual = "visualizacion"  # visualizacion, edicion, nuevo
        self.cliente_seleccionado = None

        # Conectar señales
        self.conectar_senales()

        # Configurar tabla
        self.configurar_tabla()

        # Cargar datos iniciales
        self.cargar_todos_clientes()

        # Inicializar estado
        self.limpiar_formulario()
        self.statusBar().showMessage("Listo. Seleccione un cliente o cree uno nuevo.")

    def conectar_senales(self):
        """Conecta todos los eventos de la interfaz"""
        # Botones de búsqueda y lista
        self.pushButton_buscar.clicked.connect(self.buscar_clientes)
        self.pushButton_refrescar.clicked.connect(self.cargar_todos_clientes)
        self.pushButton_nuevo.clicked.connect(self.modo_nuevo_cliente)
        self.lineEdit_buscar.returnPressed.connect(self.buscar_clientes)

        # Botones de acción
        self.pushButton_guardar.clicked.connect(self.guardar_cliente)
        self.pushButton_editar.clicked.connect(self.modo_edicion)
        self.pushButton_eliminar.clicked.connect(self.eliminar_cliente)
        self.pushButton_cancelar.clicked.connect(self.cancelar_operacion)

        # Tabla
        self.tableWidget_clientes.itemSelectionChanged.connect(self.cliente_seleccionado_cambio)

        # Checkbox de contraseña
        self.checkBox_cambiar_contrasena.stateChanged.connect(self.toggle_cambiar_contrasena)

    def configurar_tabla(self):
        """Configura las propiedades de la tabla"""
        self.tableWidget_clientes.setColumnWidth(0, 100)  # Código
        self.tableWidget_clientes.setColumnWidth(1, 200)  # Nombre
        self.tableWidget_clientes.setColumnWidth(2, 180)  # Email
        self.tableWidget_clientes.setColumnWidth(3, 120)  # Teléfono
        self.tableWidget_clientes.setColumnWidth(4, 150)  # Municipio

        # Ordenar por código al hacer clic en el header
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
            # Intentar buscar por código (si es número)
            if texto_busqueda.isdigit():
                cliente = self.cliente_controller.obtener_por_id(int(texto_busqueda))
                clientes = [cliente] if cliente else []
                # Convertir tupla a ClienteData si es necesario
                if clientes and not isinstance(clientes[0], ClienteData):
                    clientes = [ClienteData(*clientes[0])]
            else:
                # Buscar por nombre
                clientes = self.cliente_controller.buscar_por_nombre(texto_busqueda)

            self.llenar_tabla(clientes)
            self.statusBar().showMessage(f"Se encontraron {len(clientes)} clientes.")

        except Exception as e:
            QMessageBox.warning(self, "Error de Búsqueda", f"Error al buscar:\n{e}")
            self.statusBar().showMessage("Error en la búsqueda.")

    def llenar_tabla(self, clientes):
        """Llena la tabla con los clientes proporcionados"""
        self.tableWidget_clientes.setRowCount(0)  # Limpiar tabla

        for cliente in clientes:
            # Si es tupla, convertir a ClienteData
            if isinstance(cliente, tuple):
                cliente = ClienteData(*cliente)

            fila = self.tableWidget_clientes.rowCount()
            self.tableWidget_clientes.insertRow(fila)

            # Agregar datos a las columnas
            self.tableWidget_clientes.setItem(fila, 0, QTableWidgetItem(str(cliente.codigo_cliente)))
            self.tableWidget_clientes.setItem(fila, 1, QTableWidgetItem(cliente.nombre))
            self.tableWidget_clientes.setItem(fila, 2, QTableWidgetItem(cliente.email or ""))
            self.tableWidget_clientes.setItem(fila, 3, QTableWidgetItem(cliente.telefono or ""))
            self.tableWidget_clientes.setItem(fila, 4, QTableWidgetItem(cliente.municipio or ""))

            # Guardar el objeto completo en la primera celda
            self.tableWidget_clientes.item(fila, 0).setData(Qt.UserRole, cliente)

        # Actualizar contador
        self.label_total.setText(f"Total: {len(clientes)} clientes")

    def cliente_seleccionado_cambio(self):
        """Se ejecuta cuando se selecciona un cliente en la tabla"""
        seleccion = self.tableWidget_clientes.selectedItems()

        if not seleccion:
            return

        # Obtener el cliente de la primera celda de la fila seleccionada
        fila = self.tableWidget_clientes.currentRow()
        item = self.tableWidget_clientes.item(fila, 0)
        self.cliente_seleccionado = item.data(Qt.UserRole)

        # Mostrar detalles
        self.mostrar_detalles_cliente(self.cliente_seleccionado)
        self.cambiar_modo("visualizacion")

    def mostrar_detalles_cliente(self, cliente: ClienteData):
        """Muestra los detalles del cliente en el formulario"""
        self.lineEdit_codigo.setText(str(cliente.codigo_cliente))
        self.lineEdit_nombre.setText(cliente.nombre)
        self.lineEdit_email.setText(cliente.email or "")
        self.lineEdit_telefono.setText(cliente.telefono or "")
        self.lineEdit_departamento.setText(cliente.departamento or "")
        self.lineEdit_municipio.setText(cliente.municipio or "")
        self.lineEdit_calle.setText(cliente.calle or "")
        self.lineEdit_direccion.setText(cliente.direccion or "")

        # Establecer rol
        if cliente.id_rol == 2:
            self.comboBox_rol.setCurrentIndex(1)  # Usuario Paramétrico
        elif cliente.id_rol == 3:
            self.comboBox_rol.setCurrentIndex(2)  # Usuario Esporádico
        else:
            self.comboBox_rol.setCurrentIndex(0)  # Sin asignar

        # Limpiar campos de contraseña
        self.checkBox_cambiar_contrasena.setChecked(False)
        self.lineEdit_nueva_contrasena.clear()
        self.lineEdit_confirmar_contrasena.clear()

    def limpiar_formulario(self):
        """Limpia todos los campos del formulario"""
        self.lineEdit_codigo.clear()
        self.lineEdit_nombre.clear()
        self.lineEdit_email.clear()
        self.lineEdit_telefono.clear()
        self.lineEdit_departamento.clear()
        self.lineEdit_municipio.clear()
        self.lineEdit_calle.clear()
        self.lineEdit_direccion.clear()
        self.comboBox_rol.setCurrentIndex(0)
        self.checkBox_cambiar_contrasena.setChecked(False)
        self.lineEdit_nueva_contrasena.clear()
        self.lineEdit_confirmar_contrasena.clear()
        self.cliente_seleccionado = None

    def cambiar_modo(self, modo):
        """Cambia el modo de operación de la ventana"""
        self.modo_actual = modo

        if modo == "visualizacion":
            self.label_modo.setText(
                '<html><body><p align="center"><span style="font-weight:600;">Modo: Visualización</span></p></body></html>')
            self.habilitar_formulario(False)
            self.pushButton_editar.setEnabled(True)
            self.pushButton_eliminar.setEnabled(True)
            self.pushButton_guardar.setEnabled(False)
            self.pushButton_cancelar.setEnabled(False)
            self.lineEdit_codigo.setEnabled(False)

        elif modo == "edicion":
            self.label_modo.setText(
                '<html><body><p align="center"><span style="font-weight:600; color:#FF8C00;">Modo: Editando</span></p></body></html>')
            self.habilitar_formulario(True)
            self.pushButton_editar.setEnabled(False)
            self.pushButton_eliminar.setEnabled(False)
            self.pushButton_guardar.setEnabled(True)
            self.pushButton_cancelar.setEnabled(True)
            self.lineEdit_codigo.setEnabled(False)  # No se puede cambiar el código

        elif modo == "nuevo":
            self.label_modo.setText(
                '<html><body><p align="center"><span style="font-weight:600; color:#28A745;">Modo: Nuevo Cliente</span></p></body></html>')
            self.habilitar_formulario(True)
            self.pushButton_editar.setEnabled(False)
            self.pushButton_eliminar.setEnabled(False)
            self.pushButton_guardar.setEnabled(True)
            self.pushButton_cancelar.setEnabled(True)
            self.lineEdit_codigo.setEnabled(True)
            self.checkBox_cambiar_contrasena.setChecked(True)  # Nueva contraseña es obligatoria

    def habilitar_formulario(self, habilitar):
        """Habilita o deshabilita los campos del formulario"""
        self.lineEdit_nombre.setEnabled(habilitar)
        self.lineEdit_email.setEnabled(habilitar)
        self.lineEdit_telefono.setEnabled(habilitar)
        self.lineEdit_departamento.setEnabled(habilitar)
        self.lineEdit_municipio.setEnabled(habilitar)
        self.lineEdit_calle.setEnabled(habilitar)
        self.lineEdit_direccion.setEnabled(habilitar)
        self.comboBox_rol.setEnabled(habilitar)
        self.checkBox_cambiar_contrasena.setEnabled(habilitar)

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

    def toggle_cambiar_contrasena(self, state):
        """Habilita/deshabilita los campos de contraseña"""
        self.widget_password.setEnabled(state == Qt.Checked)
        if state != Qt.Checked:
            self.lineEdit_nueva_contrasena.clear()
            self.lineEdit_confirmar_contrasena.clear()

    def get_rol_id(self):
        """Obtiene el ID del rol seleccionado"""
        rol_texto = self.comboBox_rol.currentText()
        if rol_texto == "Usuario Paramétrico":
            return 2
        elif rol_texto == "Usuario Esporádico":
            return 3
        return None

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

        if not self.lineEdit_email.text().strip():
            QMessageBox.warning(self, "Validación", "El email es obligatorio.")
            self.lineEdit_email.setFocus()
            return False

        # Validar contraseña si está marcado el checkbox
        if self.checkBox_cambiar_contrasena.isChecked():
            pwd = self.lineEdit_nueva_contrasena.text()
            pwd_conf = self.lineEdit_confirmar_contrasena.text()

            if not pwd or not pwd_conf:
                QMessageBox.warning(self, "Validación", "Debe ingresar y confirmar la contraseña.")
                return False

            if len(pwd) < 6:
                QMessageBox.warning(self, "Validación", "La contraseña debe tener al menos 6 caracteres.")
                return False

            if pwd != pwd_conf:
                QMessageBox.warning(self, "Validación", "Las contraseñas no coinciden.")
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
        email = self.lineEdit_email.text().strip()
        telefono = self.lineEdit_telefono.text().strip() or None
        departamento = self.lineEdit_departamento.text().strip() or None
        municipio = self.lineEdit_municipio.text().strip() or None
        calle = self.lineEdit_calle.text().strip() or None
        direccion = self.lineEdit_direccion.text().strip() or None
        id_rol = self.get_rol_id()

        contrasena = None
        if self.checkBox_cambiar_contrasena.isChecked():
            contrasena = self.lineEdit_nueva_contrasena.text()

        try:
            if self.modo_actual == "nuevo":
                # Crear nuevo cliente
                if not contrasena:
                    QMessageBox.warning(self, "Error", "Debe establecer una contraseña para el nuevo cliente.")
                    return

                exito = self.cliente_controller.crear(
                    codigo_cliente=codigo,
                    nombre=nombre,
                    email=email,
                    telefono=telefono,
                    departamento=departamento,
                    municipio=municipio,
                    calle=calle,
                    direccion=direccion,
                    contrasena=contrasena,
                    id_rol=id_rol
                )

                if exito:
                    QMessageBox.information(self, "Éxito", "Cliente creado exitosamente.")
                    self.cargar_todos_clientes()
                    self.limpiar_formulario()
                    self.cambiar_modo("visualizacion")
                    self.statusBar().showMessage("Cliente creado exitosamente.")
                else:
                    QMessageBox.warning(self, "Error",
                                        "No se pudo crear el cliente. Verifique que el código no esté duplicado.")

            elif self.modo_actual == "edicion":
                # Actualizar cliente existente
                exito = self.cliente_controller.actualizar(
                    codigo_cliente=codigo,
                    nombre=nombre,
                    email=email,
                    telefono=telefono,
                    departamento=departamento,
                    municipio=municipio,
                    calle=calle,
                    direccion=direccion,
                    contrasena=contrasena,
                    id_rol=id_rol
                )

                if exito:
                    QMessageBox.information(self, "Éxito", "Cliente actualizado exitosamente.")
                    self.cargar_todos_clientes()
                    self.cambiar_modo("visualizacion")
                    self.statusBar().showMessage("Cliente actualizado exitosamente.")
                else:
                    QMessageBox.warning(self, "Error", "No se pudo actualizar el cliente.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar:\n{e}")
            self.statusBar().showMessage("Error al guardar cliente.")

    def eliminar_cliente(self):
        """Elimina el cliente seleccionado"""
        if not self.cliente_seleccionado:
            QMessageBox.warning(self, "Advertencia", "Debe seleccionar un cliente primero.")
            return

        # Confirmar eliminación
        respuesta = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            f"¿Está seguro de eliminar al cliente '{self.cliente_seleccionado.nombre}'?\n\n"
            "Esta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if respuesta == QMessageBox.Yes:
            try:
                exito = self.cliente_controller.eliminar(self.cliente_seleccionado.codigo_cliente)

                if exito:
                    QMessageBox.information(self, "Éxito", "Cliente eliminado exitosamente.")
                    self.cargar_todos_clientes()
                    self.limpiar_formulario()
                    self.cambiar_modo("visualizacion")
                    self.statusBar().showMessage("Cliente eliminado exitosamente.")
                else:
                    QMessageBox.warning(self, "Error", "No se pudo eliminar el cliente.")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al eliminar:\n{e}")
                self.statusBar().showMessage("Error al eliminar cliente.")

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


# Para pruebas independientes
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = CRUDClientesWindow()
    window.show()
    sys.exit(app.exec_())