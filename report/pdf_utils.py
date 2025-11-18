import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from datetime import datetime

def crear_pdf(nombre_archivo, titulo, headers, filas):
    # Definir la ruta de la carpeta de reportes
    carpeta_reportes = "c://sgp/reportes"

    # Crear la carpeta si no existe
    if not os.path.exists(carpeta_reportes):
        os.makedirs(carpeta_reportes)

    # Ruta completa del archivo
    ruta_completa = os.path.join(carpeta_reportes, nombre_archivo)

    c = canvas.Canvas(ruta_completa, pagesize=letter)

    # Título
    c.setFont("Helvetica-Bold", 18)
    c.drawString(180, 750, titulo)

    # Fecha de generación
    c.setFont("Helvetica", 10)
    fecha_generacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.drawString(50, 730, f"Generado el: {fecha_generacion}")

    y = 700

    # Encabezados
    c.setFont("Helvetica-Bold", 12)
    for i, h in enumerate(headers):
        c.drawString(50 + i * 150, y, str(h))
    y -= 20
    c.line(50, y, 550, y)
    y -= 20

    # Filas
    c.setFont("Helvetica", 11)
    for fila in filas:
        for i, col in enumerate(fila):
            c.drawString(50 + i * 150, y, str(col))
        y -= 20

        if y < 80:
            c.showPage()
            y = 700
            c.setFont("Helvetica-Bold", 12)
            for i, h in enumerate(headers):
                c.drawString(50 + i * 150, y, str(h))
            y -= 40
            c.setFont("Helvetica", 11)

    c.save()
    return ruta_completa