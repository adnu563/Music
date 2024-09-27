import asyncio
import os
import logging
import re  # Importing the re module
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
        if "unavailable videos are hidden" in (errorz.decode("utf-8")).lower():
            return out.decode("utf-8")
        else:
            return errorz.decode("utf-8")
    return out.decode("utf-8")


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="

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
            link = link.split("&")[0]  # Corrected the syntax here
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            vidid = result["id"]
            if str(duration_min) == "None":
                duration_sec = 0
            else:
                duration_sec = int(time_to_seconds(duration_min))
        return title, duration_min, duration_sec, thumbnail, vidid

    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]  # Corrected the syntax here
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
        return title

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]  # Corrected the syntax here
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            duration = result["duration"]
        return duration

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]  # Corrected the syntax here
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        return thumbnail

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]  # Corrected the syntax here

        logging.info(f"Starting video download for link: {link}")

        # List available formats
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'cookies': 'AdnanXMusic/assets/cookies.txt',
            'quiet': True,
            'listformats': True
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.extract_info(link, download=False)
                formats = result.get('formats', [])

                # Check if the desired format is available
                for fmt in formats:
                    if fmt['ext'] == 'mkv':
                        logging.info(f"Available format found: {fmt['format_id']}")
                        ydl_opts['format'] = fmt['format_id']
                        break
                else:
                    logging.warning("Desired format (mkv) not found, using default best format.")
                    ydl_opts['format'] = 'best'

                logging.info("Proceeding with download...")
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([link])
                    logging.info("Video download completed successfully.")

        except yt_dlp.DownloadError as e:
            logging.error(f"Download failed: {str(e)}")
            return 0, str(e)

        return 1, "Download complete."

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]  # Corrected the syntax here
        playlist = await shell_cmd(
            f"yt-dlp -i --get-id --flat-playlist --playlist-end {limit} --skip-download {link} --cookies AdnanXMusic/assets/cookies.txt"
        )
        try:
            result = playlist.split("\n")
            for key in result:
                if key == "":
                    result.remove(key)
        except:
            result = []
        return result

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]  # Corrected the syntax here
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

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]  # Corrected the syntax here
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

    async def slider(
        self,
        link: str,
        query_type: int,
        videoid: Union[bool, str] = None,
    ):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]  # Corrected the syntax here
        a = VideosSearch(link, limit=10)
        result = (await a.next()).get("result")
        title = result[query_type]["title"]
        duration_min = result[query_type]["duration"]
        vidid = result[query_type]["id"]
        thumbnail = result[query_type]["thumbnails"][0]["url"].split("?")[0]
        return title, duration_min, thumbnail, vidid

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
            loop = asyncio.get_running_loop()

            def audio_dl():
                logging.info("Starting audio download...")
                ydl_optssx = {
                    "format": "bestaudio/best",
                    "outtmpl": "downloads/%(id)s.%(ext)s",
                    "geo_bypass": True,
                    "nocheckcertificate": True,
                    "quiet": True,
                    "no_warnings": True,
                    "cookiefile": "AdnanXMusic/assets/cookies.txt",
                }
                try:
                    x = yt_dlp.YoutubeDL(ydl_optssx)
                    info = x.extract_info(link, False)
                    xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")
                    
                    if os.path.exists(xyz):
                        return xyz
                    
                    x.download([link])
                    return xyz
                except Exception as e:
                    logging.error(f"Audio download failed: {str(e)}")
                    return None

            def video_dl():
                logging.info("Starting MKV video download...")
                ydl_optssx = {
                    "format": "(bestvideo[ext=mkv])+bestaudio/best",
                    "outtmpl": "downloads/%(id)s.%(ext)s",
                    "geo_bypass": True,
                    "nocheckcertificate": True,
                    "quiet": True,
                    "no_warnings": True,
                    "cookiefile": "AdnanXMusic/assets/cookies.txt",
                }
                try:
                    x = yt_dlp.YoutubeDL(ydl_optssx)
                    info = x.extract_info(link, False)
                    xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")
                    if os.path.exists(xyz):
                        return xyz
                    x.download([link])
                    return xyz
                except Exception as e:
                    logging.error(f"Video download failed: {str(e)}")
                    return None

            def song_video_dl():
                formats = f"{format_id}+140"
                fpath = f"downloads/{title}.mkv"
                ydl_optssx = {
                    "format": formats,
                    "outtmpl": fpath,
                    "geo_bypass": True,
                    "nocheckcertificate": True,
                    "quiet": True,
                    "no_warnings": True,
                    "prefer_ffmpeg": True,
                    "merge_output_format": "mkv",
                    "cookiefile": "AdnanXMusic/assets/cookies.txt",
                }
                try:
                    x = yt_dlp.YoutubeDL(ydl_optssx)
                    x.download([link])
                except Exception as e:
                    logging.error(f"Song video download failed: {str(e)}")
                    return None

            def song_audio_dl():
                fpath = f"downloads/{title}.%(ext)s"
                ydl_optssx = {
                    "format": format_id,
                    "outtmpl": fpath,
                    "geo_bypass": True,
                    "nocheckcertificate": True,
                    "quiet": True,
                    "no_warnings": True,
                    "prefer_ffmpeg": True,
                    "postprocessors": [
                        {
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": "192",
                        }
                    ],
                    "cookiefile": "AdnanXMusic/assets/cookies.txt",
                }
                try:
                    x = yt_dlp.YoutubeDL(ydl_optssx)
                    x.download([link])
                except Exception as e:
                    logging.error(f"Song audio download failed: {str(e)}")
                    return None

            def auto_detect_and_download():
                ydl_optssx = {
                    "format": "bestaudio[ext=m4a]/bestvideo+bestaudio/best",
                    "outtmpl": "downloads/%(id)s.%(ext)s",
                    "geo_bypass": True,
                    "nocheckcertificate": True,
                    "quiet": True,
                    "no_warnings": True,
                    "cookiefile": "AdnanXMusic/assets/cookies.txt",
                }
                try:
                    x = yt_dlp.YoutubeDL(ydl_optssx)
                    info = x.extract_info(link, False)
                    ext = info.get('ext', '')
                    is_audio = ext in ['m4a', 'mp3', 'aac']
                    
                    if is_audio:
                        logging.info("Audio file detected, downloading as audio.")
                        return audio_dl()
                    else:
                        logging.info("Video file detected, downloading as video.")
                        return video_dl()
                except Exception as e:
                    logging.error(f"Auto-detect download failed: {str(e)}")
                    return None

            if songvideo:
                await loop.run_in_executor(None, song_video_dl)
                fpath = f"downloads/{title}.mkv"
                return fpath
            elif songaudio:
                downloaded_file = await loop.run_in_executor(None, audio_dl)
                if downloaded_file:
                    return downloaded_file
                else:
                    return None, False
            elif video or format_id:
                direct = True
                downloaded_file = await loop.run_in_executor(None, video_dl)
                if downloaded_file:
                    return downloaded_file, direct
                else:
                    return None, False
            else:
                downloaded_file = await loop.run_in_executor(None, auto_detect_and_download)
                if downloaded_file:
                    return downloaded_file, True
                else:
                    return None, False

        except Exception as e:
            logging.error(f"An error occurred during download: {str(e)}")
            return None, False

        # Handling the IndexError by checking if message contains text after the command
        try:
            if len(message.text.split(None, 1)) > 1:
                query = message.text.split(None, 1)[1]
                response = f"<b>‣ ǫᴜᴇʀʏ :</b> {query}"
            else:
                response = "<b>‣ ǫᴜᴇʀʏ :</b> No query provided."
        except IndexError:
            response = "<b>‣ ǫᴜᴇʀʏ :</b> No query provided."
