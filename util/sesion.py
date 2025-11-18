"""
Clase para la gestión del login y sesión de usuario
Por: Juan David Ramirez Carmona y
Miguel Ángel Vargas Peláez
Fecha: 2025-11
Licencia: GPLv3
"""

"""
Lit es un singleton que almacena el ID del usuario logueado
No modificar 
"""

_usuario_id = None


def get_usuario_entidad(id_usuario: int):
    """Obtiene la entidad UsuarioData del usuario logueado."""
    from model.usuario import Usuario, UsuarioData

    usuario_model = Usuario()
    return usuario_model.obtener_por_id(id_usuario)



def get_usuario_rol(id_usuario: int) -> int | None:
    """Obtiene el rol del usuario logueado."""
    usuario_data = get_usuario_entidad(id_usuario)
    if usuario_data:
        return usuario_data.id_rol
    return None

def get_usuario_nombre(id_usuario: int) -> str | None:
    """Obtiene el nombre del usuario logueado."""
    usuario_data = get_usuario_entidad(id_usuario)
    if usuario_data:
        return usuario_data.nombre_usuario
    return None

def set_usuario_id(id_usuario: int):
    """Guarda el ID del usuario logueado."""
    global _usuario_id
    if isinstance(id_usuario, int):
        _usuario_id = id_usuario
        print(f"ID de usuario guardado: {_usuario_id}")
    else:
        print("Error: El ID debe ser un número entero.")

def get_usuario_id() -> int | None:
    """Obtiene el ID del usuario actual."""
    return _usuario_id

def logout():
    """Limpia el ID de usuario."""
    global _usuario_id
    print(f"Cerrando sesión del ID: {_usuario_id}")
    _usuario_id = None

def is_logged_in() -> bool:
    """Verifica si hay un ID guardado."""
    return _usuario_id is not None