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

## Installation & Setup
### Clone the Repository
```shell
git clone https://github.com/ElliotCHEN37/MxMDL.git
cd MxMDL/Source
```

### Install Dependencies
```shell
pip install -r requirements.txt
```

### Build Executable (Optional)
```shell
pip install pyinstaller
pyinstaller build_<sys>.spec
```

Replace <sys> with your OS (win or lin)

## Usage
```shell
python3 main.py [-h] [-k TOKEN] [-a ARTIST] [-t TITLE] [-l ALBUM] [--lrctype {synced,unsynced}] [--output_type {lrc,srt}] [-e SLEEP] [filepath]
```

### Arguments:
| Short Argument	 | Full Argument | Description                                       |
|-----------------|---------------|---------------------------------------------------|
| -h              | --help        | Show help message                                 |
| -k              | --token       | Musixmatch API token (optional)                   |
| -a              | --artist      | Artist name                                       |
| -t              | --title       | Track title                                       |
| -l              | --album       | Album name (optional)                             |
| N/A             | --lrctype     | Lyrics type (synced or unsynced, default: synced) |
| N/A             | --output_type | Output format (lrc or srt, default: lrc)          |
| -e              | --sleep       | Time interval between downloads (default: 30 sec) |
| N/A             | N/A           | Path to an audio file (to extract metadata)       |

## Using `.mxdl` Batch Files
A `.mxdl` file allows you to batch download multiple lyrics easily.

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
```

### Minimal Example
```
||| Adele ||| Hello |||
||| Coldplay ||| Yellow |||
```

### Run the `.mxdl` File
```shell
python main.py your_file.mxdl
```

## Changelog
<h3>v1.3.5 (Latest)</h3>
<h4>New Features</h4>
<li>Asynchronous API Requests (asyncio + aiohttp)</li>
<h4>Optimizations & Fixes</h4>
<li>Improved Token Handling</li>
<li>Enhanced Error Handling for API Responses</li>
<li>Prevents crashes when API returns non-JSON data</li>
<li>Handles missing subtitles more gracefully</li>
<li>Fixed Empty File Issues</li>
<li>Prevents writing empty .lrc or .srt files if no lyrics are found</li>
<li>Ensures directories are created before writing output</li>

<details>
<summary><h3>Previous Versions</h3></summary>

<h3>v1.3.4</h3>
<h4>Optimizations:</h4>
<li>Renamed Classes to follow Python naming conventions.</li>
<li>API Requests More Stable with retry mechanism.</li>
<li>Reduced Unnecessary API Calls for efficiency.</li>
<li>Improved Error Handling to avoid JSON parse errors.</li>

<h3>v1.3.3</h3>
<h4>New Features</h4>
<li>Sleep Time Customization</li>
<li><code>.mxdl</code> Batch File Support</li>
<li>Logging Enhancements</li>

<h3>v1.3.2</h3>
<h4>Code Refactor</h4>
<li>Better Logging</li>
<li>Improved Code Structure</li>
<li>API Endpoint Adjustments</li>

<h3>v1.3.1</h3>
<h4>Fix</h4>
<li>Fixed LRC Timing Issues</li>

<h3>v1.3</h3>
<h4>New Features</h4>
<li>Added <code>♪ Instrumental ♪</code> for instrumental songs</li>
<li>Support for SRT file output</li>
<li>Command-line arguments improvement</li>

<h3>v1.2</h3>
<h4>New</h4>
<li>Support for Direct File Input</li>
<h4>Fix</h4>
<li>Resolved Issues with Instrumental Songs</li>

<h3>v1.1</h3>
<h4>Fix</h4>
<li>Token Retrieval Optimization</li>
<h4>New</h4>
<li>Changelog Viewing via --chlog</li>
<h4>Optimization</h4>
<li>Code Structure Improvement</li>

<h3>v1.0</h3>
<h4>Initial Release</h4>

</details>

License
[MIT License](LICENSE.txt)
