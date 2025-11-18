import sys
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import QPushButton

# ------------------
# 3. LA HOJA DE ESTILOS (QSS)
# ------------------
# Inspirada en tu ejemplo, pero adaptada para una calculadora.
MY_STYLE_SHEET = """
QMainWindow {
    background-color: #2D2D2D; /* Fondo principal oscuro */
}

/* El display de la calculadora */
QLineEdit#display {
    background-color: #444444;
    color: #FFFFFF;
    border: 1px solid #555555;
    border-radius: 5px;
    padding: 10px;
    font-size: 28px; /* Fuente más grande para el display */
}

/* Estilo base para todos los botones */
QPushButton {
    background-color: #4A4A4A; /* Gris oscuro para números */
    color: white;
    font-weight: bold;
    font-size: 16px;
    border: none;
    border-radius: 5px;
    padding: 15px; /* Botones más grandes */
}

QPushButton:hover {
    background-color: #5A5A5A;
}

QPushButton:pressed {
    background-color: #404040;
}

/* --- Botones de Operadores (naranja) --- */
QPushButton#btn_divide,
QPushButton#btn_multiply,
QPushButton#btn_subtract,
QPushButton#btn_add,
QPushButton#btn_lparen,
QPushButton#btn_rparen {
    background-color: #FF8C00; /* Naranja oscuro */
}

QPushButton#btn_divide:hover,
QPushButton#btn_multiply:hover,
QPushButton#btn_subtract:hover,
QPushButton#btn_add:hover,
QPushButton#btn_lparen:hover,
QPushButton#btn_rparen:hover {
    background-color: #E07B00;
}

QPushButton#btn_divide:pressed,
QPushButton#btn_multiply:pressed,
QPushButton#btn_subtract:pressed,
QPushButton#btn_add:pressed,
QPushButton#btn_lparen:pressed,
QPushButton#btn_rparen:pressed {
    background-color: #CC7000;
}

/* --- Botón de Limpiar (Rojo suave) --- */
QPushButton#btn_clear {
    background-color: #D9534F; /* Rojo */
}
QPushButton#btn_clear:hover {
    background-color: #C9302C;
}
QPushButton#btn_clear:pressed {
    background-color: #AC2925;
}

/* --- Botón de Igual (Azul, como tu botón de Login) --- */
QPushButton#btn_equals {
    background-color: #0078D7; /* Azul "Microsoft" */
}

QPushButton#btn_equals:hover {
    background-color: #005A9E;
}

QPushButton#btn_equals:pressed {
    background-color: #004C8A;
}

/* Estilo para la barra de estado */
QStatusBar {
    color: #E0E0E0;
}
"""


# ------------------
# 1. LA CLASE DE LA VENTANA
# ------------------
class CalculatorWindow(QtWidgets.QMainWindow):
    """Clase principal para la Calculadora."""

    def __init__(self, parent=None):  # ✅ 1. Cambiar firma del __init__
        super().__init__(parent)

        # ✅ 2. Agregar después de super().__init__()
        self.lobby_window = parent

        # Cargar el archivo .ui
        try:
            uic.loadUi('calculator.ui', self)
        except FileNotFoundError:
            print("Error: Asegúrate de que el archivo 'calculator.ui' esté en el mismo directorio.")
            sys.exit(1)

        # 1. Configurar el display
        # (La mayoría de las propiedades ya están en el .ui, pero algunas
        # como el alineamiento son más fáciles de asegurar aquí)
        self.display.setReadOnly(True)
        self.display.setAlignment(QtCore.Qt.AlignRight)

        # 2. Conectar los botones

        # Botones de números y decimal
        self.btn_0.clicked.connect(lambda: self.append_to_display('0'))
        self.btn_1.clicked.connect(lambda: self.append_to_display('1'))
        self.btn_2.clicked.connect(lambda: self.append_to_display('2'))
        self.btn_3.clicked.connect(lambda: self.append_to_display('3'))
        self.btn_4.clicked.connect(lambda: self.append_to_display('4'))
        self.btn_5.clicked.connect(lambda: self.append_to_display('5'))
        self.btn_6.clicked.connect(lambda: self.append_to_display('6'))
        self.btn_7.clicked.connect(lambda: self.append_to_display('7'))
        self.btn_8.clicked.connect(lambda: self.append_to_display('8'))
        self.btn_9.clicked.connect(lambda: self.append_to_display('9'))
        self.btn_decimal.clicked.connect(lambda: self.append_to_display('.'))

        # Botones de operadores
        self.btn_add.clicked.connect(lambda: self.append_to_display('+'))
        self.btn_subtract.clicked.connect(lambda: self.append_to_display('-'))
        self.btn_multiply.clicked.connect(lambda: self.append_to_display('*'))
        self.btn_divide.clicked.connect(lambda: self.append_to_display('/'))
        self.btn_lparen.clicked.connect(lambda: self.append_to_display('('))
        self.btn_rparen.clicked.connect(lambda: self.append_to_display(')'))

        # Botones de función
        self.btn_clear.clicked.connect(self.clear_display)
        self.btn_equals.clicked.connect(self.calculate_result)

        # 3. Inicializar la barra de estado
        self.statusBar().showMessage("Lista")

        # ✅ 3. Agregar botón de regreso
        self.crear_boton_regreso()

    def append_to_display(self, text):
        """Añade texto al display."""
        current_text = self.display.text()

        # Si hay un error, limpiar antes de escribir
        if current_text == "Error":
            current_text = ""

        self.display.setText(current_text + text)
        self.statusBar().showMessage("Escribiendo...")

    def clear_display(self):
        """Limpia el display."""
        self.display.clear()
        self.statusBar().showMessage("Lista")

    def calculate_result(self):
        """Evalúa la expresión en el display."""
        expression = self.display.text()

        if not expression:
            self.statusBar().showMessage("Nada que calcular")
            return

        try:
            # Usar eval() para calcular el resultado de la cadena
            # Nota: eval() es potente pero puede ser inseguro en apps
            # de producción si el usuario puede escribir. Aquí es seguro
            # porque solo usamos botones.
            result = str(eval(expression))
            self.display.setText(result)
            self.statusBar().showMessage(f"Resultado: {result}")

        except Exception as e:
            # Capturar errores (ej. División por cero, sintaxis mala)
            self.display.setText("Error")
            self.statusBar().showMessage(f"Error: {e}")

    # ✅ 5. Agregar los 3 métodos del checklist
    def actualizar_vista(self):
        """Actualiza la vista limpiando la calculadora"""
        self.clear_display()
        self.statusBar().showMessage("Calculadora actualizada")

    def crear_boton_regreso(self):
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


# ------------------
# 2. BLOQUE PRINCIPAL
# ------------------
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    # Aplicar la hoja de estilos globalmente
    app.setStyleSheet(MY_STYLE_SHEET)

    window = CalculatorWindow()
    window.show()
    sys.exit(app.exec_())