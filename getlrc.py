import requests
import json
import argparse
import sys
from datetime import timedelta


class MusixmatchProvider:
    def __init__(self, token=None):
        self.base_url = "https://apic-desktop.musixmatch.com/ws/1.1"
        self.headers = {"authority": "apic-desktop.musixmatch.com", "cookie": "x-mxm-token-guid="}
        self.token = token or self.refresh_token()

    def refresh_token(self):
        response = requests.get(f"{self.base_url}/token.get?app_id=web-desktop-app-v1.0", headers=self.headers)
        if response.status_code == 200:
            self.token = response.json().get("message", {}).get("body", {}).get("user_token")
            if self.token:
                print("Token refreshed successfully")
                print(self.token)
                return self.token
            print("Failed to refresh token: Too many attempts")
        print("Failed to refresh token")
        sys.exit(1)

    def find_lyrics(self, info):
        params = {
            "format": "json",
            "namespace": "lyrics_richsynched",
            "subtitle_format": "mxm",
            "app_id": "web-desktop-app-v1.0",
            "q_artist": info['artist'],
            "q_track": info['title'],
            "usertoken": self.token
        }
        if info.get("album"):
            params["q_album"] = info["album"]
        if info.get("duration"):
            duration = info["duration"] / 1000
            params.update({"q_duration": duration, "f_subtitle_length": int(duration)})

        response = requests.get(f"{self.base_url}/macro.subtitles.get", params=params, headers=self.headers)
        return response.json().get("message", {}).get("body", {}).get("macro_calls", {})

    @staticmethod
    def get_lyrics_data(body, lrctype="synced"):
        track_info = body.get("matcher.track.get", {}).get("message", {}).get("body", {})
        if track_info.get("track", {}).get("instrumental"):
            return [{"text": "♪ Instrumental ♪", "startTime": "0000"}] if lrctype == "synced" else [
                {"text": "♪ Instrumental ♪"}]

        if lrctype == "synced":
            subtitle = \
                body.get("track.subtitles.get", {}).get("message", {}).get("body", {}).get("subtitle_list", [{}])[
                    0].get(
                    "subtitle", {})
            return [
                {"text": line["text"] or "♪", "startTime": line["time"]["total"] * 1000}
                for line in json.loads(subtitle.get("subtitle_body", "[]"))
            ] if subtitle else None
        else:
            lyrics_body = body.get("track.lyrics.get", {}).get("message", {}).get("body", {}).get("lyrics", {}).get(
                "lyrics_body")
            return [{"text": line} for line in lyrics_body.split("\n")] if lyrics_body else None


def format_time(milliseconds):
    minutes, seconds = divmod(timedelta(milliseconds=milliseconds).total_seconds(), 60)
    return f"[{int(minutes):02}:{int(seconds):02}.{int((milliseconds % 1000) / 10):02}]"


def write_to_lrc(filename, lyrics_data, synced=True):
    with open(filename, 'w', encoding='utf-8') as f:
        for line in lyrics_data:
            f.write(f"{format_time(line['startTime']) if synced else ''}{line['text']}\n")


def main():
    parser = argparse.ArgumentParser(description="RMxLRC Command Line Version By ElliotCHEN37. "
                                                 "A program that can download lyrics you want from Musixmatch freely.")
    parser.add_argument("-m", "--album", help="Album name")
    parser.add_argument("-a", "--artist", required=True, help="Artist name")
    parser.add_argument("-n", "--title", required=True, help="Track title")
    parser.add_argument("-d", "--duration", type=int, help="Track duration in milliseconds")
    parser.add_argument("-t", "--token", help="Musixmatch user token")
    parser.add_argument("-y", "--lyrics-type", choices=["synced", "unsynced"], default="synced",
                        help="Type of lyrics to download")

    args = parser.parse_args()
    info = {"album": args.album, "artist": args.artist, "title": args.title, "duration": args.duration}

    provider = MusixmatchProvider(token=args.token)
    lyrics_data = provider.find_lyrics(info)

    if lyrics_data:
        filename = f"{args.artist} - {args.title}.lrc"
        lyrics = provider.get_lyrics_data(lyrics_data, lrctype=args.lyrics_type)

        if lyrics:
            write_to_lrc(filename, lyrics, synced=(args.lyrics_type == "synced"))
            print(f"LRC file '{filename}' created with {args.lyrics_type} lyrics.")
        else:
            print("No lyrics found.")
    else:
        print("Lyrics not found.")


if __name__ == "__main__":
    main()
