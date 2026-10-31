
# Don't Remove Credit Tg - @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import asyncio
import pyrogram

from pyrogram import Client, filters, enums
from pyrogram.errors import (
    FloodWait,
    UserIsBlocked,
    InputUserDeactivated,
    UserAlreadyParticipant,
    InviteHashExpired,
    UsernameNotOccupied,
)
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from config import (
    ERROR_MESSAGE,
    LOGIN_SYSTEM,
    CHANNEL_ID,
    WAITING_TIME,
)
from database.db import db
from TechVJ.strings import HELP_TXT
from bot import TechVJUser


class batch_temp:
    IS_BATCH = {}
    STATUS_TASKS = {}


def status_file(message, kind):
    return f"{message.chat.id}_{message.id}_{kind}status.txt"


def progress(current, total, message, kind):
    if not total:
        return

    try:
        with open(status_file(message, kind), "w", encoding="utf-8") as f:
            f.write(f"{current * 100 / total:.1f}%")
    except OSError:
        pass


async def status_monitor(client, statusfile, status_message, label, stop_event):
    try:
        while not stop_event.is_set():
            if os.path.exists(statusfile):
                try:
                    with open(statusfile, "r", encoding="utf-8") as f:
                        value = f.read().strip()

                    if value:
                        await client.edit_message_text(
                            status_message.chat.id,
                            status_message.id,
                            f"**{label}: {value}**",
                        )
                except Exception:
                    pass

            try:
                await asyncio.wait_for(stop_event.wait(), timeout=5)
            except asyncio.TimeoutError:
                continue

    except asyncio.CancelledError:
        raise


async def start_status(client, statusfile, status_message, label):
    stop_event = asyncio.Event()

    task = asyncio.create_task(
        status_monitor(
            client, statusfile, status_message, label, stop_event
        )
    )

    batch_temp.STATUS_TASKS[statusfile] = (task, stop_event)
    return task


async def stop_status(statusfile):
    item = batch_temp.STATUS_TASKS.pop(statusfile, None)

    if item:
        task, stop_event = item
        stop_event.set()

        if not task.done():
            task.cancel()

        await asyncio.gather(task, return_exceptions=True)

    try:
        if os.path.exists(statusfile):
            os.remove(statusfile)
    except OSError:
        pass


def output_chat(message):
    if CHANNEL_ID:
        try:
            return int(CHANNEL_ID)
        except (TypeError, ValueError):
            pass

    return message.chat.id


async def send_error(client, message, error):
    if ERROR_MESSAGE:
        try:
            await client.send_message(
                message.chat.id,
                f"Error: {str(error)[:3500]}",
                reply_to_message_id=message.id,
            )
        except Exception:
            pass


# ================= START =================

@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):

    if not message.from_user:
        return

    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(
            message.from_user.id,
            message.from_user.first_name
        )

    buttons = [
        [
            InlineKeyboardButton(
                "❣️ Developer",
                url="https://t.me/SumitTripathi"
            )
        ],
        [
            InlineKeyboardButton(
                "🔍 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ",
                url="https://t.me/HeySumit"
            ),
            InlineKeyboardButton(
                "🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ",
                url="https://t.me/HeySumit"
            ),
        ],
    ]

    await client.send_message(
        chat_id=message.chat.id,
        text=(
            f"<b>👋 Hi {message.from_user.mention}, "
            "I am Save Restricted Content Bot, I can send you "
            "restricted content by its post link.\n\n"
            "For downloading restricted content /login first.\n\n"
            "Know how to use bot by - /help</b>"
        ),
        reply_markup=InlineKeyboardMarkup(buttons),
        reply_to_message_id=message.id,
    )


# ================= HELP =================

@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    await client.send_message(
        message.chat.id,
        HELP_TXT
    )


# ================= CANCEL =================

@Client.on_message(filters.command(["cancel"]))
async def send_cancel(client: Client, message: Message):

    if not message.from_user:
        return

    batch_temp.IS_BATCH[message.from_user.id] = True

    await client.send_message(
        message.chat.id,
        "**Cancellation requested.**"
    )


# ================= LINK HANDLER =================

@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message):

    if not message.from_user or not message.text:
        return

    user_id = message.from_user.id
    text = message.text.strip()

    # JOIN CHAT

    if (
        ("https://t.me/+" in text or
         "https://t.me/joinchat/" in text)
        and LOGIN_SYSTEM is False
    ):

        if TechVJUser is None:
            await message.reply("**String Session is not Set**")
            return

        try:
            await TechVJUser.join_chat(text)
            await message.reply("Chat Joined")

        except UserAlreadyParticipant:
            await message.reply("Chat already Joined")

        except InviteHashExpired:
            await message.reply("Invalid Link")

        except Exception as e:
            await send_error(client, message, e)

        return

    if "https://t.me/" not in text:
        return

    if batch_temp.IS_BATCH.get(user_id, True) is False:
        await message.reply(
            "**One Task Is Already Processing. Wait For Complete It. "
            "If You Want To Cancel This Task Then Use - /cancel**"
        )
        return

    # PARSE LINK

    try:
        datas = text.split("/")
        temp = datas[-1].replace("?single", "").split("-")

        from_id = int(temp[0].strip())
        to_id = int(temp[1].strip()) if len(temp) > 1 else from_id

        if to_id < from_id:
            raise ValueError("Invalid message ID range")

        if to_id - from_id > 10000:
            raise ValueError("Batch is too large")

    except Exception:
        await message.reply(
            "**Invalid Telegram post link. Please send a valid link.**"
        )
        return

    acc = None
    owns_acc = False

    batch_temp.IS_BATCH[user_id] = False

    try:

        if LOGIN_SYSTEM:

            user_data = await db.get_session(user_id)

            if user_data is None:
                await message.reply(
                    "**For Downloading Restricted Content "
                    "You Have To /login First.**"
                )
                return

            api_id = int(await db.get_api_id(user_id))
            api_hash = await db.get_api_hash(user_id)

            acc = Client(
                f"saverestricted_{user_id}",
                session_string=user_data,
                api_hash=api_hash,
                api_id=api_id,
                in_memory=True,
            )

            await acc.connect()
            owns_acc = True

        else:

            if TechVJUser is None:
                await message.reply("**String Session is not Set**")
                return

            acc = TechVJUser

        # PROCESS BATCH

        for msg_id in range(from_id, to_id + 1):

            if batch_temp.IS_BATCH.get(user_id, False):
                break

            try:

                # PRIVATE CHANNEL

                if "https://t.me/c/" in text:

                    if len(datas) < 5:
                        raise ValueError("Invalid private channel link")

                    chat_id = int("-100" + datas[4])

                    await handle_private(
                        client, acc, message, chat_id, msg_id
                    )

                # BOT LINK

                elif "https://t.me/b/" in text:

                    if len(datas) < 5:
                        raise ValueError("Invalid bot message link")

                    username = datas[4]

                    await handle_private(
                        client, acc, message, username, msg_id
                    )

                # PUBLIC LINK

                else:

                    if len(datas) < 4:
                        raise ValueError("Invalid public channel link")

                    username = datas[3].split("?")[0]

                    try:
                        source_message = await client.get_messages(
                            username, msg_id
                        )

                    except UsernameNotOccupied:
                        await message.reply(
                            "The username is not occupied by anyone"
                        )
                        break

                    try:

                        if source_message and not source_message.empty:
                            await client.copy_message(
                                message.chat.id,
                                source_message.chat.id,
                                source_message.id,
                                reply_to_message_id=message.id,
                            )

                    except Exception:
                        await handle_private(
                            client, acc, message, username, msg_id
                        )

            except asyncio.CancelledError:
                raise

            except Exception as e:
                await send_error(client, message, e)

            if (
                msg_id < to_id
                and not batch_temp.IS_BATCH.get(user_id, False)
            ):
                await asyncio.sleep(max(0, WAITING_TIME))

    except asyncio.CancelledError:
        raise

    except Exception as e:
        await send_error(client, message, e)

    finally:

        if owns_acc and acc is not None:
            try:
                if acc.is_connected:
                    await acc.disconnect()
            except Exception:
                pass

        batch_temp.IS_BATCH[user_id] = True


# ================= PRIVATE MEDIA HANDLER =================

async def handle_private(
    client: Client,
    acc,
    message: Message,
    chatid,
    msgid: int
):

    if batch_temp.IS_BATCH.get(message.from_user.id, False):
        return

    msg = await acc.get_messages(chatid, msgid)

    if not msg or msg.empty:
        return

    msg_type = get_message_type(msg)

    if not msg_type:
        return

    destination = output_chat(message)

    # TEXT MESSAGE

    if msg_type == "Text":

        try:
            await client.send_message(
                destination,
                msg.text,
                entities=msg.entities,
                reply_to_message_id=message.id,
            )

        except Exception as e:
            await send_error(client, message, e)

        return

    status_message = await client.send_message(
        message.chat.id,
        "**Downloading...**",
        reply_to_message_id=message.id,
    )

    down_file = status_file(message, "down")
    up_file = status_file(message, "up")

    downloaded_file = None
    thumb_file = None

    await start_status(
        client, down_file, status_message, "Downloaded"
    )

    try:

        # DOWNLOAD

        downloaded_file = await acc.download_media(
            msg,
            progress=progress,
            progress_args=[message, "down"],
        )

        await stop_status(down_file)

        if not downloaded_file or not os.path.exists(downloaded_file):
            raise RuntimeError(
                "Download failed: media file was not created"
            )

        if batch_temp.IS_BATCH.get(message.from_user.id, False):
            return

        await start_status(
            client, up_file, status_message, "Uploaded"
        )

        caption = msg.caption or None

        common = {
            "caption": caption,
            "reply_to_message_id": message.id,
            "parse_mode": enums.ParseMode.HTML,
        }

        # DOCUMENT

        if msg_type == "Document":

            try:
                if msg.document.thumbs:
                    thumb_file = await acc.download_media(
                        msg.document.thumbs[0].file_id
                    )
            except Exception:
                thumb_file = None

            await client.send_document(
                destination,
                downloaded_file,
                thumb=thumb_file,
                progress=progress,
                progress_args=[message, "up"],
                **common,
            )

        # VIDEO

        elif msg_type == "Video":

            try:
                if msg.video.thumbs:
                    thumb_file = await acc.download_media(
                        msg.video.thumbs[0].file_id
                    )
            except Exception:
                thumb_file = None

            await client.send_video(
                destination,
                downloaded_file,
                duration=msg.video.duration,
                width=msg.video.width,
                height=msg.video.height,
                thumb=thumb_file,
                progress=progress,
                progress_args=[message, "up"],
                **common,
            )

        # ANIMATION

        elif msg_type == "Animation":

            await client.send_animation(
                destination,
                downloaded_file,
                caption=caption,
                reply_to_message_id=message.id,
                parse_mode=enums.ParseMode.HTML,
            )

        # STICKER

        elif msg_type == "Sticker":

            await client.send_sticker(
                destination,
                downloaded_file,
                reply_to_message_id=message.id,
            )

        # VOICE

        elif msg_type == "Voice":

            await client.send_voice(
                destination,
                downloaded_file,
                caption=caption,
                reply_to_message_id=message.id,
                parse_mode=enums.ParseMode.HTML,
                progress=progress,
                progress_args=[message, "up"],
            )

        # AUDIO

        elif msg_type == "Audio":

            try:
                if msg.audio.thumbs:
                    thumb_file = await acc.download_media(
                        msg.audio.thumbs[0].file_id
                    )
            except Exception:
                thumb_file = None

            await client.send_audio(
                destination,
                downloaded_file,
                thumb=thumb_file,
                **common,
                progress=progress,
                progress_args=[message, "up"],
            )

        # PHOTO

        elif msg_type == "Photo":

            await client.send_photo(
                destination,
                downloaded_file,
                **common,
            )

    except asyncio.CancelledError:
        raise

    except Exception as e:
        await send_error(client, message, e)

    finally:

        await stop_status(down_file)
        await stop_status(up_file)

        for path in (thumb_file, downloaded_file):

            if (
                path
                and isinstance(path, str)
                and os.path.isfile(path)
            ):

                try:
                    os.remove(path)
                except OSError:
                    pass

        try:
            await status_message.delete()
        except Exception:
            pass


# ================= MESSAGE TYPE =================

def get_message_type(
    msg: pyrogram.types.messages_and_media.message.Message
):

    if msg.document:
        return "Document"

    if msg.video:
        return "Video"

    if msg.animation:
        return "Animation"

    if msg.sticker:
        return "Sticker"

    if msg.voice:
        return "Voice"

    if msg.audio:
        return "Audio"

    if msg.photo:
        return "Photo"

    if msg.text:
        return "Text"

    return None


# Don't Remove Credit @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01
