import json
import re
import argparse
from pathlib import Path
from urllib.parse import urljoin
import requests
from tinytag import TinyTag

BASE_URL = "https://apic.musixmatch.com/ws/1.1/"


class LyricsDownloader:
    def __init__(self):
        self.token = None
        self.session = requests.Session()

    def get_token(self):
        try:
            url = urljoin(BASE_URL, "token.get")
            response = self.session.get(url, params={"app_id": "web-desktop-app-v1.0"})
            response.raise_for_status()

            data = response.json()
            self.token = data["message"]["body"]["user_token"]
            print("[INF] 成功取得 Token")
            return self.token
        except Exception as e:
            print(f"[ERR] 無法取得 Token: {e}")
            return None

    def search_lyrics(self, artist, title, album=None):
        if not self.token:
            self.get_token()

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
            print(f"[INF] 查找歌詞: {artist} - {title}")
            url = urljoin(BASE_URL, "macro.subtitles.get")
            response = self.session.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            body = data.get("message", {}).get("body", {}).get("macro_calls", {})

            lyrics_info = body.get("track.lyrics.get", {}).get("message", {}).get("body", {}).get("lyrics", {})
            if lyrics_info.get("instrumental"):
                return {"instrumental": True}

            return body
        except Exception as e:
            print(f"[ERR] 查找時出錯: {e}")
            return None

    def parse_synced_lyrics(self, data):
        try:
            subtitles = data.get("track.subtitles.get", {}).get("message", {}).get("body", {}).get("subtitle_list", [])
            if not subtitles:
                return None

            subtitle_body = subtitles[0].get("subtitle", {}).get("subtitle_body")
            if not subtitle_body:
                return None

            parsed = json.loads(subtitle_body)
            lyrics = []
            for line in parsed:
                time_ms = int(line.get("time", {}).get("total", 0) * 1000)
                text = line.get("text", "♪")
                lyrics.append((time_ms, text))

            return lyrics
        except Exception:
            return None

    def parse_unsynced_lyrics(self, data):
        try:
            lyrics_text = data.get("track.lyrics.get", {}).get("message", {}).get("body", {}).get("lyrics", {}).get(
                "lyrics_body", "")
            return [(0, line) for line in lyrics_text.split("\n") if line.strip()]
        except Exception:
            return None

    def format_time_lrc(self, ms):
        total_seconds = ms / 1000
        minutes, seconds = divmod(total_seconds, 60)
        return f"{int(minutes):02d}:{seconds:05.2f}"

    def save_lyrics(self, lyrics, filename, synced=True):
        try:
            Path(filename).parent.mkdir(parents=True, exist_ok=True)

            with open(filename, 'w', encoding='utf-8') as f:
                for time_ms, text in lyrics:
                    if synced and time_ms > 0:
                        timestamp = self.format_time_lrc(time_ms)
                        f.write(f"[{timestamp}]{text}\n")
                    else:
                        f.write(f"{text}\n")

            print(f"[INF] 歌詞已保存: {filename}")
            return True
        except Exception as e:
            print(f"[ERR] 保存失敗: {e}")
            return False

    def download(self, artist, title, album=None, output_dir=".", synced=True):
        data = self.search_lyrics(artist, title, album)
        if not data:
            return False

        if data.get("instrumental"):
            lyrics = [(0, "♪ Instrumental ♪")]
        else:
            if synced:
                lyrics = self.parse_synced_lyrics(data)
                if not lyrics:
                    lyrics = self.parse_unsynced_lyrics(data)
                    synced = False
            else:
                lyrics = self.parse_unsynced_lyrics(data)

        if not lyrics:
            print("[ERR] 找不到歌詞")
            return False

        safe_name = re.sub(r'[<>:"/\\|?*]', '_', f"{artist} - {title}")[:200]
        filename = Path(output_dir) / f"{safe_name}.lrc"

        return self.save_lyrics(lyrics, filename, synced)


def extract_metadata(file_path):
    try:
        tag = TinyTag.get(file_path)
        return {
            'artist': tag.artist or "Unknown Artist",
            'title': tag.title or "Unknown Title",
            'album': tag.album
        }
    except Exception as e:
        print(f"[ERR] 無法讀取元數據: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="RE:MxMDL 2.0")
    parser.add_argument("file", nargs="?", help="音訊路徑")
    parser.add_argument("-a", "--artist", help="歌手名稱")
    parser.add_argument("-t", "--title", help="歌曲標題")
    parser.add_argument("-l", "--album", help="專輯名稱")
    parser.add_argument("-o", "--output", default=".", help="輸出目錄")
    parser.add_argument("--unsynced", action="store_true", help="下載未同步歌詞")

    args = parser.parse_args()

    downloader = LyricsDownloader()

    if args.file:
        metadata = extract_metadata(args.file)
        if metadata:
            downloader.download(
                metadata['artist'],
                metadata['title'],
                metadata['album'],
                args.output,
                not args.unsynced
            )
        else:
            print("[ERR] 無法讀取元數據")
    elif args.artist and args.title:
        downloader.download(
            args.artist,
            args.title,
            args.album,
            args.output,
            not args.unsynced
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
