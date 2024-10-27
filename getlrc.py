import requests
import json
import argparse
import sys
from datetime import timedelta


class MusixmatchProvider:
    def __init__(self, token=None):
        self.base_url = "https://apic-desktop.musixmatch.com/ws/1.1"
        self.headers = {
            "authority": "apic-desktop.musixmatch.com",
            "cookie": "x-mxm-token-guid="
        }
        self.token = token

        if not self.token:
            self.refresh_token()

    def refresh_token(self):
        url = f"{self.base_url}/token.get?app_id=web-desktop-app-v1.0"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            data = response.json().get('message', {}).get('body', {})
            if 'user_token' in data:
                self.token = data['user_token']
                print("Token refreshed successfully")
            else:
                print("Failed to refresh token: Too many attempts")
        else:
            print("Failed to refresh token")
            sys.exit(1)

    def find_lyrics(self, info):
        params = {
            "format": "json",
            "namespace": "lyrics_richsynched",
            "subtitle_format": "mxm",
            "app_id": "web-desktop-app-v1.0",
            "q_artist": info['artist'],
            "q_artists": info['artist'],
            "q_track": info['title'],
            "usertoken": self.token
        }

        if "album" in info and info["album"]:
            params["q_album"] = info["album"]
        if "uri" in info and info["uri"]:
            params["track_spotify_id"] = info["uri"]
        if "duration" in info and info["duration"]:
            duration = info["duration"] / 1000
            params["q_duration"] = duration
            params["f_subtitle_length"] = int(duration)

        url = f"{self.base_url}/macro.subtitles.get"
        response = requests.get(url, params=params, headers=self.headers)

        body = response.json().get('message', {}).get('body', {}).get('macro_calls', {})

        if body.get("matcher.track.get", {}).get("message", {}).get("header", {}).get("status_code") != 200:
            return {"error": "Requested error", "uri": info['uri']}

        if body.get("track.lyrics.get", {}).get("message", {}).get("body", {}).get("lyrics", {}).get("restricted"):
            return {"error": "Unfortunately we're not authorized to show these lyrics.", "uri": info['uri']}

        return body

    def get_synced(self, body):
        meta = body.get("matcher.track.get", {}).get("message", {}).get("body", {})

        if not meta:
            return None

        if meta.get("track", {}).get("instrumental"):
            return [{"text": "♪ Instrumental ♪", "startTime": "0000"}]

        subtitle = body.get("track.subtitles.get", {}).get("message", {}).get("body", {}).get("subtitle_list", [{}])[0].get("subtitle", {})
        if subtitle:
            return [
                {
                    "text": line["text"] or "♪",
                    "startTime": line["time"]["total"] * 1000
                } for line in json.loads(subtitle.get("subtitle_body", "[]"))
            ]

        return None

    def get_unsynced(self, body):
        meta = body.get("matcher.track.get", {}).get("message", {}).get("body", {})

        if not meta:
            return None

        if meta.get("track", {}).get("instrumental"):
            return [{"text": "♪ Instrumental ♪"}]

        lyrics = body.get("track.lyrics.get", {}).get("message", {}).get("body", {}).get("lyrics", {}).get("lyrics_body")
        if lyrics:
            return [{"text": line} for line in lyrics.split("\n")]

        return None


def format_time(milliseconds):
    td = timedelta(milliseconds=milliseconds)
    minutes, seconds = divmod(td.total_seconds(), 60)
    return f"[{int(minutes):02}:{int(seconds):02}.{int((milliseconds % 1000) / 10):02}]"


def write_to_lrc(filename, lyrics_data, synced=True):
    with open(filename, 'w', encoding='utf-8') as f:
        for line in lyrics_data:
            if synced:
                time_tag = format_time(line['startTime'])
                f.write(f"{time_tag}{line['text']}\n")
            else:
                f.write(f"{line['text']}\n")


def main():
    parser = argparse.ArgumentParser(description="Download lyrics using Musixmatch.")
    parser.add_argument("--album", help="Album name (optional)")
    parser.add_argument("--artist", required=True, help="Artist name")
    parser.add_argument("--title", required=True, help="Track title")
    parser.add_argument("--uri", help="Spotify track URI (optional)")
    parser.add_argument("--duration", type=int, help="Track duration in milliseconds (optional)")
    parser.add_argument("--token", help="Musixmatch user token (optional)")
    parser.add_argument("--lyrics-type", choices=["synced", "unsynced"], default="synced",
                        help="Type of lyrics to download: synced or unsynced (default: synced)")

    args = parser.parse_args()

    info = {
        "album": args.album,
        "artist": args.artist,
        "title": args.title,
        "uri": args.uri,
        "duration": args.duration
    }

    provider = MusixmatchProvider(token=args.token)
    lyrics_data = provider.find_lyrics(info)

    if lyrics_data:
        filename = f"{args.artist} - {args.title}.lrc"

        if args.lyrics_type == "synced":
            synced_data = provider.get_synced(lyrics_data)
            if synced_data:
                write_to_lrc(filename, synced_data, synced=True)
                print(f"LRC file '{filename}' created with synced lyrics.")
            else:
                print("No synced lyrics found. Switching to unsynced lyrics...")
                unsynced_data = provider.get_unsynced(lyrics_data)
                if unsynced_data:
                    write_to_lrc(filename, unsynced_data, synced=False)
                    print(f"LRC file '{filename}' created with unsynced lyrics.")
                else:
                    print("No unsynced lyrics found.")
        else:
            unsynced_data = provider.get_unsynced(lyrics_data)
            if unsynced_data:
                write_to_lrc(filename, unsynced_data, synced=False)
                print(f"LRC file '{filename}' created with unsynced lyrics.")
            else:
                print("No unsynced lyrics found.")

    else:
        print("Lyrics not found.")


if __name__ == "__main__":
    main()
