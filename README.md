# RMxLRC
> Last build time: 2024/10/29, 22:50 (UTC+8) | Latest version: [v1.0](https://github.com/ElliotCHEN37/RMxLRC/releases/latest)

## Feature
- Download lyrics you want from Musixmatch freely
- Auto-generate or refresh your token
- Directory mode for multiple songs
- More...

## Config
Config file should be named as `config.json`
```json
{
  "token": "Your Mxm User Token (You can leave it blank)",
  "trans": "Locale file (Leave it blank if you don't want to use it)"
}
```

## Build
> [!CAUTION]
> For Windows only!

Open your terminal and run the following commands<br>
#### Clone
`cd <path to somewhere>`<br>
`git clone https://github.com/ElliotCHEN37/RMxLRC.git`<Br>
`cd RMxLRC`<br>
#### Build
`pip install -r requirements.txt`<br>
`pip install pyinstaller`<br>
`pyinstaller build.spec`<br>

## License
[The MIT License](LICENSE.txt)

## Used Projects
- [QFluentWidgets](https://qfluentwidgets.com/)
- PySide6
