from PIL import Image, ImageFont, ImageDraw
import textwrap


img = Image.new('RGB', (756, 1051))
font_text = ImageFont.truetype(font='Inter-Medium.ttf', size=60)
draw = ImageDraw.Draw(im=img)
text = """Americkým indiánům navždy změnilo život, když jim bílý muž představil ___."""
avg_char_width = 0
for i in range(len(text)):
    avg_char_width += font_text.getlength(text[i])
else:
    avg_char_width /= len(text)

max_char_count = int(img.size[0] * 0.82 / avg_char_width)
text = textwrap.fill(text=text, width=max_char_count)
draw.text(xy=(60, 55), text=text, font=font_text, fill='#FFFFFF', anchor='la', spacing=18)
img.show()
