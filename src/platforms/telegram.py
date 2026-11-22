"""Publish report photos to Telegram."""

import asyncio
from configparser import SectionProxy
from pathlib import Path

from telegram import Bot


async def _publish_photo(settings: SectionProxy, image_path: Path, message: str) -> None:
    async with Bot(token=settings["BOT_TOKEN"]) as bot:
        with image_path.open("rb") as photo:
            await bot.send_photo(
                chat_id=settings["ROOM_ID"],
                photo=photo,
                caption=message,
                read_timeout=20,
            )


def publish(settings: SectionProxy, image_path: Path, message: str) -> None:
    """Publish a photo and caption to the configured Telegram chat."""
    asyncio.run(_publish_photo(settings, image_path, message))
