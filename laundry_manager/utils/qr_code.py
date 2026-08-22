"""QR-code helpers for invoice lookup and sharing."""
from pathlib import Path
import tempfile


def invoice_qr_payload(invoice: dict) -> str:
    """Return a compact, stable payload that can be read by any QR scanner."""
    return "|".join((
        "INTERNATIONAL-LAUNDRIES",
        str(invoice.get("invoice_number", "")),
        str(invoice.get("order_id", "")),
        f"RM {float(invoice.get('total_amount') or 0):.2f}",
        str(invoice.get("issued_date", ""))[:10],
    ))


def generate_invoice_qr(invoice: dict) -> Path:
    """Generate a PNG QR image for an invoice and return its path."""
    import qrcode

    safe_number = "".join(
        char if char.isalnum() or char in "-_" else "_"
        for char in str(invoice.get("invoice_number", "invoice"))
    )
    path = Path(tempfile.gettempdir()) / f"laundry_invoice_{safe_number}_qr.png"
    qr = qrcode.QRCode(version=None, box_size=8, border=2)
    qr.add_data(invoice_qr_payload(invoice))
    qr.make(fit=True)
    qr.make_image(fill_color="black", back_color="white").save(path)
    return path
