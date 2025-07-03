# MxMDL
Download any lyrics from Musixmatch directly and freely!<br>
Latest Release: [Click Here](http://github.com/ElliotCHEN37/MxMDL/releases/latest)

## Features
✅ Download Synced or Unsynced Lyrics<br>
✅ Supports `.mxdl` Batch File for Multiple Downloads<br>
✅ Auto-fetch API Token (if not provided)<br>
✅ Supports `.lrc` and `.srt` Output Formats<br>
✅ Extract Metadata from Audio Files<br>
✅ Configurable Sleep Time Between Downloads<br>
✅ Enhanced Error Handling & Robust File Operations<br>
✅ Smart Filename Sanitization<br>
✅ Improved Type Safety with Full Type Hints<br>
✅ Better Logging System with Detailed Progress Tracking<br>
✅ Optimized Performance & Memory Usage<br>

## Usage
```shell
python main.py [-h] [-k TOKEN] [-a ARTIST] [-t TITLE] [-l ALBUM] [--lrctype {synced,unsynced}] [--output_type {lrc,srt}] [-e SLEEP] [-o OUTPUT] [--async] [filepath]
```

### Arguments:
| Short Argument | Full Argument | Description                                        |
|----------------|---------------|----------------------------------------------------|
| -h             | --help        | Show help message                                  |
| -k             | --token       | Musixmatch API token (optional)                    |
| -a             | --artist      | Artist name                                        |
| -t             | --title       | Track title                                        |
| -l             | --album       | Album name (optional)                              |
| N/A            | --lrctype     | Lyrics type (synced or unsynced, default: synced)  |
| N/A            | --output_type | Output format (lrc or srt, default: lrc)           |
| -e             | --sleep       | Time interval between downloads (default: 30 sec)  |
| -o             | --output      | Output directory path (default: current directory) |
| N/A            | --async       | Use async mode for batch downloads                 |
| N/A            | N/A           | Path to an audio file or .mxdl file                |

### Examples

#### Download Single Song
```shell
# Basic usage
python main.py -a "Taylor Swift" -t "Love Story"

# With album and custom format
python main.py -a "Ed Sheeran" -t "Shape of You" -l "Divide" --output_type srt --lrctype unsynced
```

#### Download from Audio File
```shell
python main.py /path/to/song.mp3
```

#### Batch Download with .mxdl File
```shell
# Standard batch download
python main.py playlist.mxdl

# With async mode for faster processing
python main.py playlist.mxdl --async
```

## Using `.mxdl` Batch Files
A `.mxdl` file allows you to batch download multiple lyrics easily with enhanced error handling and progress tracking.

### Example `.mxdl` File
```
# Lines starting with "#" are ignored
!format = lrc  # Output format (lrc/srt)
!sleep = 10  # Sleep time between downloads
!output = /path/to/output  # Output directory
!token = your_api_token  # (Optional) API token
!synced = true  # Download synced lyrics

!download
||| Taylor Swift ||| Love Story |||
||| Ed Sheeran ||| Shape of You ||| Divide |||
||| BTS ||| Dynamite |||
||| Adele ||| Hello |||
||| Coldplay ||| Yellow |||
```

### Advanced Configuration
```
# Enhanced configuration options
!format = lrc
!sleep = 5
!output = ./lyrics_output
!synced = true

!download
||| Artist with Special Characters!@# ||| Song Title ||| Album |||
||| 陳奕迅 ||| 富士山下 |||
||| Émilie Simon ||| Café Noir |||
```

### Minimal Example
```
||| Adele ||| Hello |||
||| Coldplay ||| Yellow |||
```

## License
[MIT License](LICENSE.txt)

## Disclaimer
This tool is for educational and personal use only. Please respect Musixmatch's terms of service and copyright laws in your jurisdiction.
