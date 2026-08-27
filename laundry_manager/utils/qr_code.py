"""QR helpers for invoices.

The TLV payload follows the basic ZATCA e-invoicing QR encoding. It is only
produced when a VAT number is configured; without one, the app keeps a clearly
non-compliance-claiming internal QR payload.
"""
from base64 import b64encode
from pathlib import Path
import tempfile


def _tlv(tag: int, value: str) -> bytes:
    raw = str(value or "").encode("utf-8")
    return bytes([tag, len(raw)]) + raw


def zatca_tlv_payload(invoice: dict) -> str | None:
    """Return base64-encoded basic TLV fields, or None without seller VAT data."""
    vat_number = invoice.get("vat_number") or invoice.get("seller_vat_number")
    if not vat_number:
        return None
    seller = invoice.get("seller_name") or invoice.get("business_name") or ""
    issued = str(invoice.get("issued_date") or "")
    total = f"{float(invoice.get('total_amount') or 0):.2f}"
    tax = f"{float(invoice.get('tax_amount') or 0):.2f}"
    payload = b"".join((_tlv(1, seller), _tlv(2, vat_number), _tlv(3, issued), _tlv(4, total), _tlv(5, tax)))
    return b64encode(payload).decode("ascii")


def invoice_qr_payload(invoice: dict) -> str:
    """Return ZATCA TLV data when configured, otherwise an internal QR payload."""
    zatca = zatca_tlv_payload(invoice)
    if zatca:
        return zatca
    return "|".join((
        "INTERNAL-LAUNDRIES",
        str(invoice.get("invoice_number", "")),
        str(invoice.get("order_id", "")),
        f"SAR {float(invoice.get('total_amount') or 0):.2f}",
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
