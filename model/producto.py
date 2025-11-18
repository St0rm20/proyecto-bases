"""
Clase para la gestión de productos
Por: Juan David Ramirez Carmona y
Miguel Ángel Vargas Peláez
Fecha: 2025-11
Licencia: GPLv3
"""
from modelo_base import BaseModel
from dataclasses import dataclass
from typing import Optional, List
from decimal import Decimal


@dataclass
class ProductoData:
    """Representa un producto"""
    codigo: int
    descripcion: Optional[str]
    nombre: str
    valor_adquisicion: Decimal
    valor_venta: Optional[Decimal]
    codigo_categoria: int
    cantidad: int

    def __str__(self):
        return (f"Producto(codigo={self.codigo}, nombre='{self.nombre}', "
                f"precio=${self.valor_venta}, cant={self.cantidad})")


class Producto(BaseModel):
    """Gestión de productos"""

    def get_table_name(self):
        return "Producto"

    def get_primary_key(self):
        return "codigo"

    def crear(self, codigo: int, nombre: str, valor_adquisicion: float,
              codigo_categoria: int, descripcion: str = None,
              valor_venta: float = None, cantidad: int = 0) -> bool:
        """Crea un nuevo producto"""
        sql = """
            INSERT INTO Producto (codigo, descripcion, nombre, valor_adquisicion, 
                                 valor_venta, codigo_categoria, cantidad)
            VALUES (:codigo, :descripcion, :nombre, :valor_adquisicion, 
                    :valor_venta, :codigo_categoria, :cantidad)
        """
        try:
            self.db.execute_query(sql, {
                'codigo': codigo,
                'descripcion': descripcion,
                'nombre': nombre,
                'valor_adquisicion': valor_adquisicion,
                'valor_venta': valor_venta,
                'codigo_categoria': codigo_categoria,
                'cantidad': cantidad
            }, fetch=False)
            return True
        except Exception as e:
            print(f"Error al crear producto: {e}")
            return False

    def actualizar(self, codigo: int, nombre: str = None, descripcion: str = None,
                   valor_adquisicion: float = None, valor_venta: float = None,
                   codigo_categoria: int = None, cantidad: int = None) -> bool:  # ← AÑADIDO cantidad
        """Actualiza un producto existente"""
        campos = []
        params = {'codigo': codigo}

        if nombre is not None:
            campos.append("nombre = :nombre")
            params['nombre'] = nombre
        if descripcion is not None:
            campos.append("descripcion = :descripcion")
            params['descripcion'] = descripcion
        if valor_adquisicion is not None:
            campos.append("valor_adquisicion = :valor_adquisicion")
            params['valor_adquisicion'] = valor_adquisicion
        if valor_venta is not None:
            campos.append("valor_venta = :valor_venta")
            params['valor_venta'] = valor_venta
        if codigo_categoria is not None:
            campos.append("codigo_categoria = :codigo_categoria")
            params['codigo_categoria'] = codigo_categoria
        if cantidad is not None:  # ← AÑADIDO: manejo del parámetro cantidad
            campos.append("cantidad = :cantidad")
            params['cantidad'] = cantidad

        if not campos:
            return False

        sql = f"UPDATE Producto SET {', '.join(campos)} WHERE codigo = :codigo"

        try:
            filas = self.db.execute_query(sql, params, fetch=False)
            return filas > 0
        except Exception as e:
            print(f"Error al actualizar producto: {e}")
            return False

    def obtener_todos_como_objetos(self) -> List[ProductoData]:
        """Obtiene todos los productos como objetos"""
        resultados = self.obtener_todos()
        # Si hay problemas con el orden de las columnas, usa mapeo explícito:
        productos = []
        for r in resultados:
            producto = ProductoData(
                codigo=r[0],
                descripcion=r[1],
                nombre=r[2],
                valor_adquisicion=r[3],
                valor_venta=r[4],
                codigo_categoria=r[5],
                cantidad=r[6] if len(r) > 6 else 0  # ← Maneja el caso donde pueda faltar la columna
            )
            productos.append(producto)
        return productos

    def buscar_por_nombre(self, nombre: str) -> List[ProductoData]:
        """Busca productos por nombre"""
        sql = "SELECT * FROM Producto WHERE UPPER(nombre) LIKE UPPER(:nombre)"
        resultados = self.db.execute_query(sql, {'nombre': f'%{nombre}%'})
        return [ProductoData(
            codigo=r[0],
            descripcion=r[1],
            nombre=r[2],
            valor_adquisicion=r[3],
            valor_venta=r[4],
            codigo_categoria=r[5],
            cantidad=r[6] if len(r) > 6 else 0
        ) for r in resultados]

    def buscar_por_categoria(self, codigo_categoria: int) -> List[ProductoData]:
        """Obtiene todos los productos de una categoría"""
        sql = "SELECT * FROM Producto WHERE codigo_categoria = :categoria"
        resultados = self.db.execute_query(sql, {'categoria': codigo_categoria})
        return [ProductoData(
            codigo=r[0],
            descripcion=r[1],
            nombre=r[2],
            valor_adquisicion=r[3],
            valor_venta=r[4],
            codigo_categoria=r[5],
            cantidad=r[6] if len(r) > 6 else 0
        ) for r in resultados]

    def buscar_por_rango_precio(self, precio_min: float, precio_max: float) -> List[ProductoData]:
        """Busca productos en un rango de precios"""
        sql = """
            SELECT * FROM Producto 
            WHERE valor_venta BETWEEN :precio_min AND :precio_max
            ORDER BY valor_venta
        """
        resultados = self.db.execute_query(sql, {
            'precio_min': precio_min,
            'precio_max': precio_max
        })
        return [ProductoData(
            codigo=r[0],
            descripcion=r[1],
            nombre=r[2],
            valor_adquisicion=r[3],
            valor_venta=r[4],
            codigo_categoria=r[5],
            cantidad=r[6] if len(r) > 6 else 0
        ) for r in resultados]

    def obtener_por_id(self, codigo: int) -> Optional[ProductoData]:
        """Obtiene un producto por su código"""
        sql = "SELECT * FROM Producto WHERE codigo = :codigo"
        resultados = self.db.execute_query(sql, {'codigo': codigo})
        if resultados:
            r = resultados[0]
            return ProductoData(
                codigo=r[0],
                descripcion=r[1],
                nombre=r[2],
                valor_adquisicion=r[3],
                valor_venta=r[4],
                codigo_categoria=r[5],
                cantidad=r[6] if len(r) > 6 else 0
            )
        return None