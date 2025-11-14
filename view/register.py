"""
Ventana de Registro de Nuevos Clientes
Por: Juan David Ramirez Carmona y Miguel Ángel Vargas Peláez
Fecha: 2025-11
Licencia: GPLv3
"""

import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox
# Importamos la clase Cliente que maneja la lógica de BD
from model.cliente import Cliente


class RegisterWindow(QtWidgets.QMainWindow):
    """
    Clase para la ventana de Registro de Nuevos Clientes.
    """

    def __init__(self, login_window):
        """
        Constructor de la ventana de registro.
        Recibe una referencia a la ventana de login para poder volver a ella.
        """
        super().__init__()

        # Guardar la referencia a la ventana de login
        self.login_window = login_window

        # Cargar el archivo .ui
        try:
            uic.loadUi('register_window.ui', self)
        except FileNotFoundError:
            print("Error: Asegúrate de que 'register_window.ui' esté en el mismo directorio.")
            sys.exit(1)

        # Instanciar el controlador de Cliente
        try:
            self.cliente_controller = Cliente()
        except Exception as e:
            QMessageBox.critical(self, "Error de Base de Datos",
                                 f"No se pudo conectar a la base de datos.\nError: {e}")
            sys.exit(1)

        # Conectar botones
        self.pushButton_register_submit.clicked.connect(self.handle_register)
        self.pushButton_go_to_login.clicked.connect(self.back_to_login)

        # Inicializar barra de estado
        self.statusBar().showMessage("Por favor, ingrese sus datos para registrarse.")

        # Enfocar el primer campo
        self.lineEdit_codigo.setFocus()

    def get_rol_id(self):
        """
        Obtiene el ID del rol según la selección del ComboBox.
        Retorna None si no se seleccionó un rol válido.
        """
        rol_texto = self.comboBox_rol.currentText()

        if rol_texto == "Usuario Paramétrico":
            return 2
        elif rol_texto == "Usuario Esporádico":
            return 3
        else:
            return None  # No se seleccionó un tipo válido

    def handle_register(self):
        """
        Maneja la lógica de registro al presionar el botón.
        """
        # 1. Recoger los datos de los campos OBLIGATORIOS
        codigo_str = self.lineEdit_codigo.text().strip()
        nombre = self.lineEdit_nombre.text().strip()
        email = self.lineEdit_email.text().strip()
        password = self.lineEdit_password.text()
        password_confirm = self.lineEdit_password_confirm.text()

        # Obtener el ID del rol desde el ComboBox
        id_rol = self.get_rol_id()

        # 2. Validaciones de campos OBLIGATORIOS
        if not all([codigo_str, nombre, email, password, password_confirm]):
            self.statusBar().showMessage("Error: Los campos marcados con * son obligatorios.")
            QMessageBox.warning(self, "Campos Vacíos",
                                "Por favor, llene todos los campos obligatorios:\n"
                                "- Código (Cédula)\n"
                                "- Nombre Completo\n"
                                "- Email\n"
                                "- Tipo de Usuario\n"
                                "- Contraseña y Confirmación")
            return

        # Validar que se haya seleccionado un tipo de usuario válido
        if id_rol is None:
            self.statusBar().showMessage("Error: Debe seleccionar un tipo de usuario.")
            QMessageBox.warning(self, "Tipo de Usuario",
                                "Por favor, seleccione un tipo de usuario válido.")
            self.comboBox_rol.setFocus()
            return

        # Validar formato de email (básico)
        if "@" not in email or "." not in email:
            self.statusBar().showMessage("Error: El email no parece válido.")
            QMessageBox.warning(self, "Email Inválido",
                                "Por favor, ingrese un email válido.")
            self.lineEdit_email.setFocus()
            return

        # Validar longitud mínima de contraseña
        if len(password) < 6:
            self.statusBar().showMessage("Error: La contraseña debe tener al menos 6 caracteres.")
            QMessageBox.warning(self, "Contraseña Débil",
                                "La contraseña debe tener al menos 6 caracteres.")
            self.lineEdit_password.setFocus()
            return

        # Validar que las contraseñas coincidan
        if password != password_confirm:
            self.statusBar().showMessage("Error: Las contraseñas no coinciden.")
            QMessageBox.warning(self, "Error de Contraseña", "Las contraseñas no coinciden.")
            self.lineEdit_password.clear()
            self.lineEdit_password_confirm.clear()
            self.lineEdit_password.setFocus()
            return

        # Validar que el código sea un número
        try:
            codigo_cliente = int(codigo_str)
        except ValueError:
            self.statusBar().showMessage("Error: El código (cédula) debe ser un número.")
            QMessageBox.warning(self, "Dato Inválido",
                                "El código (cédula) debe ser un valor numérico.")
            self.lineEdit_codigo.setFocus()
            return

        # 3. Recoger campos OPCIONALES
        telefono = self.lineEdit_telefono.text().strip() or None
        departamento = self.lineEdit_departamento.text().strip() or None
        municipio = self.lineEdit_municipio.text().strip() or None
        calle = self.lineEdit_calle.text().strip() or None
        direccion = self.lineEdit_direccion.text().strip() or None

        # 4. Intentar crear el cliente usando el controlador
        try:
            # Se llama al método crear() del modelo Cliente
            success = self.cliente_controller.crear(
                codigo_cliente=codigo_cliente,
                nombre=nombre,
                email=email,
                contrasena=password,
                id_rol=id_rol,
                telefono=telefono,
                departamento=departamento,
                municipio=municipio,
                calle=calle,
                direccion=direccion
            )

            if success:
                self.register_success(nombre)
            else:
                # Esto puede pasar si el 'crear' retorna False (ej. clave duplicada)
                self.register_failure("El código o email ya podría estar en uso.")

        except Exception as e:
            # Captura errores específicos de la BD (ej. ORA-00001: unique constraint violated)
            error_msg = str(e)
            if "UNIQUE constraint" in error_msg or "ORA-00001" in error_msg:
                self.register_failure("El código (cédula) o el email ya están registrados.")
            else:
                self.register_failure(f"Error inesperado de la base de datos:\n{e}")

    def register_success(self, username):
        """Maneja el registro exitoso."""
        self.statusBar().showMessage("¡Registro exitoso! Ahora puede iniciar sesión.")
        QMessageBox.information(self, "Registro Exitoso",
                                f"¡Bienvenido, {username}!\n\n"
                                "Su cuenta ha sido creada exitosamente.\n"
                                "Ahora será redirigido al inicio de sesión.")

        # Vuelve automáticamente al login
        self.back_to_login()

    def register_failure(self, message):
        """Maneja el fallo en el registro."""
        self.statusBar().showMessage(f"Error de registro: {message}")
        QMessageBox.warning(self, "Error de Registro", message)
        self.lineEdit_password.clear()
        self.lineEdit_password_confirm.clear()

    def back_to_login(self):
        """
        Cierra esta ventana y muestra la ventana de login que se pasó
        en el constructor.
        """
        self.login_window.show()  # Muestra el login
        self.close()  # Cierra esta ventana