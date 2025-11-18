"""
Ventana principal (Lobby) con control de acceso basado en roles
Por: Juan David Ramirez Carmona y Miguel Ángel Vargas Peláez
Fecha: 2025-11
Licencia: GPLv3
"""

import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QGridLayout, QPushButton, QLabel, QMessageBox,
                             QGroupBox, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont
from util import sesion
from model.usuario import Usuario


class LobbyWindow(QMainWindow):
    """
    Ventana principal con menú de opciones según el rol del usuario
    """

    def __init__(self):
        super().__init__()

        # Verificar sesión primero
        if not sesion.is_logged_in():
            QMessageBox.warning(
                self,
                "Sesión Requerida",
                "Debe iniciar sesión para acceder al sistema."
            )
            sys.exit(1)

        # Obtener información del usuario
        self.usuario_id = sesion.get_usuario_id()
        self.usuario_controller = Usuario()
        self.id_rol = None
        self.nombre_usuario = None

        # Cargar datos del usuario
        self.cargar_datos_usuario()

        # Configurar ventana
        self.setWindowTitle("Sistema de Gestión - Menú Principal")
        self.setGeometry(100, 100, 1000, 700)

        # Crear interfaz
        self.crear_interfaz()

        # Aplicar estilos
        self.aplicar_estilos()

        # Mensaje de bienvenida
        self.statusBar().showMessage(
            f"Bienvenido, {self.nombre_usuario} - {self.obtener_nombre_rol()}"
        )

    def cargar_datos_usuario(self):
        """Carga los datos del usuario logueado"""
        try:
            usuario = self.usuario_controller.obtener_por_id(self.usuario_id)

            if not usuario:
                QMessageBox.critical(
                    self,
                    "Error",
                    "No se pudo cargar la información del usuario."
                )
                sys.exit(1)

            # Manejar tanto tuplas como objetos
            if isinstance(usuario, tuple):
                # Orden: id_usuario, nombre_usuario, email, contrasena, id_rol
                self.nombre_usuario = usuario[1]
                self.id_rol = usuario[4] if len(usuario) > 4 else None
            else:
                self.nombre_usuario = usuario.nombre_usuario
                self.id_rol = usuario.id_rol

            print(f"Usuario cargado: {self.nombre_usuario}, Rol: {self.id_rol}")

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al cargar datos del usuario:\n{e}"
            )
            sys.exit(1)

    def obtener_nombre_rol(self) -> str:
        """Retorna el nombre del rol según el ID"""
        roles = {
            1: "Administrador",
            2: "Usuario Paramétrico",
            3: "Usuario Esporádico"
        }
        return roles.get(self.id_rol, "Desconocido")

    def crear_interfaz(self):
        """Crea la interfaz principal"""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        layout_principal = QVBoxLayout()
        central_widget.setLayout(layout_principal)

        # Encabezado
        self.crear_encabezado(layout_principal)

        # Contenedor de módulos
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Crear secciones según el rol
        self.crear_seccion_gestion(scroll_layout)
        self.crear_seccion_ventas(scroll_layout)
        self.crear_seccion_creditos(scroll_layout)
        self.crear_seccion_reportes(scroll_layout)
        self.crear_seccion_sistema(scroll_layout)

        scroll_area.setWidget(scroll_widget)
        layout_principal.addWidget(scroll_area)

        # Pie de página
        self.crear_pie_pagina(layout_principal)

    def crear_encabezado(self, layout):
        """Crea el encabezado con información del usuario"""
        frame_header = QFrame()
        frame_header.setObjectName("headerFrame")
        header_layout = QVBoxLayout(frame_header)

        # Título
        titulo = QLabel("🏢 SISTEMA DE GESTIÓN")
        titulo.setObjectName("titulo")
        titulo.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(titulo)

        # Info del usuario
        info_usuario = QLabel(
            f"👤 {self.nombre_usuario} | 🎫 {self.obtener_nombre_rol()}"
        )
        info_usuario.setObjectName("infoUsuario")
        info_usuario.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(info_usuario)

        layout.addWidget(frame_header)

    def crear_seccion_gestion(self, layout):
        """Crea la sección de gestión (CRUD)"""
        # Solo Admin y Paramétrico ven esta sección completa
        if self.id_rol in [1, 2]:
            grupo = self.crear_grupo("📋 Gestión")
            grid = QGridLayout()

            # Botón Clientes (Admin y Paramétrico)
            btn_clientes = self.crear_boton_modulo(
                "👥 Clientes",
                "Gestión de clientes",
                "crud_clientes"
            )
            grid.addWidget(btn_clientes, 0, 0)

            # Botón Productos (Todos los roles)
            btn_productos = self.crear_boton_modulo(
                "📦 Productos",
                "Gestión de productos",
                "crud_productos"
            )
            grid.addWidget(btn_productos, 0, 1)

            grupo.setLayout(grid)
            layout.addWidget(grupo)

        elif self.id_rol == 3:
            # Esporádicos solo ven Productos
            grupo = self.crear_grupo("📋 Gestión")
            grid = QGridLayout()

            btn_productos = self.crear_boton_modulo(
                "📦 Productos",
                "Consulta de productos (Solo lectura)",
                "crud_productos"
            )
            grid.addWidget(btn_productos, 0, 0)

            grupo.setLayout(grid)
            layout.addWidget(grupo)

    def crear_seccion_ventas(self, layout):
        """Crea la sección de ventas"""
        grupo = self.crear_grupo("💰 Ventas")
        grid = QGridLayout()

        # Ventas (Todos)
        btn_ventas = self.crear_boton_modulo(
            "🛒 Registrar Venta",
            "Crear nueva venta",
            "ventas"
        )
        grid.addWidget(btn_ventas, 0, 0)

        # Consultar Ventas (Todos)
        btn_consultar = self.crear_boton_modulo(
            "📊 Consultar Ventas",
            "Ver historial de ventas",
            "ventas_window"
        )
        grid.addWidget(btn_consultar, 0, 1)

        grupo.setLayout(grid)
        layout.addWidget(grupo)

    def crear_seccion_creditos(self, layout):
        """Crea la sección de créditos y pagos"""
        grupo = self.crear_grupo("💳 Créditos y Pagos")
        grid = QGridLayout()

        # Pago de Cuotas (Admin y Paramétrico)
        if self.id_rol in [1, 2]:
            btn_pagos = self.crear_boton_modulo(
                "💵 Pago de Cuotas",
                "Gestionar pagos de créditos",
                "pago_cuotas"
            )
            grid.addWidget(btn_pagos, 0, 0)

        # Deudores (Todos)
        btn_deudores = self.crear_boton_modulo(
            "📉 Clientes Deudores",
            "Ver clientes con deudas",
            "deudores"
        )
        grid.addWidget(btn_deudores, 0, 1)

        grupo.setLayout(grid)
        layout.addWidget(grupo)

    def crear_seccion_reportes(self, layout):
        """Crea la sección de reportes"""
        grupo = self.crear_grupo("📈 Reportes")
        grid = QGridLayout()

        # Inventario (Todos)
        btn_inventario = self.crear_boton_modulo(
            "📦 Inventario",
            "Reporte de inventario",
            "inventario"
        )
        grid.addWidget(btn_inventario, 0, 0)

        # IVA (Todos)
        btn_iva = self.crear_boton_modulo(
            "📊 IVA",
            "Reporte de IVA",
            "ventana_iva"
        )
        grid.addWidget(btn_iva, 0, 1)

        # Ventas por Tipo (Todos)
        btn_tipo = self.crear_boton_modulo(
            "📋 Ventas por Tipo",
            "Reporte de ventas por tipo",
            "ventas_tipo"
        )
        grid.addWidget(btn_tipo, 1, 0)

        grupo.setLayout(grid)
        layout.addWidget(grupo)

    def crear_seccion_sistema(self, layout):
        """Crea la sección de sistema y herramientas"""
        grupo = self.crear_grupo("⚙️ Sistema")
        grid = QGridLayout()

        # Calculadora (Todos)
        btn_calc = self.crear_boton_modulo(
            "🔢 Calculadora",
            "Calculadora financiera",
            "calculadora"
        )
        grid.addWidget(btn_calc, 0, 0)

        # Auditoría (Solo Admin)
        if self.id_rol == 1:
            btn_auditoria = self.crear_boton_modulo(
                "🔍 Auditoría",
                "Bitácora del sistema",
                "auditoria_window"
            )
            grid.addWidget(btn_auditoria, 0, 1)

        grupo.setLayout(grid)
        layout.addWidget(grupo)

    def crear_grupo(self, titulo: str) -> QGroupBox:
        """Crea un grupo para organizar botones"""
        grupo = QGroupBox(titulo)
        grupo.setObjectName("moduloGrupo")
        return grupo

    def crear_boton_modulo(self, texto: str, descripcion: str,
                           modulo: str) -> QPushButton:
        """
        Crea un botón para acceder a un módulo

        Args:
            texto: Texto del botón
            descripcion: Descripción del módulo
            modulo: Nombre del archivo del módulo (sin .py)
        """
        btn = QPushButton(f"{texto}\n{descripcion}")
        btn.setObjectName("botonModulo")
        btn.setMinimumSize(250, 80)
        btn.setCursor(Qt.PointingHandCursor)

        # Conectar al método de apertura
        btn.clicked.connect(lambda: self.abrir_modulo(modulo))

        return btn

    def crear_pie_pagina(self, layout):
        """Crea el pie de página con botones de acción"""
        frame_footer = QFrame()
        frame_footer.setObjectName("footerFrame")
        footer_layout = QHBoxLayout(frame_footer)

        # Botón Cerrar Sesión
        btn_logout = QPushButton("🚪 Cerrar Sesión")
        btn_logout.setObjectName("btnLogout")
        btn_logout.clicked.connect(self.cerrar_sesion)
        footer_layout.addWidget(btn_logout)

        footer_layout.addStretch()

        # Botón Salir
        btn_salir = QPushButton("❌ Salir")
        btn_salir.setObjectName("btnSalir")
        btn_salir.clicked.connect(self.close)
        footer_layout.addWidget(btn_salir)

        layout.addWidget(frame_footer)

    def abrir_modulo(self, modulo: str):
        """
        Abre un módulo específico

        Args:
            modulo: Nombre del archivo del módulo (sin .py)
        """
        try:
            # Mapeo de módulos a clases
            modulos = {
                'crud_clientes': ('view.crud_clientes', 'CrudClientesWindow'),
                'crud_productos': ('view.crud_productos', 'CRUDProductosWindow'),
                'ventas': ('view.ventas_window', 'VentasWindow'),
                'ventas_window': ('view.consulta', 'VentasWindow'),
                'pago_cuotas': ('view.pago_cuotas', 'PagoCuotasWindow'),
                'deudores': ('view.deudores', 'VentanaMorosos'),
                'inventario': ('view.inventario', 'VentanaInventario'),
                'ventana_iva': ('view.ventana_iva', 'VentanaIVA'),
                'ventas_tipo': ('view.ventas_tipo', 'VentanaVentasTipo'),
                'calculadora': ('view.calculadora', 'CalculatorWindow'),
                'auditoria_window': ('view.auditoria_window', 'AuditoriaWindow'),
            }

            if modulo not in modulos:
                QMessageBox.warning(
                    self,
                    "Módulo no encontrado",
                    f"El módulo '{modulo}' no está configurado."
                )
                return

            # Obtener información del módulo
            paquete, clase = modulos[modulo]

            # Importar dinámicamente
            import importlib
            modulo_importado = importlib.import_module(paquete)
            ClaseVentana = getattr(modulo_importado, clase)

            # Crear y mostrar la ventana
            self.ventana_modulo = ClaseVentana()
            self.ventana_modulo.show()

            self.statusBar().showMessage(f"✅ Módulo '{modulo}' abierto")

        except ImportError as e:
            QMessageBox.critical(
                self,
                "Error al cargar módulo",
                f"No se pudo cargar el módulo '{modulo}':\n{e}"
            )
            print(f"Error de importación: {e}")
            import traceback
            traceback.print_exc()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al abrir el módulo:\n{e}"
            )
            print(f"Error al abrir módulo: {e}")
            import traceback
            traceback.print_exc()

    def cerrar_sesion(self):
        """Cierra la sesión del usuario y abre la ventana de login"""
        respuesta = QMessageBox.question(
            self,
            "Cerrar Sesión",
            "¿Está seguro que desea cerrar sesión?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if respuesta == QMessageBox.Yes:
            sesion.logout()
            QMessageBox.information(
                self,
                "Sesión Cerrada",
                "La sesión se cerró correctamente."
            )

            # ✅ CERRAR EL LOBBY Y ABRIR LOGIN
            self.abrir_login()

    def abrir_login(self):
        """Cierra el lobby y abre la ventana de login"""
        try:
            # Cerrar el lobby
            self.close()

            # Importar y abrir login
            from view.login import LoginWindow
            self.login_window = LoginWindow()
            self.login_window.show()

        except ImportError as e:
            QMessageBox.critical(
                None,
                "Error",
                f"No se pudo cargar la ventana de login:\n{e}\n\nLa aplicación se cerrará."
            )
            sys.exit(1)
        except Exception as e:
            QMessageBox.critical(
                None,
                "Error",
                f"Error al abrir login:\n{e}\n\nLa aplicación se cerrará."
            )
            sys.exit(1)

    def aplicar_estilos(self):
        """Aplica estilos CSS a la ventana"""
        self.setStyleSheet("""
            /* Ventana principal */
            QMainWindow {
                background-color: #F5F7FA;
            }

            /* Encabezado */
            #headerFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498DB, stop:1 #2C3E50
                );
                border-radius: 10px;
                padding: 20px;
                margin: 10px;
            }

            #titulo {
                color: white;
                font-size: 28px;
                font-weight: bold;
                padding: 10px;
            }

            #infoUsuario {
                color: #ECF0F1;
                font-size: 16px;
                padding: 5px;
            }

            /* Grupos de módulos */
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #2C3E50;
                border: 2px solid #BDC3C7;
                border-radius: 10px;
                margin-top: 15px;
                padding: 20px;
                background-color: white;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }

            /* Botones de módulo */
            #botonModulo {
                background-color: white;
                border: 2px solid #3498DB;
                border-radius: 10px;
                color: #2C3E50;
                padding: 15px;
                font-size: 13px;
                font-weight: bold;
                text-align: center;
            }

            #botonModulo:hover {
                background-color: #3498DB;
                color: white;
                border: 2px solid #2980B9;
            }

            #botonModulo:pressed {
                background-color: #2980B9;
            }

            /* Footer */
            #footerFrame {
                background-color: #ECF0F1;
                border-radius: 10px;
                padding: 10px;
                margin: 10px;
            }

            #btnLogout, #btnSalir {
                background-color: #E74C3C;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }

            #btnLogout:hover, #btnSalir:hover {
                background-color: #C0392B;
            }

            /* Barra de estado */
            QStatusBar {
                background-color: #34495E;
                color: white;
                font-size: 12px;
                padding: 5px;
            }
        """)

    def closeEvent(self, event):
        """Maneja el cierre de la ventana"""
        respuesta = QMessageBox.question(
            self,
            "Salir",
            "¿Está seguro que desea salir del sistema?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if respuesta == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    @staticmethod
    def abrir_lobby():
        """Método estático para abrir el lobby desde otras ventanas (como login)"""
        try:
            from view.lobby import LobbyWindow
            lobby = LobbyWindow()
            lobby.show()
            return lobby
        except ImportError as e:
            QMessageBox.critical(
                None,
                "Error",
                f"No se pudo abrir el lobby:\n{e}"
            )
            return None
        except Exception as e:
            QMessageBox.critical(
                None,
                "Error",
                f"Error al abrir el lobby:\n{e}"
            )
            return None

if __name__ == "__main__":
    # Para pruebas - simular login

    app = QtWidgets.QApplication(sys.argv)
    window = LobbyWindow()
    window.show()
    sys.exit(app.exec_())