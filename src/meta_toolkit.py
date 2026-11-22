"""Publish a Facebook photo and use its public image URL for Instagram."""

from configparser import SectionProxy
from pathlib import Path
from time import sleep

import requests


def graph_request(method: str, url: str, **kwargs):
    for attempt in range(5):
        try:
            response = requests.request(method, url, timeout=30, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as error:
            status = error.response.status_code if error.response is not None else None
            retryable = status == 429 or (method == "GET" and (status is None or status >= 500))
            if not retryable or attempt == 4:
                raise
            sleep(5)
            if "files" in kwargs:
                kwargs["files"]["image"][1].seek(0)


def post_to_meta_both(settings: SectionProxy, image: Path, message: str) -> None:
    root = "https://graph.facebook.com"
    if version := settings.get("GRAPH_API_VERSION", "").strip():
        root = f"{root}/{version.rstrip('/')}"

    token = settings["ACCESS_TOKEN"]
    with image.open("rb") as photo:
        facebook_post = graph_request(
            "POST", f"{root}/{settings['FB_PAGE_ID']}/photos",
            data={"message": message, "access_token": token},
            files={"image": (image.name, photo, "image/png")},
        )
    facebook_image = graph_request(
        "GET", f"{root}/{facebook_post['id']}",
        params={"fields": "images", "access_token": token},
    )
    user_url = f"{root}/{settings['IG_USER_ID']}"
    container = graph_request(
        "POST", f"{user_url}/media",
        data={
            "caption": message,
            "image_url": facebook_image["images"][0]["source"],
            "access_token": token,
        },
    )
    graph_request(
        "POST", f"{user_url}/media_publish",
        data={"creation_id": container["id"], "access_token": token},
    )
