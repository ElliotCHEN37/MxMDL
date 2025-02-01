# MxMDL
Download any lyrics on Musixmatch directly and freely!<br>
Go to latest release -> [Here](https://github.com/ElliotCHEN37/MxMDL/releases/latest)

## Usage
```
usage: main.py [-h] [-k TOKEN] [-a ARTIST] [-t TITLE] [-l ALBUM] [--lrctype {synced,unsynced}] [--output_type {lrc,srt}] [-e SLEEP] [filepath]

MxMDL v1.3.3 by ElliotCHEN37. Download synced lyrics from Musixmatch freely!

positional arguments:
  filepath              Path to an audio file

optional arguments:
  -h, --help            show this help message and exit
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
  -e SLEEP, --sleep SLEEP
                        Time interval between downloads (in seconds)
```

## MXDL Instruction
An MXDL file should be ended with .mxdl as its extension.<br>
An example MXDL file:<br>
```
# MxMDL will ignore lines start with "#"
!format = <SRT or LRC, default: LRC>
!sleep = <sleep time, default: 30>
!output = <path to output folder, default: current folder>
!token = <optional line, if this line isn't available, MxMDL will get one automatically>
!synced = <"true" or "false" (don't add quotes!), if the value is true, MxMDL will download the synced lyrics>
!download <this line means the download list start here>
|||<artist|||<track title>|||<album, optional, if not provided MxMDL will ignore>|||
|||<artist 2>|||<track title 2>|||
|||<artist 3>|||<track title 3>|||<album 3>|||
```
If you want a simplified one, here you are:<Br>
```
#Each line must be ended and started with "|||"
|||<artist>|||<track title>|||
|||<artist 2>|||<track title 2>|||
```

## Changelog
<details>
<summary>
<h3>v1.3.3</h3>
</summary>
NEW:<br>
    1. Sleep time<br>
    2. Sleep time output<br>
    3. Using MXDL file to download multiple lyrics at one time<br>
</details>
<details>
<summary>
<h3>v1.3.2</h3>
</summary>
OPT:<br>
    1. Refactor code with ChatGPT<br>
    2. Using logging instead of print<Br>
    3. Using "apic"<br>
</details>
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
