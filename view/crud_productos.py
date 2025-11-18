"""
Ventana CRUD para Gestión de Productos
Por: Juan David Ramirez Carmona y Miguel Ángel Vargas Peláez
Fecha: 2025-11
Licencia: GPLv3
"""

import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
from PyQt5.QtCore import Qt
from decimal import Decimal
from model.producto import Producto, ProductoData
from model.categoria import Categoria, CategoriaData
from model.usuario import Usuario  # ← CAMBIADO: Cliente por Usuario
from util import sesion


class CRUDProductosWindow(QtWidgets.QMainWindow):
    """
    Ventana CRUD completa para gestionar productos
    """

    def __init__(self):
        super().__init__()

        # Cargar el archivo .ui
        try:
            uic.loadUi('crud_productos.ui', self)
        except FileNotFoundError:
            print("Error: Asegúrate de que 'crud_productos.ui' esté en el mismo directorio.")
            sys.exit(1)

        # Instanciar controladores
        try:
            self.producto_controller = Producto()
            self.categoria_controller = Categoria()
            self.usuario_controller = Usuario()
        except Exception as e:
            QMessageBox.critical(self, "Error de Base de Datos",
                                 f"No se pudo conectar a la base de datos.\nError: {e}")
            sys.exit(1)

        # Variables de estado
        self.modo_actual = "visualizacion"
        self.producto_seleccionado = None
        self.categorias = []  # Lista de categorías disponibles
        self.es_solo_lectura = False  # ← AÑADIR: Control de permisos

        # Conectar señales
        self.conectar_senales()

        # Configurar tabla
        self.configurar_tabla()

        # Verificar permisos del usuario
        self.verificar_permisos()

        # Cargar categorías
        self.cargar_categorias()

        # Cargar datos iniciales
        self.cargar_todos_productos()

        # Inicializar estado
        self.limpiar_formulario()
        self.cambiar_modo("visualizacion")
        self.statusBar().showMessage("Listo. Seleccione un producto o cree uno nuevo.")

    def conectar_senales(self):
        """Conecta todos los eventos de la interfaz"""
        # Botones de búsqueda y lista
        self.pushButton_buscar.clicked.connect(self.buscar_productos)
        self.pushButton_refrescar.clicked.connect(self.cargar_todos_productos)
        self.pushButton_nuevo.clicked.connect(self.modo_nuevo_producto)
        self.lineEdit_buscar.returnPressed.connect(self.buscar_productos)

        # Filtros
        self.pushButton_aplicar_filtros.clicked.connect(self.aplicar_filtros)
        self.pushButton_limpiar_filtros.clicked.connect(self.limpiar_filtros)
        self.comboBox_filtro_categoria.currentIndexChanged.connect(self.aplicar_filtros)

        # Botones de acción
        self.pushButton_guardar.clicked.connect(self.guardar_producto)
        self.pushButton_editar.clicked.connect(self.modo_edicion)
        self.pushButton_eliminar.clicked.connect(self.eliminar_producto)
        self.pushButton_cancelar.clicked.connect(self.cancelar_operacion)

        # Cálculo de precio
        self.pushButton_calcular_venta.clicked.connect(self.calcular_precio_venta)
        self.lineEdit_valor_adquisicion.textChanged.connect(self.actualizar_resumen)
        self.lineEdit_valor_venta.textChanged.connect(self.actualizar_resumen)
        self.comboBox_categoria.currentIndexChanged.connect(self.actualizar_resumen)

        # Tabla
        self.tableWidget_productos.itemSelectionChanged.connect(self.producto_seleccionado_cambio)

    def configurar_tabla(self):
        """Configura las propiedades de la tabla"""
        self.tableWidget_productos.setColumnWidth(0, 80)   # Código
        self.tableWidget_productos.setColumnWidth(1, 200)  # Nombre
        self.tableWidget_productos.setColumnWidth(2, 130)  # Valor Adquisición
        self.tableWidget_productos.setColumnWidth(3, 130)  # Valor Venta
        self.tableWidget_productos.setColumnWidth(4, 100)  # Ganancia
        self.tableWidget_productos.setColumnWidth(5, 80)   # Cantidad ← AÑADIDO
        self.tableWidget_productos.setColumnWidth(6, 100)  # Categoría

        self.tableWidget_productos.setSortingEnabled(True)

    def verificar_permisos(self):
        """
        Verifica los permisos del usuario logueado.
        Si el rol es 3 (Usuario Esporádico), solo permite lectura.
        """
        # Verificar si hay usuario logueado
        if not sesion.is_logged_in():
            QMessageBox.warning(
                self,
                "Sesión Requerida",
                "Debe iniciar sesión para acceder a esta sección."
            )
            self.close()
            return

        # Obtener ID del usuario
        usuario_id = sesion.get_usuario_id()

        try:
            # Obtener datos del usuario ← CAMBIADO: Cliente por Usuario
            usuario = self.usuario_controller.obtener_por_id(usuario_id)

            if not usuario:
                QMessageBox.warning(self, "Error", "Usuario no encontrado en el sistema.")
                self.close()
                return

            # Convertir tupla a objeto si es necesario
            if isinstance(usuario, tuple):
                # Asumiendo el orden: id_usuario, nombre_usuario, email, contrasena, id_rol
                id_rol = usuario[4] if len(usuario) > 4 else None
            else:
                id_rol = usuario.id_rol

            # Verificar el rol
            if id_rol == 3:
                # Usuario Esporádico - SOLO LECTURA
                self.es_solo_lectura = True
                self.aplicar_modo_solo_lectura()
                self.statusBar().showMessage(
                    "⚠️ Modo Solo Lectura: Usuario Esporádico no puede editar productos"
                )
            else:
                # Roles 1 (Admin) o 2 (Paramétrico) - PERMISOS COMPLETOS
                self.es_solo_lectura = False
                self.statusBar().showMessage("✅ Permisos completos habilitados")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al verificar permisos:\n{e}")
            print(f"Error en verificar_permisos: {e}")

    def aplicar_modo_solo_lectura(self):
        """
        Deshabilita botones de edición para usuarios con solo lectura
        """
        self.pushButton_nuevo.setEnabled(False)
        self.pushButton_editar.setEnabled(False)
        self.pushButton_eliminar.setEnabled(False)
        self.pushButton_guardar.setEnabled(False)

        # Cambiar el título para indicar modo solo lectura
        self.setWindowTitle("Gestión de Productos - 👁️ SOLO LECTURA")

        # Agregar mensaje visual
        self.label_modo.setText(
            '<html><body><p align="center">'
            '<span style="font-weight:600; color:#FF0000;">⚠️ Modo: Solo Lectura</span>'
            '</p></body></html>'
        )

    def cargar_categorias(self):
        """Carga las categorías desde la base de datos"""
        try:
            self.categorias = self.categoria_controller.obtener_todos_como_objetos()

            # Limpiar ComboBoxes
            self.comboBox_categoria.clear()
            self.comboBox_filtro_categoria.clear()

            # Agregar opción por defecto
            self.comboBox_categoria.addItem("-- Seleccione una categoría --", None)
            self.comboBox_filtro_categoria.addItem("-- Todas las categorías --", None)

            # Agregar categorías - SOLO MOSTRAR NOMBRE
            for cat in self.categorias:
                print(cat.nombre)
                # En el comboBox principal: mostrar solo el nombre
                self.comboBox_categoria.addItem(
                    cat.nombre,  # ← SOLO NOMBRE
                    cat.codigo_categoria
                )
                # En el filtro: mostrar solo el nombre también
                self.comboBox_filtro_categoria.addItem(
                    cat.nombre,  # ← SOLO NOMBRE
                    cat.codigo_categoria
                )

        except Exception as e:
            QMessageBox.warning(self, "Advertencia",
                              f"No se pudieron cargar las categorías:\n{e}\n\n"
                              "Asegúrese de tener categorías creadas en la base de datos.")

    def cargar_todos_productos(self):
        """Carga todos los productos en la tabla"""
        try:
            productos = self.producto_controller.obtener_todos_como_objetos()
            self.llenar_tabla(productos)
            self.statusBar().showMessage(f"Se cargaron {len(productos)} productos.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar productos:\n{e}")
            self.statusBar().showMessage("Error al cargar productos.")

    def buscar_productos(self):
        """Busca productos según el texto ingresado"""
        texto_busqueda = self.lineEdit_buscar.text().strip()

        if not texto_busqueda:
            self.cargar_todos_productos()
            return

        try:
            if texto_busqueda.isdigit():
                # Buscar por código
                producto = self.producto_controller.obtener_por_id(int(texto_busqueda))
                productos = [producto] if producto else []
                if productos and not isinstance(productos[0], ProductoData):
                    productos = [ProductoData(*productos[0])]
            else:
                # Buscar por nombre
                productos = self.producto_controller.buscar_por_nombre(texto_busqueda)

            self.llenar_tabla(productos)
            self.statusBar().showMessage(f"Se encontraron {len(productos)} productos.")

        except Exception as e:
            QMessageBox.warning(self, "Error de Búsqueda", f"Error al buscar:\n{e}")

    def aplicar_filtros(self):
        """Aplica los filtros de categoría y precio"""
        try:
            productos = self.producto_controller.obtener_todos_como_objetos()

            # Filtro por categoría
            categoria_id = self.comboBox_filtro_categoria.currentData()
            if categoria_id is not None:
                productos = [p for p in productos if p.codigo_categoria == categoria_id]

            # Filtro por rango de precio
            precio_min_text = self.lineEdit_precio_min.text().strip()
            precio_max_text = self.lineEdit_precio_max.text().strip()

            if precio_min_text or precio_max_text:
                precio_min = float(precio_min_text) if precio_min_text else 0
                precio_max = float(precio_max_text) if precio_max_text else float('inf')

                productos = [p for p in productos
                           if p.valor_venta and precio_min <= float(p.valor_venta) <= precio_max]

            self.llenar_tabla(productos)
            self.statusBar().showMessage(f"Filtros aplicados: {len(productos)} productos.")

        except ValueError:
            QMessageBox.warning(self, "Error", "Los valores de precio deben ser numéricos.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al aplicar filtros:\n{e}")

    def limpiar_filtros(self):
        """Limpia todos los filtros y recarga la tabla"""
        self.lineEdit_buscar.clear()
        self.lineEdit_precio_min.clear()
        self.lineEdit_precio_max.clear()
        self.comboBox_filtro_categoria.setCurrentIndex(0)
        self.cargar_todos_productos()

    def llenar_tabla(self, productos):
        """Llena la tabla con los productos proporcionados"""
        self.tableWidget_productos.setRowCount(0)

        for producto in productos:
            if isinstance(producto, tuple):
                producto = ProductoData(*producto)

            fila = self.tableWidget_productos.rowCount()
            self.tableWidget_productos.insertRow(fila)

            # Obtener categoría para calcular IVA
            categoria_producto = None
            for cat in self.categorias:
                if cat.codigo_categoria == producto.codigo_categoria:
                    categoria_producto = cat
                    break

            iva_decimal = float(categoria_producto.iva) if categoria_producto else 0

            # Calcular ganancia NETA (considerando IVA)
            ganancia_bruta = 0
            ganancia_neta = 0
            porcentaje_ganancia_bruta = 0
            porcentaje_ganancia_neta = 0

            if producto.valor_venta and producto.valor_adquisicion:
                # Ganancia bruta
                ganancia_bruta = float(producto.valor_venta) - float(producto.valor_adquisicion)

                # Calcular IVA a pagar
                base_imponible = float(producto.valor_venta) / (1 + iva_decimal) if iva_decimal > 0 else float(
                    producto.valor_venta)
                iva_a_pagar = base_imponible * iva_decimal

                # Ganancia neta (después de pagar IVA)
                ganancia_neta = ganancia_bruta - iva_a_pagar

                # Porcentajes
                if producto.valor_adquisicion > 0:
                    porcentaje_ganancia_bruta = (ganancia_bruta / float(producto.valor_adquisicion)) * 100
                    porcentaje_ganancia_neta = (ganancia_neta / float(producto.valor_adquisicion)) * 100

            # Obtener nombre de categoría
            nombre_categoria = str(producto.codigo_categoria)
            for cat in self.categorias:
                if cat.codigo_categoria == producto.codigo_categoria:
                    nombre_categoria = cat.nombre
                    break

            # Agregar datos - MOSTRAR GANANCIA NETA
            self.tableWidget_productos.setItem(fila, 0, QTableWidgetItem(str(producto.codigo)))
            self.tableWidget_productos.setItem(fila, 1, QTableWidgetItem(producto.nombre))
            self.tableWidget_productos.setItem(fila, 2,
                                               QTableWidgetItem(f"${producto.valor_adquisicion:,.2f}"))
            self.tableWidget_productos.setItem(fila, 3,
                                               QTableWidgetItem(
                                                   f"${producto.valor_venta:,.2f}" if producto.valor_venta else "N/A"))
            # MOSTRAR GANANCIA NETA EN LUGAR DE BRUTA
            self.tableWidget_productos.setItem(fila, 4,
                                               QTableWidgetItem(
                                                   f"${ganancia_neta:,.2f} ({porcentaje_ganancia_neta:.1f}%)"))
            # ← AÑADIR COLUMNA DE CANTIDAD
            self.tableWidget_productos.setItem(fila, 5,
                                               QTableWidgetItem(str(producto.cantidad)))
            self.tableWidget_productos.setItem(fila, 6,
                                               QTableWidgetItem(nombre_categoria))

            # Guardar objeto completo
            self.tableWidget_productos.item(fila, 0).setData(Qt.UserRole, producto)

        self.label_total.setText(f"Total: {len(productos)} productos")

    def producto_seleccionado_cambio(self):
        """Se ejecuta cuando se selecciona un producto en la tabla"""
        seleccion = self.tableWidget_productos.selectedItems()

        if not seleccion:
            return

        fila = self.tableWidget_productos.currentRow()
        item = self.tableWidget_productos.item(fila, 0)
        self.producto_seleccionado = item.data(Qt.UserRole)

        self.mostrar_detalles_producto(self.producto_seleccionado)
        self.cambiar_modo("visualizacion")

    def mostrar_detalles_producto(self, producto: ProductoData):
        """Muestra los detalles del producto en el formulario"""
        self.lineEdit_codigo.setText(str(producto.codigo))
        self.lineEdit_nombre.setText(producto.nombre)
        self.textEdit_descripcion.setPlainText(producto.descripcion or "")
        self.lineEdit_valor_adquisicion.setText(str(producto.valor_adquisicion))
        self.lineEdit_valor_venta.setText(str(producto.valor_venta) if producto.valor_venta else "")
        self.spinBox_cantidad.setValue(producto.cantidad)  # ← ESTO YA ESTÁ BIEN

        # Establecer categoría
        for i in range(self.comboBox_categoria.count()):
            if self.comboBox_categoria.itemData(i) == producto.codigo_categoria:
                self.comboBox_categoria.setCurrentIndex(i)
                break

        self.actualizar_resumen()

    def limpiar_formulario(self):
        """Limpia todos los campos del formulario"""
        self.lineEdit_codigo.clear()
        self.lineEdit_nombre.clear()
        self.textEdit_descripcion.clear()
        self.lineEdit_valor_adquisicion.clear()
        self.lineEdit_valor_venta.clear()
        self.spinBox_cantidad.setValue(0)  # ← ESTO YA ESTÁ BIEN
        self.comboBox_categoria.setCurrentIndex(0)
        self.producto_seleccionado = None
        self.actualizar_resumen()

    def cambiar_modo(self, modo):
        """Cambia el modo de operación de la ventana"""
        self.modo_actual = modo

        # Si el usuario tiene solo lectura, no permitir edición
        if self.es_solo_lectura and modo != "visualizacion":
            QMessageBox.warning(
                self,
                "Permiso Denegado",
                "Los usuarios esporádicos no tienen permisos para editar productos."
            )
            return

        if modo == "visualizacion":
            self.label_modo.setText('<html><body><p align="center"><span style="font-weight:600;">Modo: Visualización</span></p></body></html>')
            self.habilitar_formulario(False)
            self.pushButton_editar.setEnabled(not self.es_solo_lectura)  # ← VERIFICAR PERMISOS
            self.pushButton_eliminar.setEnabled(not self.es_solo_lectura)  # ← VERIFICAR PERMISOS
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
            self.label_modo.setText('<html><body><p align="center"><span style="font-weight:600; color:#28A745;">Modo: Nuevo Producto</span></p></body></html>')
            self.habilitar_formulario(True)
            self.pushButton_editar.setEnabled(False)
            self.pushButton_eliminar.setEnabled(False)
            self.pushButton_guardar.setEnabled(True)
            self.pushButton_cancelar.setEnabled(True)
            self.lineEdit_codigo.setEnabled(True)

    def habilitar_formulario(self, habilitar):
        """Habilita o deshabilita los campos del formulario"""
        self.lineEdit_nombre.setEnabled(habilitar)
        self.textEdit_descripcion.setEnabled(habilitar)
        self.lineEdit_valor_adquisicion.setEnabled(habilitar)
        self.lineEdit_valor_venta.setEnabled(habilitar)
        self.comboBox_categoria.setEnabled(habilitar)
        self.spinBox_cantidad.setEnabled(habilitar)  # ← AÑADIR
        self.pushButton_calcular_venta.setEnabled(habilitar)

    def modo_nuevo_producto(self):
        """Activa el modo para crear un nuevo producto"""
        self.limpiar_formulario()
        self.cambiar_modo("nuevo")
        self.lineEdit_codigo.setFocus()
        self.statusBar().showMessage("Ingrese los datos del nuevo producto.")

    def modo_edicion(self):
        """Activa el modo de edición"""
        if not self.producto_seleccionado:
            QMessageBox.warning(self, "Advertencia", "Debe seleccionar un producto primero.")
            return

        self.cambiar_modo("edicion")
        self.lineEdit_nombre.setFocus()
        self.statusBar().showMessage("Editando producto. Realice los cambios y guarde.")

    def get_categoria_seleccionada(self):
        """Obtiene la categoría completa seleccionada"""
        categoria_id = self.comboBox_categoria.currentData()
        if categoria_id is None:
            return None

        for cat in self.categorias:
            if cat.codigo_categoria == categoria_id:
                return cat
        return None

    def calcular_precio_venta(self):
        """Calcula el precio de venta basado en el valor de adquisición, IVA y utilidad"""
        try:
            # Validar valor de adquisición
            valor_adq_text = self.lineEdit_valor_adquisicion.text().strip()
            if not valor_adq_text:
                QMessageBox.warning(self, "Error", "Debe ingresar el valor de adquisición.")
                return

            valor_adquisicion = float(valor_adq_text)
            if valor_adquisicion <= 0:
                QMessageBox.warning(self, "Error", "El valor de adquisición debe ser mayor a 0.")
                return

            # Obtener categoría
            categoria = self.get_categoria_seleccionada()
            if not categoria:
                QMessageBox.warning(self, "Error", "Debe seleccionar una categoría.")
                return

            # CORRECCIÓN: Los valores vienen de la base de datos así:
            # IVA: 0.16, 0.19, 0.12 (decimales que representan 16%, 19%, 12%)
            # Utilidad: 35.00, 39.00, 40.00 (porcentajes que representan 35%, 39%, 40%)

            iva_decimal = float(categoria.iva)  # Ej: 0.16 (16%)
            utilidad_porcentaje = float(categoria.utilidad)  # Ej: 35.00 (35%)

            # Convertir utilidad de porcentaje a valor monetario
            utilidad_monetaria = valor_adquisicion * (utilidad_porcentaje / 100)

            # Fórmula corregida: Precio Venta = (Valor Adq + Utilidad) * (1 + IVA)
            precio_con_utilidad = valor_adquisicion + utilidad_monetaria
            precio_venta = precio_con_utilidad * (1 + iva_decimal)

            # Establecer el precio calculado
            self.lineEdit_valor_venta.setText(f"{precio_venta:.2f}")

            self.statusBar().showMessage(
                f"Precio calculado: ${precio_venta:,.2f} "
                f"(IVA: {iva_decimal * 100}%, Utilidad: {utilidad_porcentaje}%)"
            )

        except ValueError:
            QMessageBox.warning(self, "Error", "Los valores deben ser numéricos válidos.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al calcular precio:\n{e}")

    def actualizar_resumen(self):
        """Actualiza el panel de resumen financiero"""
        try:
            valor_adq = 0
            valor_venta = 0

            if self.lineEdit_valor_adquisicion.text().strip():
                valor_adq = float(self.lineEdit_valor_adquisicion.text())

            if self.lineEdit_valor_venta.text().strip():
                valor_venta = float(self.lineEdit_valor_venta.text())

            # Obtener categoría para el cálculo del IVA
            categoria = self.get_categoria_seleccionada()
            iva_decimal = 0
            if categoria:
                iva_decimal = float(categoria.iva)

            # CALCULAR GANANCIA REAL (considerando que el IVA se paga al estado)
            # Ganancia bruta = Precio de venta - Costo de adquisición
            ganancia_bruta = valor_venta - valor_adq

            # IVA a pagar = (Precio de venta / (1 + IVA)) * IVA
            # Esto representa el monto de IVA que debemos pagar al estado
            base_imponible = valor_venta / (1 + iva_decimal) if iva_decimal > 0 else valor_venta
            iva_a_pagar = base_imponible * iva_decimal

            # Ganancia neta = Ganancia bruta - IVA a pagar
            ganancia_neta = ganancia_bruta - iva_a_pagar

            # Porcentajes
            porcentaje_bruto = (ganancia_bruta / valor_adq * 100) if valor_adq > 0 else 0
            porcentaje_neto = (ganancia_neta / valor_adq * 100) if valor_adq > 0 else 0

            # Calcular IVA incluido en el precio
            iva_monto = valor_venta * (iva_decimal / (1 + iva_decimal)) if iva_decimal > 0 else 0

            # Actualizar labels - MOSTRAR GANANCIA NETA (la real)
            self.label_resumen_adquisicion.setText(f"📥 Costo de Adquisición: ${valor_adq:,.2f}")
            self.label_resumen_venta.setText(f"💰 Precio de Venta: ${valor_venta:,.2f}")
            self.label_resumen_ganancia.setText(
                f"📈 Ganancia Neta: ${ganancia_neta:,.2f} ({porcentaje_neto:.2f}%)"
            )
            self.label_resumen_iva.setText(f"🧾 IVA a Pagar: ${iva_a_pagar:,.2f}")

        except ValueError:
            pass

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

        if not self.lineEdit_valor_adquisicion.text().strip():
            QMessageBox.warning(self, "Validación", "El valor de adquisición es obligatorio.")
            self.lineEdit_valor_adquisicion.setFocus()
            return False

        if self.comboBox_categoria.currentData() is None:
            QMessageBox.warning(self, "Validación", "Debe seleccionar una categoría.")
            self.comboBox_categoria.setFocus()
            return False

        return True

    def guardar_producto(self):
        """Guarda el producto (nuevo o editado)"""
        if not self.validar_formulario():
            return

        try:
            codigo = int(self.lineEdit_codigo.text().strip())
            nombre = self.lineEdit_nombre.text().strip()
            descripcion = self.textEdit_descripcion.toPlainText().strip() or None
            valor_adquisicion = float(self.lineEdit_valor_adquisicion.text().strip())
            valor_venta_text = self.lineEdit_valor_venta.text().strip()
            valor_venta = float(valor_venta_text) if valor_venta_text else None
            codigo_categoria = self.comboBox_categoria.currentData()
            cantidad = self.spinBox_cantidad.value()  # ← AÑADIR ESTA LÍNEA

            if self.modo_actual == "nuevo":
                exito = self.producto_controller.crear(
                    codigo=codigo,
                    nombre=nombre,
                    descripcion=descripcion,
                    valor_adquisicion=valor_adquisicion,
                    valor_venta=valor_venta,
                    codigo_categoria=codigo_categoria,
                    cantidad=cantidad  # ← AÑADIR ESTE PARÁMETRO
                )

                if exito:
                    QMessageBox.information(self, "Éxito", "Producto creado exitosamente.")
                    self.cargar_todos_productos()
                    self.limpiar_formulario()
                    self.cambiar_modo("visualizacion")
                    self.statusBar().showMessage("Producto creado exitosamente.")
                else:
                    QMessageBox.warning(self, "Error", "No se pudo crear el producto.")

            elif self.modo_actual == "edicion":
                exito = self.producto_controller.actualizar(
                    codigo=codigo,
                    nombre=nombre,
                    descripcion=descripcion,
                    valor_adquisicion=valor_adquisicion,
                    valor_venta=valor_venta,
                    codigo_categoria=codigo_categoria,
                    cantidad=cantidad  # ← AÑADIR ESTE PARÁMETRO
                )

                if exito:
                    QMessageBox.information(self, "Éxito", "Producto actualizado exitosamente.")
                    self.cargar_todos_productos()
                    self.cambiar_modo("visualizacion")
                    self.statusBar().showMessage("Producto actualizado exitosamente.")
                else:
                    QMessageBox.warning(self, "Error", "No se pudo actualizar el producto.")

        except ValueError:
            QMessageBox.warning(self, "Error", "El código y los valores deben ser numéricos válidos.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar:\n{e}")

    def eliminar_producto(self):
        """Elimina el producto seleccionado"""
        if not self.producto_seleccionado:
            QMessageBox.warning(self, "Advertencia", "Debe seleccionar un producto primero.")
            return

        respuesta = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            f"¿Está seguro de eliminar el producto '{self.producto_seleccionado.nombre}'?\n\n"
            "Esta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if respuesta == QMessageBox.Yes:
            try:
                exito = self.producto_controller.eliminar(self.producto_seleccionado.codigo)

                if exito:
                    QMessageBox.information(self, "Éxito", "Producto eliminado exitosamente.")
                    self.cargar_todos_productos()
                    self.limpiar_formulario()
                    self.cambiar_modo("visualizacion")
                    self.statusBar().showMessage("Producto eliminado exitosamente.")
                else:
                    QMessageBox.warning(self, "Error", "No se pudo eliminar el producto.")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al eliminar:\n{e}")

    def cancelar_operacion(self):
        """Cancela la operación actual"""
        if self.modo_actual == "nuevo":
            self.limpiar_formulario()
            self.cambiar_modo("visualizacion")
        elif self.modo_actual == "edicion":
            if self.producto_seleccionado:
                self.mostrar_detalles_producto(self.producto_seleccionado)
            self.cambiar_modo("visualizacion")

        self.statusBar().showMessage("Operación cancelada.")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = CRUDProductosWindow()
    window.show()
    sys.exit(app.exec_())