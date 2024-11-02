import os
import requests
import json
from datetime import timedelta
import time
import tinytag
from PySide6.QtWidgets import QMessageBox, QFileDialog


class MusixmatchProvider:
    def __init__(self, token=None):
        self.base_url = "https://apic-desktop.musixmatch.com/ws/1.1"
        self.headers = {
            "authority": "apic-desktop.musixmatch.com",
            "cookie": "x-mxm-token-guid="
        }
        self.token = token or self.refresh_token

    def refresh_token(self, ui):
        response = requests.get(f"{self.base_url}/token.get?app_id=web-desktop-app-v1.0", headers=self.headers)
        if response.status_code == 200:
            self.token = response.json().get("message", {}).get("body", {}).get("user_token")
            if self.token:
                ui.statusbar.showMessage("Token refreshed successfully")
                return self.token
        print("Failed to refresh token")
        return None

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

        response = requests.get(f"{self.base_url}/macro.subtitles.get", params=params, headers=self.headers)
        return response.json().get("message", {}).get("body", {}).get("macro_calls", {})

    @staticmethod
    def get_lyrics_data(body, lrctype="synced"):
        if lrctype == "synced":
            subtitle = \
            body.get("track.subtitles.get", {}).get("message", {}).get("body", {}).get("subtitle_list", [{}])[0].get(
                "subtitle", {})
            return [
                {"text": line["text"] or "♪", "startTime": line["time"]["total"] * 1000}
                for line in json.loads(subtitle.get("subtitle_body", "[]"))
            ] if subtitle else None

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


def download_lyrics(ui, token, artist, title, album, lrctype):
    try:
        info = {"album": album, "artist": artist, "title": title}
        provider = MusixmatchProvider(token=token)
        lyrics_data = provider.find_lyrics(info)

        if lyrics_data:
            filename = f"{artist} - {title}.lrc"
            lyrics = provider.get_lyrics_data(lyrics_data, lrctype=lrctype)

            if lyrics:
                write_to_lrc(filename, lyrics, synced=(lrctype == "synced"))
                ui.statusbar.showMessage(f"LRC file '{filename}' saved with {lrctype} lyrics.")
            else:
                ui.statusbar.showMessage("No lyrics found.")
        else:
            ui.statusbar.showMessage("Lyrics not found.")
    except Exception as e:
        QMessageBox.critical(ui.window, "Error", f"An error occurred: {str(e)}")


def dir_mode(ui, token, directory, interval):
    for root, _, files in os.walk(directory):
        for filename in files:
            if not filename.lower().endswith(('.aiff', '.aif', '.aifc', '.wma', '.flac', '.opus', '.ogg', '.wav',
                                              '.m4a', '.mp3', '.mp2', '.mp1')):
                continue

            audio_file_path = os.path.join(root, filename)
            try:
                tag = tinytag.TinyTag.get(audio_file_path)
                artist = tag.artist
                title = tag.title

                info = {"album": None, "artist": artist, "title": title}
                provider = MusixmatchProvider(token=token)
                lyrics_data = provider.find_lyrics(info)

                if not lyrics_data:
                    ui.statusbar.showMessage(f"No lyrics data found for '{title}' by {artist}. Skipping...")
                    continue

                lrc_filename = f"{os.path.splitext(filename)[0]}.lrc"
                lrc_file_path = os.path.join(root, lrc_filename)
                lyrics = provider.get_lyrics_data(lyrics_data, lrctype="synced")

                if lyrics:
                    write_to_lrc(lrc_file_path, lyrics, synced=True)
                    ui.statusbar.showMessage(f"LRC file '{lrc_filename}' saved.")
                else:
                    ui.statusbar.showMessage(f"No lyrics found for '{title}' by {artist}. Skipping...")

                time.sleep(interval)

            except Exception as e:
                ui.statusbar.showMessage(f"Error processing {filename}: {str(e)}")


def read_audio(ui, app):
    file_path, _ = QFileDialog.getOpenFileName(
        caption=app.tr("Open Audio File"),
        filter=app.tr(
            "Supported Audio Files (*.aiff *.aif *.aifc *.wma *.flac *.opus *.ogg *.wav *.m4a *.mp3 *.mp2 *.mp1)")
    )
    if file_path:
        try:
            ui.statusbar.showMessage(app.tr(f"Selected audio file: {file_path}"))
            tag = tinytag.TinyTag.get(file_path)
            ui.artist_LineEdit.setText(tag.artist)
            ui.title_LineEdit.setText(tag.title)
            ui.album_LineEdit.setText(tag.album)
        except Exception as e:
            QMessageBox.critical(ui.window, app.tr("Error"), app.tr(f"Failed to read audio file: {str(e)}"))
    else:
        ui.statusbar.showMessage(app.tr("No audio file selected"))
