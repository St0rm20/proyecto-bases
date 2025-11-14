"""
Clase para la gestión de clientes
Por: Juan David Ramirez Carmona y
Miguel Ángel Vargas Peláez
Fecha: 2025-11
Licencia: GPLv3
"""

from modelo_base import BaseModel
from dataclasses import dataclass
from typing import Optional, List


# Importaciones para manejo seguro de contraseñas
"""
Werkzeug es una biblioteca de utilidades para aplicaciones web en Python.
Dentro de sus muchas funcionalidades, incluye herramientas para manejar
la seguridad de las contraseñas, como el hashing y la verificación."""
from werkzeug.security import generate_password_hash, check_password_hash



"""
La anotación @dataclass se utiliza para simplificar la creación de clases
que principalmente almacenan datos. Proporciona automáticamente métodos
como __init__(), __repr__(), __eq__(), entre otros, basados en los
atributos definidos en la clase.

init = constructor
repr = toString
eq = equals
"""
@dataclass
class ClienteData:
    """Representa un cliente"""
    codigo_cliente: int
    nombre: str
    telefono: Optional[str] = None
    departamento: Optional[str] = None
    municipio: Optional[str] = None
    calle: Optional[str] = None
    direccion: Optional[str] = None
    email: Optional[str] = None
    contrasena: Optional[str] = None
    id_rol: Optional[int] = None

    def __str__(self):
        return f"Cliente(codigo={self.codigo_cliente}, nombre='{self.nombre}', email='{self.email}')"

    def __repr__(self):
        # ¡Importante! Nunca mostrar la contraseña en los logs o repr
        return f"ClienteData(codigo_cliente={self.codigo_cliente!r}, nombre={self.nombre!r}, email={self.email!r}, ...)"


class Cliente(BaseModel):
    """Gestión de clientes"""

    def get_table_name(self):
        return "Cliente"

    def get_primary_key(self):
        return "codigo_cliente"

    def crear(self, codigo_cliente: int, nombre: str, telefono: str = None,
              departamento: str = None, municipio: str = None, calle: str = None,
              direccion: str = None, email: str = None, contrasena: str = None,
              id_rol: int = None) -> bool:
        """Crea un nuevo cliente"""

        # --- MODIFICADO: HASHING DE CONTRASEÑA ---
        hash_contrasena = None
        if contrasena:
            # Genera un hash seguro para la contraseña
            hash_contrasena = generate_password_hash(contrasena)
        # --------------------------------------------

        sql = """
            INSERT INTO Cliente (codigo_cliente, nombre, telefono, departamento, 
                                municipio, calle, direccion, email, contrasena, id_rol)
            VALUES (:codigo_cliente, :nombre, :telefono, :departamento, 
                    :municipio, :calle, :direccion, :email, :contrasena, :id_rol)
        """
        try:
            self.db.execute_query(sql, {
                'codigo_cliente': codigo_cliente,
                'nombre': nombre,
                'telefono': telefono,
                'departamento': departamento,
                'municipio': municipio,
                'calle': calle,
                'direccion': direccion,
                'email': email,
                'contrasena': hash_contrasena,
                'id_rol': id_rol
            }, fetch=False)
            return True
        except Exception as e:
            print(f"Error al crear cliente: {e}")
            return False

    def actualizar(self, codigo_cliente: int, nombre: str = None, telefono: str = None,
                   departamento: str = None, municipio: str = None, calle: str = None,
                   direccion: str = None, email: str = None, contrasena: str = None,
                   id_rol: int = None) -> bool:
        """Actualiza un cliente existente (solo los campos proporcionados)"""
        campos = []
        params = {'codigo_cliente': codigo_cliente}

        if nombre is not None:
            campos.append("nombre = :nombre")
            params['nombre'] = nombre
        if telefono is not None:
            campos.append("telefono = :telefono")
            params['telefono'] = telefono
        if departamento is not None:
            campos.append("departamento = :departamento")
            params['departamento'] = departamento
        if municipio is not None:
            campos.append("municipio = :municipio")
            params['municipio'] = municipio
        if calle is not None:
            campos.append("calle = :calle")
            params['calle'] = calle
        if direccion is not None:
            campos.append("direccion = :direccion")
            params['direccion'] = direccion
        if email is not None:
            campos.append("email = :email")
            params['email'] = email

        # --- BLOQUE AÑADIDO: ACTUALIZAR CONTRASEÑA ---
        if contrasena is not None:
            # Si se provee una nueva contraseña, generar un nuevo hash
            campos.append("contrasena = :contrasena")
            params['contrasena'] = generate_password_hash(contrasena)
        # ----------------------------------------------

        if id_rol is not None:
            campos.append("id_rol = :id_rol")
            params['id_rol'] = id_rol

        if not campos:
            return False

        sql = f"UPDATE Cliente SET {', '.join(campos)} WHERE codigo_cliente = :codigo_cliente"

        try:
            filas = self.db.execute_query(sql, params, fetch=False)
            return filas > 0
        except Exception as e:
            print(f"Error al actualizar cliente: {e}")
            return False

    def obtener_todos_como_objetos(self) -> List[ClienteData]:
        """Obtiene todos los clientes como objetos"""
        resultados = self.obtener_todos()
        # El *r expandirá todos los campos de la BD, incluyendo 'contrasena'
        return [ClienteData(*r) for r in resultados]

    def buscar_por_nombre(self, nombre: str) -> List[ClienteData]:
        """Busca clientes por nombre"""
        sql = "SELECT * FROM Cliente WHERE UPPER(nombre) LIKE UPPER(:nombre)"
        resultados = self.db.execute_query(sql, {'nombre': f'%{nombre}%'})
        return [ClienteData(*r) for r in resultados]

    def buscar_por_municipio(self, municipio: str) -> List[ClienteData]:
        """Busca clientes por municipio"""
        sql = "SELECT * FROM Cliente WHERE UPPER(municipio) = UPPER(:municipio)"
        resultados = self.db.execute_query(sql, {'municipio': municipio})
        return [ClienteData(*r) for r in resultados]

    def buscar_por_email(self, email: str) -> Optional[ClienteData]:
        """Busca un cliente por email"""
        sql = "SELECT * FROM Cliente WHERE UPPER(email) = UPPER(:email)"
        resultado = self.db.execute_query(sql, {'email': email})
        return ClienteData(*resultado[0]) if resultado else None

    # --- MÉTODO ESENCIAL AÑADIDO PARA LOGIN ---
    def verificar_contrasena(self, email: str, contrasena_ingresada: str) -> bool:
        """
        Verifica si la contraseña ingresada por el usuario coincide con el
        hash almacenado en la base de datos.
        """
        # 1. Buscar al cliente por su email
        cliente = self.buscar_por_email(email)

        if not cliente:
            return False # Usuario no existe

        if not cliente.contrasena:
            return False # Usuario no tiene una contraseña registrada

        # 2. Comparar la contraseña ingresada con el hash de la BD
        #    check_password_hash se encarga de todo el proceso de forma segura.
        return check_password_hash(cliente.contrasena, contrasena_ingresada)
    # -------------------------------------------