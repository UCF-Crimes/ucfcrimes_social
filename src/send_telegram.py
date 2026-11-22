"""Send a crime report photo and caption to Telegram."""

import asyncio
from configparser import SectionProxy
from pathlib import Path

from telegram import Bot


async def _send_photo(settings: SectionProxy, image: Path, message: str) -> None:
    async with Bot(token=settings["BOT_TOKEN"]) as bot:
        with image.open("rb") as photo:
            await bot.send_photo(chat_id=settings["ROOM_ID"], photo=photo, caption=message, read_timeout=20)


def send_telegram(settings: SectionProxy, image: Path, message: str) -> None:
    asyncio.run(_send_photo(settings, image, message))
