import re
import json
import requests
import textwrap
import urllib.request
from bs4 import BeautifulSoup
from datetime import timedelta
from AdnanXMusic.utils.thumbnails import get_thumb
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont

NAME = "ADDA X MUSIC"

def get_duration(response):
    soup = BeautifulSoup(response, 'html.parser')
    script_tag = soup.find('script', text=re.compile('ytInitialPlayerResponse'))
    if script_tag:
        video_details = re.search(r'ytInitialPlayerResponse\s*=\s*({.*?});', script_tag.string)
        if video_details:
            video_json = video_details.group(1)
            video_data = json.loads(video_json)
            if 'lengthSeconds' in video_data['videoDetails']:
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
    except Exception as e:
        print("Error downloading thumbnail:", e)
        return None

def edit(image_title, video_id, duration, views, channel):
    try:
        image = Image.open(f"assets/{video_id}.jpg")
        converter = ImageEnhance.Color(image)
        image = image.filter(ImageFilter.BLUR)
        overlay = Image.new("RGBA", image.size, (50, 50, 50, 50))
        image = Image.alpha_composite(image.convert("RGBA"), overlay)
        draw = ImageDraw.Draw(image)

        # Fonts And Color
        font_path = "assets/font.ttf"
        font = ImageFont.truetype(font_path, 30)
        text_color = (255, 255, 255) 

        # Top Left Sight Writing
        position = (30, 30)  
        draw.text(position, NAME, fill=text_color, font=font)

        # Bottom X Y Value 
        image_width, image_height = image.size
        x = ((image_width // 2) // 2)
        y = (image_height //2 ) + (image_height  // 4)

        # Title OF The Video
        position = (x, y - 80)
        text = textwrap.fill(f"{image_title}", width=50)
        draw.text(position, text, fill=text_color, font=font)

        # Duration Start And Close
        duritionX = duration.split(":")
        middle_duration = get_middle(duritionX)
        position = (x - 200 , y)  
        draw.text(position, middle_duration, fill=text_color, font=font)

        full_duration = f"{duritionX[1]} : {duritionX[2]}"
        position = (x - 80 + 800 , y)  
        draw.text(position, full_duration, fill=text_color, font=font)

        draw.text((x + 150, y + 125), f"{channel} | {views}", fill=text_color, font=ImageFont.truetype("arial.ttf", 20))

        # Overlay Image
        overlay = Image.new("RGBA", image.size, (50, 50, 50, 50))
        image = Image.alpha_composite(image.convert("RGBA"), overlay)
        image_to_paste = Image.open("overlay.png")
        image_to_paste = image_to_paste.convert("RGBA")
        paste_position = (x - 80, y - 50)
        image.paste(image_to_paste, paste_position, image_to_paste)

        image.show()
        image.save(f"assets/{video_id}_edited.png")
    except Exception as e:
        print("Error editing image:", e)

def main():
    try:
        url = input("Give Link: ")
        data = download_thumb(url)
        if data:
            edit(data[0], data[1], data[2], data[3],
def get_thumb():
    # Function implementation
 data[4])
    except KeyboardInterrupt:
        print("\nProgram interrupted.")
    except Exception as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    main()
