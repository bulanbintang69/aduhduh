import time
import datetime

from hydrogram import Client, filters
from hydrogram.helpers import ikb
from hydrogram.raw import functions
from hydrogram.types import CallbackQuery, Message

from bot import helper_buttons, logger

startup_time = datetime.datetime.now()

async def ping_function(client: Client) -> str:
    start = time.time()
    await client.invoke(functions.Ping(ping_id=0))
    return f"{(time.time() - start)*1000:.2f} ms"

def get_full_uptime_block() -> str:
    now = datetime.datetime.now()
    total = int((now - startup_time).total_seconds())

    weeks, rem = divmod(total, 604800)
    days, rem  = divmod(rem, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)

    since = startup_time.strftime("%B %d, %Y at %I:%M %p")
    parts = []
    if weeks:   parts.append(f"{weeks} Bulan{'s' if weeks>1 else ''}")
    if days:    parts.append(f"{days} Hari{'s' if days>1 else ''}")
    if hours:   parts.append(f"{hours} Jam{'s' if hours>1 else ''}")
    if minutes: parts.append(f"{minutes} Menit{'s' if minutes>1 else ''}")
    if seconds: parts.append(f"{seconds} Detik{'s' if seconds>1 else ''}")
    total_str = ", ".join(parts[:5])

    return (
        "```"
        f"Latency      : {{latency}}\n\n"
        f"Uptime Since : {since}\n"
        f"Uptime Total : {total_str}"
        "```"
    )

@Client.on_message(filters.private & filters.command("ping"))
async def ping_handler(client: Client, message: Message) -> None:
    try:
        latency = await ping_function(client)
        block = get_full_uptime_block().format(latency=latency)
        await message.reply_text(
            block,
            parse_mode="Markdown",   # lowercase
            quote=True,
            reply_markup=ikb(helper_buttons.Ping),
            disable_web_page_preview=True,
        )
    except Exception as exc:
        logger.error(f"Ping/Uptime Error: {exc}")
        await message.reply_text(
            "```Error retrieving ping/uptime```",
            parse_mode="Markdown",
            quote=True
        )

@Client.on_callback_query(filters.regex(r"\bping\b"))
async def ping_callback(client: Client, query: CallbackQuery) -> None:
    await query.answer()
    await query.message.edit_text(
        "```Refreshing…```",
        parse_mode="Markdown"
    )
    try:
        latency = await ping_function(client)
        block = get_full_uptime_block().format(latency=latency)
        await query.message.edit_text(
            block,
            parse_mode="Markdown",  # lowercase
            reply_markup=ikb(helper_buttons.Ping),
            disable_web_page_preview=True,
        )
    except Exception as exc:
        logger.error(f"Ping/Uptime Callback Error: {exc}")
        await query.message.edit_text(
            "```Error retrieving ping/uptime```",
            parse_mode="Markdown"
        )
