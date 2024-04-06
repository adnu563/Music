import os
import re

import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from unidecode import unidecode
from youtubesearchpython.__future__ import VideosSearch

from AdnanXMusic import app
from config import YOUTUBE_IMG_URL


async def changeable_thumb_design(videoid):
    if os.path.isfile(f"cache/{videoid}.png"):
        return f"cache/{videoid}.png"

    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = VideosSearch(url, limit=1)
        for result in (await results.next())["result"]:
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            async with aiohttp.ClientSession() as session:
                async with session.get(thumbnail) as resp:
                    if resp.status == 200:
                        f = await aiofiles.open(f"cache/thumb{videoid}.png", mode="wb")
                        await f.write(await resp.read())
                        await f.close()

            youtube = Image.open(f"cache/thumb{videoid}.png")
            image1 = changeImageSize(1280, 720, youtube)
            image2 = image1.convert("RGBA")
            background = image2.filter(filter=ImageFilter.BoxBlur(10))
            enhancer = ImageEnhance.Brightness(background)
            background = enhancer.enhance(0.5)
            draw = ImageDraw.Draw(background)
            
            # Font Paths
            arial = ImageFont.truetype("AdnanXMusic/assets/font2.ttf", 30)
            font = ImageFont.truetype("AdnanXMusic/assets/font.ttf", 30)
            
            # Draw Bot Name
            draw.text((20, 20), unidecode(app.name), fill="white", font=arial)
            
            # Draw Channel Name or Views in Footer Middle
            footer_text = f"{result.get('channel', {}).get('name', 'Unknown Channel')} | {result.get('viewCount', {}).get('short', 'Unknown Views')[:23]}"
            footer_width, footer_height = draw.textsize(footer_text, font=arial)
            draw.text(((1280-footer_width)/2, 650), footer_text, (255, 255, 255), font=arial)
            
            # Draw Song Name
            title = result.get("title", "Unsupported Title")
            title = re.sub("\W+", " ", title)
            title = title.title()
            song_name = clear(title)
            draw.text((20, 570), song_name, (255, 255, 255), font=font)
            
            # Draw Song Duration
            duration = result.get("duration", "Unknown Mins")
            duration_text = f"{duration[:23]}"
            draw.text((20, 600), duration_text, (255, 255, 255), font=font)
            
            # Draw Control Symbols
            symbols = "⇆ ↻ ◁ 𝕀𝕀 ▷ ↺ ♡"
            draw.text((20, 630), symbols, (255, 255, 255), font=font)
            
            try:
                os.remove(f"cache/thumb{videoid}.png")
            except:
                pass
            background.save(f"cache/{videoid}.png")
            return f"cache/{videoid}.png"
    except Exception as e:
        print(e)
        return YOUTUBE_IMG_


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