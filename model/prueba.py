"""
Ejemplos de uso del sistema de gestión de base de datos
"""

from rol import Rol
from cliente import Cliente
from producto import Producto
from venta import Venta
from datetime import date


def ejemplo_roles():

    print("\n=== GESTIÓN DE ROLES ===")

    rol = Rol()

    # Crear roles
    print("Creando roles...")
    rol.crear(3, "Usuario Esporadico")




def ejemplo_clientes():
    """Ejemplos de operaciones con Clientes"""
    print("\n=== GESTIÓN DE CLIENTES ===")

    cliente = Cliente()

    # Crear cliente
    print("Creando cliente...")
    cliente.crear(
        codigo_cliente=1001,
        nombre="Juan Pérez",
        telefono="3001234567",
        departamento="Quindío",
        municipio="Armenia",
        direccion="Calle 15 # 20-30",
        email="juan.perez@email.com",
        contrasena="segura123",
        id_rol=2
    )

    # Obtener cliente por ID
    print("\nBuscando cliente por ID:")
    cli = cliente.obtener_por_id(1001)
    if cli:
        print(f"  Encontrado: {cli}")



def ejemplo_productos():
    """Ejemplos de operaciones con Productos"""
    print("\n=== GESTIÓN DE PRODUCTOS ===")

    producto = Producto()

    # Crear productos
    print("Creando productos...")
    producto.crear(
        codigo=101,
        nombre="Televisor Samsung 55\"",
        descripcion="Smart TV 4K Ultra HD",
        valor_adquisicion=1200000,
        valor_venta=1800000,
        codigo_categoria=1
    )

    producto.crear(
        codigo=102,
        nombre="Nevera LG 420L",
        descripcion="Refrigerador No Frost",
        valor_adquisicion=1500000,
        valor_venta=2200000,
        codigo_categoria=1
    )

    # Buscar por nombre
    print("\nBuscando productos con 'Samsung':")
    samsung = producto.buscar_por_nombre("Samsung")
    for p in samsung:
        print(f"  {p}")

    # Buscar por rango de precio
    print("\nProductos entre $1.500.000 y $2.000.000:")
    rango = producto.buscar_por_rango_precio(1500000, 2000000)
    for p in rango:
        print(f"  {p}")

    # Actualizar precio
    print("\nActualizando precio del TV...")
    producto.actualizar(101, valor_venta=1750000)


def ejemplo_ventas():
    """Ejemplos de operaciones con Ventas"""
    print("\n=== GESTIÓN DE VENTAS ===")

    venta = Venta()

    # Crear venta
    print("Creando venta...")
    venta.crear(
        id_venta=5001,
        codigo_venta="VTA-2025-001",
        estado_venta="Completada",
        fecha=date.today(),
        tipo_venta="Contado",
        codigo_cliente=1001,
        total_bruto=1800000,
        iva_total=342000,
        total_neto=2142000
    )

    # Agregar productos a la venta
    print("Agregando productos a la venta...")
    venta.agregar_producto(5001, 101)

    # Buscar ventas por cliente
    print("\nVentas del cliente 1001:")
    ventas_cliente = venta.buscar_por_cliente(1001)
    for v in ventas_cliente:
        print(f"  {v}")

    # Obtener productos de la venta
    print("\nProductos en la venta 5001:")
    productos = venta.obtener_productos(5001)
    print(f"  Códigos de productos: {productos}")

    # Actualizar estado
    print("\nActualizando estado de venta...")
    venta.actualizar_estado(5001, "Entregada")

    # Buscar por fecha
    print("\nVentas de hoy:")
    ventas_hoy = venta.buscar_por_fecha(date.today(), date.today())
    for v in ventas_hoy:
        print(f"  {v}")


def menu_principal():
    """Menú interactivo simple"""
    while True:
        print("\n" + "=" * 50)
        print("SISTEMA DE GESTIÓN")
        print("=" * 50)
        print("1. Ejemplos de Roles")
        print("2. Ejemplos de Clientes")
        print("3. Ejemplos de Productos")
        print("4. Ejemplos de Ventas")
        print("0. Salir")
        print("=" * 50)

        opcion = input("\nSeleccione una opción: ")

        try:
            if opcion == "1":
                ejemplo_roles()
            elif opcion == "2":
                ejemplo_clientes()
            elif opcion == "3":
                ejemplo_productos()
            elif opcion == "4":
                ejemplo_ventas()
            elif opcion == "0":
                print("\n¡Hasta luego!")
                break
            else:
                print("Opción inválida")
        except Exception as e:
            print(f"\n❌ Error: {e}")


def ejemplo_categoria():
    print("\nEjemplos de Categorias")


if __name__ == "__main__":
    try:
        ejemplo_roles()
        #ejemplo_clientes()
        #ejemplo_productos()
        #ejemplo_ventas()
    except Exception as e:
        print(f"Error ejecutando ejemplos: {e}")

