import os
import argparse
import json
import logging
import re
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from tinytag import TinyTag
from urllib3.util.retry import Retry

BASE_URL = "https://apic.musixmatch.com/ws/1.1/"
APPVER = "1.3.6"
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3
MAX_FILENAME_LENGTH = 240
BATCH_SIZE = 10

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


class LyricsType(Enum):
    SYNCED = "synced"
    UNSYNCED = "unsynced"


class OutputFormat(Enum):
    LRC = "lrc"
    SRT = "srt"


@dataclass
class Song:
    artist: str
    title: str
    album: Optional[str] = None

    def __post_init__(self):
        self.artist = self.artist.strip()
        self.title = self.title.strip()
        if self.album:
            self.album = self.album.strip()


@dataclass
class LyricsLine:
    text: str
    start_time: int = 0


@dataclass
class MxdlConfig:
    format: OutputFormat = OutputFormat.LRC
    sleep: int = 30
    output: str = os.getcwd()
    token: Optional[str] = None
    songs: List[Song] = None
    lrctype: LyricsType = LyricsType.SYNCED

    def __post_init__(self):
        if self.songs is None:
            self.songs = []


class MxdlParseError(Exception):
    pass


class LyricsNotFoundError(Exception):
    pass


class TokenError(Exception):
    pass


class MxdlParser:
    @staticmethod
    def parse_mxdl_file(mxdl_path: str) -> MxdlConfig:
        if not os.path.exists(mxdl_path):
            raise MxdlParseError(f"MXDL file not found: {mxdl_path}")

        config = MxdlConfig()

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
                            MxdlParser._parse_setting_line(line, config)
                        else:
                            MxdlParser._parse_song_line(line, config)
                    except Exception as e:
                        logger.warning(f"Error parsing line {line_num} in {mxdl_path}: {e}")

        except Exception as e:
            raise MxdlParseError(f"Error reading MXDL file {mxdl_path}: {e}")

        return config

    @staticmethod
    def _parse_setting_line(line: str, config: MxdlConfig) -> None:
        key_value_parts = line[1:].split("=", 1)
        if len(key_value_parts) != 2:
            return

        key, value = key_value_parts[0].strip(), key_value_parts[1].strip()

        setting_handlers = {
            "format": lambda v: OutputFormat(v.lower()),
            "sleep": lambda v: max(1, int(v)),
            "output": lambda v: v,
            "token": lambda v: v,
            "synced": lambda v: LyricsType.SYNCED if v.lower() == "true" else LyricsType.UNSYNCED
        }

        if key in setting_handlers:
            try:
                if key == "synced":
                    config.lrctype = setting_handlers[key](value)
                else:
                    setattr(config, key, setting_handlers[key](value))
            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid value for setting '{key}': {value} - {e}")

    @staticmethod
    def _parse_song_line(line: str, config: MxdlConfig) -> None:
        parts = line.split("|||")[1:-1]
        if len(parts) >= 2:
            artist, title = parts[:2]
            album = parts[2] if len(parts) > 2 else None
            config.songs.append(Song(artist, title, album))


class LyricsDownloader:
    def __init__(self, base_url: str = BASE_URL, app_ver: str = APPVER):
        self.base_url = base_url
        self.app_ver = app_ver
        self.token = None
        self._setup_session()

    def _setup_session(self) -> None:
        self.session = requests.Session()
        retries = Retry(
            total=MAX_RETRIES,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def refresh_token(self) -> str:
        try:
            logger.info("Obtaining new token...")
            url = urljoin(self.base_url, "token.get")
            response = self.session.get(
                url,
                params={"app_id": "web-desktop-app-v1.0"},
                timeout=DEFAULT_TIMEOUT
            )
            response.raise_for_status()

            data = response.json()
            token = data.get("message", {}).get("body", {}).get("user_token")

            if not token:
                raise TokenError("Token not found in response")

            self.token = token
            logger.info("Token obtained successfully")
            return token

        except requests.RequestException as e:
            raise TokenError(f"Network error obtaining token: {e}")
        except (KeyError, json.JSONDecodeError) as e:
            raise TokenError(f"Invalid response format: {e}")

    def _ensure_token(self) -> None:
        if not self.token:
            self.refresh_token()

    def find_lyrics(self, song: Song) -> Optional[Dict]:
        self._ensure_token()

        params = {
            "format": "json",
            "namespace": "lyrics_richsynched",
            "subtitle_format": "mxm",
            "app_id": "web-desktop-app-v1.0",
            "q_artist": song.artist,
            "q_track": song.title,
            "usertoken": self.token
        }

        if song.album:
            params["q_album"] = song.album

        try:
            logger.info(f"Finding lyrics for '{song.title}' by '{song.artist}'...")
            url = urljoin(self.base_url, "macro.subtitles.get")
            response = self.session.get(url, params=params, timeout=DEFAULT_TIMEOUT)
            response.raise_for_status()

            data = response.json()
            body = data.get("message", {}).get("body", {}).get("macro_calls", {})

            lyrics_info = body.get("track.lyrics.get", {}).get("message", {}).get("body", {}).get("lyrics", {})
            if lyrics_info.get("instrumental"):
                logger.info(f"Song '{song.title}' by '{song.artist}' is instrumental")
                return {"instrumental": True}

            logger.info("Lyrics found successfully")
            return body

        except requests.RequestException as e:
            logger.error(f"Network error finding lyrics: {e}")
            return None
        except (KeyError, json.JSONDecodeError) as e:
            logger.error(f"Error parsing lyrics response: {e}")
            return None

    def download_lyrics(self, song: Song, lrctype: LyricsType = LyricsType.SYNCED,
                        output_type: OutputFormat = OutputFormat.LRC,
                        output_path: Optional[str] = None) -> bool:
        try:
            lyrics_data = self.find_lyrics(song)
            if not lyrics_data:
                raise LyricsNotFoundError(f"No lyrics found for '{song.title}' by '{song.artist}'")

            if lyrics_data.get("instrumental"):
                lyrics_lines = [LyricsLine("♪ Instrumental ♪", 0)]
            else:
                lyrics_lines = self._parse_lyrics(lyrics_data, lrctype)

            if not lyrics_lines:
                raise LyricsNotFoundError(f"No parseable lyrics found for '{song.title}' by '{song.artist}'")

            filename = output_path or self._generate_filename(song, output_type)
            return self._write_lyrics_to_file(filename, lyrics_lines, output_type, lrctype == LyricsType.SYNCED)

        except (LyricsNotFoundError, TokenError) as e:
            logger.error(str(e))
            return False
        except Exception as e:
            logger.error(f"Unexpected error downloading lyrics: {e}")
            return False

    def _parse_lyrics(self, body: Dict, lrctype: LyricsType) -> List[LyricsLine]:
        try:
            if lrctype == LyricsType.SYNCED:
                return self._parse_synced_lyrics(body) or self._parse_unsynced_lyrics(body)
            else:
                return self._parse_unsynced_lyrics(body)
        except Exception as e:
            logger.error(f"Error parsing lyrics: {e}")
            return []

    def _parse_synced_lyrics(self, body: Dict) -> Optional[List[LyricsLine]]:
        try:
            subtitles_data = body.get("track.subtitles.get")
            if not subtitles_data:
                return None

            if isinstance(subtitles_data, list):
                if not subtitles_data:
                    return None
                subtitles_data = subtitles_data[0]

            message_data = subtitles_data.get("message", {})
            if isinstance(message_data, list):
                if not message_data:
                    return None
                message_data = message_data[0]

            body_data = message_data.get("body", [])
            if isinstance(body_data, list):
                if not body_data:
                    return None
                body_data = body_data[0]

            subtitle_list = body_data.get("subtitle_list", [])
            if not subtitle_list:
                return None

            subtitle_body = subtitle_list[0].get("subtitle", {}).get("subtitle_body")
            if not subtitle_body:
                return None

            parsed_lyrics = json.loads(subtitle_body)
            logger.info(f"Successfully parsed {len(parsed_lyrics)} synced lyrics lines")

            return [
                LyricsLine(
                    text=line.get("text", "♪"),
                    start_time=int(line.get("time", {}).get("total", 0) * 1000)
                )
                for line in parsed_lyrics
            ]

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.warning(f"Error parsing synced lyrics: {e}")
            return None

    def _parse_unsynced_lyrics(self, body: Dict) -> Optional[List[LyricsLine]]:
        try:
            lyrics_data = body.get("track.lyrics.get")
            if not lyrics_data:
                return None

            if isinstance(lyrics_data, list):
                if not lyrics_data:
                    return None
                lyrics_data = lyrics_data[0]

            message_data = lyrics_data.get("message", {})
            if isinstance(message_data, list):
                if not message_data:
                    return None
                message_data = message_data[0]

            body_data = message_data.get("body", {})
            if isinstance(body_data, list):
                if not body_data:
                    return None
                body_data = body_data[0]

            lyrics_info = body_data.get("lyrics", {})
            lyrics_body = lyrics_info.get("lyrics_body")

            if not lyrics_body:
                return None

            logger.info("Successfully found unsynced lyrics")
            return [
                LyricsLine(text=line, start_time=0)
                for line in lyrics_body.split("\n")
                if line.strip()
            ]

        except (KeyError, TypeError) as e:
            logger.warning(f"Error parsing unsynced lyrics: {e}")
            return None

    def _generate_filename(self, song: Song, output_type: OutputFormat) -> str:
        safe_name = sanitize_filename(f"{song.artist} - {song.title}")
        return f"{safe_name}.{output_type.value}"

    def _write_lyrics_to_file(self, filename: str, lyrics_lines: List[LyricsLine],
                              output_type: OutputFormat, synced: bool) -> bool:
        try:
            logger.info(f"Writing lyrics to {output_type.value.upper()} file: {filename}")

            Path(filename).parent.mkdir(parents=True, exist_ok=True)

            with open(filename, 'w', encoding='utf-8') as f:
                if output_type == OutputFormat.SRT:
                    self._write_srt_format(f, lyrics_lines)
                else:
                    self._write_lrc_format(f, lyrics_lines, synced)

            logger.info(f"{output_type.value.upper()} file saved successfully: {filename}")
            return True

        except IOError as e:
            logger.error(f"Error writing to file {filename}: {e}")
            return False

    def _write_srt_format(self, file, lyrics_lines: List[LyricsLine]) -> None:
        for i, line in enumerate(lyrics_lines):
            start_time = format_time_srt(line.start_time)
            end_time = format_time_srt(
                lyrics_lines[i + 1].start_time if i + 1 < len(lyrics_lines)
                else line.start_time + 2000
            )
            file.write(f"{i + 1}\n{start_time} --> {end_time}\n{line.text}\n\n")

    def _write_lrc_format(self, file, lyrics_lines: List[LyricsLine], synced: bool) -> None:
        for line in lyrics_lines:
            if synced and line.start_time > 0:
                timestamp = format_time_lrc(line.start_time)
                file.write(f"[{timestamp}]{line.text}\n")
            else:
                file.write(f"{line.text}\n")


def sanitize_filename(filename: str) -> str:
    illegal_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(illegal_chars, '_', filename)
    return sanitized[:MAX_FILENAME_LENGTH]


def extract_metadata(file_path: str) -> Optional[Song]:
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return None

    try:
        logger.info(f"Extracting metadata from {file_path}...")
        tag = TinyTag.get(file_path)

        song = Song(
            artist=tag.artist or "Unknown Artist",
            title=tag.title or "Unknown Title",
            album=tag.album
        )

        logger.info(f"Metadata extracted: {song.artist} - {song.title}")
        return song

    except Exception as e:
        logger.error(f"Error extracting metadata from {file_path}: {e}")
        return None


def format_time_srt(milliseconds: int) -> str:
    seconds, ms = divmod(milliseconds, 1000)
    minutes, sec = divmod(seconds, 60)
    hours, min = divmod(minutes, 60)
    return f"{hours:02d}:{min:02d}:{sec:02d},{ms:03d}"


def format_time_lrc(milliseconds: int) -> str:
    total_seconds = milliseconds / 1000
    minutes, seconds = divmod(total_seconds, 60)
    return f"{int(minutes):02d}:{seconds:05.2f}"


def create_progress_callback(total: int):
    def callback(completed: int):
        percentage = (completed / total) * 100
        logger.info(f"Progress: {completed}/{total} ({percentage:.1f}%)")

    return callback


def main():
    parser = argparse.ArgumentParser(
        description=f"MxMDL v{APPVER} - Enhanced Musixmatch lyrics downloader",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("filepath", nargs="?", help="Path to an audio file or .mxdl file")
    parser.add_argument("-a", "--artist", help="Artist name")
    parser.add_argument("-t", "--title", help="Track title")
    parser.add_argument("-l", "--album", help="Album name (optional)")
    parser.add_argument("-k", "--token", help="Musixmatch API token")
    parser.add_argument("--lrctype", choices=["synced", "unsynced"], default="synced",
                        help="Lyrics type (default: synced)")
    parser.add_argument("--output-type", choices=["lrc", "srt"], default="lrc", help="Output format (default: lrc)")
    parser.add_argument("-o", "--output", help="Output directory (default: current directory)")
    parser.add_argument("-e", "--sleep", type=int, default=30,
                        help="Sleep time between downloads in seconds (default: 30)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress non-error output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.quiet:
        logging.getLogger().setLevel(logging.ERROR)

    try:
        downloader = LyricsDownloader()

        if args.token:
            downloader.token = args.token

        if args.filepath and args.filepath.endswith(".mxdl"):
            config = MxdlParser.parse_mxdl_file(args.filepath)
            if args.output:
                config.output = args.output
            if args.sleep:
                config.sleep = args.sleep
            downloader.token = config.token or downloader.refresh_token()

            progress = create_progress_callback(len(config.songs))
            for idx, song in enumerate(config.songs, 1):
                output_path = Path(
                    config.output) / f"{sanitize_filename(f'{song.artist} - {song.title}')}.{config.format.value}"
                success = downloader.download_lyrics(song, config.lrctype, config.format, str(output_path))
                progress(idx)
                if not success:
                    logger.error(f"Failed to download lyrics for '{song.title}' by '{song.artist}'")
                if idx < len(config.songs):
                    time.sleep(config.sleep)

        elif args.filepath:
            song = extract_metadata(args.filepath)
            if song:
                lrctype = LyricsType(args.lrctype)
                output_type = OutputFormat(args.output_type)
                output_path = Path(args.filepath).with_suffix(f".{output_type.value}")
                downloader.download_lyrics(song, lrctype, output_type, str(output_path))

        elif args.artist and args.title:
            song = Song(args.artist, args.title, args.album)
            lrctype = LyricsType(args.lrctype)
            output_type = OutputFormat(args.output_type)
            downloader.download_lyrics(song, lrctype, output_type)

        else:
            parser.print_help()

    except (MxdlParseError, TokenError) as e:
        logger.error(f"Error: {e}")
        return 1
    except KeyboardInterrupt:
        logger.info("Download interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
