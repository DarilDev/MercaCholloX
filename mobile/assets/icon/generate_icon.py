"""Genera el icono base de la app (1024x1024) con Pillow — sin herramienta de
diseño de imágenes disponible en este entorno, se dibuja una marca geométrica
simple (fondo verde de marca + "M" en blanco + acento ámbar) en vez de un
logo elaborado. Uso: python3 generate_icon.py (desde esta carpeta)."""

from PIL import Image, ImageDraw, ImageFont

SIZE = 1024
PRIMARY_GREEN = (15, 157, 88)  # mismo verde que theme.dart AppColors.primary
ACCENT_AMBER = (255, 179, 0)  # mismo ámbar que theme.dart AppColors.starred/accent

img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

margin = 40
draw.rounded_rectangle(
    [margin, margin, SIZE - margin, SIZE - margin],
    radius=220,
    fill=PRIMARY_GREEN,
)

font = ImageFont.truetype("/usr/share/fonts/truetype/lato/Lato-Black.ttf", 560)
text = "M"
bbox = draw.textbbox((0, 0), text, font=font)
text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
draw.text(
    ((SIZE - text_w) / 2 - bbox[0], (SIZE - text_h) / 2 - bbox[1] - 30),
    text,
    font=font,
    fill=(255, 255, 255, 255),
)

# Acento: punto ámbar bajo la M, como un "." de precio/oferta.
dot_radius = 42
dot_cy = SIZE / 2 + text_h / 2 + 60
draw.ellipse(
    [SIZE / 2 - dot_radius, dot_cy - dot_radius, SIZE / 2 + dot_radius, dot_cy + dot_radius],
    fill=ACCENT_AMBER,
)

img.save("icon.png")
print("icon.png generado")
