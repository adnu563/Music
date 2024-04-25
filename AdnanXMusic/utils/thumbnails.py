import os
import re
import textwrap
import urllib.request
from datetime import timedelta
from urllib.parse import urlparse

import requests
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from bs4 import BeautifulSoup
import json

from config import YOUTUBE_IMG_URL

def get_thumb(url):
    try:
        # Check if the URL has a scheme, if not, add "http://" as the default scheme
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            url = "http://" + url

        response = requests.get(url).text
        image_link = (response.split('<link rel="image_src" href="'))[1].split('">')[0]
        image_name = image_link.split('vi/')[1].split('/')[0]
        img_filename, _ = urllib.request.urlretrieve(image_link, f"assets/{image_name}.jpg")
        return img_filename
    except (ConnectionError, requests.RequestException) as e:
        print(f"Error occurred while fetching thumbnail: {e}")
        return None


def get_duration(response):
    soup = BeautifulSoup(response, 'html.parser')
    script_tag = soup.find('script', text=re.compile('ytInitialPlayerResponse'))
    if script_tag:
        video_details = re.search(r'ytInitialPlayerResponse\s*=\s*({.*?});', script_tag.string)
        if video_details:
            video_json = video_details.group(1)
            video_data = json.loads(video_json)
            if 'videoDetails' in video_data and 'lengthSeconds' in video_data['videoDetails']:
                duration_seconds = int(video_data['videoDetails']['lengthSeconds'])
                duration_formatted = str(timedelta(seconds=duration_seconds))
                return duration_formatted


def get_views(response):
    views = response.split('"shortViewCount":{"simpleText":"')[1].split('"}')[0]
    return views


def get_middle(duration):
    minute = int(int(duration[1]) / 2)
    if minute < 10:
        minute = f"0{minute}"
    seconds = int(int(duration[2]) / 2)
    if seconds < 10:
        seconds = f"0{seconds}"
    return f"{minute} : {seconds}"


def download_thumb(url):
    try:
        response = requests.get(url).text
        image_title = response.split('<meta name="title" content="')[1].split('">')[0]
        duration = get_duration(response)
        views = get_views(response)
        channel_name = response.split(', "name": "')[1].split('"}}]}')[0]

        image_link = (response.split('<link rel="image_src" href="'))[1].split('">')[0]
        image_name = image_link.split('vi/')[1].split('/')[0]

        img_filename, _ = urllib.request.urlretrieve(image_link, f"assets/{image_name}.jpg")
        img = Image.open(img_filename)
        return image_title, image_name, duration, views, channel_name
    except (ConnectionError, requests.RequestException) as e:
        print(f"Error occurred while downloading thumbnail: {e}")
        return None, None, None, None, None


def edit(image_title, video_id, duration, views, channel):
    try:
        image_path = f"assets/{video_id}.jpg"
        if not os.path.exists(image_path):
            print(f"Error: Image file '{image_path}' not found.")
            return

        image = Image.open(image_path)
        converter = ImageEnhance.Color(image)
        image = image.filter(ImageFilter.BLUR)
        overlay = Image.new("RGBA", image.size, (50, 50, 50, 50))
        image = Image.alpha_composite(image.convert("RGBA"), overlay)
        draw = ImageDraw.Draw(image)

        font = ImageFont.truetype("arial.ttf", 30)
        text_color = (255, 255, 255)

        position = (30, 30)
        draw.text(position, channel, fill=text_color, font=font)

        image_width, image_height = image.size
        x = ((image_width // 2) // 2)
        y = (image_height // 2) + (image_height // 4)

        position = (x, y - 80)
        text = textwrap.fill(f"{image_title}", width=50)
        draw.text(position, text, fill=text_color, font=font)

        if duration:
            duritionX = duration.split(":")
            middle_duration = get_middle(duritionX)
            position = (x - 200, y)
            draw.text(position, middle_duration, fill=text_color, font=font)

            full_duration = f"{duritionX[1]} : {duritionX[2]}"
            position = (x - 80 + 800, y)
            draw.text(position, full_duration, fill=text_color, font=font)

        draw.text((x + 150, y + 125), f"{channel} | {views}", fill=text_color,
                  font=ImageFont.truetype("arial.ttf", 20))

        overlay = Image.new("RGBA", image.size, (50, 50, 50, 50))
        image = Image.alpha_composite(image.convert("RGBA"), overlay)
        image_to_paste = Image.open("overlay.png")
        image_to_paste = image_to_paste.convert("RGBA")
        paste_position = (x - 80, y - 50)
        image.paste(image_to_paste, paste_position, image_to_paste)

        image.show()
        image.save(f"assets/{video_id}_edited.png")
    except Exception as e:
        print(e)
        return None

if __name__ == "__main__":
    # Example usage:
    youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Example YouTube URL
    thumbnail_path = get_thumb(youtube_url)
    if thumbnail_path:
        image_title, video_id, duration, views, channel_name = download_thumb(youtube_url)
        if image_title and video_id and duration and views and channel_name:
            edit(image_title, video_id, duration, views, channel_name)
    else:
        print("Thumbnail could not be retrieved.")
