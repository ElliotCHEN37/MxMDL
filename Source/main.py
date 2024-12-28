import argparse
import requests
import json
from datetime import timedelta

class MusixmatchProvider:
    BASE_URL = "https://apic-desktop.musixmatch.com/ws/1.1"

    def __init__(self, token=None):
        self.token = token or self.refresh_token()

    def refresh_token(self):
        try:
            response = requests.get(f"{self.BASE_URL}/token.get?app_id=web-desktop-app-v1.0")
            response.raise_for_status()
            self.token = response.json().get("message", {}).get("body", {}).get("user_token")
            return self.token
        except requests.RequestException as e:
            print(f"Error refreshing token: {e}")
            return None

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
            response = requests.get(f"{self.BASE_URL}/macro.subtitles.get", params=params)
            response.raise_for_status()
            return response.json().get("message", {}).get("body", {}).get("macro_calls", {})
        except requests.RequestException as e:
            print(f"Error finding lyrics: {e}")
            return None

    @staticmethod
    def parse_lyrics(body, lrctype="synced"):
        try:
            if lrctype == "synced":
                subtitle = body.get("track.subtitles.get", {}).get("message", {}).get("body", {}).get("subtitle_list", [{}])[0].get("subtitle", {})
                return [
                    {"text": line["text"] or "♪", "startTime": line["time"]["total"] * 1000}
                    for line in json.loads(subtitle.get("subtitle_body", "[]"))
                ] if subtitle else None

            lyrics_body = body.get("track.lyrics.get", {}).get("message", {}).get("body", {}).get("lyrics", {}).get("lyrics_body")
            return [{"text": line} for line in lyrics_body.split("\n") if line] if lyrics_body else None
        except (KeyError, json.JSONDecodeError) as e:
            print(f"Error parsing lyrics: {e}")
            return None

def format_time(milliseconds):
    minutes, seconds = divmod(timedelta(milliseconds=milliseconds).total_seconds(), 60)
    return f"[{int(minutes):02}:{int(seconds):02}.{int((milliseconds % 1000) / 10):02}]"

def write_to_lrc(filename, lyrics_data, synced=True):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            for line in lyrics_data:
                timestamp = format_time(line['startTime']) if synced else ''
                f.write(f"{timestamp}{line['text']}\n")
    except IOError as e:
        print(f"Error writing to file: {e}")

def download_lyrics(token, artist, title, album=None, lrctype="synced"):
    provider = MusixmatchProvider(token=token)

    if not provider.token:
        print("Failed to obtain a valid token.")
        return

    lyrics_data = provider.find_lyrics(artist, title, album)

    if not lyrics_data:
        print("Lyrics not found.")
        return

    lyrics = provider.parse_lyrics(lyrics_data, lrctype=lrctype)

    if not lyrics:
        print("No lyrics found.")
        return

    filename = f"{artist} - {title}.lrc"
    write_to_lrc(filename, lyrics, synced=(lrctype == "synced"))
    print(f"LRC file '{filename}' saved with {lrctype} lyrics.")

def get_new_token():
    provider = MusixmatchProvider()
    if provider.token:
        print(f"New token obtained: {provider.token}")
    else:
        print("Failed to obtain a new token.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RMxLRC CLI v1.0 by ElliotCHEN37. Download synced lyrics from Musixmatch freely!")
    parser.add_argument("--gettk", action="store_true", help="Retrieve a new Musixmatch API token")
    parser.add_argument("--token", help="Musixmatch API token")
    parser.add_argument("--artist", help="Artist name")
    parser.add_argument("--title", help="Track title")
    parser.add_argument("--album", help="Album name (optional)")
    parser.add_argument("--lrctype", choices=["synced", "unsynced"], default="synced", help="Lyrics type (default: synced)")

    args = parser.parse_args()

    if args.gettk:
        get_new_token()
    elif args.artist and args.title:
        download_lyrics(
            token=args.token or MusixmatchProvider().refresh_token(),
            artist=args.artist,
            title=args.title,
            album=args.album,
            lrctype=args.lrctype
        )
    else:
        parser.print_help()
