import os
import argparse
import requests
import json
from tinytag import TinyTag
import logging
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import asyncio
import aiohttp
import aiofiles
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re

BASE_URL = "https://apic.musixmatch.com/ws/1.1"
APPVER = "1.3.6"

LOG_FORMAT = "[%(asctime)s][%(levelname)s][%(name)s] %(message)s"
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
    def parse_mxdl_file(mxdl_path: str) -> Dict:
        default_settings = {
            "format": "lrc",
            "sleep": 30,
            "output": os.getcwd(),
            "token": None,
            "songs": [],
            "lrctype": "synced"
        }

        if not os.path.exists(mxdl_path):
            logger.error(f"MXDL file not found: {mxdl_path}")
            return default_settings

        try:
            with open(mxdl_path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    try:
                        if line.startswith("!"):
                            if line.startswith("!download"):
                                continue
                            MxdlParser._parse_setting_line(line, default_settings)
                        else:
                            MxdlParser._parse_song_line(line, default_settings)
                    except Exception as e:
                        logger.warning(f"Error parsing line {line_num} in {mxdl_path}: {e}")
                        continue

        except Exception as e:
            logger.error(f"Error reading MXDL file {mxdl_path}: {e}")

        return default_settings

    @staticmethod
    def _parse_setting_line(line: str, settings: Dict) -> None:
        key_value_parts = line[1:].split("=", 1)
        if len(key_value_parts) != 2:
            return

        key, value = key_value_parts[0].strip(), key_value_parts[1].strip()

        setting_handlers = {
            "format": lambda v: v.lower(),
            "sleep": lambda v: int(v),
            "output": lambda v: v,
            "token": lambda v: v,
            "synced": lambda v: "synced" if v.lower() == "true" else "unsynced"
        }

        if key in setting_handlers:
            try:
                if key == "synced":
                    settings["lrctype"] = setting_handlers[key](value)
                else:
                    settings[key] = setting_handlers[key](value)
            except ValueError as e:
                logger.warning(f"Invalid value for setting '{key}': {value}")

    @staticmethod
    def _parse_song_line(line: str, settings: Dict) -> None:
        parts = line.split("|||")[1:-1]
        if len(parts) >= 2:
            artist, title = parts[:2]
            album = parts[2] if len(parts) > 2 else None
            settings["songs"].append((artist.strip(), title.strip(), album.strip() if album else None))


class LyricsDownloader:

    def __init__(self, base_url: str, app_ver: str):
        self.base_url = base_url
        self.app_ver = app_ver
        self.token = None
        self._setup_session()

    def _setup_session(self) -> None:
        self.session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))
        self.session.timeout = 30

    def refresh_token(self) -> Optional[str]:
        try:
            logger.info("Obtaining token...")
            response = self.session.get(f"{self.base_url}/token.get?app_id=web-desktop-app-v1.0")
            response.raise_for_status()

            data = response.json()
            self.token = data.get("message", {}).get("body", {}).get("user_token")

            if self.token:
                logger.info("Token obtained successfully")
            else:
                logger.error("Token not found in response")

            return self.token
        except requests.RequestException as e:
            logger.error(f"Error obtaining token: {e}")
            return None

    def find_lyrics(self, artist: str, title: str, album: Optional[str] = None) -> Optional[Dict]:
        if not self.token:
            logger.error("No valid token available")
            return None

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
            response = self.session.get(f"{self.base_url}/macro.subtitles.get", params=params)
            response.raise_for_status()

            data = response.json()
            body = data.get("message", {}).get("body", {}).get("macro_calls", {})

            instrumental = body.get("track.lyrics.get", {}).get("message", {}).get("body", {}).get("lyrics", {}).get(
                "instrumental")
            if instrumental:
                logger.info(f"The song '{title}' by '{artist}' is instrumental.")
                return {"instrumental": True}

            logger.info("Lyrics found successfully.")
            return body

        except requests.JSONDecodeError as e:
            logger.error(f"Error parsing API response: {e}")
            return None
        except requests.RequestException as e:
            logger.error(f"Error finding lyrics: {e}")
            return None

    async def async_find_lyrics(self, session: aiohttp.ClientSession, artist: str, title: str,
                                album: Optional[str] = None) -> Optional[Dict]:
        if not self.token:
            self.refresh_token()
            if not self.token:
                logger.error("Failed to obtain a valid token")
                return None

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
            async with session.get(f"{self.base_url}/macro.subtitles.get", params=params) as response:
                data = await response.json()
                return data.get("message", {}).get("body", {}).get("macro_calls", {})
        except Exception as e:
            logger.error(f"Error fetching lyrics for '{title}': {e}")
            return None

    async def download_multiple_lyrics(self, songs: List[Tuple[str, str, Optional[str]]]) -> List[Optional[Dict]]:
        connector = aiohttp.TCPConnector(limit=10)
        timeout = aiohttp.ClientTimeout(total=30)

        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            tasks = [self.async_find_lyrics(session, artist, title, album) for artist, title, album in songs]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            processed_results = []
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Task failed: {result}")
                    processed_results.append(None)
                else:
                    processed_results.append(result)

            return processed_results

    def download_lyrics(self, artist: str, title: str, album: Optional[str] = None,
                        lrctype: str = "synced", output_type: str = "lrc",
                        output_path: Optional[str] = None) -> bool:
        if not self.token:
            self.token = self.refresh_token()
            if not self.token:
                logger.error("Failed to obtain a valid token, cannot proceed.")
                return False

        lyrics_data = self.find_lyrics(artist, title, album)

        if not lyrics_data or not isinstance(lyrics_data, dict):
            logger.warning(f"Lyrics not found for '{title}' by '{artist}'.")
            return False

        if lyrics_data.get("instrumental"):
            lyrics_data = [{"text": "♪ Instrumental ♪", "startTime": 0}]
        else:
            lyrics_data = parse_lyrics(lyrics_data, lrctype=lrctype)

        if not lyrics_data:
            logger.warning(f"No lyrics found for '{title}' by '{artist}'.")
            return False

        safe_filename = sanitize_filename(f"{artist} - {title}")
        extension = "srt" if output_type == "srt" else "lrc"
        filename = output_path or f"{safe_filename}.{extension}"

        return write_to_file(filename, lyrics_data, output_type=output_type, synced=(lrctype == "synced"))


def sanitize_filename(filename: str) -> str:
    illegal_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(illegal_chars, '_', filename)
    return sanitized


def extract_metadata(file_path: str) -> Optional[Dict[str, str]]:
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return None

    try:
        logger.info(f"Extracting metadata from {file_path}...")
        tag = TinyTag.get(file_path)

        metadata = {
            "artist": tag.artist or "Unknown Artist",
            "title": tag.title or "Unknown Title",
            "album": tag.album
        }

        logger.info(
            f"Metadata extracted: Artist - {metadata['artist']}, Title - {metadata['title']}, Album - {metadata['album']}")
        return metadata

    except Exception as e:
        logger.error(f"Error extracting metadata from {file_path}: {e}")
        return None


def write_to_file(filename: str, lyrics_data: List[Dict], output_type: str = "lrc", synced: bool = True) -> bool:
    try:
        logger.info(f"Writing lyrics to {output_type.upper()} file: {filename}")

        Path(filename).parent.mkdir(parents=True, exist_ok=True)

        with open(filename, 'w', encoding='utf-8') as f:
            for i, line in enumerate(lyrics_data):
                if output_type == "srt":
                    timestamp = format_time_srt(line.get("startTime", 0))
                    end_time = format_time_srt(
                        lyrics_data[i + 1].get("startTime", 0) if i + 1 < len(lyrics_data)
                        else line.get("startTime", 0) + 2000
                    )
                    formatted_text = f"{i + 1}\n{timestamp} --> {end_time}\n{line['text']}\n\n"
                else:
                    timestamp = format_time(line.get("startTime", 0))
                    formatted_text = f"[{timestamp}]{line['text']}\n" if synced else f"{line['text']}\n"

                f.write(formatted_text)

        logger.info(f"{output_type.upper()} file saved successfully at: {filename}")
        return True

    except IOError as e:
        logger.error(f"Error writing to file: {e}")
        return False


async def async_write_to_file(filename: str, lyrics_data: List[Dict], output_type: str = "lrc",
                              synced: bool = True) -> bool:
    try:
        logger.info(f"Writing lyrics to {output_type.upper()} file: {filename}")

        Path(filename).parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(filename, 'w', encoding='utf-8') as f:
            for i, line in enumerate(lyrics_data):
                if output_type == "srt":
                    timestamp = format_time_srt(line.get("startTime", 0))
                    end_time = format_time_srt(
                        lyrics_data[i + 1].get("startTime", 0) if i + 1 < len(lyrics_data)
                        else line.get("startTime", 0) + 2000
                    )
                    formatted_text = f"{i + 1}\n{timestamp} --> {end_time}\n{line['text']}\n\n"
                else:
                    timestamp = format_time(line.get("startTime", 0))
                    formatted_text = f"[{timestamp}]{line['text']}\n" if synced else f"{line['text']}\n"

                await f.write(formatted_text)

        logger.info(f"{output_type.upper()} file saved successfully at: {filename}")
        return True

    except IOError as e:
        logger.error(f"Error writing to file: {e}")
        return False


def format_time_srt(milliseconds: int) -> str:
    seconds, milliseconds = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{int(milliseconds):03}"


def format_time(milliseconds: int) -> str:
    total_seconds = milliseconds / 1000
    minutes, seconds = divmod(total_seconds, 60)
    return f"{int(minutes):02}:{seconds:05.2f}"


def parse_lyrics(body: Dict, lrctype: str = "synced") -> Optional[List[Dict]]:
    try:
        logger.info("Parsing lyrics...")

        if body.get("instrumental"):
            return [{"text": "♪ Instrumental ♪", "startTime": 0}]

        if lrctype == "synced":
            subtitle_list = body.get("track.subtitles.get", {}).get("message", {}).get("body", {}).get("subtitle_list",
                                                                                                       [])
            if not subtitle_list:
                logger.warning("No subtitle list found")
                return None

            subtitle = subtitle_list[0].get("subtitle", {})
            subtitle_body = subtitle.get("subtitle_body")

            if not subtitle_body:
                logger.warning("No subtitle body found")
                return None

            try:
                parsed_lyrics = json.loads(subtitle_body)
                return [
                    {
                        "text": line.get("text", "♪"),
                        "startTime": int(line.get("time", {}).get("total", 0) * 1000)
                    }
                    for line in parsed_lyrics
                ]
            except (json.JSONDecodeError, TypeError) as e:
                logger.error(f"Error decoding subtitle body: {e}")
                return None
        else:
            lyrics_body = body.get("track.lyrics.get", {}).get("message", {}).get("body", {}).get("lyrics", {}).get(
                "lyrics_body")
            if lyrics_body:
                return [{"text": line, "startTime": 0} for line in lyrics_body.split("\n") if line.strip()]

        return None

    except (KeyError, json.JSONDecodeError) as e:
        logger.error(f"Error parsing lyrics: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description=f"MxMDL v{APPVER} by ElliotCHEN37. Download synced lyrics from Musixmatch freely!",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("-k", "--token", help="Musixmatch API token")
    parser.add_argument("-a", "--artist", help="Artist name")
    parser.add_argument("-t", "--title", help="Track title")
    parser.add_argument("-l", "--album", help="Album name (optional)")
    parser.add_argument("--lrctype", choices=["synced", "unsynced"], default="synced",
                        help="Lyrics type (default: synced)")
    parser.add_argument("--output_type", choices=["lrc", "srt"], default="lrc",
                        help="Output file format (default: lrc)")
    parser.add_argument("-e", "--sleep", type=int, default=30, help="Time interval between downloads (in seconds)")
    parser.add_argument("filepath", nargs="?", help="Path to an audio file or mxdl file")
    parser.add_argument("-o", "--output", help="Output directory path (default: current directory)")
    parser.add_argument("--async", action="store_true", help="Use async mode for batch downloads")

    args = parser.parse_args()
    downloader = LyricsDownloader(BASE_URL, APPVER)

    if args.filepath and args.filepath.endswith(".mxdl"):
        logger.info(f"Processing MXDL file: {args.filepath}")
        config = MxdlParser.parse_mxdl_file(args.filepath)

        downloader.token = config["token"] or downloader.refresh_token()
        if not downloader.token:
            logger.error("Failed to obtain token, exiting")
            return

        total_songs = len(config["songs"])
        success_count = 0

        for idx, (artist, title, album) in enumerate(config["songs"]):
            output_path = os.path.join(config["output"],
                                       f"{sanitize_filename(f'{artist} - {title}')}.{config['format']}")

            success = downloader.download_lyrics(
                artist=artist,
                title=title,
                album=album,
                lrctype=config["lrctype"],
                output_type=config["format"],
                output_path=output_path
            )

            if success:
                success_count += 1

            if idx < total_songs - 1:
                remaining_sleep = config["sleep"]
                while remaining_sleep > 0:
                    logger.info(f"Sleeping... {remaining_sleep} seconds left")
                    time.sleep(1)
                    remaining_sleep -= 1

        logger.info(f"Batch download completed: {success_count}/{total_songs} successful")

    elif args.filepath:
        downloader.token = args.token or downloader.refresh_token()
        if not downloader.token:
            logger.error("Failed to obtain token, exiting")
            return

        metadata = extract_metadata(args.filepath)
        if metadata:
            output_path = os.path.splitext(args.filepath)[0] + (".srt" if args.output_type == "srt" else ".lrc")
            downloader.download_lyrics(
                artist=metadata.get("artist"),
                title=metadata.get("title"),
                album=metadata.get("album"),
                lrctype=args.lrctype,
                output_type=args.output_type,
                output_path=output_path
            )
    elif args.artist and args.title:
        downloader.token = args.token or downloader.refresh_token()
        if not downloader.token:
            logger.error("Failed to obtain token, exiting")
            return

        downloader.download_lyrics(
            artist=args.artist,
            title=args.title,
            album=args.album,
            lrctype=args.lrctype,
            output_type=args.output_type
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
