# MxMDL

Download any lyrics from Musixmatch directly and freely!  
Latest Release: [Click Here](http://github.com/ElliotCHEN37/MxMDL/releases/latest)

## Usage
```shell
python main.py [-h] [-a ARTIST] [-t TITLE] [-l ALBUM] [-k TOKEN] [--lrctype {synced,unsynced}] [--output-type {lrc,srt}] [-o OUTPUT] [-e SLEEP] [-v] [-q] [filepath]
```

## MXDL file
Example file<br>
```text
# Lines starting with "#" are ignored
# Not every line was required
# Except lines strat with |||
# which tell the program what song to download

# Output format (lrc/srt)
!format = lrc

# Sleep time between downloads
# This can avoid too many requests in short time
!sleep = 10

# Output directory
!output = /path/to/output

# API token
# If not available, the program will get one automatically
!token = your_api_token  

# Download synced lyrics
!synced = true

# This line tells people what lyrics you want to download
# But the program will not read this line, it's useless
!download

# These lines tell the program what to download
||| Taylor Swift ||| Love Story |||
||| Ed Sheeran ||| Shape of You ||| Divide |||
||| BTS ||| Dynamite |||
||| Adele ||| Hello |||
||| Coldplay ||| Yellow |||
```
