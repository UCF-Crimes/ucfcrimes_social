"""Publish report photos to X."""

from configparser import SectionProxy
from pathlib import Path

import tweepy


def publish(settings: SectionProxy, image_path: Path, message: str, *, place: str) -> None:
    """Upload the photo with alt text and attach it to a post."""
    credentials = {
        "consumer_key": settings["CONSUMER_KEY"],
        "consumer_secret": settings["CONSUMER_SECRET"],
        "access_token": settings["ACCESS_TOKEN"],
        "access_token_secret": settings["ACCESS_TOKEN_SECRET"],
    }

    auth = tweepy.OAuth1UserHandler(**credentials)
    media_api = tweepy.API(auth, wait_on_rate_limit=True)
    media = media_api.media_upload(str(image_path))
    media_api.create_media_metadata(media_id=media.media_id, alt_text=f"Map image over {place}")

    client = tweepy.Client(**credentials)
    client.create_tweet(text=message, media_ids=[media.media_id])
