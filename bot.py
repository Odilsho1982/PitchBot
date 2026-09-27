# -*- coding: utf-8 -*-
import os, random, time, requests, asyncio
from PIL import Image, ImageDraw, ImageFont
from telethon import TelegramClient
from dotenv import load_dotenv

load_dotenv()
FOLDER = os.path.dirname(__file__)
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
CHANNEL = os.getenv("CHANNEL", "@pitchmypitch")
BG_PATH = os.path.join(FOLDER, "bg.jpg")

def make_img(text):
    # Если есть bg.jpg - берем его, если нет - делаем фон
    if os.path.exists(BG_PATH):
        img = Image.open(BG_PATH).convert("RGB")
        img = img.resize((1080, 1080))
    else:
        w, h = 1080, 1080
        img = Image.new("RGB", (w, h), (15,15,15))

    w, h = img.size
    draw = ImageDraw.Draw(img, "RGBA")

    # затемнение снизу для текста
    overlay = Image.new("RGBA", (w, int(h*0.32)), (0,0,0,180))
    img.paste(Image.new("RGB", (w, int(h*0.32)), (0,0,0)), (0, h - int(h*0.32)), mask=overlay)
    draw = ImageDraw.Draw(img)

    try:
        font_big = ImageFont.truetype("arial.ttf", 70)
        font_small = ImageFont.truetype("arial.ttf", 38)
        font_logo = ImageFont.truetype("arial.ttf", 40)
    except:
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()
        font_logo = ImageFont.load_default()

    # линия
    draw.rectangle([(30, h - int(h*0.32)), (180, h - int(h*0.32) + 6)], fill=(0,255,136))
    draw.text((30, h - int(h*0.32) + 20), "ПИТЧ ДНЯ:", font=font_small, fill=(0,255,136))

    # перенос длинного названия
    txt = text[:50].upper()
    if len(txt) > 20:
        draw.text((30, h - int(h*0.32) + 60), txt[:25], font=font_big, fill=(255,255,255))
        draw.text((30, h - int(h*0.32) + 135), txt[25:], font=font_big, fill=(255,255,255))
    else:
        draw.text((30, h - int(h*0.32) + 60), txt, font=font_big, fill=(255,255,255))

    draw.text((30, 30), "PITCH MY PITCH", font=font_logo, fill=(255,255,255))

    out_path = os.path.join(FOLDER, "post.jpg")
    img.save(out_path, quality=95)
    return out_path

async def main():
    # 3 попытки взять с Product Hunt с ретраем
    name = "AI Startup of the Day"
    for _ in range(3):
        try:
            rss = requests.get("https://www.producthunt.com/feed", timeout=15).text
            if "<title>" in rss:
                parts = rss.split("<title>")
                if len(parts) > 2:
                    name = parts[2].split("</title>")[0]
            break
        except:
            time.sleep(2)

    name = name.replace("<![CDATA[", "").replace("]]>", "").strip()

    img_path = make_img(name)

    caption = f"""🚀 ПИТЧ ДНЯ: {name}

Разбор: сильный хук, но добавь traction и цифры.

📊 Шаблон 12 слайдов: boosty.to/pitchdeck_tj (150 сомони)

Кидай свой питч: @sanoi1982

#vc #startup #pitch"""

    client = TelegramClient(os.path.join(FOLDER, 'session'), API_ID, API_HASH)
    await client.start()
    await client.send_file(CHANNEL, img_path, caption=caption)
    print(f"✅ Запостил: {name}")
    await client.disconnect()
    print("Готово. Для следующего поста просто запусти python bot.py снова.")

if __name__ == "__main__":
    asyncio.run(main())