# UCF Crimes

UCF Crimes gathers data from the UCFPD daily crime log and posts information to Instagram and Discord. Incidents are made public according to the Clery Act, a federal law that requires all U.S. colleges and universities (including foreign campuses of U.S. institutions), both public and private, participating in federal student aid programs to maintain and disclose certain crime statistics and campus security/fire information. All information republished by UCF Crimes is gathered directly from the UCFPD daily crime log, and no erronous or false information is injected into the posts.

The UCF Crimes Discord has ability to query over dates and locations. More options will be available in the future.

View our work here: [UCF NSM Article](https://www.nicholsonstudentmedia.com/news/ucf-students-create-crime-tracking-social-media/article_af24e17a-79d4-11ee-8c27-e3a2cc49333f.html)

## Run the social publisher

Use Python 3.11 or newer. For Cairo map rendering, install Cairo and `pkg-config` through your system package manager if your platform builds Pycairo from source.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp config.example.ini config.ini
```

Fill in the PostgreSQL settings for the shared `crimes` table and enable the desired publisher sections in `config.ini`. The publisher uses the `title`, `place`, and coordinates written by the current loader. Existing monorepo publisher credentials can be used with the same section and key names. Set the CARTO key in `[CARTO]` or through `CARTO_API_KEY`. Meta uses the version configured on the app unless you set `graph_api_version`.

```sh
python src --config config.ini
```

The integrations for Meta, Telegram, and X live in `src/platforms/`.

Each invocation processes the previous day's reports. Schedule it to run once a day after the loader. Running it again for the same day can repost those reports.

## Notes

- UCF Crimes is not affiliated with UCFPD
- UCF Crimes is not created with malicioius intent
- UCF Crimes does not encourage malicious behavior of any kind

## Connect

- IG: [@UCFcrimes](https://www.instagram.com/ucfcrimes/)
- Discord: [UCF Crimes](https://discord.gg/NEEbsbu8Np)
