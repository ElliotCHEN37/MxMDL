import os
import argparse
import requests
import json
from datetime import timedelta
from tinytag import TinyTag
import logging
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://apic.musixmatch.com/ws/1.1"
APPVER = "1.3.4"

LOG_FORMAT = "[%(asctime)s][%(levelname)s]%(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("mxmdl.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

class MxdlParser:
    @staticmethod
    def parse_mxdl_file(mxdl_path):
        settings = {
            "format": "lrc",
            "sleep": 30,
            "output": os.getcwd(),
            "token": None,
            "songs": [],
            "lrctype": "synced"
        }

        with open(mxdl_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                if line.startswith("!"):
                    if line.startswith("!download"):
                        continue
                    key_value_parts = line[1:].split("=", 1)
                    if len(key_value_parts) == 2:
                        key, value = key_value_parts
                        key, value = key.strip(), value.strip()

                        if key == "format":
                            settings["format"] = value.lower()
                        elif key == "sleep":
                            settings["sleep"] = int(value)
                        elif key == "output":
                            settings["output"] = value
                        elif key == "token":
                            settings["token"] = value
                        elif key == "synced":
                            settings["lrctype"] = "synced" if value.lower() == "true" else "unsynced"
                else:
                    parts = line.split("|||")[1:-1]
                    if len(parts) >= 2:
                        artist, title = parts[:2]
                        album = parts[2] if len(parts) > 2 else None
                        settings["songs"].append((artist, title, album))

        return settings

class LyricsDownloader:
    def __init__(self, base_url, app_ver):
        self.base_url = base_url
        self.app_ver = app_ver
        self.token = None

    def refresh_token(self):
        try:
            logger.info("Obtaining token...")
            response = requests.get(f"{self.base_url}/token.get?app_id=web-desktop-app-v1.0")
            response.raise_for_status()
            self.token = response.json().get("message", {}).get("body", {}).get("user_token")
            logger.info(f"Token obtained: {self.token}")
            return self.token
        except requests.RequestException as e:
            logger.error(f"Error obtaining token: {e}", exc_info=True)

    def find_lyrics(self, artist, title, album=None):
        params = {
            "format": "json",
            "namespace": "lyrics_richsynched",
            "subtitle_format": "mxm",
            "app_id": "web-desktop-app-v1.0",
            "q_artist": artist,
            "q_track": title,
            "usertoken": self.token
        }
        if album:
            params["q_album"] = album

        try:
            logger.info(f"Finding lyrics for '{title}' by '{artist}'...")
            self.session = requests.Session()
            retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
            self.session.mount("https://", HTTPAdapter(max_retries=retries))

            response = self.session.get(f"{self.base_url}/macro.subtitles.get", params=params)
            response.raise_for_status()
            try:
                data = response.json()
                body = data.get("message", {}).get("body", {}).get("macro_calls", {})
            except (requests.JSONDecodeError, AttributeError) as e:
                logger.error(f"Error parsing API response: {e}", exc_info=True)
                return None
            instrumental = body.get("track.lyrics.get", {}).get("message", {}).get("body", {}).get("lyrics", {}).get("instrumental")
            if instrumental:
                logger.info(f"The song '{title}' by '{artist}' is instrumental.")
                return {"instrumental": True}
            logger.info("Lyrics found successfully.")
            return body
        except requests.RequestException as e:
            logger.error(f"Error finding lyrics: {e}", exc_info=True)
            return None

    def download_lyrics(self, artist, title, album=None, lrctype="synced", output_type="lrc", output_path=None):
        if not self.token:
            self.token = self.refresh_token()
            return

        lyrics_data = self.find_lyrics(artist, title, album)

        if not lyrics_data:
            logger.warning(f"Lyrics not found for {title} by {artist}.")
            return

        if lyrics_data.get("instrumental"):
            lyrics_data = [{"text": "♪ Instrumental ♪", "startTime": 0}]
        else:
            lyrics_data = parse_lyrics(lyrics_data, lrctype=lrctype)

        if not lyrics_data:
            logger.warning(f"No lyrics found for {title} by {artist}.")
            return

        filename = output_path or f"{artist} - {title}." + ("srt" if output_type == "srt" else "lrc")
        write_to_file(filename, lyrics_data, output_type=output_type, synced=(lrctype == "synced"))


def extract_metadata(file_path):
    try:
        logger.info(f"Extracting metadata from {file_path}...")
        tag = TinyTag.get(file_path)
        logger.info(f"Metadata extracted: Artist - {tag.artist}, Title - {tag.title}, Album - {tag.album}")
        return {
            "artist": tag.artist,
            "title": tag.title,
            "album": tag.album
        }
    except Exception as e:
        logger.error(f"Error extracting metadata from {file_path}: {e}", exc_info=True)
        return None


def write_to_file(filename, lyrics_data, output_type="lrc", synced=True):
    try:
        logger.info(f"Writing lyrics to {output_type.upper()} file: {filename}")
        with open(filename, 'w', encoding='utf-8') as f:
            for i, line in enumerate(lyrics_data):
                timestamp = format_time_srt(line['startTime']) if output_type == "srt" else format_time(
                    line['startTime'])
                formatted_text = f"{i + 1}\n{timestamp} --> {format_time_srt(lyrics_data[i + 1]['startTime'])}\n{line['text']}\n\n" if output_type == "srt" else f"[{timestamp}]{line['text']}\n"
                f.write(formatted_text)
        logger.info(f"{output_type.upper()} file saved successfully.")
    except IOError as e:
        logger.error(f"Error writing to file: {e}", exc_info=True)


def format_time_srt(milliseconds):
    seconds, milliseconds = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{int(milliseconds):03}"


def format_time(milliseconds):
    minutes, seconds = divmod(timedelta(milliseconds=milliseconds).total_seconds(), 60)
    return f"{int(minutes):02}:{int(seconds):02}.{int((milliseconds % 1000) / 10):02}"


def parse_lyrics(body, lrctype="synced"):
    try:
        logger.info("Parsing lyrics...")
        if body.get("instrumental"):
            return [{"text": "♪ Instrumental ♪", "startTime": 0}]

        if lrctype == "synced":
            subtitle = body.get("track.subtitles.get", {}).get("message", {}).get("body", {}).get("subtitle_list", [{}])[0].get("subtitle", {})
            return [
                {"text": line["text"] or "♪", "startTime": line["time"]["total"] * 1000}
                for line in json.loads(subtitle.get("subtitle_body", "[]"))
            ] if subtitle else None

        lyrics_body = body.get("track.lyrics.get", {}).get("message", {}).get("body", {}).get("lyrics", {}).get("lyrics_body")
        return [{"text": line} for line in lyrics_body.split("\n") if line] if lyrics_body else None
    except (KeyError, json.JSONDecodeError) as e:
        logger.error(f"Error parsing lyrics: {e}", exc_info=True)
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f"MxMDL v{APPVER} by ElliotCHEN37. Download synced lyrics from Musixmatch freely!")
    parser.add_argument("-k", "--token", help="Musixmatch API token")
    parser.add_argument("-a", "--artist", help="Artist name")
    parser.add_argument("-t", "--title", help="Track title")
    parser.add_argument("-l", "--album", help="Album name (optional)")
    parser.add_argument("--lrctype", choices=["synced", "unsynced"], default="synced", help="Lyrics type (default: synced)")
    parser.add_argument("--output_type", choices=["lrc", "srt"], default="lrc", help="Output file format (default: lrc)")
    parser.add_argument("-e", "--sleep", type=int, default=30, help="Time interval between downloads (in seconds)")
    parser.add_argument("filepath", nargs="?", help="Path to an audio file")

    args = parser.parse_args()
    downloader = LyricsDownloader(BASE_URL, APPVER)

    if args.filepath and args.filepath.endswith(".mxdl"):
        logger.info(f"Processing MXDL file: {args.filepath}")
        config = MxdlParser.parse_mxdl_file(args.filepath)

        downloader.token = config["token"] or downloader.refresh_token()

        total_songs = len(config["songs"])
        for idx, (artist, title, album) in enumerate(config["songs"]):
            downloader.download_lyrics(
                artist=artist,
                title=title,
                album=album,
                lrctype=config["lrctype"],
                output_type=config["format"],
                output_path=os.path.join(config["output"], f"{artist} - {title}.{config['format']}")
            )

            remaining_sleep = config["sleep"]
            if idx < total_songs - 1:
                while remaining_sleep > 0:
                    logger.info(f"Sleeping... {remaining_sleep} seconds left")
                    time.sleep(1)
                    remaining_sleep -= 1
    elif args.filepath:
        downloader.token = args.token or downloader.refresh_token()
        metadata = extract_metadata(args.filepath)
        if metadata:
            downloader.download_lyrics(
                artist=metadata.get("artist"),
                title=metadata.get("title"),
                album=metadata.get("album"),
                lrctype=args.lrctype,
                output_type=args.output_type,
                output_path=os.path.splitext(args.filepath)[0] + (".srt" if args.output_type == "srt" else ".lrc")
            )
    elif args.artist and args.title:
        downloader.token = args.token or downloader.refresh_token()
        downloader.download_lyrics(
            artist=args.artist,
            title=args.title,
            album=args.album,
            lrctype=args.lrctype,
            output_type=args.output_type
        )
    else:
        parser.print_help()
