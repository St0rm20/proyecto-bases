"""
Clase para la gestión de usuarios
Por: Juan David Ramirez Carmona y
Miguel Ángel Vargas Peláez
Fecha: 2025-11
Licencia: GPLv3
"""

from modelo_base import BaseModel
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class UsuarioData:
    """Representa un usuario (datos principales + rol)"""
    id_usuario: int
    nombre_usuario: str
    email: str
    contrasena: str
    id_rol: Optional[int] = None

    def __str__(self):
        return f"Usuario(id={self.id_usuario}, usuario='{self.nombre_usuario}')"

    def __repr__(self):
        return (f"UsuarioData(id_usuario={self.id_usuario!r}, "
                f"nombre_usuario={self.nombre_usuario!r}, "
                f"email={self.email!r})")


class Usuario(BaseModel):
    """Gestión de usuarios"""

    def get_table_name(self):
        return "Usuario"

    def get_primary_key(self):
        return "id_usuario"

    # ---------------------------------------------------------
    # CREAR
    # ---------------------------------------------------------
    def crear(self, id_usuario: int, nombre_usuario: str, email: str,
              contrasena: str, id_rol: int = None) -> bool:
        """Crea un nuevo usuario"""
        print(f"Creando usuario: {nombre_usuario} con rol {id_rol}" 
              f"(id_usuario={id_usuario})")
        if id_rol == 1:  # 1 = administrador
            if self._existe_administrador():
                print("Error: Ya existe un administrador en el sistema")
                return False


        sql = """
            INSERT INTO Usuario (id_usuario, nombre_usuario, email, contrasena, id_rol)
            VALUES (:id_usuario, :nombre_usuario, :email, :contrasena, :id_rol)
        """
        try:
            self.db.execute_query(sql, {
                'id_usuario': id_usuario,
                'nombre_usuario': nombre_usuario,
                'email': email,
                'contrasena': contrasena,
                'id_rol': id_rol
            }, fetch=False)
            return True
        except Exception as e:
            print(f"Error al crear usuario: {e}")
            return False

    def _existe_administrador(self) -> bool:
        """Verifica si ya existe un administrador en la base de datos"""

        # Asumiendo que id_rol = 1 representa el rol de administrador
        sql = "SELECT COUNT(*) FROM Usuario WHERE id_rol = 1"

        try:
            resultado = self.db.execute_query(sql)
            # resultado será una lista de tuplas, ej: [(1,)]
            count = resultado[0][0] if resultado else 0
            return count > 0
        except Exception as e:
            print(f"Error al verificar administradores: {e}")
            return True  # Por seguridad, si hay error, no permitir crear
    # ---------------------------------------------------------
    # ACTUALIZAR
    # ---------------------------------------------------------
    def actualizar(self, id_usuario: int, nombre_usuario: str = None,
                   email: str = None, contrasena: str = None,
                   id_rol: int = None) -> bool:
        """Actualiza un usuario existente (solo los campos proporcionados)"""

        campos = []
        params = {'id_usuario': id_usuario}

        if nombre_usuario is not None:
            campos.append("nombre_usuario = :nombre_usuario")
            params['nombre_usuario'] = nombre_usuario

        if email is not None:
            campos.append("email = :email")
            params['email'] = email

        if contrasena is not None:
            campos.append("contrasena = :contrasena")
            params['contrasena'] = contrasena

        if id_rol is not None:
            campos.append("id_rol = :id_rol")
            params['id_rol'] = id_rol

        if not campos:
            return False

        sql = f"UPDATE Usuario SET {', '.join(campos)} WHERE id_usuario = :id_usuario"

        try:
            filas = self.db.execute_query(sql, params, fetch=False)
            return filas > 0
        except Exception as e:
            print(f"Error al actualizar usuario: {e}")
            return False

    # ---------------------------------------------------------
    # OBTENER TODOS COMO OBJETOS
    # ---------------------------------------------------------
    def obtener_todos_como_objetos(self) -> List[UsuarioData]:
        """Obtiene todos los usuarios como objetos"""
        resultados = self.obtener_todos()
        return [UsuarioData(*r) for r in resultados]

    # ---------------------------------------------------------
    # BÚSQUEDAS
    # ---------------------------------------------------------
    def buscar_por_nombre(self, nombre_usuario: str) -> List[UsuarioData]:
        """Busca usuarios por nombre"""
        sql = "SELECT * FROM Usuario WHERE UPPER(nombre_usuario) LIKE UPPER(:nombre)"
        resultados = self.db.execute_query(sql, {'nombre': f'%{nombre_usuario}%'})
        return [UsuarioData(*r) for r in resultados]

    def buscar_por_email(self, email: str) -> Optional[UsuarioData]:
        """Busca usuario por email exacto"""
        sql = "SELECT * FROM Usuario WHERE UPPER(email) = UPPER(:email)"
        resultado = self.db.execute_query(sql, {'email': email})
        return UsuarioData(*resultado[0]) if resultado else None


    # ---------------------------------------------------------
    # ELIMINAR
    # ---------------------------------------------------------
    def eliminar(self, id_usuario):
        """Elimina un usuario por ID"""
        sql = "DELETE FROM Usuario WHERE id_usuario = :id_usuario"
        try:
            filas = self.db.execute_query(sql, {'id_usuario': id_usuario}, fetch=False)
            return filas > 0
        except Exception as e:
            print(f"Error al eliminar usuario: {e}")
            return False

    # ---------------------------------------------------------
    # OBTENER POR ID
    # ---------------------------------------------------------

    def obtener_por_id(self, id_usuario: int) -> Optional[UsuarioData]:
        """Obtiene un usuario por ID como objeto UsuarioData"""
        sql = "SELECT * FROM Usuario WHERE id_usuario = :id_usuario"
        resultado = self.db.execute_query(sql, {'id_usuario': id_usuario})
        return UsuarioData(*resultado[0]) if resultado else None

