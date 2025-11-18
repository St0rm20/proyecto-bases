import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox
from model.usuario import Usuario
from view.register import RegisterWindow
from util import sesion
from view.lobby import LobbyWindow

from model import auditoria


# ------------------

class LoginWindow(QtWidgets.QMainWindow):
    """Clase principal para la ventana de Login."""

    def __init__(self):
        super().__init__()

        # Cargar el archivo .ui. Asegúrate de que este archivo esté en el mismo directorio.
        try:
            uic.loadUi('login_window.ui', self)
        except FileNotFoundError:
            print("Error: Asegúrate de que el archivo 'login_window.ui' esté en el mismo directorio.")
            sys.exit(1)

        # 1. Instanciar el controlador de Usuario (cambio aquí)
        try:
            self.usuario_controller = Usuario()
        except Exception as e:
            # Manejo de error si la BD no se puede conectar
            print(f"Error fatal al conectar con la BD: {e}")
            QMessageBox.critical(self, "Error de Base de Datos",
                                 f"No se pudo conectar a la base de datos.\nError: {e}")
            sys.exit(1)
        # ----------------

        # 2. Conectar los botones
        self.pushButton_login.clicked.connect(self.handle_login)

        # Esta es la conexión que faltaba para el botón de registro
        self.pushButton_register.clicked.connect(self.show_register_window)
        # ---------------------

        # 3. Inicializar la barra de estado
        self.statusBar().showMessage("Listo para iniciar sesión...")

        # 4. Establecer el foco inicial
        self.lineEdit_username.setFocus()

    def handle_login(self):
        """Método que se ejecuta al hacer clic en 'Iniciar Sesión'."""

        # 1. Recoger los datos de los campos
        email = self.lineEdit_username.text()
        password = self.lineEdit_password.text()

        # 2. Validar que los campos no estén vacíos
        if not email or not password:
            self.statusBar().showMessage("Email y contraseña son requeridos.")
            QMessageBox.warning(self, "Campos Vacíos", "Por favor, ingrese su email y contraseña.")
            return

        # 3. Autenticar usando el controlador de Usuario (cambio aquí)
        try:
            # Buscar usuario por email
            usuario_data = self.usuario_controller.buscar_por_email(email)

            if usuario_data and usuario_data.contrasena == password:
                # ¡Éxito! Ahora obtenemos los datos del usuario
                # Determinamos el nombre para el saludo


                sesion.set_usuario_id(usuario_data.id_usuario)

                print("hasta aqui corre")
                nombre_saludo = sesion.get_usuario_nombre(usuario_data.id_usuario)


                self.login_success(nombre_saludo)

            else:
                # Falla de autenticación (usuario o contra incorrecta)
                self.login_failure()

        except Exception as e:
            # Manejar cualquier error inesperado de la base de datos
            print(f"Error durante el login: {e}")
            self.statusBar().showMessage("Error del sistema.")
            QMessageBox.critical(self, "Error del Sistema",
                                 f"Ocurrió un error inesperado: {e}")

    def login_success(self, username):
        """Maneja el inicio de sesión exitoso."""

        self.statusBar().showMessage(f"¡Bienvenido, {username}!")

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Inicio de Sesión Exitoso")
        msg.setInformativeText(f"Bienvenido al sistema, {username}.")
        msg.setWindowTitle("Éxito")
        msg.exec_()

        # Limpiar los campos después del éxito
        self.lineEdit_username.clear()
        self.lineEdit_password.clear()
        self.close()
        LobbyWindow.abrir_lobby()


    def login_failure(self):
        """Maneja el error de autenticación."""
        self.statusBar().showMessage("Error de autenticación. Intente de nuevo.")

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText("Credenciales Incorrectas")
        msg.setInformativeText("El email o la contraseña son incorrectos.")
        msg.setWindowTitle("Error")
        msg.exec_()

        # Limpiar solo el campo de contraseña
        self.lineEdit_password.clear()
        self.lineEdit_password.setFocus()

    def show_register_window(self):
        """
        Oculta la ventana de login y muestra la ventana de registro.
        """
        self.hide()  # Oculta la ventana de login
        # Crea la instancia de registro y le pasa la instancia actual de login
        # para que 'RegisterWindow' pueda volver a mostrarla
        self.register_win = RegisterWindow(self)
        self.register_win.show()


# --- Bloque principal para ejecutar la aplicación ---
if __name__ == '__main__':
    # Añadir un parche para asegurar que las importaciones funcionen
    # al ejecutar 'python view/login.py'
    import os

    # Añade el directorio raíz (dos niveles arriba) al path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    app = QtWidgets.QApplication(sys.argv)


    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())