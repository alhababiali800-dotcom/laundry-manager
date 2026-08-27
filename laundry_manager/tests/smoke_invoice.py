import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.pdf_generator import generate_invoice_pdf
from utils.qr_code import zatca_tlv_payload

invoice = {
    'invoice_number': 'INV-TEST-0001',
    'order_id': 1,
    'issued_date': '2026-08-26T12:00:00',
    'customer_name': 'عميل تجريبي',
    'subtotal_amount': 100.0,
    'tax_rate': 15.0,
    'tax_amount': 15.0,
    'total_amount': 115.0,
    'paid_amount': 0.0,
    'seller_name': 'مغسلة تجريبية',
    'vat_number': '300000000000003',
}
items = [{'item_name': 'ثوب', 'service_type': 'wash', 'quantity': 2, 'total_price': 100.0}]
assert zatca_tlv_payload(invoice)
path = generate_invoice_pdf(invoice, items, {'order_number': 'ORD-TEST-0001'})
assert path
print(path)
