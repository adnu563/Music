import asyncio 
import os 
import logging 
import re 
from typing import Union 
import yt_dlp from 
pyrogram.enums 
import MessageEntityType 
from pyrogram.types import Message 
from youtubesearchpython.future 
import VideosSearch 
from AdnanXMusic.utils.database import is_on_off 
from AdnanXMusic.utils.formatters import time_to_seconds

Configure logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DEFAULT_HEADERS = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept-Language": "en-US,en;q=0.9", }

async def shell_cmd(cmd): proc = await asyncio.create_subprocess_shell( cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, ) out, errorz = await proc.communicate() if errorz: if "unavailable videos are hidden" in (errorz.decode("utf-8")).lower(): return out.decode("utf-8") else: return errorz.decode("utf-8") return out.decode("utf-8")

class YouTubeAPI: def init(self): self.base = "https://www.youtube.com/watch?v=" self.regex = r"(?:youtube\.com|youtu\.be)" self.status = "https://www.youtube.com/oembed?url=" self.listbase = "https://youtube.com/playlist?list="

async def exists(self, link: str, videoid: Union[bool, str] = None):
    if videoid:
        link = self.base + link
    return bool(re.search(self.regex, link))

async def url(self, message_1: Message) -> Union[str, None]:
    messages = [message_1]
    if message_1.reply_to_message:
        messages.append(message_1.reply_to_message)
    text = ""
    offset = None
    length = None
    for message in messages:
        if offset:
            break
        if message.entities:
            for entity in message.entities:
                if entity.type == MessageEntityType.URL:
                    text = message.text or message.caption
                    offset, length = entity.offset, entity.length
                    break
        elif message.caption_entities:
            for entity in message.caption_entities:
                if entity.type == MessageEntityType.TEXT_LINK:
                    return entity.url
    if offset is None:
        return None
    return text[offset : offset + length]

async def details(self, link: str, videoid: Union[bool, str] = None):
    if videoid:
        link = self.base + link
    if "&" in link:
        link = link.split("&")[0]
    results = VideosSearch(link, limit=1)
    for result in (await results.next())["result"]:
        title = result["title"]
        duration_min = result["duration"]
        thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        vidid = result["id"]
        duration_sec = int(time_to_seconds(duration_min)) if duration_min else 0
    return title, duration_min, duration_sec, thumbnail, vidid

async def title(self, link: str, videoid: Union[bool, str] = None):
    if videoid:
        link = self.base + link
    if "&" in link:
        link = link.split("&")[0]
    results = VideosSearch(link, limit=1)
    for result in (await results.next())["result"]:
        title = result["title"]
    return title

async def duration(self, link: str, videoid: Union[bool, str] = None):
    if videoid:
        link = self.base + link
    if "&" in link:
        link = link.split("&")[0]
    results = VideosSearch(link, limit=1)
    for result in (await results.next())["result"]:
        duration = result["duration"]
    return duration

async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
    if videoid:
        link = self.base + link
    if "&" in link:
        link = link.split("&")[0]
    results = VideosSearch(link, limit=1)
    for result in (await results.next())["result"]:
        thumbnail = result["thumbnails"][0]["url"].split("?")[0]
    return thumbnail

async def video(self, link: str, videoid: Union[bool, str] = None):
    if videoid:
        link = self.base + link
    if "&" in link:
        link = link.split("&")[0]

    logging.info(f"Preparing video download for: {link}")

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'quiet': True,
        'merge_output_format': 'mp4',
        'cookiefile': 'AdnanXMusic/assets/cookies.txt',
        'writethumbnail': True,
        'http_headers': DEFAULT_HEADERS,
        'postprocessors': [
            {'key': 'EmbedThumbnail'},
            {'key': 'FFmpegMetadata'},
        ],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            file_path = ydl.prepare_filename(info)
            logging.info(f"Downloaded successfully: {file_path}")
            return 1, file_path
    except yt_dlp.DownloadError as e:
        logging.error(f"Download failed: {e}")
        return 0, str(e)

async def download(self, link: str, mystic, video: Union[bool, str] = None, videoid: Union[bool, str] = None, songaudio: Union[bool, str] = None, songvideo: Union[bool, str] = None, format_id: Union[bool, str] = None, title: Union[bool, str] = None) -> str:
    if videoid:
        link = self.base + link
    if "&" in link:
        link = link.split("&")[0]

    loop = asyncio.get_running_loop()

    def download_media():
        ext = 'mp4'
        if songaudio:
            format_selection = 'bestaudio[ext=m4a]/bestaudio'
            ext = 'm4a'
        elif songvideo:
            format_selection = 'bestvideo[height=720][ext=mp4]+bestaudio[ext=m4a]/best[height=720]'
        elif format_id:
            format_selection = f"{format_id}+bestaudio"
        else:
            format_selection = 'bestvideo[height=720][ext=mp4]+bestaudio[ext=m4a]/best'

        output_template = f'downloads/{title if title else "%(id)s"}.{ext}'

        ydl_opts = {
            "format": format_selection,
            "outtmpl": output_template,
            "quiet": True,
            "merge_output_format": ext,
            "cookiefile": "AdnanXMusic/assets/cookies.txt",
            "http_headers": DEFAULT_HEADERS,
            "writethumbnail": True,
            "postprocessors": [
                {"key": "EmbedThumbnail"},
                {"key": "FFmpegMetadata"},
            ],
        }

        if songaudio:
            ydl_opts["postprocessors"].append(
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            )
            ext = 'mp3'

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=True)
                downloaded_file = ydl.prepare_filename(info)
                if songaudio:
                    downloaded_file = downloaded_file.rsplit('.', 1)[0] + '.mp3'
                logging.info(f"Media downloaded successfully: {downloaded_file}")
                return downloaded_file, True
        except Exception as e:
            logging.error(f"Media download failed: {str(e)}")
            return None, False

    downloaded_file, success = await loop.run_in_executor(None, download_media)
    return downloaded_file, success
