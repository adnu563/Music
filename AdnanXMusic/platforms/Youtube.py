import asyncio
import os
import logging
import re
from typing import Union
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch
from AdnanXMusic.utils.database import is_on_off
from AdnanXMusic.utils.formatters import time_to_seconds

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, errorz = await proc.communicate()
    if errorz:
        error_message = errorz.decode("utf-8")
        logging.error(f"Error executing shell command: {error_message}")
        if "unavailable videos are hidden" in error_message.lower():
            return out.decode("utf-8")
        else:
            return error_message
    return out.decode("utf-8")


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        try:
            if videoid:
                link = self.base + link
            return bool(re.search(self.regex, link))
        except Exception as e:
            logging.error(f"Error in checking if URL exists: {str(e)}")
            return False

    async def url(self, message_1: Message) -> Union[str, None]:
        try:
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
        except Exception as e:
            logging.error(f"Error extracting URL from message: {str(e)}")
            return None

    async def details(self, link: str, videoid: Union[bool, str] = None):
        try:
            if videoid:
                link = self.base + link
            if "&" in link:
                link = link.split("&")[0]  # Corrected the syntax here
            results = VideosSearch(link, limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
                duration_min = result["duration"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                vidid = result["id"]
                duration_sec = int(time_to_seconds(duration_min)) if duration_min != "None" else 0
            return title, duration_min, duration_sec, thumbnail, vidid
        except Exception as e:
            logging.error(f"Error getting video details: {str(e)}")
            return None, None, None, None, None

    async def title(self, link: str, videoid: Union[bool, str] = None):
        try:
            if videoid:
                link = self.base + link
            if "&" in link:
                link = link.split("&")[0]  # Corrected the syntax here
            results = VideosSearch(link, limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
            return title
        except Exception as e:
            logging.error(f"Error getting video title: {str(e)}")
            return None

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        try:
            if videoid:
                link = self.base + link
            if "&" in link:
                link = link.split("&")[0]  # Corrected the syntax here
            results = VideosSearch(link, limit=1)
            for result in (await results.next())["result"]:
                duration = result["duration"]
            return duration
        except Exception as e:
            logging.error(f"Error getting video duration: {str(e)}")
            return None

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        try:
            if videoid:
                link = self.base + link
            if "&" in link:
                link = link.split("&")[0]  # Corrected the syntax here
            results = VideosSearch(link, limit=1)
            for result in (await results.next())["result"]:
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            return thumbnail
        except Exception as e:
            logging.error(f"Error getting video thumbnail: {str(e)}")
            return None

    async def video(self, link: str, videoid: Union[bool, str] = None):
        try:
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
                'writethumbnail': True,  # Include thumbnail
                'postprocessors': [
                    {'key': 'EmbedThumbnail'},
                    {'key': 'FFmpegMetadata'},
                ],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(link, download=True)
                    file_path = ydl.prepare_filename(info)
                    logging.info(f"Downloaded successfully: {file_path}")
                    return 1, file_path
                except yt_dlp.DownloadError as e:
                    logging.error(f"Download failed: {e}")
                    return 0, str(e)
        except Exception as e:
            logging.error(f"Error in video download: {str(e)}")
            return 0, str(e)

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        try:
            if videoid:
                link = self.listbase + link
            if "&" in link:
                link = link.split("&")[0]
            playlist = await shell_cmd(
                f"yt-dlp -i --get-id --flat-playlist --playlist-end {limit} --skip-download {link} --cookies AdnanXMusic/assets/cookies.txt"
            )
            result = playlist.split("\n")
            result = [key for key in result if key != ""]
            return result
        except Exception as e:
            logging.error(f"Error in playlist processing: {str(e)}")
            return []

    async def track(self, link: str, videoid: Union[bool, str] = None):
        try:
            if videoid:
                link = self.base + link
            if "&" in link:
                link = link.split("&")[0]
            results = VideosSearch(link, limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
                duration_min = result["duration"]
                vidid = result["id"]
                yturl = result["link"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            track_details = {
                "title": title,
                "link": yturl,
                "vidid": vidid,
                "duration_min": duration_min,
                "thumb": thumbnail,
            }
            return track_details, vidid
        except Exception as e:
            logging.error(f"Error fetching track details: {str(e)}")
            return None, None

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        try:
            if videoid:
                link = self.base + link
            if "&" in link:
                link = link.split("&")[0]
            ytdl_opts = {
                "quiet": True,
                "cookiefile": "AdnanXMusic/assets/cookies.txt"
            }
            ydl = yt_dlp.YoutubeDL(ytdl_opts)
            with ydl:
                formats_available = []
                r = ydl.extract_info(link, download=False)
                for format in r["formats"]:
                    try:
                        str(format["format"])
                    except:
                        continue
                    if not "dash" in str(format["format"]).lower():
                        try:
                            format["format"]
                            format["filesize"]
                            format["format_id"]
                            format["ext"]
                            format["format_note"]
                        except:
                            continue
                        formats_available.append(
                            {
                                "format": format["format"],
                                "filesize": format["filesize"],
                                "format_id": format["format_id"],
                                "ext": format["ext"],
                                "format_note": format["format_note"],
                                "yturl": link,
                            }
                        )
            return formats_available, link
        except Exception as e:
            logging.error(f"Error fetching formats: {str(e)}")
            return [], link

    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> str:
        try:
            if videoid:
                link = self.base + link
            if "&" in link:
                link = link.split("&")[0]

            loop = asyncio.get_running_loop()

            def download_media():
                ext = 'mp4'

                # Define specific quality format for 720p explicitly
                if songaudio:
                    format_selection = 'bestaudio[ext=m4a]/bestaudio'
                    ext = 'm4a'
                elif songvideo:
                    format_selection = 'bestvideo[height=720][ext=mp4]+bestaudio[ext=m4a]/best[height=720]'
                elif format_id:
                    format_selection = f"{format_id}+bestaudio"
                else:
                    # Default to best available if no specific condition provided
                    format_selection = 'bestvideo[height=720][ext=mp4]+bestaudio[ext=m4a]/best'

                output_template = f'downloads/{title if title else "%(id)s"}.{ext}'

                ydl_opts = {
                    "format": format_selection,
                    "outtmpl": output_template,
                    "quiet": True,
                    "merge_output_format": ext,
                    "writethumbnail": True,
                    "cookiefile": "AdnanXMusic/assets/cookies.txt",
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
        except Exception as e:
            logging.error(f"Error during download process: {str(e)}")
            return None, False
