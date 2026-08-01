import qrcode

# ⚠️ REMPLACE PAR LA VRAIE URL DE TON APP STREAMLIT :
url_app = "https://restennis-9svx4sgawlfu7u9afym8qt.streamlit.app/"

# Génération du QR code statique (direct)
qr = qrcode.QRCode(
    version=1,
    box_size=10,
    border=4,
)
qr.add_data(url_app)
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white")
img.save("qr_permanent.png")

print("✅ QR Code permanent généré : qr_permanent.png")