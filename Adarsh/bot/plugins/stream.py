import os
import asyncio
from asyncio import TimeoutError
from urllib.parse import quote_plus
from datetime import datetime
from pyrogram import filters, Client
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from Adarsh.bot import StreamBot
from Adarsh.utils.database import Database
from Adarsh.utils.human_readable import humanbytes
from Adarsh.vars import Var
from Adarsh.utils.file_properties import get_name, get_hash, get_media_file_size

db = Database(Var.DATABASE_URL, Var.name)
pass_db = Database(Var.DATABASE_URL, "ag_passwords")

MY_PASS = os.environ.get("MY_PASS", None)


@StreamBot.on_message((filters.regex("login🔑") | filters.command("login")), group=4)
async def login_handler(c: Client, m: Message):
    try:
        try:
            ag = await m.reply_text("Now send me the password.\n\nIf you don't know, check the MY_PASS variable in Heroku.\n\n(You can use /cancel command to cancel the process)")
            _text = await c.listen(m.chat.id, filters=filters.text, timeout=90)
            if _text.text:
                textp = _text.text
                if textp == "/cancel":
                    await ag.edit("Process Cancelled Successfully")
                    return
            else:
                return
        except TimeoutError:
            await ag.edit("I can't wait any longer for the password, please try again.")
            return
        if textp == MY_PASS:
            await pass_db.add_user_pass(m.chat.id, textp)
            ag_text = "Yeah! You entered the password correctly."
        else:
            ag_text = "Wrong password, please try again."
        await ag.edit(ag_text)
    except Exception as e:
        print(e)


@StreamBot.on_message((filters.private) & (filters.document | filters.video | filters.audio | filters.photo), group=4)
async def private_receive_handler(c: Client, m: Message):
    if MY_PASS:
        check_pass = await pass_db.get_user_pass(m.chat.id)
        if check_pass is None:
            await m.reply_text("Please login first using /login command. If you don't know the password, request it from the developer.")
            return
        if check_pass != MY_PASS:
            await pass_db.delete_user(m.chat.id)
            return
    if not await db.is_user_exist(m.from_user.id):
        await db.add_user(m.from_user.id)
        await c.send_message(
            Var.BIN_CHANNEL,
            f"#NewUser\n\nUser ID: `{m.from_user.id}`\nUser Name: [{m.from_user.first_name}](tg://user?id={m.from_user.id})\nDatetime: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`"
        )
    if Var.UPDATES_CHANNEL != "None":
        try:
            user = await c.get_chat_member(Var.UPDATES_CHANNEL, m.chat.id)
            if user.status == "kicked":
                await c.send_message(
                    chat_id=m.chat.id,
                    text="You are banned!\n\nContact developer [VJ](https://t.me/vj_bots) for assistance.",
                    disable_web_page_preview=True
                )
                return
        except UserNotParticipant:
            await c.send_message(
                chat_id=m.chat.id,
                text="<i>Join the Update Channel to use me 🔐</i>",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("Join Update Channel 🔓", url=f"https://t.me/{Var.UPDATES_CHANNEL}")
                        ]
                    ]
                ),
            )
            return
        except Exception as e:
            await m.reply_text(str(e))
            await c.send_message(
                chat_id=m.chat.id,
                text="Something went wrong! Please contact my admin.",
                disable_web_page_preview=True
            )
            return
    try:
        log_msg = await m.forward(chat_id=Var.BIN_CHANNEL)
        stream_link = f"{Var.URL}watch/{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
        online_link = f"{Var.URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"

        msg_text = """<i><u>𝗬𝗼𝘂𝗿 𝗟𝗶𝗻𝗸 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱!</u></i>\n\n<b>📂 File Name :</b> <i>{}</i>\n\n<b>📦 File Size :</b> <i>{}</i>\n\n<b>📥 Download :</b> <i>{}</i>\n\n<b>🖥 Watch :</b> <i>{}</i>\n\n<b>🚸 Nᴏᴛᴇ : LINK WON'T EXPIRE TILL I DELETE</b>"""

        await log_msg.reply_text(text=f"#Requested_By: [{m.from_user.first_name}](tg://user?id={m.from_user.id})\nUser ID: `{m.from_user.id}`\n\nDownload link:\n{online_link}\n\nStream link:\n{stream_link}", disable_web_page_preview=True, quote=True)
        await m.reply_text(
            text=msg_text.format(get_name(log_msg), humanbytes(get_media_file_size(m)), online_link, stream_link),
            quote=True,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Stream 🖥", url=stream_link),  # Stream Link
                        InlineKeyboardButton("Download 📥", url=online_link)  # Download Link
                    ]
                ]
            )
        )
    except FloodWait as e:
        print(f"Sleeping for {str(e.x)}s")
        await asyncio.sleep(e.x)
        await c.send_message(
            chat_id=Var.BIN_CHANNEL,
            text=f"Got FloodWait of {str(e.x)}s From [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n\nUser ID: <`{str(m.from_user.id)}`",
            disable_web_page_preview=True
        )


@StreamBot.on_message(filters.channel & ~filters.group & (filters.document | filters.video | filters.photo) & ~filters.forwarded, group=-1)
async def channel_receive_handler(bot, broadcast):
    if MY_PASS:
        check_pass = await pass_db.get_user_pass(broadcast.chat.id)
        if check_pass is None:
            await broadcast.reply_text("Please login first using /login command. If you don't know the password, request it from the developer!")
            return
        if check_pass != MY_PASS:
            await broadcast.reply_text("Wrong password, login again")
            await pass_db.delete_user(broadcast.chat.id)
            return
    if int(broadcast.chat.id) in Var.BANNED_CHANNELS:
        await bot.leave_chat(broadcast.chat.id)
        return
    try:
        log_msg = await broadcast.forward(chat_id=Var.BIN_CHANNEL)
        stream_link = f"{Var.URL}watch/{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
        online_link = f"{Var.URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
        await log_msg.reply_text(
            text=f"Channel Name: `{broadcast.chat.title}`\nChannel ID: `{broadcast.chat.id}`\nDownload link:\n{online_link}\n\nStream link:\n{stream_link}",
            quote=True
        )
        await bot.edit_message_reply_markup(
            chat_id=broadcast.chat.id,
            message_id=broadcast.id,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🖥 Stream", url=stream_link),
                        InlineKeyboardButton("Download 📥", url=online_link)
                    ]
                ]
            )
        )
    except FloodWait as w:
        print(f"Sleeping for {str(w.x)}s")
        await asyncio.sleep(w.x)
        await bot.send_message(
            chat_id=Var.BIN_CHANNEL,
            text=f"Got FloodWait of {str(w.x)}s From {broadcast.chat.title}\n\nChannel ID: `{str(broadcast.chat.id)}`",
            disable_web_page_preview=True
        )
    except Exception as e:
        await bot.send_message(
            chat_id=Var.BIN_CHANNEL,
            text=f"#Error: `{e}`",
            disable_web_page_preview=True
        )
        print(f"Can't Edit Broadcast Message!\nError: Give me edit permission in updates and bin Channel!{e}")

