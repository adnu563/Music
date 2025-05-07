from pyrogram.types import (
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from youtubesearchpython.__future__ import VideosSearch

from AdnanXMusic import app
from config import BANNED_USERS


def get_cmd(duration):
    return "/play"  # You can modify this if you want other commands based on duration


@app.on_inline_query(~BANNED_USERS)
async def search(client, query):
    answers = []
    string = query.query.strip()

    if string == "":
        await client.answer_inline_query(
            query.id,
            results=answers,
            switch_pm_text="Search a YouTube video",
            switch_pm_parameter="help",
            cache_time=0
        )
        return

    videosSearch = VideosSearch(string.lower(), limit=20)
    result = (await videosSearch.next()).get("result")
    for v in result:
        title = v["title"]
        duration = v["duration"]
        views = v["viewCount"]["short"]
        video_id = v["id"]
        link = f"https://www.youtube.com/watch?v={video_id}"
        play_cmd = f"{get_cmd(duration)} {link}"

        answers.append(
            InlineQueryResultArticle(
                title=title,
                description=f"Duration: {duration} | Views: {views}",
                input_message_content=InputTextMessageContent(play_cmd),
                thumb_url=v["thumbnails"][0]["url"]
            )
        )

    try:
        await client.answer_inline_query(query.id, results=answers, cache_time=0)
    except:
        await client.answer_inline_query(
            query.id,
            results=[],
            switch_pm_text="Nothing found",
            switch_pm_parameter="",
            cache_time=0
        )
