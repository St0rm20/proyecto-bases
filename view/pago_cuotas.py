"""
Ventana para gestión de pago de cuotas de créditos
Por: Juan David Ramirez Carmona y Miguel Ángel Vargas Peláez
Fecha: 2025-11
Licencia: GPLv3
"""

import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox, QPushButton
from datetime import date, datetime
from typing import Union
from model.credito import Credito
from model.cuota import Cuota
from model.pago import Pago
from model.venta import Venta
from util import sesion


def convertir_a_date(fecha_obj: Union[date, str, None]) -> date:
    """
    Convierte una fecha string o date a objeto date de Python
    Maneja diferentes formatos de Oracle
    """
    if fecha_obj is None:
        return date.today()

    if isinstance(fecha_obj, date):
        return fecha_obj

    if isinstance(fecha_obj, str):
        # Intentar diferentes formatos
        formatos = [
            '%Y-%m-%d',           # 2025-01-15
            '%d/%m/%Y',           # 15/01/2025
            '%Y-%m-%d %H:%M:%S',  # 2025-01-15 00:00:00
            '%d-%m-%Y',           # 15-01-2025
        ]

        for fmt in formatos:
            try:
                return datetime.strptime(fecha_obj, fmt).date()
            except ValueError:
                continue

        # Si ningún formato funciona, intentar parse automático
        try:
            from dateutil import parser
            return parser.parse(fecha_obj).date()
        except:
            print(f"⚠️ No se pudo convertir fecha: {fecha_obj}")
            return date.today()

    return date.today()


class PagoCuotasWindow(QtWidgets.QMainWindow):
    """
    Ventana para realizar pagos de cuotas de créditos activos
    """

    def __init__(self, parent=None):  # ✅ 1. Cambiar firma del __init__
        super().__init__(parent)

        # ✅ 2. Agregar después de super().__init__()
        self.lobby_window = parent

        # Cargar el archivo .ui
        try:
            uic.loadUi('pago_cuotas.ui', self)
        except FileNotFoundError:
            print("Error: Asegúrate de que 'pago_cuotas.ui' esté en el mismo directorio.")
            sys.exit(1)

        # Instanciar controladores
        try:
            self.credito_controller = Credito()
            self.cuota_controller = Cuota()
            self.pago_controller = Pago()
            self.venta_controller = Venta()
        except Exception as e:
            QMessageBox.critical(self, "Error de Base de Datos",
                                 f"No se pudo conectar a la base de datos.\nError: {e}")
            sys.exit(1)

        # Variables de estado
        self.credito_seleccionado = None
        self.cuota_actual = None
        self.info_credito = None

        # Conectar señales
        self.conectar_senales()

        # Verificar sesión
        self.verificar_sesion()

        # Cargar créditos activos
        self.cargar_creditos_activos()

        # Inicializar interfaz
        self.limpiar_interfaz()
        self.statusBar().showMessage("Seleccione un crédito para gestionar pagos.")

        # ✅ 3. Agregar botón de regreso
        self.crear_boton_regreso()

    def conectar_senales(self):
        """Conecta todos los eventos de la interfaz"""
        self.comboBox_creditos.currentIndexChanged.connect(self.credito_seleccionado_cambio)
        self.pushButton_cargar.clicked.connect(self.actualizar_vista)  # ✅ 4. Cambiar a actualizar_vista
        self.pushButton_realizar_pago.clicked.connect(self.realizar_pago)

    def verificar_sesion(self):
        """Verifica que haya un usuario logueado"""
        if not sesion.is_logged_in():
            QMessageBox.warning(
                self,
                "Sesión Requerida",
                "Debe iniciar sesión para acceder a esta sección."
            )
            self.close()
            return

    def cargar_creditos_activos(self):
        """Carga los créditos activos en el ComboBox"""
        try:
            creditos_activos = self.credito_controller.obtener_creditos_activos()

            self.comboBox_creditos.clear()
            self.comboBox_creditos.addItem("-- Seleccione un crédito --", None)

            if not creditos_activos:
                self.statusBar().showMessage("⚠️ No hay créditos activos en el sistema.")
                return

            for credito in creditos_activos:
                # Obtener info básica para mostrar en el combo
                info = self.credito_controller.obtener_info_credito_completa(credito.id_credito)
                if info:
                    texto_combo = (f"Crédito #{credito.id_credito} - {info['nombre_cliente']} "
                                   f"(Venta: {info['codigo_venta']}) - Saldo: ${info['saldo_pendiente']:,.2f}")
                    self.comboBox_creditos.addItem(texto_combo, credito.id_credito)

            self.statusBar().showMessage(f"✅ Se cargaron {len(creditos_activos)} créditos activos.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar créditos:\n{e}")
            self.statusBar().showMessage("❌ Error al cargar créditos.")

    def credito_seleccionado_cambio(self):
        """Se ejecuta cuando se selecciona un crédito del ComboBox"""
        id_credito = self.comboBox_creditos.currentData()

        if id_credito is None:
            self.limpiar_interfaz()
            return

        try:
            # Obtener información completa del crédito
            self.info_credito = self.credito_controller.obtener_info_credito_completa(id_credito)

            if not self.info_credito:
                QMessageBox.warning(self, "Error", "No se pudo obtener información del crédito.")
                return

            # ⚠️ VERIFICAR SI EL CRÉDITO NO TIENE CUOTAS GENERADAS
            if self.info_credito['total_cuotas'] == 0:
                respuesta = QMessageBox.question(
                    self,
                    "⚠️ Cuotas No Generadas",
                    f"Este crédito no tiene cuotas generadas.\n\n"
                    f"Plazo: {self.info_credito['plazo_meses']} meses\n"
                    f"Saldo a financiar: ${self.info_credito['saldo_financiado']:,.2f}\n\n"
                    f"¿Desea generar las cuotas automáticamente?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )

                if respuesta == QMessageBox.Yes:
                    # Generar las cuotas
                    exito = self.credito_controller.generar_cuotas(id_credito)

                    if exito:
                        QMessageBox.information(
                            self,
                            "✅ Cuotas Generadas",
                            f"Se generaron exitosamente {self.info_credito['plazo_meses']} cuotas."
                        )
                        # Recargar la información
                        self.info_credito = self.credito_controller.obtener_info_credito_completa(id_credito)
                    else:
                        QMessageBox.critical(
                            self,
                            "❌ Error",
                            "No se pudieron generar las cuotas. Verifique la configuración del crédito."
                        )
                        self.limpiar_interfaz()
                        return
                else:
                    self.limpiar_interfaz()
                    self.statusBar().showMessage("⚠️ Crédito sin cuotas. Debe generar las cuotas primero.")
                    return

            # Obtener la siguiente cuota pendiente
            self.cuota_actual = self.credito_controller.obtener_siguiente_cuota_pendiente(id_credito)

            # Mostrar información
            self.mostrar_informacion_credito()

            # Habilitar/deshabilitar botón de pago según si hay cuotas pendientes
            if self.cuota_actual:
                self.pushButton_realizar_pago.setEnabled(True)
                self.statusBar().showMessage(
                    f"✅ Crédito cargado. Cuota {self.cuota_actual.n_cuota} pendiente de pago."
                )
            else:
                self.pushButton_realizar_pago.setEnabled(False)
                self.statusBar().showMessage("✅ ¡Crédito completamente pagado!")
                QMessageBox.information(
                    self,
                    "Crédito Pagado",
                    "Este crédito ya ha sido pagado en su totalidad."
                )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar información del crédito:\n{e}")
            print(f"Error en credito_seleccionado_cambio: {e}")
            import traceback
            traceback.print_exc()

    def mostrar_informacion_credito(self):
        """Muestra toda la información del crédito en la interfaz"""
        if not self.info_credito:
            return

        info = self.info_credito

        # Datos del Cliente
        self.label_nombre_cliente.setText(info['nombre_cliente'])
        self.label_telefono.setText(info['telefono'] or "No registrado")
        self.label_codigo_venta.setText(info['codigo_venta'])

        # Detalles del Crédito
        self.label_cuota_inicial.setText(f"${info['cuota_inicial']:,.2f}")
        self.label_saldo_financiado.setText(f"${info['saldo_financiado']:,.2f}")
        self.label_interes.setText(f"{info['interes']:.2f}%")
        self.label_plazo.setText(f"{info['plazo_meses']} meses")

        # Estado de Cuotas
        total_cuotas = info['total_cuotas']
        cuotas_pagadas = info['cuotas_pagadas']
        cuotas_pendientes = total_cuotas - cuotas_pagadas

        self.label_total_cuotas.setText(str(total_cuotas))
        self.label_cuotas_pagadas.setText(str(cuotas_pagadas))
        self.label_cuotas_pendientes.setText(str(cuotas_pendientes))

        # Resumen Financiero
        total_pagado = info['total_pagado']
        saldo_pendiente = info['saldo_pendiente']

        self.label_total_pagado.setText(f"💰 Total Pagado: ${total_pagado:,.2f}")
        self.label_saldo_pendiente.setText(f"⏳ Saldo Pendiente: ${saldo_pendiente:,.2f}")

        # Barra de progreso
        if info['saldo_financiado'] > 0:
            porcentaje_pagado = int((total_pagado / info['saldo_financiado']) * 100)
            self.progressBar_pago.setValue(porcentaje_pagado)
        else:
            self.progressBar_pago.setValue(0)

        # Información de la Cuota Actual
        if self.cuota_actual:
            self.label_numero_cuota.setText(f"Cuota #{self.cuota_actual.n_cuota}")
            self.label_valor_cuota.setText(f"${self.cuota_actual.valor_cuota:,.2f}")

            # Convertir fecha_vencimiento a date si es string
            fecha_venc = convertir_a_date(self.cuota_actual.fecha_vencimiento)
            self.label_fecha_vencimiento.setText(fecha_venc.strftime("%d/%m/%Y"))

            self.label_estado_cuota.setText(self.cuota_actual.estado)

            # Cambiar color según el estado
            if self.cuota_actual.estado == "Pendiente":
                self.label_estado_cuota.setStyleSheet("color: #FFC107; font-weight: bold;")
            elif self.cuota_actual.estado == "Vencida":
                self.label_estado_cuota.setStyleSheet("color: #DC3545; font-weight: bold;")
        else:
            self.label_numero_cuota.setText("✅ TODAS PAGADAS")
            self.label_valor_cuota.setText("$0.00")
            self.label_fecha_vencimiento.setText("-")
            self.label_estado_cuota.setText("Completado")
            self.label_estado_cuota.setStyleSheet("color: #28A745; font-weight: bold;")

    def limpiar_interfaz(self):
        """Limpia todos los campos de la interfaz"""
        # Datos del Cliente
        self.label_nombre_cliente.setText("-")
        self.label_telefono.setText("-")
        self.label_codigo_venta.setText("-")

        # Detalles del Crédito
        self.label_cuota_inicial.setText("$0.00")
        self.label_saldo_financiado.setText("$0.00")
        self.label_interes.setText("0.00%")
        self.label_plazo.setText("0 meses")

        # Estado de Cuotas
        self.label_total_cuotas.setText("0")
        self.label_cuotas_pagadas.setText("0")
        self.label_cuotas_pendientes.setText("0")

        # Resumen Financiero
        self.label_total_pagado.setText("💰 Total Pagado: $0.00")
        self.label_saldo_pendiente.setText("⏳ Saldo Pendiente: $0.00")
        self.progressBar_pago.setValue(0)

        # Cuota Actual
        self.label_numero_cuota.setText("-")
        self.label_valor_cuota.setText("$0.00")
        self.label_fecha_vencimiento.setText("-")
        self.label_estado_cuota.setText("Pendiente")

        # Deshabilitar botón de pago
        self.pushButton_realizar_pago.setEnabled(False)

        # Limpiar variables
        self.credito_seleccionado = None
        self.cuota_actual = None
        self.info_credito = None

    def realizar_pago(self):
        """Procesa el pago de la cuota actual"""
        if not self.cuota_actual or not self.info_credito:
            QMessageBox.warning(self, "Error", "No hay una cuota seleccionada para pagar.")
            return

        # Confirmación
        respuesta = QMessageBox.question(
            self,
            "Confirmar Pago",
            f"¿Confirma el pago de la cuota #{self.cuota_actual.n_cuota}?\n\n"
            f"Valor: ${self.cuota_actual.valor_cuota:,.2f}\n"
            f"Cliente: {self.info_credito['nombre_cliente']}\n\n"
            "Esta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if respuesta != QMessageBox.Yes:
            return

        try:
            # 1. Generar código de pago único
            codigo_pago = self.generar_codigo_pago()

            # 2. Crear el registro de Pago
            exito_pago = self.pago_controller.crear(
                codigo_pago=codigo_pago,
                fecha_pago=date.today(),
                estado="Completado",
                valor=float(self.cuota_actual.valor_cuota),
                id_pago=self.cuota_actual.id_pago
            )

            if not exito_pago:
                raise Exception("No se pudo crear el registro de pago.")

            # 3. Actualizar el estado de la Cuota a "Pagada"
            exito_cuota = self.cuota_controller.actualizar(
                id_pago=self.cuota_actual.id_pago,
                estado="Pagada"
            )

            if not exito_cuota:
                raise Exception("No se pudo actualizar el estado de la cuota.")

            # 4. Verificar si era la última cuota
            cuotas_pendientes = self.info_credito['total_cuotas'] - self.info_credito['cuotas_pagadas'] - 1

            if cuotas_pendientes == 0:
                # Actualizar el estado del crédito en la Venta a "Finalizado"
                exito_venta = self.venta_controller.actualizar_estado_credito(
                    id_venta=self.info_credito['id_venta'],
                    estado_credito="Finalizado"
                )

                if not exito_venta:
                    print("⚠️ Advertencia: No se pudo actualizar el estado del crédito en la venta.")

                QMessageBox.information(
                    self,
                    "🎉 ¡Crédito Completado!",
                    f"El pago se realizó exitosamente.\n\n"
                    f"✅ ¡Este crédito ha sido pagado en su totalidad!\n"
                    f"Cliente: {self.info_credito['nombre_cliente']}\n"
                    f"Total pagado: ${self.info_credito['saldo_financiado']:,.2f}"
                )
            else:
                QMessageBox.information(
                    self,
                    "✅ Pago Exitoso",
                    f"El pago de la cuota #{self.cuota_actual.n_cuota} se realizó correctamente.\n\n"
                    f"Valor pagado: ${self.cuota_actual.valor_cuota:,.2f}\n"
                    f"Cuotas restantes: {cuotas_pendientes}"
                )

            # 5. Guardar el id_credito antes de recargar
            id_credito_actual = self.info_credito['id_credito']

            # Recargar la información
            self.cargar_creditos_activos()

            # Volver a seleccionar el mismo crédito si aún está activo
            if cuotas_pendientes > 0:
                for i in range(self.comboBox_creditos.count()):
                    if self.comboBox_creditos.itemData(i) == id_credito_actual:
                        self.comboBox_creditos.setCurrentIndex(i)
                        break
            else:
                self.limpiar_interfaz()

            self.statusBar().showMessage("✅ Pago procesado exitosamente.")

        except Exception as e:
            QMessageBox.critical(
                self,
                "❌ Error al Procesar Pago",
                f"Ocurrió un error al procesar el pago:\n\n{e}\n\n"
                "El pago no se completó. Intente nuevamente."
            )
            print(f"Error en realizar_pago: {e}")
            import traceback
            traceback.print_exc()
            self.statusBar().showMessage("❌ Error al procesar el pago.")

    def generar_codigo_pago(self) -> int:
        """Genera un código único para el pago"""
        try:
            # Obtener todos los pagos y generar el siguiente código
            todos_pagos = self.pago_controller.obtener_todos()

            if not todos_pagos:
                return 1

            # Obtener el código máximo y sumar 1
            codigos = [p[0] for p in todos_pagos]  # codigo_pago es la primera columna
            return max(codigos) + 1

        except Exception as e:
            print(f"Error al generar código de pago: {e}")
            # En caso de error, usar timestamp como fallback
            return int(datetime.now().timestamp())

    # ✅ 5. Agregar los 3 métodos del checklist
    def actualizar_vista(self):
        """Actualiza la vista recargando los créditos activos"""
        self.cargar_creditos_activos()
        self.statusBar().showMessage("Vista actualizada correctamente")

    def crear_boton_regreso(self):
        from PyQt5.QtWidgets import QPushButton
        btn = QPushButton("← Regresar al Menú")
        btn.setStyleSheet("""
            QPushButton {
                background-color: #6C757D; color: white; border: none;
                border-radius: 5px; padding: 10px 20px; font-size: 14px; font-weight: bold;
            }
            QPushButton:hover { background-color: #5A6268; }
        """)
        btn.clicked.connect(self.regresar_al_lobby)
        self.statusBar().addPermanentWidget(btn)

    def regresar_al_lobby(self):
        if self.lobby_window:
            self.lobby_window.show()
            self.lobby_window.raise_()
            self.lobby_window.activateWindow()
        self.close()


if __name__ == "__main__":
    # Para pruebas
    sesion.set_usuario_id(1001)
    app = QtWidgets.QApplication(sys.argv)
    window = PagoCuotasWindow()
    window.show()
    sys.exit(app.exec_())