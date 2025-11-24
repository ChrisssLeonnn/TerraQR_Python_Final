from fpdf import FPDF
from app.db import models
import qrcode
from PIL import Image
import io

def generate_qr_pdf(persona: models.Persona, qr_url: str) -> str:
    """
    Generates a PDF with the QR code and person's information,
    saves it to a file, and returns the path to the file.
    """
    
    # Generate QR code image
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")

    # Save QR code to a byte stream
    img_byte_arr = io.BytesIO()
    qr_img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('DejaVu', '', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', uni=True)
    
    # Title
    pdf.set_font("DejaVu", "B", 16)
    pdf.cell(200, 10, "Pase de Acceso TerraQR", ln=True, align="C")
    pdf.ln(10)

    # Person's information
    pdf.set_font("DejaVu", "", 12)
    pdf.cell(200, 10, f"Nombre: {persona.Nombre} {persona.ApellidoPaterno} {persona.ApellidoMaterno}", ln=True)
    pdf.cell(200, 10, f"Tipo de Persona: {persona.TipoPersona}", ln=True)
    
    # Calculate age
    from datetime import date
    today = date.today()
    age = today.year - persona.AnioNacimiento
    pdf.cell(200, 10, f"Edad: {age} años", ln=True)

    pdf.ln(10)

    # QR Code
    pdf.image(io.BytesIO(img_byte_arr), x=55, y=None, w=100)

    pdf.ln(10)
    pdf.set_font("DejaVu", "I", 8)
    pdf.cell(200, 10, "Presenta este código QR en el acceso del evento.", ln=True, align="C")

    # Save the PDF to a file
    file_path = f"app/static/qrs/{persona.PersonaId}.pdf"
    pdf.output(file_path)
    
    return file_path
