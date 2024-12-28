import os
import argparse
import requests
import json
from datetime import timedelta
from tinytag import TinyTag
import time

BASE_URL = "https://apic-desktop.musixmatch.com/ws/1.1"

def refresh_token():
    try:
        print("Obtaining token...")
        response = requests.get(f"{BASE_URL}/token.get?app_id=web-desktop-app-v1.0")
        response.raise_for_status()
        token = response.json().get("message", {}).get("body", {}).get("user_token")
        print(f"Token obtained: {token}")
        return token
    except requests.RequestException as e:
        print(f"Error obtaining token: {e}")
        return None

def find_lyrics(token, artist, title, album=None):
    params = {
        "format": "json",
        "namespace": "lyrics_richsynched",
        "subtitle_format": "mxm",
        "app_id": "web-desktop-app-v1.0",
        "q_artist": artist,
        "q_track": title,
        "usertoken": token
    }
    if album:
        params["q_album"] = album

    try:
        print("Finding lyrics...")
        response = requests.get(f"{BASE_URL}/macro.subtitles.get", params=params)
        response.raise_for_status()
        return response.json().get("message", {}).get("body", {}).get("macro_calls", {})
    except requests.RequestException as e:
        print(f"Error finding lyrics: {e}")
        return None

def parse_lyrics(body, lrctype="synced"):
    try:
        print("Downloading lyrics...")
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
    print("Formatting time...")
    minutes, seconds = divmod(timedelta(milliseconds=milliseconds).total_seconds(), 60)
    return f"[{int(minutes):02}:{int(seconds):02}.{int((milliseconds % 1000) / 10):02}]"

def write_to_lrc(filename, lyrics_data, synced=True):
    try:
        print("Writing to LRC file...")
        with open(filename, 'w', encoding='utf-8') as f:
            for line in lyrics_data:
                timestamp = format_time(line['startTime']) if synced else ''
                f.write(f"{timestamp}{line['text']}\n")
    except IOError as e:
        print(f"Error writing to file: {e}")

def extract_metadata(file_path):
    try:
        print("Reading metadata...")
        tag = TinyTag.get(file_path)
        return {
            "artist": tag.artist,
            "title": tag.title,
            "album": tag.album
        }
    except Exception as e:
        print(f"Error reading metadata from {file_path}: {e}")
        return None

def process_directory(token, directory, lrctype="synced", sleep_time=0):
    skipped_files = []
    for root, _, files in os.walk(directory):
        print(f'Scanning "{directory}"...')
        for file in files:
            if file.lower().endswith(('.mp1', '.mp2', '.mp3', '.m4a', '.aac', '.wav', '.ogg', '.flac', '.wma', '.aiff', '.aif')):
                file_path = os.path.join(root, file)
                print(f'Processing "{file}"...')
                metadata = extract_metadata(file_path)
                if not metadata:
                    skipped_files.append(f"{file}: Missing metadata")
                    continue

                artist = metadata.get("artist")
                title = metadata.get("title")

                if not artist or not title:
                    skipped_files.append(f"{file}: Incomplete metadata")
                    continue

                print("Ready to download lyrics...")
                download_lyrics(
                    token=token,
                    artist=artist,
                    title=title,
                    album=metadata.get("album"),
                    lrctype=lrctype,
                    output_path=os.path.splitext(file_path)[0] + ".lrc"
                )

                if sleep_time > 0:
                    print(f"Waiting for {sleep_time} seconds before next download...")
                    time.sleep(sleep_time)

    if skipped_files:
        print("\nSummary of skipped files:")
        for reason in skipped_files:
            print(reason)

def download_lyrics(token, artist, title, album=None, lrctype="synced", output_path=None):
    if not token:
        print("Failed to obtain a valid token.")
        return

    lyrics_data = find_lyrics(token, artist, title, album)

    if not lyrics_data:
        print(f"Lyrics not found for {title} by {artist}.")
        return

    lyrics = parse_lyrics(lyrics_data, lrctype=lrctype)

    if not lyrics:
        print(f"No lyrics found for {title} by {artist}.")
        return

    filename = output_path or f"{artist} - {title}.lrc"
    write_to_lrc(filename, lyrics, synced=(lrctype == "synced"))
    print(f"LRC file '{filename}' saved with {lrctype} lyrics.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RMxLRC CLI v1.1 by ElliotCHEN37. Download synced lyrics from Musixmatch freely!")
    parser.add_argument("--gettk", action="store_true", help="Retrieve a new Musixmatch API token")
    parser.add_argument("--token", help="Musixmatch API token")
    parser.add_argument("--artist", help="Artist name")
    parser.add_argument("--title", help="Track title")
    parser.add_argument("--album", help="Album name (optional)")
    parser.add_argument("--lrctype", choices=["synced", "unsynced"], default="synced", help="Lyrics type (default: synced)")
    parser.add_argument("--dir", help="Directory containing audio files")
    parser.add_argument("--slp", type=int, default=30, help="Seconds to wait between downloads (default: 30)")
    parser.add_argument("--chlog", action="store_true", help="View changelog")

    args = parser.parse_args()

    if args.gettk:
        token = refresh_token()
        if token:
            print(f"New token obtained: {token}")
        else:
            print("Failed to obtain a new token.")
    elif args.chlog:
        print(f"""Visit GitHub repository to get more detailed changes!
https://github.com/ElliotCHEN37/RMxLRC/commits/main/
CHANGELOG:
v1.1
FIX:
    1. Obtain token multiple times.
NEW:
    1. Use --chlog to view changelog
OPT:
    1. Adjust code structure.
v1.0
Initial Release""")
    elif args.dir:
        token = args.token or refresh_token()
        if not token:
            print("Failed to obtain a valid token.")
        else:
            process_directory(token, args.dir, lrctype=args.lrctype, sleep_time=args.slp)
    elif args.artist and args.title:
        download_lyrics(
            token=args.token or refresh_token(),
            artist=args.artist,
            title=args.title,
            album=args.album,
            lrctype=args.lrctype
        )
    else:
        parser.print_help()
