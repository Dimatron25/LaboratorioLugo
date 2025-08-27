from reportlab.pdfgen import canvas
from datetime import datetime
import os

def generar_recibo(examen, paciente):
    if not os.path.exists("receipts"):
        os.makedirs("receipts")
    filename = f"receipts/recibo_{examen['id']}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    c = canvas.Canvas(filename)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, 800, "LABORATORIO LUGO")
    c.setFont("Helvetica", 12)
    c.drawString(50, 760, f"Recibo N°: {examen['id']}")
    c.drawString(50, 740, f"Fecha: {examen['fecha']}")
    c.drawString(50, 720, f"Paciente: {paciente['nombre']}")
    c.drawString(50, 700, f"CURP: {paciente['curp']}")
    c.drawString(50, 680, f"Teléfono: {paciente['telefono']}")
    c.drawString(50, 660, f"Examen: {examen['tipo']}")
    c.drawString(50, 640, f"Precio: $ {examen['precio']:.2f} MXN")
    c.drawString(50, 620, f"Pagado: $ {examen['pagado']:.2f} MXN")
    c.drawString(50, 600, f"Estado: {examen['estado_pago'].upper()}")
    c.drawString(50, 560, "----------------------------------------")
    c.drawString(50, 540, "¡Gracias por su confianza!")
    c.save()
    return filename