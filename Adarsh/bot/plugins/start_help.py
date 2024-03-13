import logging
import datetime
from Adarsh.bot import StreamBot
from Adarsh.vars import Var
from Adarsh.bot.plugins.stream import MY_PASS
from Adarsh.utils.database import Database
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from pyrogram.types import ReplyKeyboardMarkup

logger = logging.getLogger(__name__)
db = Database(Var.DATABASE_URL, Var.name)

if Var.MY_PASS:
    buttonz = ReplyKeyboardMarkup(
        [
            ["start⚡️", "help📚", "login🔑", "DC"],
            ["follow❤️", "ping📡", "status📊", "maintainers😎"]
        ],
        resize_keyboard=True
    )
else:
    buttonz = ReplyKeyboardMarkup(
        [
            ["start⚡️", "help📚", "DC"],
            ["follow❤️", "ping📡", "status📊", "maintainers😎"]
        ],
        resize_keyboard=True
    )

@StreamBot.on_message((filters.command("start") | filters.regex('start⚡️')) & filters.private )
async def start(bot, message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id)
        await bot.send_message(
            Var.BIN_CHANNEL,
            f"#NewUser\n\nUser ID: `{message.from_user.id}`\nUser Name: [{message.from_user.first_name}](tg://user?id={message.from_user.id})\nDatetime: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`"
        )
    if Var.UPDATES_CHANNEL != "None":
        try:
            user = await bot.get_chat_member(Var.UPDATES_CHANNEL, message.chat.id)
            if user.status == "kicked":
                await bot.send_message(
                    chat_id=message.chat.id,
                    text="<i>Sorry Sir, You are banned from using me. Contact the developer</i>",
                    disable_web_page_preview=True
                )
                return
        except UserNotParticipant:
            await StreamBot.send_photo(
                chat_id=message.chat.id,
                photo="https://te.legra.ph/file/5f5e1b0a5752b55c90f02.jpg",
                caption="<i>JOIN CHANNEL TO USE ME🔐</i>",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("Join Updates Channel 🔓", url=f"https://t.me/{Var.UPDATES_CHANNEL}")
                        ]
                    ]
                ),
                
            )
            return
        except Exception:
            await bot.send_message(
                chat_id=message.chat.id,
                text="<i>Something went wrong</i>",
                disable_web_page_preview=True
            )
            return
    await StreamBot.send_photo(
        chat_id=message.chat.id,
        photo ="https://te.legra.ph/file/119729ea3cdce4fefb6a1.jpg",
        caption =f'Hi {message.from_user.mention(style="md")}!,\nI am Telegram File to Link Generator Bot with Channel support.\nSend me any file and get a direct download link and streamable link.!',
        reply_markup=buttonz
    )

@StreamBot.on_message((filters.command("help") | filters.regex('help📚')) & filters.private )
async def help_handler(bot, message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id)
        await bot.send_message(
            Var.BIN_CHANNEL,
            f"#NewUser\n\nUser ID: `{message.from_user.id}`\nUser Name: [{message.from_user.first_name}](tg://user?id={message.from_user.id})\nDatetime: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`"
        )
    if Var.UPDATES_CHANNEL != "None":
        try:
            user = await bot.get_chat_member(Var.UPDATES_CHANNEL, message.chat.id)
            if user.status == "kicked":
                await bot.send_message(
                    chat_id=message.chat.id,
                    text="<i>Sorry Sir, You are banned from using me. Contact the Admin</i>",
                    disable_web_page_preview=True
                )
                return
        except UserNotParticipant:
            await StreamBot.send_photo(
                chat_id=message.chat.id,
                photo="https://te.legra.ph/file/119729ea3cdce4fefb6a1.jpg",
                caption="**JOIN SUPPORT GROUP TO USE this Bot!**\n\nDue to Overload, Only Channel Subscribers can use the Bot!",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("Join Updates Channel 🔓", url=f"https://t.me/{Var.UPDATES_CHANNEL}")
                        ]
                    ]
                ),
                
            )
            return
        except Exception:
            await bot.send_message(
                chat_id=message.chat.id,
                text="Something went Wrong. Contact Admin.",
                disable_web_page_preview=True)
            return
    await message.reply_text(
        text="""<b> Send me any file or video i will give you streamable link and download link.</b>\n
<b> I also support Channels, add me to you Channel and send any media files and see miracle✨ also send /list to know all commands""",        
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("💁‍♂️ DEV", url="https://t.me/iPepkornUpdate")],
                [InlineKeyboardButton("💥 Source Code", url="https://t.me/iPepkornUpdate")]
            ]
        )
    )
    
@StreamBot.on_message((filters.command("logs"))
async def logs(bot, message):
    """Send log file"""
    try:
        await message.reply_document('Logs.txt')
    except Exception as e:
        await message.reply(str(e))

