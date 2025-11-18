from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from textwrap import dedent
from database.connection import get_connection
# <--- IMPORTANTE    # <--- IMPORTANTE
from report.pdf_utils import crear_pdf
def generar_factura_pdf(venta_id):
    print("Factura solicitada para venta:", venta_id)

    conn = get_connection()
    cursor = conn.cursor()

    # Consulta CORREGIDA con nombres exactos de tablas y columnas
    sql = dedent("""
        SELECT 
            v.codigo_venta,
            v.fecha,
            c.nombre AS cliente,
            p.nombre AS producto,
            dp.cantidad,
            p.valor_venta,
            (dp.cantidad * p.valor_venta) AS subtotal,  -- CALCULAR subtotal
            v.total_bruto,
            v.iva_total,
            v.total_neto
        FROM VENTA v
        JOIN CLIENTE c ON v.codigo_cliente = c.codigo_cliente        -- CORREGIDO
        JOIN DETALLEVENTAPRODUCTO dp ON dp.id_venta = v.id_venta     -- CORREGIDO
        JOIN PRODUCTO p ON p.codigo = dp.codigo_producto             -- CORREGIDO
        WHERE v.codigo_venta = :venta
    """)

    cursor.execute(sql, {"venta": venta_id})
    filas = cursor.fetchall()

    if not filas:
        raise Exception(f"No existe la venta con código {venta_id}")

    nombre_pdf = f"factura_{venta_id}.pdf"
    c = canvas.Canvas(nombre_pdf, pagesize=letter)

    # ENCABEZADO
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, 750, "FACTURA DE VENTA")

    # DATOS BÁSICOS
    c.setFont("Helvetica", 12)
    y = 710

    codigo_venta, fecha, cliente, _, _, _, _, total_bruto, iva_total, total_neto = filas[0]

    c.drawString(50, y, f"Factura N°: {codigo_venta}")
    y -= 20
    c.drawString(50, y, f"Fecha: {fecha.strftime('%d/%m/%Y')}")  # Formatear fecha
    y -= 20
    c.drawString(50, y, f"Cliente: {cliente}")
    y -= 40

    # Detalles de productos
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Producto")
    c.drawString(250, y, "Cantidad")
    c.drawString(330, y, "Precio Unit.")
    c.drawString(410, y, "Subtotal")
    y -= 20
    c.line(50, y, 550, y)
    y -= 20

    c.setFont("Helvetica", 12)

    for fila in filas:
        _, _, _, producto, cantidad, precio, subtotal, _, _, _ = fila

        c.drawString(50, y, producto[:30])  # Limitar longitud del nombre
        c.drawString(250, y, str(cantidad))
        c.drawString(330, y, f"${precio:,.2f}")
        c.drawString(410, y, f"${subtotal:,.2f}")
        y -= 20

        # Salto de página si es necesario
        if y < 100:
            c.showPage()
            y = 750
            c.setFont("Helvetica", 12)

    # Totales
    y -= 30
    c.setFont("Helvetica-Bold", 12)
    c.drawString(350, y, f"Bruto: ${total_bruto:,.2f}")
    y -= 20
    c.drawString(350, y, f"IVA: ${iva_total:,.2f}")
    y -= 20
    c.drawString(350, y, f"Total: ${total_neto:,.2f}")

    c.save()
    print(f"Factura generada con éxito: {nombre_pdf}")
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