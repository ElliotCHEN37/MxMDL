import os
import argparse
import requests
import json
from datetime import timedelta
from tinytag import TinyTag
import time

BASE_URL = "https://apic-desktop.musixmatch.com/ws/1.1"
APPVER = "1.3.2"

class LyricsDownloader:
    def __init__(self, base_url, app_ver):
        self.base_url = base_url
        self.app_ver = app_ver
        self.token = None

    def refresh_token(self):
        try:
            print("[I] Obtaining token...")
            response = requests.get(f"{self.base_url}/token.get?app_id=web-desktop-app-v1.0")
            response.raise_for_status()
            self.token = response.json().get("message", {}).get("body", {}).get("user_token")
            print(f"[I] Token obtained: {self.token}")
            return(self.token)
        except requests.RequestException as e:
            print(f"[X] Error obtaining token: {e}")

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
            print("[I] Finding lyrics...")
            response = requests.get(f"{self.base_url}/macro.subtitles.get", params=params)
            response.raise_for_status()
            body = response.json().get("message", {}).get("body", {}).get("macro_calls", {})
            instrumental = body.get("track.lyrics.get", {}).get("message", {}).get("body", {}).get("lyrics", {}).get("instrumental")
            if instrumental:
                print(f"[I] The song '{title}' by '{artist}' is instrumental.")
                return {"instrumental": True}

            return body
        except requests.RequestException as e:
            print(f"[X] Error finding lyrics: {e}")
            return None

    @staticmethod
    def parse_lyrics(body, lrctype="synced"):
        try:
            print("[I] Downloading lyrics...")
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
            print(f"[X] Error parsing lyrics: {e}")
            return None

    @staticmethod
    def format_time(milliseconds):
        minutes, seconds = divmod(timedelta(milliseconds=milliseconds).total_seconds(), 60)
        return f"{int(minutes):02}:{int(seconds):02}.{int((milliseconds % 1000) / 10):02}"

    @staticmethod
    def format_time_srt(milliseconds):
        seconds, milliseconds = divmod(milliseconds, 1000)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{int(milliseconds):03}"

    @staticmethod
    def write_to_file(filename, lyrics_data, output_type="lrc", synced=True):
        try:
            print(f"[I] Writing to {output_type.upper()} file...")
            with open(filename, 'w', encoding='utf-8') as f:
                if output_type == "lrc":
                    for line in lyrics_data:
                        timestamp = LyricsDownloader.format_time(line['startTime']) if synced else ''
                        f.write(f"[{timestamp}]{line['text']}\n")
                elif output_type == "srt":
                    for i, line in enumerate(lyrics_data):
                        start_time = LyricsDownloader.format_time_srt(line['startTime'])
                        end_time = LyricsDownloader.format_time_srt(lyrics_data[i + 1]['startTime']) if i + 1 < len(lyrics_data) else LyricsDownloader.format_time_srt(line['startTime'] + 2000)
                        f.write(f"{i + 1}\n{start_time} --> {end_time}\n{line['text']}\n\n")
        except IOError as e:
            print(f"[X] Error writing to file: {e}")

    @staticmethod
    def extract_metadata(file_path):
        try:
            print("[I] Reading metadata...")
            tag = TinyTag.get(file_path)
            return {
                "artist": tag.artist,
                "title": tag.title,
                "album": tag.album
            }
        except Exception as e:
            print(f"[X] Error reading metadata from {file_path}: {e}")
            return None

    def download_lyrics(self, artist, title, album=None, lrctype="synced", output_type="lrc", output_path=None):
        if not self.token:
            self.refresh_token()
            return

        lyrics_data = self.find_lyrics(artist, title, album)

        if not lyrics_data:
            print(f"[W] Lyrics not found for {title} by {artist}.")
            return

        if lyrics_data.get("instrumental"):
            lyrics_data = [{"text": "♪ Instrumental ♪", "startTime": 0}]
        else:
            lyrics_data = self.parse_lyrics(lyrics_data, lrctype=lrctype)

        if not lyrics_data:
            print(f"[W] No lyrics found for {title} by {artist}.")
            return

        filename = output_path or f"{artist} - {title}." + ("srt" if output_type == "srt" else "lrc")
        self.write_to_file(filename, lyrics_data, output_type=output_type, synced=(lrctype == "synced"))
        print(f"[I] {output_type.upper()} file '{filename}' saved with {lrctype} lyrics.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f"MxMDL v{APPVER} by ElliotCHEN37. Download synced lyrics from Musixmatch freely!")
    parser.add_argument("-g", "--get_token", action="store_true", help="Retrieve a new Musixmatch API token")
    parser.add_argument("-k", "--token", help="Musixmatch API token")
    parser.add_argument("-a", "--artist", help="Artist name")
    parser.add_argument("-t", "--title", help="Track title")
    parser.add_argument("-l", "--album", help="Album name (optional)")
    parser.add_argument("--lrctype", choices=["synced", "unsynced"], default="synced", help="Lyrics type (default: synced)")
    parser.add_argument("--output_type", choices=["lrc", "srt"], default="lrc", help="Output file format (default: lrc)")
    parser.add_argument("filepath", nargs="?", help="Path to an audio file")

    args = parser.parse_args()
    downloader = LyricsDownloader(BASE_URL, APPVER)

    if args.get_token:
        downloader.refresh_token()
    elif args.filepath:
        downloader.token = args.token or downloader.refresh_token()
        metadata = LyricsDownloader.extract_metadata(args.filepath)
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
