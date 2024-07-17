from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph

from app.schemas import SReceipt
from services.documents.func import col_width

MARGIN = 10
FONT_SIZE = 11
LEADING = 14
SPACE_AFTER = 10


def create_receipt_doc(receipt: SReceipt):
    pdf_path = f'services/documents/temp/receipt{receipt.id}.pdf'
    pdf = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN
    )

    h_l_style = ParagraphStyle('', fontName='OpenSans', fontSize=FONT_SIZE, leading=LEADING)
    h_r_style = ParagraphStyle('', fontName='OpenSansBold', fontSize=FONT_SIZE, leading=LEADING, alignment=TA_RIGHT)

    p_default_style = ParagraphStyle('', fontName='OpenSans', fontSize=FONT_SIZE, spaceAfter=SPACE_AFTER, leading=LEADING)
    p_bold_style = ParagraphStyle('', fontName='OpenSansBold', fontSize=FONT_SIZE, spaceAfter=SPACE_AFTER, leading=LEADING)

    width = A4[0] - MARGIN * 2

    story = [
        Table(  # header
            data=[[
                Paragraph(f"ШАПКА<br/>СЛЕВА<br/>", style=h_l_style),
                Paragraph(f"ШАПКА<br/>СПРАВА<br/>", style=h_r_style),
            ]],
            spaceAfter=SPACE_AFTER,
            colWidths=col_width(width, .5, .5)
        )
    ]

    pdf.build(story)

    return pdf_path
