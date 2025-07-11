import random
import string

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InputMediaPhoto, Message
from pytgcalls.exceptions import NoActiveGroupCall

import config
from AdnanXMusic import Apple, Resso, SoundCloud, Spotify, Telegram, YouTube, app
from AdnanXMusic.core.call import Adnany
from AdnanXMusic.utils import seconds_to_min, time_to_seconds
from AdnanXMusic.utils.channelplay import get_channeplayCB
from AdnanXMusic.utils.decorators.language import languageCB
from AdnanXMusic.utils.decorators.play import PlayWrapper
from AdnanXMusic.utils.formatters import formats
from AdnanXMusic.utils.inline import (
    botplaylist_markup,
    livestream_markup,
    playlist_markup,
    slider_markup,
    track_markup,
)
from AdnanXMusic.utils.logger import play_logs
from AdnanXMusic.utils.stream.stream import stream
from config import BANNED_USERS, lyrical


@app.on_message(
    filters.command([
        "play", "vplay", "cplay", "cvplay",
        "playforce", "vplayforce", "cplayforce", "cvplayforce"
    ])
    & filters.group
    & ~BANNED_USERS
)
@PlayWrapper
async def play_commnd(
    client,
    message: Message,
    _,
    chat_id,
    video,
    channel,
    playmode,
    url,
    fplay,
):
    mystic = await message.reply_text(
        _["play_2"].format(channel) if channel else _["play_1"]
    )

    plist_id = None
    plist_type = None
    spotify = None
    img = None
    cap = None

    if len(message.command) < 2:
        buttons = botplaylist_markup(_)
        return await mystic.edit_text(
            _["play_18"],
            reply_markup=InlineKeyboardMarkup(buttons),
        )

    query = message.text.split(None, 1)[1]
    if "-v" in query:
        query = query.replace("-v", "")

    try:
        details, track_id = await YouTube.track(query)
        if not details:
            return await mystic.edit_text(_["play_3"])
    except Exception as e:
        return await mystic.edit_text(f"{_['play_3']}\n\n{type(e).__name__}: {e}")

    streamtype = "youtube"
    duration_min = details.get("duration_min")

    if str(playmode) == "Direct":
        if not plist_type:
            if not duration_min:
                buttons = livestream_markup(
                    _,
                    track_id,
                    message.from_user.id,
                    "v" if video else "a",
                    "c" if channel else "g",
                    "f" if fplay else "d",
                )
                return await mystic.edit_text(
                    _["play_13"],
                    reply_markup=InlineKeyboardMarkup(buttons),
                )
            duration_sec = time_to_seconds(duration_min)
            if duration_sec > config.DURATION_LIMIT:
                return await mystic.edit_text(
                    _["play_6"].format(config.DURATION_LIMIT_MIN, app.mention)
                )

        try:
            await stream(
                _,
                mystic,
                message.from_user.id,
                details,
                chat_id,
                message.from_user.first_name,
                message.chat.id,
                video=video,
                streamtype=streamtype,
                spotify=spotify,
                forceplay=fplay,
            )
        except Exception as e:
            ex_type = type(e).__name__
            err = e if ex_type == "AssistantErr" else _["general_2"].format(ex_type)
            return await mystic.edit_text(err)

        await mystic.delete()
        return await play_logs(message, streamtype=streamtype)

    else:
        ran_hash = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=10)
        )
        lyrical[ran_hash] = plist_id or ""
        buttons = slider_markup(
            _,
            track_id,
            message.from_user.id,
            query,
            0,
            "c" if channel else "g",
            "f" if fplay else "d",
        )
        await mystic.delete()
        await message.reply_photo(
            photo=details["thumb"],
            caption=_["play_10"].format(
                details["title"].title(),
                details["duration_min"],
            ),
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        return await play_logs(message, streamtype="Searched on Youtube")
