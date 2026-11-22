"""Publish the previous day's UCF crime reports."""

import argparse
from configparser import ConfigParser
from contextlib import closing
from datetime import date, timedelta
from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor

from notify_case import notify_crime


def read_reports(config: ConfigParser, report_date: date):
    db = config["POSTGRESQL"] if config.has_section("POSTGRESQL") else config["postgresql"]
    with closing(psycopg2.connect(
        host=db["host"],
        port=db.getint("port", fallback=None),
        dbname=db["database"],
        user=db["user"],
        password=db["password"],
    )) as connection, connection.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(
            "SELECT * FROM crimes WHERE report_dt::date = %s ORDER BY report_dt, case_id",
            (report_date,),
        )
        return cursor.fetchall()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("config.ini"), help="Path to the INI configuration")
    options = parser.parse_args(argv)
    config = ConfigParser(interpolation=None)
    with options.config.open(encoding="utf-8") as config_file:
        config.read_file(config_file)

    yesterday = date.today() - timedelta(days=1)
    reports = read_reports(config, yesterday)
    print(f"Found {len(reports)} reports for {yesterday}.")

    failed = False
    for report in reports:
        try:
            if not notify_crime(report, config):
                failed = True
        except Exception as error:
            print(f"Could not prepare case {report['case_id']}: {type(error).__name__}")
            failed = True
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
