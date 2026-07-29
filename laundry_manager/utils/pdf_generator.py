"""
Generate PDF invoices using reportlab.
Redesigned for cashier-style receipts.
"""
import os
import tempfile
from datetime import datetime
from utils.branding import BUSINESS_NAME, BUSINESS_TAGLINE, get_logo_path

def generate_invoice_pdf(invoice: dict, order_items: list = None,
                         order: dict = None) -> str | None:
    try:
        from reportlab.lib.pagesizes import portrait
        from reportlab.lib import colors
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            SimpleDocTemplate, Table, TableStyle, Paragraph,
            Spacer, HRFlowable, Image
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
    except ImportError:
        return _fallback_txt_invoice(invoice, order_items, order)

    # Cashier receipt size (approx 80mm width, height dynamic but we'll use a long portrait)
    RECEIPT_WIDTH = 80 * mm
    # Estimate height based on items
    item_count = len(order_items) if order_items else 1
    RECEIPT_HEIGHT = (100 + item_count * 10) * mm
    
    import time
    timestamp = int(time.time())
    fname = f"receipt_{invoice.get('invoice_number', 'INV').replace('/', '-')}_{timestamp}.pdf"
    path = os.path.join(tempfile.gettempdir(), fname)

    try:
        doc = SimpleDocTemplate(
            path, pagesize=(RECEIPT_WIDTH, RECEIPT_HEIGHT),
            rightMargin=5 * mm, leftMargin=5 * mm,
            topMargin=5 * mm, bottomMargin=5 * mm,
        )
    except Exception as e:
        print(f"Error creating DocTemplate: {e}")
        return _fallback_txt_invoice(invoice, order_items, order)

    DARK = colors.HexColor('#000000')
    GRAY = colors.HexColor('#333333')

    styles = getSampleStyleSheet()
    
    header_style = ParagraphStyle(
        'header', fontSize=12, textColor=DARK,
        fontName='Helvetica-Bold', alignment=TA_CENTER, leading=14,
    )
    tagline_style = ParagraphStyle(
        'tagline', fontSize=8, textColor=GRAY,
        fontName='Helvetica', alignment=TA_CENTER, leading=10,
    )
    normal_style = ParagraphStyle(
        'normal', fontSize=9, textColor=DARK,
        fontName='Helvetica', leading=11,
    )
    bold_style = ParagraphStyle(
        'bold', fontSize=9, textColor=DARK,
        fontName='Helvetica-Bold', leading=11,
    )
    center_style = ParagraphStyle(
        'center', fontSize=9, textColor=DARK,
        fontName='Helvetica', alignment=TA_CENTER, leading=11,
    )
    right_style = ParagraphStyle(
        'right', fontSize=9, textColor=DARK,
        fontName='Helvetica', alignment=TA_RIGHT, leading=11,
    )

    elements = []

    # ── Header ──
    logo_path = get_logo_path()
    if logo_path:
        try:
            img = Image(str(logo_path), width=15 * mm, height=15 * mm)
            img.hAlign = 'CENTER'
            elements.append(img)
            elements.append(Spacer(1, 2 * mm))
        except Exception:
            pass
    
    elements.append(Paragraph(BUSINESS_NAME.upper(), header_style))
    elements.append(Paragraph(BUSINESS_TAGLINE, tagline_style))
    elements.append(Spacer(1, 4 * mm))
    elements.append(HRFlowable(width='100%', thickness=0.5, color=DARK, dash=(1, 1)))
    elements.append(Spacer(1, 2 * mm))

    # ── Info ──
    inv_num = invoice.get('invoice_number', '')
    issued = str(invoice.get('issued_date', datetime.now().strftime('%Y-%m-%d')))[:10]
    customer = invoice.get('customer_name') or invoice.get('company_name') or 'Guest'
    
    elements.append(Paragraph(f"<b>RECEIPT:</b> {inv_num}", normal_style))
    elements.append(Paragraph(f"<b>DATE:</b> {issued}", normal_style))
    elements.append(Paragraph(f"<b>CUST:</b> {customer}", normal_style))
    if order and order.get('order_number'):
        elements.append(Paragraph(f"<b>ORDER:</b> {order['order_number']}", normal_style))
    
    elements.append(Spacer(1, 2 * mm))
    elements.append(HRFlowable(width='100%', thickness=0.5, color=DARK, dash=(1, 1)))
    elements.append(Spacer(1, 2 * mm))

    # ── Items ──
    if order_items:
        # Table for items: Qty | Item | Total
        tbl_data = [[
            Paragraph("<b>QTY</b>", center_style),
            Paragraph("<b>ITEM</b>", normal_style),
            Paragraph("<b>TOTAL</b>", right_style)
        ]]
        for it in order_items:
            name = it.get('item_name', '')
            svc = it.get('service_type', '').upper()
            tbl_data.append([
                Paragraph(str(it.get('quantity', 1)), center_style),
                Paragraph(f"{name} ({svc})", normal_style),
                Paragraph(f"{it.get('total_price', 0):.2f}", right_style)
            ])
        
        item_tbl = Table(tbl_data, colWidths=[12 * mm, 38 * mm, 20 * mm])
        item_tbl.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        elements.append(item_tbl)
    
    elements.append(Spacer(1, 2 * mm))
    elements.append(HRFlowable(width='100%', thickness=0.5, color=DARK, dash=(1, 1)))
    elements.append(Spacer(1, 2 * mm))

    # ── Totals ──
    total = invoice.get('total_amount', 0)
    paid = invoice.get('paid_amount', 0)
    balance = total - paid

    totals_data = [
        [Paragraph("<b>TOTAL RM</b>", normal_style), Paragraph(f"<b>{total:.2f}</b>", right_style)],
        [Paragraph("PAID RM", normal_style), Paragraph(f"{paid:.2f}", right_style)],
        [Paragraph("BALANCE RM", normal_style), Paragraph(f"{balance:.2f}", right_style)],
    ]
    totals_tbl = Table(totals_data, colWidths=[40 * mm, 30 * mm])
    totals_tbl.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(totals_tbl)
    
    elements.append(Spacer(1, 6 * mm))
    elements.append(Paragraph("THANK YOU!", center_style))
    elements.append(Paragraph("Please come again", tagline_style))
    elements.append(Spacer(1, 4 * mm))
    elements.append(HRFlowable(width='100%', thickness=0.5, color=DARK, dash=(1, 1)))

    try:
        doc.build(elements)
    except Exception as e:
        import logging
        logging.error(f"ReportLab build failed: {e}")
        return _fallback_txt_invoice(invoice, order_items, order)
    return path

def _fallback_txt_invoice(invoice: dict, order_items: list = None,
                          order: dict = None) -> str:
    """Plain text receipt when reportlab is not installed."""
    fname = f"receipt_{invoice.get('invoice_number', 'INV').replace('/', '-')}.txt"
    path = os.path.join(tempfile.gettempdir(), fname)
    lines = [
        BUSINESS_NAME.upper(),
        BUSINESS_TAGLINE,
        "-" * 32,
        f"Receipt: {invoice.get('invoice_number', '')}",
        f"Date:    {str(invoice.get('issued_date', ''))[:10]}",
        f"Cust:    {invoice.get('customer_name') or invoice.get('company_name') or 'Guest'}",
        "-" * 32,
        f"{'QTY':<4} {'ITEM':<18} {'TOTAL':>8}",
    ]
    if order_items:
        for it in order_items:
            lines.append(
                f"{it.get('quantity', 1):<4} "
                f"{it.get('item_name', '')[:17]:<18} "
                f"{it.get('total_price', 0):>8.2f}"
            )
    lines += [
        "-" * 32,
        f"{'TOTAL RM':<20} {invoice.get('total_amount', 0):>11.2f}",
        f"{'PAID RM':<20} {invoice.get('paid_amount', 0):>11.2f}",
        f"{'BALANCE RM':<20} {invoice.get('total_amount', 0) - invoice.get('paid_amount', 0):>11.2f}",
        "-" * 32,
        "   THANK YOU!",
        "-" * 32,
    ]
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(line for line in lines if line is not None))
    return path
