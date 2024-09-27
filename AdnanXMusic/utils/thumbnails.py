import os
import re
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from urllib.parse import urlparse, parse_qs
from youtubesearchpython.__future__ import VideosSearch
from unidecode import unidecode

from AdnanXMusic import app  # Ensure this module is accessible
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
    cache_path = f"cache/{videoid}.png"
    if os.path.isfile(cache_path):
        return cache_path

    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        # Fetch YouTube video details using the search API
        results = VideosSearch(url, limit=1)
        result = (await results.next())["result"][0]
        
        # Extract information from the result
        title = re.sub("\W+", " ", result.get("title", "Unsupported Title")).title()
        duration = result.get("duration", "Unknown Mins")
        thumbnail_url = result["thumbnails"][0]["url"].split("?")[0]
        views = result.get("viewCount", {}).get("short", "Unknown Views")
        channel = result.get("channel", {}).get("name", "Unknown Channel")

        # Download thumbnail image
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail_url) as resp:
                if resp.status == 200:
                    temp_thumb_path = f"cache/temp_thumb_{videoid}.png"
                    async with aiofiles.open(temp_thumb_path, "wb") as f:
                        await f.write(await resp.read())

        # Open and process the image
        youtube_img = Image.open(temp_thumb_path)
        resized_image = change_image_size(1280, 720, youtube_img).convert("RGBA")

        # Create a blurred background
        background = resized_image.filter(ImageFilter.BoxBlur(6))
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(0.5)

        draw = ImageDraw.Draw(background)

        # Use fonts from the assets directory
        arial_font = ImageFont.truetype("AdnanXMusic/assets/AutourOne-Regular.ttf", 35)
        regular_font = ImageFont.truetype("AdnanXMusic/assets/AutourOne-Regular.ttf", 20)
        main_font = ImageFont.truetype("AdnanXMusic/assets/font.ttf", 28)

        # Draw the app name at the top-left corner
        draw.text((22, 14), unidecode(app.name), fill="white", font=arial_font)

        # Draw the YouTube title centered above the duration
        title_text = clean_title(title)
        title_bbox = draw.textbbox((0, 0), title_text, font=main_font)
        draw.text(
            ((background.width - (title_bbox[2] - title_bbox[0])) / 2, 430),  # Centered above duration
            title_text,
            fill="white",
            font=main_font
        )

        # Draw the duration overlay
        draw.text((70, 475), "00:00", fill="white", font=arial_font)  # Start duration
        draw.text((1122, 475), duration, fill="white", font=arial_font)  # End duration

        # Create and position channel info and views
        channel_info = f"{channel} | {views}"

        # Calculate the bounding box for the channel name and views
        channel_bbox = draw.textbbox((0, 0), channel, font=regular_font)
        views_bbox = draw.textbbox((0, 0), views, font=regular_font)
        pipe_symbol = "|"

        # Calculate total width of the channel name, pipe symbol, and views
        total_text_width = (channel_bbox[2] - channel_bbox[0]) + 2 + (views_bbox[2] - views_bbox[0])  # 2px space for pipe

        # Calculate the central position for the pipe symbol and adjust the text positions
        pipe_x = (background.width - total_text_width) // 2
        channel_x = pipe_x - 50 - (channel_bbox[2] - channel_bbox[0])  # Move channel 50px to the left
        views_x = pipe_x + 2 + (views_bbox[2] - views_bbox[0]) + 50  # Move views 50px to the right

        # Draw the channel name, pipe symbol, and views on the image
        draw.text((channel_x, 450), channel, fill="white", font=arial_font)  # Channel text
        draw.text((pipe_x, 650), pipe_symbol, fill="white", font=arial_font)  # Pipe symbol "|"
        draw.text((views_x, 450), views, fill="white", font=arial_font)  # Views text

        # Overlay image just below the YouTube title
        overlay_img = Image.open("AdnanXMusic/assets/overly.png")
        overlay_img = overlay_img.resize((890, 280))
        overlay_position = ((background.width - overlay_img.width) // 2, 400)
        background.paste(overlay_img, overlay_position, overlay_img)

        # Clean up and save the final image
        os.remove(temp_thumb_path)
        background.save(cache_path)
        return cache_path

    except Exception as e:
        print(f"Error occurred while processing video: {e}")
        return YOUTUBE_IMG_URL
