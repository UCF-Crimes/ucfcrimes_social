"""Publish report photos to Facebook and Instagram."""

from configparser import SectionProxy
from contextlib import nullcontext
from pathlib import Path
from time import sleep

import requests

GRAPH_URL = "https://graph.facebook.com"
MAX_ATTEMPTS = 5
REQUEST_TIMEOUT = 30
RETRY_DELAY = 5


def _request_json(
    method: str,
    url: str,
    *,
    data: dict[str, str] | None = None,
    params: dict[str, str] | None = None,
    image_path: Path | None = None,
) -> dict:
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            image_file = image_path.open("rb") if image_path is not None else nullcontext()
            with image_file as photo:
                files = {"image": (image_path.name, photo, "image/png")} if image_path is not None else None
                response = requests.request(
                    method,
                    url,
                    data=data,
                    params=params,
                    files=files,
                    timeout=REQUEST_TIMEOUT,
                )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as error:
            status = error.response.status_code if error.response is not None else None
            retryable = status == 429 or (method == "GET" and (status is None or status >= 500))
            if not retryable or attempt == MAX_ATTEMPTS:
                raise
            sleep(RETRY_DELAY)


def publish(settings: SectionProxy, image_path: Path, message: str) -> None:
    """Upload the photo to Facebook and publish its image URL on Instagram."""
    version = settings.get("GRAPH_API_VERSION", "").strip().rstrip("/")
    graph_url = f"{GRAPH_URL}/{version}" if version else GRAPH_URL
    token = settings["ACCESS_TOKEN"]

    facebook_photo = _request_json(
        "POST",
        f"{graph_url}/{settings['FB_PAGE_ID']}/photos",
        data={"message": message, "access_token": token},
        image_path=image_path,
    )
    photo_details = _request_json(
        "GET",
        f"{graph_url}/{facebook_photo['id']}",
        params={"fields": "images", "access_token": token},
    )
    instagram_url = f"{graph_url}/{settings['IG_USER_ID']}"
    container = _request_json(
        "POST",
        f"{instagram_url}/media",
        data={
            "caption": message,
            "image_url": photo_details["images"][0]["source"],
            "access_token": token,
        },
    )
    _request_json(
        "POST",
        f"{instagram_url}/media_publish",
        data={"creation_id": container["id"], "access_token": token},
    )
