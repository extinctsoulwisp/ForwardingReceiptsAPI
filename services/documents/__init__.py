from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from .receipt import create_receipt_doc


pdfmetrics.registerFont(TTFont("OpenSans", 'services/documents/OpenSans.ttf'))
pdfmetrics.registerFont(TTFont("OpenSansBold", 'services/documents/OpenSans-Bold.ttf'))

