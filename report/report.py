from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import os


class ReportesVentas:
    def __init__(self, db_connection):
        self.db = db_connection

    def generar_reporte_ventas_mes(self):
        # Ventana para seleccionar mes y año
        self.ventana_seleccion("Ventas por Mes", self._generar_reporte_ventas_mes)

    def _generar_reporte_ventas_mes(self, mes, año):
        try:
            filename = f"reporte_ventas_{mes}_{año}.pdf"
            doc = SimpleDocTemplate(filename, pagesize=A4)
            elements = []

            styles = getSampleStyleSheet()

            # Título
            title = Paragraph(f"Reporte de Ventas - {mes}/{año}", styles['Title'])
            elements.append(title)
            elements.append(Spacer(1, 0.2 * inch))

            # Obtener datos
            query = """
            SELECT v.id_venta, c.nombres || ' ' || c.apellidos as cliente,
                   v.fecha_venta, v.subtotal, v.iva_total, v.total, tv.nombre as tipo_venta
            FROM venta v
            JOIN cliente c ON v.id_cliente = c.id_cliente
            JOIN tipo_venta tv ON v.id_tipo_venta = tv.id_tipo_venta
            WHERE EXTRACT(MONTH FROM v.fecha_venta) = :mes
            AND EXTRACT(YEAR FROM v.fecha_venta) = :año
            ORDER BY v.fecha_venta
            """
            datos = self.db.execute_query(query, {'mes': mes, 'año': año})

            # Encabezados de tabla
            data = [['ID', 'Cliente', 'Fecha', 'Subtotal', 'IVA', 'Total', 'Tipo']]

            total_ventas = 0
            total_iva = 0

            for venta in datos:
                data.append([
                    str(venta[0]),
                    venta[1],
                    venta[2].strftime('%d/%m/%Y'),
                    f"${venta[3]:,.2f}",
                    f"${venta[4]:,.2f}",
                    f"${venta[5]:,.2f}",
                    venta[6]
                ])
                total_ventas += venta[5]
                total_iva += venta[4]

            # Totales
            data.append(['', '', '', '', '', '', ''])
            data.append(['', '', 'TOTALES:', '', f"${total_iva:,.2f}", f"${total_ventas:,.2f}", ''])

            # Crear tabla
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -3), colors.beige),
                ('FONTNAME', (0, -2), (-1, -1), 'Helvetica-Bold'),
                ('BACKGROUND', (0, -2), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            elements.append(table)
            doc.build(elements)

            messagebox.showinfo("Éxito", f"Reporte generado: {filename}")
            os.startfile(filename)  # Abrir el PDF automáticamente

        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {str(e)}")

    def generar_reporte_inventario(self):
        try:
            filename = "reporte_inventario.pdf"
            doc = SimpleDocTemplate(filename, pagesize=A4)
            elements = []

            styles = getSampleStyleSheet()

            title = Paragraph("Reporte de Inventario por Categoría", styles['Title'])
            elements.append(title)
            elements.append(Spacer(1, 0.2 * inch))

            query = """
            SELECT c.nombre as categoria, COUNT(p.id_producto) as cantidad,
                   SUM(p.stock) as total_stock, 
                   SUM(p.stock * p.valor_adquisicion) as costo_total
            FROM categoria c
            JOIN producto p ON c.id_categoria = p.id_categoria
            WHERE p.estado = 'A'
            GROUP BY c.nombre
            ORDER BY c.nombre
            """
            datos = self.db.execute_query(query)

            data = [['Categoría', 'Productos', 'Stock Total', 'Costo Total']]

            for item in datos:
                data.append([
                    item[0],
                    str(item[1]),
                    str(item[2]),
                    f"${item[3]:,.2f}"
                ])

            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            elements.append(table)
            doc.build(elements)

            messagebox.showinfo("Éxito", f"Reporte generado: {filename}")
            os.startfile(filename)

        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {str(e)}")

    def ventana_seleccion(self, titulo, callback):
        ventana = tk.Toplevel()
        ventana.title(titulo)
        ventana.geometry("300x200")
        ventana.resizable(False, False)

        main_frame = ttk.Frame(ventana, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Mes:").grid(row=0, column=0, sticky='w', pady=5)
        mes_combo = ttk.Combobox(main_frame, values=list(range(1, 13)), state="readonly")
        mes_combo.grid(row=0, column=1, pady=5, padx=5, sticky='w')
        mes_combo.set(datetime.now().month)

        ttk.Label(main_frame, text="Año:").grid(row=1, column=0, sticky='w', pady=5)
        año_combo = ttk.Combobox(main_frame,
                                 values=list(range(2020, datetime.now().year + 1)),
                                 state="readonly")
        año_combo.grid(row=1, column=1, pady=5, padx=5, sticky='w')
        año_combo.set(datetime.now().year)

        def generar():
            if mes_combo.get() and año_combo.get():
                ventana.destroy()
                callback(int(mes_combo.get()), int(año_combo.get()))

        ttk.Button(main_frame, text="Generar", command=generar).grid(row=2, column=0, columnspan=2, pady=20)

    # Implementar otros reportes similares...
    def generar_reporte_morosos(self):
        pass

    def generar_reporte_iva(self):
        pass

    def generar_reporte_facturas(self):
        pass