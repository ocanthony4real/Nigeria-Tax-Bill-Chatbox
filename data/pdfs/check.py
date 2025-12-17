import pypdfium2 as pdfium
from PIL import Image
import pytesseract

# Load PDF
pdf = pdfium.PdfDocument("scanned copy 2.pdf")

# Render first page to PIL image
page = pdf[0]
pil_image = page.render(scale=300/72).to_pil()
page.close()
pdf.close()

# OCR directly on PIL image
text = pytesseract.image_to_string(pil_image)

print(text[:5000])
