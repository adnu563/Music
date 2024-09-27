import os
import re
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from urllib.parse import urlparse, parse_qs
from youtubesearchpython.__future__ import VideosSearch
from unidecode import unidecode

from AdnanXMusic import app  # Make sure this module is accessible
from config import YOUTUBE_IMG_URL


def change_image_size(max_width, max_height, image):
    """Resizes the image to fit within the given max_width and max_height."""
    width_ratio = max_width / image.size[0]
    height_ratio = max_height / image.size[1]
    new_width = int(width_ratio * image.size[0])
    new_height = int(height_ratio * image.size[1])
    return image.resize((new_width, new_height))


def clean_title(text, max_length=60):
    """Cleans and truncates the title to a maximum length."""
    words = text.split(" ")
    title = ""
    for word in words:
        if len(title) + len(word) < max_length:
            title += " " + word
    return title.strip()


def extract_video_id(youtube_url):
    """Extracts the video ID from a YouTube URL."""
    parsed_url = urlparse(youtube_url)
    video_id = parse_qs(parsed_url.query).get("v")
    if video_id:
        return video_id[0]
    return None


async def get_thumb(videoid):
    """Fetches the YouTube thumbnail, modifies it, and returns the path to the saved image."""
    # Check if the thumbnail already exists in the cache
    if os.path.isfile(f"cache/{videoid}.png"):
        return f"cache/{videoid}.png"

    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        # Fetch YouTube video details using the search API
        results = VideosSearch(url, limit=1)
        for result in (await results.next())["result"]:
            try:
                title = re.sub("\W+", " ", result.get("title", "Unsupported Title")).title()
            except:
                title = "Unsupported Title"

            try:
                duration = result.get("duration", "Unknown Mins")
            except:
                duration = "Unknown Mins"

            thumbnail_url = result["thumbnails"][0]["url"].split("?")[0]

            try:
                views = result.get("viewCount", {}).get("short", "Unknown Views")
            except:
                views = "Unknown Views"

            try:
                channel = result.get("channel", {}).get("name", "Unknown Channel")
            except:
                channel = "Unknown Channel"

        # Download thumbnail image
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail_url) as resp:
                if resp.status == 200:
                    async with aiofiles.open(f"cache/temp_thumb_{videoid}.png", "wb") as f:
                        await f.write(await resp.read())

        # Open and process the image
        youtube_img = Image.open(f"cache/temp_thumb_{videoid}.png")
        resized_image = change_image_size(1280, 720, youtube_img).convert("RGBA")

        # Create a blurred background
        background = resized_image.filter(ImageFilter.BoxBlur(6))
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(0.5)

        draw = ImageDraw.Draw(background)

        # Use fonts from the assets directory
        arial_font = ImageFont.truetype("AdnanXMusic/assets/AutourOne-Regular.ttf", 35)
        regular_font = ImageFont.truetype("AdnanXMusic/assets/AutourOne-Regular.ttf", 25)
        main_font = ImageFont.truetype("AdnanXMusic/assets/font.ttf", 28)

        # Draw the app name at the top-left corner
        draw.text((22, 14), unidecode(app.name), fill="white", font=arial_font)  # Position on the left side

        # Draw the YouTube title centered above the duration
        title_text = clean_title(title)
        title_bbox = draw.textbbox((0, 0), title_text, font=main_font)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(
            ((background.width - title_width) / 2, 430),  # Centered above the duration
            title_text,
            fill=(255, 255, 255),
            font=main_font
        )

        # Draw the duration overlay
        draw.text((70, 475), "00:00", fill=(255, 255, 255), font=arial_font)  # Start duration
        draw.text((1122, 475), duration, fill=(255, 255, 255), font=arial_font)  # End duration

        # Draw channel and views, centered between 50-pixel margins from both sides
        channel_info = f"{channel} | {views}"
        channel_bbox = draw.textbbox((0, 0), channel_info, font=regular_font)
        channel_width = channel_bbox[2] - channel_bbox[0]

        # Set the margin of 50 pixels from left and right, so the text is centered within the remaining width
        left_margin = 50
        right_margin = background.width - 50

        # Calculate the starting position to center the text between the margins
        x_position = (right_margin - left_margin - channel_width) / 2 + left_margin

        # Move 10px to the left
        x_position -= 30

        # Draw the text at the new position
        draw.text(
            (x_position, 650),  # Position near the bottom, keeping it centered between the margins
            channel_info,
            fill=(255, 255, 255),
            font=arial_font
        )

        # Overlay image just below the YouTube title
        overlay_img = Image.open("AdnanXMusic/assets/overly.png")
        overlay_img = overlay_img.resize((890, 280))  # Resize overlay if necessary
        overlay_position = ((background.width - overlay_img.width) // 2, 400)  # Position below title
        background.paste(overlay_img, overlay_position, overlay_img)

        # Clean up and save the final image
        os.remove(f"cache/temp_thumb_{videoid}.png")
        background.save(f"cache/{videoid}.png")
        return f"cache/{videoid}.png"

    except Exception as e:
        print(e)
        return YOUTUBE_IMG_URL
