import json
import os
import sys
import webbrowser
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog
from PySide6 import QtGui
from PySide6.QtCore import QTranslator
from mainwin import Ui_MainWindow
from getlrc import download_lyrics, dir_mode, read_audio, MusixmatchProvider


class MainWindow:
    def __init__(self):
        self.vernum = "v1.1"
        self.config = self.load_config()
        self.token = self.config.get("token", "")
        self.trans_file = self.config.get("trans", "")

        self.app = QApplication(sys.argv)
        self.setup_translator()
        self.setup_ui()
        self.setup_connections()

    def setup_translator(self):
        trans = QTranslator()
        trans.load(self.trans_file)
        self.app.installTranslator(trans)

    def setup_ui(self):
        self.app.setStyle('windowsvista')
        self.window = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.window)
        self.window.setWindowTitle(self.app.tr(f"RMxLRC GUI {self.vernum} By ElliotCHEN37"))
        self.window.setWindowIcon(QtGui.QIcon(":/ico/icon.png"))
        self.ui.statusbar.showMessage(self.app.tr("Ready"))

        if self.token:
            self.ui.token_LineEdit.setText(self.token)

    def setup_connections(self):
        self.ui.pushButton.clicked.connect(self.download_lyrics)
        self.ui.actionAbout.triggered.connect(self.about_message)
        self.ui.actionLicense.triggered.connect(self.license_message)
        self.ui.actionRelease_Page.triggered.connect(self.view_release)
        self.ui.actionOpen_config_file.triggered.connect(self.open_config)
        self.ui.actionExit.triggered.connect(sys.exit)
        self.ui.actionReadGenConfig.triggered.connect(self.load_config)
        self.ui.actionOpen_Audio_File.triggered.connect(self.read_audio)
        self.ui.actionOpenDir.triggered.connect(self.dir_mode)
        self.ui.refresh_pushButton.clicked.connect(self.refreshtoken)

    def download_lyrics(self):
        artist = self.ui.artist_LineEdit.text()
        title = self.ui.title_LineEdit.text()
        album = self.ui.album_LineEdit.text() or None
        token = self.ui.token_LineEdit.text() or None
        lrctype = "synced" if self.ui.lrctype_comboBox.currentIndex() == 0 else "unsynced"

        download_lyrics(self.ui, token, artist, title, album, lrctype)

    def dir_mode(self):
        directory = QFileDialog.getExistingDirectory(self.window, self.app.tr("Select Directory"))
        if not directory:
            return
        try:
            interval = int(self.ui.slpdur_LineEdit.text())
        except ValueError:
            QMessageBox.warning(self.window, self.app.tr("Input Error"),
                                self.app.tr("Please enter a valid number for the time interval."))
            return
        dir_mode(self.ui, self.token, directory, interval)

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
                default_config = {"token": "", "trans": ""}
                with open("config.json", "w") as f:
                    json.dump(default_config, f, indent=3)

            with open("config.json", "r") as f:
                return json.load(f)
        except Exception as e:
            QMessageBox.critical(self.window, self.app.tr("Error"), self.app.tr(f"Failed to load config: {str(e)}"))
            return {}

    def read_audio(self):
        read_audio(self.ui, self.app)

    def refreshtoken(self):
        try:
            provider = MusixmatchProvider(token=self.token)
            new_token = provider.refresh_token(self.ui)
            if new_token:
                self.token = new_token
                self.ui.token_LineEdit.setText(new_token)
                self.ui.statusbar.showMessage(self.app.tr("Token refreshed successfully."))
                self.update_config(new_token)
            else:
                self.ui.statusbar.showMessage(self.app.tr("Failed to refresh token."))
        except Exception as e:
            self.ui.statusbar.showMessage(self.app.tr(f"An error occurred: {str(e)}"))

    def update_config(self, new_token):
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
            config["token"] = new_token
            with open("config.json", "w") as f:
                json.dump(config, f, indent=3)
        except Exception as e:
            QMessageBox.critical(self.window, self.app.tr("Error"),
                                 self.app.tr(f"Failed to update config: {str(e)}"))

    def run(self):
        self.window.show()
        sys.exit(self.app.exec())


if __name__ == "__main__":
    app = MainWindow()
    app.run()
