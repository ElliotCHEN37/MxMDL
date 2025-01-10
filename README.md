# MxMDL
> Latest version: [v1.3.1](https://github.com/ElliotCHEN37/RMxLRC/releases/latest)

## History
The project was gradually derived from GMxLRC.<br>
GMxLRC was designed to provide a GUI interface for MxLRC. Over time GMxLRC was rewritten and renamed RMxLRC. However, RMxLRC still requires MxLRC as a dependency.<br>
Now, MxMDL is a new beginning. It can work independently without MxLRC and has richer functions than MxLRC!<br>

## Usage
```
usage: main.py [-h] [-g] [-k TOKEN] [-a ARTIST] [-t TITLE] [-l ALBUM] [--lrctype {synced,unsynced}] [--output_type {lrc,srt}] [filepath]

MxMDL v1.3.2 by ElliotCHEN37. Download synced lyrics from Musixmatch freely!

positional arguments:
  filepath              Path to an audio file

optional arguments:
  -h, --help            show this help message and exit
  -g, --get_token       Retrieve a new Musixmatch API token
  -k TOKEN, --token TOKEN
                        Musixmatch API token
  -a ARTIST, --artist ARTIST
                        Artist name
  -t TITLE, --title TITLE
                        Track title
  -l ALBUM, --album ALBUM
                        Album name (optional)
  --lrctype {synced,unsynced}
                        Lyrics type (default: synced)
  --output_type {lrc,srt}
                        Output file format (default: lrc)
```

## Changelog
<!-- <details> -->
<!-- <summary> -->
<h3>v1.3.2</h3>
<!-- </summary> -->
OPT:<br>
    1. Refactor code with ChatGPT<br>
    2. Using logging instead of print<Br>
    3. Using "apic"<br>
<!-- </details> -->
<details>
<summary><h3>v1.3.1</h3></summary>
FIX:<br>
    1. LRC file timing
</details>
<details>
<summary><h3>v1.3</h3></summary>
NEW:<br>
    1. Using "♪ Instrumental ♪" for instrumental songs<br>
    2. Output type<br>
    3. Save lyrics as SRT file<br>
OPT:<br>
    1. Adjust arguments<br>
</details>
<details>
    <summary><h3>v1.2</h3></summary>
    NEW:<br>
        1. Add support for direct file input.<br>
    FIX:<br>
        1. Error when downloading Instrumental songs.
</details>
<details>
    <summary><h3>v1.1</h3></summary>
    FIX:<br>
        1. Obtain token multiple times.<br>
    NEW:<br>
        1. Use --chlog to view changelog.<br>
    OPT:<br>
        1. Adjust code structure.
</details>
<details>
    <summary><h3>v1.0</h3></summary>
    Initial Release
</details>

## Build
Open your terminal and run the following commands<br>
#### Clone
```shell
cd <somewhere>
git clone https://github.com/ElliotCHEN37/MxMDL.git
cd MxmDL/Source
```
#### Build
```shell
pip install -r requirements.txt
pip install pyinstaller
pyinstaller build_<sys>.spec
```
> Replace \<sys\> with your os

## License
[The MIT License](LICENSE.txt)
