"""Format a database report and publish it to the enabled social platforms."""

from configparser import ConfigParser
from datetime import datetime
from functools import partial
from pathlib import Path
from tempfile import TemporaryDirectory

from image import generate_image
from platforms import meta, telegram, x
from string_adjustments import get_emojis, titlize


def format_datetime(value: datetime | str) -> str:
    """Format a report timestamp for the post caption."""
    parsed = value if isinstance(value, datetime) else datetime.fromisoformat(value)
    return parsed.strftime("%m/%d/%y %I:%M %p")


def format_report(crime) -> str:
    """Build the caption shared by the platform integrations."""
    return "\n".join((
        crime["title"] + get_emojis(crime["title"]),
        f"Occurred at {titlize(crime['campus'])}, {crime['place']}",
        f"Case: {crime['case_id']}",
        f"Reported on {format_datetime(crime['report_dt'])}",
        f"Between {format_datetime(crime['start_dt'])} - {format_datetime(crime['end_dt'])}",
        f"Status: {crime['disposition'].title()}",
    ))


def notify_crime(crime, config: ConfigParser) -> bool:
    """Return whether every enabled platform published the report."""
    publishers = (
        ("META", meta.publish),
        ("TELEGRAM", telegram.publish),
        ("TWITTER", partial(x.publish, place=crime["place"])),
    )
    enabled = [
        (section, publish)
        for section, publish in publishers
        if config.getboolean(section, "ENABLE", fallback=False)
    ]
    if not enabled:
        return True

    message = format_report(crime)
    succeeded = True
    with TemporaryDirectory(prefix="ucfcrimes-social-") as temporary:
        image = Path(temporary) / "caseout.png"
        generate_image(crime, image, config)
        for section, publish in enabled:
            try:
                publish(config[section], image, message)
            except Exception as error:
                print(f"{section} failed for case {crime['case_id']}: {type(error).__name__}")
                succeeded = False
            else:
                print(f"{section} published case {crime['case_id']}.")

    return succeeded
