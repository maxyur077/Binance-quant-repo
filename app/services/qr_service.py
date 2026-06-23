from __future__ import annotations

import io
import urllib.parse
try:
    import qrcode
except ImportError:
    qrcode = None


class QRService:
    @staticmethod
    def generate_solana_pay_qr(
        recipient: str, 
        amount: float, 
        reference: str, 
        label: str = "Binance Quant Subscription", 
        message: str = "Premium Access"
    ) -> bytes:
        if qrcode is None:
            raise ImportError("qrcode package is required for generating QR codes")
            
        # solana:<recipient>?amount=<amount>&reference=<reference>&label=<label>&message=<message>
        base_url = f"solana:{recipient}"
        
        params = {
            "amount": str(amount),
            "reference": reference,
            "label": label,
            "message": message,
            "spl-token": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB" # USDT on Solana
        }
        
        query_string = urllib.parse.urlencode(params)
        solana_pay_url = f"{base_url}?{query_string}"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(solana_pay_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()


qr_service = QRService()
