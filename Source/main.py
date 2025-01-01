import os
import argparse
import requests
import json
from datetime import timedelta
from tinytag import TinyTag
import time

BASE_URL = "https://apic-desktop.musixmatch.com/ws/1.1"
APPVER = "1.3"

def refresh_token():
    try:
        print("[I] Obtaining token...")
        response = requests.get(f"{BASE_URL}/token.get?app_id=web-desktop-app-v1.0")
        response.raise_for_status()
        token = response.json().get("message", {}).get("body", {}).get("user_token")
        print(f"[I] Token obtained: {token}")
        return token
    except requests.RequestException as e:
        print(f"[X] Error obtaining token: {e}")
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
        print("[I] Finding lyrics...")
        response = requests.get(f"{BASE_URL}/macro.subtitles.get", params=params)
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

def format_time(milliseconds):
    print("[I] Formatting time...")
    minutes, seconds = divmod(timedelta(milliseconds=milliseconds).total_seconds(), 60)
    return f"[{int(minutes):02}:{int(seconds):02}.{int((milliseconds % 1000) / 10):02}]"

def write_to_lrc(filename, lyrics_data, synced=True):
    try:
        print("[I] Writing to LRC file...")
        with open(filename, 'w', encoding='utf-8') as f:
            for line in lyrics_data:
                timestamp = format_time(line['startTime']) if synced else ''
                f.write(f"{timestamp}{line['text']}\n")
    except IOError as e:
        print(f"[X] Error writing to file: {e}")

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

def process_directory(token, directory, lrctype="synced", sleep_time=0):
    skipped_files = []
    for root, _, files in os.walk(directory):
        print(f'[I] Scanning "{directory}"...')
        for file in files:
            if file.lower().endswith((
                '.mp1', '.mp2', '.mp3', '.m4a', '.aac', '.wav', '.ogg', '.flac', '.wma', '.aiff', '.aif')):
                file_path = os.path.join(root, file)
                print(f'[I] Processing "{file}"...')
                metadata = extract_metadata(file_path)
                if not metadata:
                    skipped_files.append(f"{file}: Missing metadata")
                    continue

                artist = metadata.get("artist")
                title = metadata.get("title")

                if not artist or not title:
                    skipped_files.append(f"{file}: Incomplete metadata")
                    continue

                print("[I] Ready to download lyrics...")
                download_lyrics(
                    token=token,
                    artist=artist,
                    title=title,
                    album=metadata.get("album"),
                    lrctype=lrctype,
                    output_path=os.path.splitext(file_path)[0] + ".lrc"
                )

                if sleep_time > 0:
                    print(f"[I] Waiting for {sleep_time} seconds before next download...")
                    time.sleep(sleep_time)

    if skipped_files:
        print("\n[I] Summary of skipped files:")
        for reason in skipped_files:
            print(reason)

def download_lyrics(token, artist, title, album=None, lrctype="synced", output_path=None):
    if not token:
        print("[X] Failed to obtain a valid token.")
        return

    lyrics_data = find_lyrics(token, artist, title, album)

    if not lyrics_data:
        print(f"[W] Lyrics not found for {title} by {artist}.")
        return

    if lyrics_data.get("instrumental"):
        lyrics_data = [{"text": "♪ Instrumental ♪", "startTime": 0}]
    else:
        lyrics_data = parse_lyrics(lyrics_data, lrctype=lrctype)

    if not lyrics_data:
        print(f"[W] No lyrics found for {title} by {artist}.")
        return

    filename = output_path or f"{artist} - {title}.lrc"
    write_to_lrc(filename, lyrics_data, synced=(lrctype == "synced"))
    print(f"[I] LRC file '{filename}' saved with {lrctype} lyrics.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f"MxMDL v{APPVER} by ElliotCHEN37. Download synced lyrics from Musixmatch freely!")
    parser.add_argument("-g", "--get_token", action="store_true", help="Retrieve a new Musixmatch API token")
    parser.add_argument("-k", "--token", help="Musixmatch API token")
    parser.add_argument("-a", "--artist", help="Artist name")
    parser.add_argument("-t", "--title", help="Track title")
    parser.add_argument("-l", "--album", help="Album name (optional)")
    parser.add_argument("--lrctype", choices=["synced", "unsynced"], default="synced", help="Lyrics type (default: synced)")
    parser.add_argument("-d", "--directory", help="Directory containing audio files")
    parser.add_argument("-s", "--sleep", type=int, default=30, help="Seconds to wait between downloads (default: 30)")
    parser.add_argument("filepath", nargs="?", help="Path to an audio file")

    args = parser.parse_args()

    if args.get_token:
        token = refresh_token()
        if token:
            print(f"[I] New token obtained: {token}")
        else:
            print("[X] Failed to obtain a new token.")
    elif args.filepath:
        token = args.token or refresh_token()
        if not token:
            print("[X] Failed to obtain a valid token.")
        else:
            metadata = extract_metadata(args.filepath)
            if not metadata:
                print(f"[X] Failed to extract metadata from file: {args.filepath}")
            else:
                artist = metadata.get("artist")
                title = metadata.get("title")
                album = metadata.get("album")

                if not artist or not title:
                    print(f"[W] Incomplete metadata for file: {args.filepath}. Artist and title are required.")
                else:
                    print(f"[I] Downloading lyrics for '{title}' by '{artist}'...")
                    download_lyrics(
                        token=token,
                        artist=artist,
                        title=title,
                        album=album,
                        lrctype=args.lrctype,
                        output_path=os.path.splitext(args.filepath)[0] + ".lrc"
                    )
    elif args.directory:
        token = args.token or refresh_token()
        if not token:
            print("[X] Failed to obtain a valid token.")
        else:
            process_directory(token, args.directory, lrctype=args.lrctype, sleep_time=args.sleep)
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
