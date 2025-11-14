import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox
# Importamos la clase Cliente que maneja la lógica de BD
from model.cliente import Cliente
# Importamos la nueva ventana de registro
from view.register import RegisterWindow


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

        # 1. Instanciar el controlador de Cliente
        try:
            self.cliente_controller = Cliente()
        except Exception as e:
            # Manejo de error si la BD no se puede conectar
            print(f"Error fatal al conectar con la BD: {e}")
            QMessageBox.critical(self, "Error de Base de Datos",
                                 f"No se pudo conectar a la base de datos.\nError: {e}")
            sys.exit(1)
        # ----------------

        # 2. Conectar los botones
        self.pushButton_login.clicked.connect(self.handle_login)

        # --- LÍNEA AÑADIDA ---
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

        # 3. Autenticar usando el controlador
        try:
            if self.cliente_controller.verificar_contrasena(email, password):
                # ¡Éxito! Ahora obtenemos los datos del usuario
                cliente_data = self.cliente_controller.buscar_por_email(email)

                # Determinamos el nombre para el saludo
                if cliente_data and cliente_data.nombre:
                    nombre_saludo = cliente_data.nombre
                else:
                    nombre_saludo = email  # Fallback si no tiene nombre

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

        # Opcional: Aquí podrías abrir la ventana principal de la app y cerrar esta
        # self.main_app_window = MainApplicationWindow()
        # self.main_app_window.show()
        # self.close()

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

    MY_STYLE_SHEET = """
    QMainWindow {
        background-color: #2D2D2D; /* Fondo principal oscuro */
    }

    QLabel {
        color: #E0E0E0; /* Texto de etiquetas claro */
        font-size: 14px;
    }

    QLineEdit {
        background-color: #444444; /* Fondo del campo de texto */
        color: #FFFFFF; /* Texto del campo de texto */
        border: 1px solid #555555;
        border-radius: 5px; /* Bordes redondeados */
        padding: 8px; /* Relleno interno */
        font-size: 14px;
    }

    QLineEdit:focus {
        /* Estilo cuando el campo está seleccionado (en foco) */
        border: 1px solid #0078D7; /* Borde azul brillante */
        background-color: #4A4A4A;
    }

    /* --- Botón Principal (Login) --- */
    QPushButton#pushButton_login {
        background-color: #0078D7; /* Azul "Microsoft" */
        color: white;
        font-weight: bold;
        font-size: 15px;
        border: none;
        border-radius: 5px;
        padding: 10px;
    }

    QPushButton#pushButton_login:hover {
        background-color: #005A9E; /* Tono más oscuro al pasar el ratón */
    }

    QPushButton#pushButton_login:pressed {
        background-color: #004C8A; /* Tono al hacer clic */
    }

    /* --- Botón Secundario (Registrarse) --- */
    QPushButton#pushButton_register {
        background-color: transparent; /* Sin fondo */
        color: #0078D7; /* Mismo azul que el botón de login */
        border: none; /* Sin borde */
        font-size: 13px;
        padding: 5px;
        text-decoration: underline; /* Subrayado como un link */
    }

    QPushButton#pushButton_register:hover {
        color: #005A9E;
    }

    QPushButton#pushButton_register:pressed {
        color: #004C8A;
    }

    /* Estilo para la barra de estado */
    QStatusBar {
        color: #E0E0E0;
    }

    /* Estilo para los botones de la ventana de registro */
    QPushButton#pushButton_register_submit {
        background-color: #0078D7;
        color: white;
        font-weight: bold;
        font-size: 15px;
        border: none;
        border-radius: 5px;
        padding: 10px;
    }
    QPushButton#pushButton_register_submit:hover {
        background-color: #005A9E;
    }
    QPushButton#pushButton_register_submit:pressed {
        background-color: #004C8A;
    }

    QPushButton#pushButton_go_to_login {
        background-color: transparent;
        color: #0078D7;
        border: none;
        font-size: 13px;
        padding: 5px;
        text-decoration: underline;
    }
    QPushButton#pushButton_go_to_login:hover {
        color: #005A9E;
    }
    QPushButton#pushButton_go_to_login:pressed {
        color: #004C8A;
    }
    """
    app.setStyleSheet(MY_STYLE_SHEET)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())