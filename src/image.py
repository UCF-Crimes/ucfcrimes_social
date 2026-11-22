"""Render the single-report map used by the UCF Crimes social publisher.

Based on the monorepo map code by Jack Sweeney and Ethan Frakes.
"""

from configparser import ConfigParser
from io import BytesIO
from math import isfinite
from os import environ
from pathlib import Path

import staticmaps
from PIL import Image, ImageDraw


def generate_image(crime, destination: Path, config: ConfigParser) -> None:
    carto_key = environ.get("CARTO_API_KEY", "").strip() or config.get("CARTO", "CARTO_API_KEY", fallback="").strip()
    context = staticmaps.Context()
    context.set_tile_provider(staticmaps.TileProvider(
        "cartodb-voyager",
        url_pattern="https://basemaps.cartocdn.com/rastertiles/voyager/$z/$x/$y.png?key=$k",
        api_key=carto_key,
        attribution="Maps (C) CARTO (C) OpenStreetMap.org contributors",
        max_zoom=20,
    ))

    lat, lng = crime["lat"], crime["lng"]
    if lat is None or lng is None or not (isfinite(lat) and isfinite(lng)):
        lat, lng = 28.60, -81.20
    location = staticmaps.create_latlng(lat, lng)
    context.add_object(staticmaps.Marker(location, color=staticmaps.RED, size=12))

    with BytesIO() as overview, BytesIO() as zoomed:
        context.render_cairo(380, 380).write_to_png(overview)
        context.set_zoom(18)
        context.render_cairo(1080, 1080).write_to_png(zoomed)
        overview.seek(0)
        zoomed.seek(0)
        with Image.open(zoomed) as image, Image.open(overview) as inset:
            image.paste(inset, (700, 700))
            draw = ImageDraw.Draw(image)
            draw.line((700, 700, 700, 1080), fill=(0, 0, 0), width=10)
            draw.line((696, 700, 1080, 700), fill=(0, 0, 0), width=10)
            image.save(destination)
