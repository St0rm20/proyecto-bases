import tkinter as tk
from tkinter import messagebox
from database.connection import DatabaseConnection
from view.login import LoginWindow


class MainApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistema de Gestión de Electrodomésticos")
        self.root.geometry("1200x700")
        self.db_connection = None
        self.current_user = None

    def initialize_database(self):
        """Inicializar conexión a la base de datos"""
        self.db_connection = DatabaseConnection()
        if not self.db_connection.connect():
            messagebox.showerror("Error", "No se pudo conectar a la base de datos")
            return False
        return True

    def run(self):
        """Ejecutar la aplicación"""
        if not self.initialize_database():
            return

        # Mostrar ventana de login
        login_window = LoginWindow(self.root, self.db_connection, self)
        login_window.show()

        self.root.mainloop()

    def show_main_window(self, user_data):
        """Mostrar ventana principal después del login exitoso"""
        self.current_user = user_data
        from view.main_view import MainWindow
        MainWindow(self.root, self.db_connection, user_data)


if __name__ == "__main__":
    app = MainApp()
    app.run()