import sys
import os
from PyQt5 import QtWidgets

# Añadir el directorio raíz al path para las importaciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from view.login import LoginWindow

# Hoja de estilos global
MY_STYLE_SHEET = """
QMainWindow {
    background-color: #2D2D2D;
}

QLabel {
    color: #E0E0E0;
    font-size: 14px;
}

QLineEdit {
    background-color: #444444;
    color: #FFFFFF;
    border: 1px solid #555555;
    border-radius: 5px;
    padding: 8px;
    font-size: 14px;
}

QLineEdit:focus {
    border: 1px solid #0078D7;
    background-color: #4A4A4A;
}

/* --- Botón Principal (Login) --- */
QPushButton#pushButton_login {
    background-color: #0078D7;
    color: white;
    font-weight: bold;
    font-size: 15px;
    border: none;
    border-radius: 5px;
    padding: 10px;
}

QPushButton#pushButton_login:hover {
    background-color: #005A9E;
}

QPushButton#pushButton_login:pressed {
    background-color: #004C8A;
}

/* --- Botón Secundario (Registrarse) --- */
QPushButton#pushButton_register {
    background-color: transparent;
    color: #0078D7;
    border: none;
    font-size: 13px;
    padding: 5px;
    text-decoration: underline;
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


class MainApplication:
    """Clase principal que inicia la aplicación."""

    def __init__(self):
        self.app = None
        self.main_window = None

    def run(self):
        """Método principal que ejecuta la aplicación."""
        # Crear la aplicación Qt
        self.app = QtWidgets.QApplication(sys.argv)

        # Aplicar la hoja de estilos
        self.app.setStyleSheet(MY_STYLE_SHEET)

        # Crear y mostrar la ventana principal de login
        self.main_window = LoginWindow()
        self.main_window.show()

        # Ejecutar el bucle principal de la aplicación
        return_code = self.app.exec_()

        # Salir del programa
        sys.exit(return_code)


# Punto de entrada principal
if __name__ == '__main__':
    application = MainApplication()
    application.run()