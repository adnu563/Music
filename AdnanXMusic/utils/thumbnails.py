import os
import re
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from unidecode import unidecode
from youtubesearchpython.__future__ import VideosSearch
from config import YOUTUBE_IMG_URL

def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage

def clear(text):
    list = text.split(" ")
    title = ""
    for i in list:
        if len(title) + len(i) < 60:
            title += " " + i
    return title.strip()

async def get_thumb(videoid):
    # your existing get_thumb function
    pass

def get_middle(duration):
    # your existing get_middle function
    pass

def edit(image_title, video_id, duration, views, channel):
    image = Image.open(f"assets/{video_id}.jpg")
    converter = ImageEnhance.Color(image)
    image = image.filter(ImageFilter.BLUR)
    overlay = Image.new("RGBA", image.size, (50, 50, 50, 50))
    image = Image.alpha_composite(image.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(image)

    font_path = "AdnanXMusic/assets/font.ttf"
    arial_path = "AdnanXMusic/assets/font2.ttf"
    font = ImageFont.truetype(font_path, 30)
    arial = ImageFont.truetype(arial_path, 30)
    text_color = (255, 255, 255)

    x, y = image.size[0] // 4, image.size[1] // 2

    draw.text((x, 30), unidecode(app.name), fill=text_color, font=arial)
    draw.text((x - 300, y - 80), clear(image_title), fill=text_color, font=font)
    draw.text((x - 480, y), get_middle(duration), fill=text_color, font=font)
    draw.text((x + 320, y), f"{duration}", fill=text_color, font=font)
    draw.text((x + 30, y + 125), f"{channel} | {views}", fill=text_color, font=arial)

    overlay = Image.new("RGBA", image.size, (50, 50, 50, 50))
    image = Image.alpha_composite(image.convert("RGBA"), overlay)
    image_to_paste = Image.open("overlay.png")
    image_to_paste = image_to_paste.convert("RGBA")
    paste_position = (x - 80, y - 50)
    image.paste(image_to_paste, paste_position, image_to_paste)

    image.show()
    image.save(f"assets/{video_id}_edited.png")

def main():
    data = await get_thumb(input("Give Link: "))  # assuming this is an async function
    edit(data["title"], data["id"], data["duration"], data["views"], data["channel"])

if __name__ == "__main__":
    main()