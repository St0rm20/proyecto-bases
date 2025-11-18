from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from textwrap import dedent
from database.connection import get_connection
from report.pdf_utils import crear_pdf
def generar_factura_pdf(venta_id):
    """
    Genera una factura en PDF para una venta específica usando crear_pdf()
    """
    print("Factura solicitada para venta:", venta_id)

    conn = get_connection()
    cursor = conn.cursor()

    # Consulta para obtener datos generales de la venta
    sql_venta = dedent("""
        SELECT 
            v.codigo_venta,
            v.fecha,
            c.nombre AS cliente,
            c.telefono,
            c.direccion,
            v.total_bruto,
            v.iva_total,
            v.total_neto
        FROM VENTA v
        JOIN CLIENTE c ON v.codigo_cliente = c.codigo_cliente
        WHERE v.codigo_venta = :venta
    """)

    cursor.execute(sql_venta, {"venta": venta_id})
    datos_venta = cursor.fetchone()

    if not datos_venta:
        raise Exception(f"No existe la venta con código {venta_id}")

    # Consulta para obtener los productos de la venta
    sql_productos = dedent("""
        SELECT 
            p.nombre AS producto,
            dp.cantidad,
            p.valor_venta,
            (dp.cantidad * p.valor_venta) AS subtotal
        FROM DETALLEVENTAPRODUCTO dp
        JOIN PRODUCTO p ON p.codigo = dp.codigo_producto
        JOIN VENTA v ON dp.id_venta = v.id_venta
        WHERE v.codigo_venta = :venta
        ORDER BY p.nombre
    """)

    cursor.execute(sql_productos, {"venta": venta_id})
    productos = cursor.fetchall()

    cursor.close()
    conn.close()

    # Desempaquetar datos de la venta
    codigo_venta, fecha, cliente, telefono, direccion, total_bruto, iva_total, total_neto = datos_venta

    # Preparar datos para el PDF
    nombre_pdf = f"factura_{venta_id}.pdf"
    titulo = "FACTURA DE VENTA"

    # Encabezado con información de la venta
    info_venta = [
        ("Factura N°:", codigo_venta),
        ("Fecha:", fecha.strftime('%d/%m/%Y')),
        ("Cliente:", cliente),
        ("Teléfono:", telefono or "No registrado"),
        ("Dirección:", direccion or "No registrada"),
    ]

    # Headers de la tabla de productos
    headers = ["Producto", "Cantidad", "Precio Unit.", "Subtotal"]

    # Formatear productos para la tabla
    filas_productos = []
    for producto, cantidad, precio, subtotal in productos:
        filas_productos.append([
            producto[:40],  # Limitar nombre del producto
            str(cantidad),
            f"${precio:,.2f}",
            f"${subtotal:,.2f}"
        ])

    # Agregar fila de totales
    filas_productos.append(["", "", "", ""])  # Fila vacía para separar
    filas_productos.append(["", "", "Subtotal:", f"${total_bruto:,.2f}"])
    filas_productos.append(["", "", "IVA:", f"${iva_total:,.2f}"])
    filas_productos.append(["", "", "TOTAL:", f"${total_neto:,.2f}"])

    # Crear el PDF usando la función crear_pdf
    crear_pdf(
        nombre_pdf,
        titulo,
        headers,
        filas_productos  # Pasar información de la venta como info adicional
    )

    print(f"✅ Factura generada con éxito: {nombre_pdf}")
    return nombre_pdf

def reporte_total_ventas_mes(anio, mes):
    conn = get_connection()
    c = conn.cursor()

    sql = """
        SELECT fecha, total_neto, cliente 
        FROM venta
        WHERE fecha BETWEEN
              TO_DATE(:anio || '-' || :mes || '-01','YYYY-MM-DD')
        AND LAST_DAY(TO_DATE(:anio || '-' || :mes || '-01','YYYY-MM-DD'))
    """

    c.execute(sql, {"anio": anio, "mes": mes})
    filas = c.fetchall()

    total = sum(f[1] for f in filas)

    headers = ["Fecha", "Total Neto", "Cliente"]
    pdf_name = f"reporte_ventas_mes_{anio}_{mes}.pdf"

    crear_pdf(pdf_name, f"Ventas del Mes {anio}-{mes}", headers, filas + [("TOTAL", total, "")])

    return pdf_name

# -------------------------------
# REPORTE 3: IVA POR TRIMESTRE
# -------------------------------
def reporte_iva_trimestre(anio, trimestre):
    conn = get_connection()
    c = conn.cursor()

    sql = """
        SELECT codigo_venta, fecha, iva_total
        FROM venta
        WHERE EXTRACT(YEAR FROM fecha) = :anio
          AND CEIL(EXTRACT(MONTH FROM fecha)/3) = :trimestre
    """

    c.execute(sql, {"anio": anio, "trimestre": trimestre})
    filas = c.fetchall()

    total = sum(f[2] for f in filas)

    headers = ["Venta", "Fecha", "IVA"]
    pdf_name = f"reporte_iva_Q{trimestre}_{anio}.pdf"

    crear_pdf(pdf_name, f"IVA Trimestre Q{trimestre} {anio}", headers, filas + [("TOTAL", "", total)])

    return pdf_name

# -------------------------------
# REPORTE 4: VENTAS POR TIPO
# -------------------------------
def reporte_ventas_por_tipo(fecha_inicio, fecha_fin):
    conn = get_connection()
    c = conn.cursor()

    sql = """
        SELECT tipo_venta, COUNT(*)
        FROM venta
        WHERE fecha BETWEEN TO_DATE(:fi,'YYYY-MM-DD')
        AND TO_DATE(:ff,'YYYY-MM-DD')
        GROUP BY tipo_venta
    """

    c.execute(sql, {"fi": fecha_inicio, "ff": fecha_fin})
    filas = c.fetchall()

    headers = ["Tipo Venta", "Cantidad"]
    pdf_name = f"reporte_ventas_tipo_{fecha_inicio}_{fecha_fin}.pdf"

    crear_pdf(pdf_name, f"Ventas por Tipo", headers, filas)

    return pdf_name

def reporte_inventario_por_categoria():
    conn = get_connection()
    c = conn.cursor()

    sql = """
        SELECT p.codigo,
               p.nombre,
               p.codigo_categoria,
               p.valor_adquisicion,
               p.valor_venta
        FROM Producto p
        ORDER BY p.codigo_categoria, p.nombre
    """

    c.execute(sql)
    filas = c.fetchall()

    headers = ["Código", "Producto", "Categoría", "Adquisición", "Venta"]
    pdf_name = "reporte_inventario.pdf"

    crear_pdf(pdf_name, "Inventario de Productos por Categoría", headers, filas)

    return pdf_name

# -------------------------------
# REPORTE 6: CLIENTES MOROSOS
# -------------------------------
def reporte_clientes_morosos():
    conn = get_connection()
    c = conn.cursor()

    sql = """
        SELECT cl.nombre, v.codigo_venta, cu.codigo_cuota,
               cu.fecha_vencimiento_cuota, cu.estado_cuota
        FROM cliente cl
        JOIN venta v ON v.cliente = cl.codigo_cliente
        JOIN credito cr ON cr.venta = v.codigo_venta
        JOIN cuota cu ON cu.credito = cr.credito_id
        WHERE cu.estado_cuota IN ('VENCIDA', 'PENDIENTE')
        ORDER BY cl.nombre
    """

    c.execute(sql)
    filas = c.fetchall()

    headers = ["Cliente", "Venta", "Cuota", "Vencimiento", "Estado"]
    pdf_name = "reporte_morosos.pdf"

    crear_pdf(pdf_name, "Clientes Morosos", headers, filas)

    return pdf_name