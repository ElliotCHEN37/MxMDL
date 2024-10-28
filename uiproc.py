import json
import os
import sys
import webbrowser
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog
from PySide6 import QtGui
from PySide6.QtCore import QTranslator
from mainwin import Ui_MainWindow
from getlrc import MusixmatchProvider, write_to_lrc
import tinytag


class MainWindow:
    def __init__(self):
        self.vernum = "v1.0"

        self.config = self.load_config()
        self.token = self.config.get("token", "")
        self.trans_file = self.config.get("trans", "")

        self.app = QApplication(sys.argv)
        trans = QTranslator()
        trans.load(self.trans_file)
        self.app.installTranslator(trans)
        self.app.setStyle('windowsvista')
        self.window = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.window)
        self.window.setWindowTitle(self.app.tr(f"RMxLRC GUI {self.vernum} By ElliotCHEN37"))
        self.window.setWindowIcon(QtGui.QIcon(":/ico/icon.png"))
        self.ui.statusbar.showMessage(self.app.tr("Ready"))

        if self.token:
            self.ui.token_LineEdit.setText(self.token)

        self.ui.pushButton.clicked.connect(self.download_lyrics)
        self.ui.actionAbout.triggered.connect(self.about_message)
        self.ui.actionLicense.triggered.connect(self.license_message)
        self.ui.actionRelease_Page.triggered.connect(self.view_release)
        self.ui.actionOpen_config_file.triggered.connect(self.open_config)
        self.ui.actionExit.triggered.connect(sys.exit)
        self.ui.actionReadGenConfig.triggered.connect(self.load_config)
        self.ui.actionOpen_Audio_File.triggered.connect(self.read_audio)

    def download_lyrics(self):
        try:
            artist = self.ui.artist_LineEdit.text()
            title = self.ui.title_LineEdit.text()
            album = self.ui.album_LineEdit.text() or None
            duration = self.ui.duration_LineEdit.text()
            token = self.ui.token_LineEdit.text() or None

            lrctype_index = self.ui.lrctype_comboBox.currentIndex()
            lrctype = "synced" if lrctype_index == 0 else "unsynced"

            duration = int(duration) if duration.isdigit() else None

            info = {"album": album, "artist": artist, "title": title, "duration": duration}

            provider = MusixmatchProvider(token=token)
            lyrics_data = provider.find_lyrics(info)

            if lyrics_data:
                filename = f"{artist} - {title}.lrc"
                lyrics = provider.get_lyrics_data(lyrics_data, lrctype=lrctype)

                if lyrics:
                    write_to_lrc(filename, lyrics, synced=(lrctype == "synced"))
                    self.ui.statusbar.showMessage(self.app.tr(f"LRC file '{filename}' saved with {lrctype} lyrics."))
                else:
                    self.ui.statusbar.showMessage(self.app.tr("No lyrics found."))
            else:
                self.ui.statusbar.showMessage(self.app.tr("Lyrics not found."))
        except Exception as e:
            QMessageBox.critical(self.window, "Error", f"An error occurred: {str(e)}")

    def about_message(self):
        QMessageBox.about(self.window, self.app.tr("About"), self.app.tr(f"RMxLRC GUI {self.vernum} By ElliotCHEN37\n"
                                                                         "A program that can download lyrics you want "
                                                                         "from Musixmatch freely.\n"
                                                                         "Used projects:\n- PySide6\n- QFluentWidgets\n"
                                                                         "App icon is from Google's Material Symbols"))

    def license_message(self):
        QMessageBox.information(self.window, self.app.tr("License"), """MIT License

Copyright (c) 2024 Elliot

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

1. The original author and the authors of any other software used with this
software must be credited

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""")

    @staticmethod
    def view_release():
        webbrowser.open_new_tab("https://github.com/ElliotCHEN37/RMxLRC/releases")

    @staticmethod
    def open_config():
        os.startfile("config.json")

    def load_config(self):
        try:
            if not os.path.exists("config.json"):
                default_config = {
                    "token": "",
                    "trans": ""
                }
                with open("config.json", "w") as f:
                    json.dump(default_config, f, indent=3)

            with open("config.json", "r") as f:
                return json.load(f)
        except Exception as e:
            QMessageBox.critical(self.window, "Error", f"Failed to load config: {str(e)}")
            return {}

    def read_audio(self):
        file_path, _ = QFileDialog.getOpenFileName(caption="Open Audio File",
                                                   filter="Supported Audio Files (*.aiff *.aif *.aifc *.wma *.flac "
                                                          "*.opus *.ogg *.wav *.m4a *.mp3 *.mp2 *.mp1)")
        if file_path:
            try:
                print(f"Selected audio file: {file_path}")
                tag = tinytag.TinyTag.get(file_path)
                print(f"Artist: {tag.artist}")
                print(f"Title: {tag.title}")
                print(f"Album: {tag.album}")
                self.ui.artist_LineEdit.setText(tag.artist)
                self.ui.title_LineEdit.setText(tag.title)
                self.ui.album_LineEdit.setText(tag.album)
            except Exception as e:
                QMessageBox.critical(self.window, "Error", f"Failed to read audio file: {str(e)}")
        else:
            print("No audio file selected")

    def run(self):
        self.window.show()
        sys.exit(self.app.exec())


if __name__ == "__main__":
    app = MainWindow()
    app.run()
