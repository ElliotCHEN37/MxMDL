# MxMDL
> Latest version: [v1.2](https://github.com/ElliotCHEN37/RMxLRC/releases/latest)

## Changelog
v1.2
NEW:
    1. Add support for direct file input.
FIX:
    1. Error when downloading Instrumental songs.
v1.1
FIX:
    1. Obtain token multiple times.
NEW:
    1. Use --chlog to view changelog.
OPT:
    1. Adjust code structure.
v1.0
Initial Release

## Build
Open your terminal and run the following commands<br>
#### Clone
`cd <path to somewhere>`<br>
`git clone https://github.com/ElliotCHEN37/RMxLRC.git`<Br>
`cd ./RMxLRC/Source`<br>
#### Build
`pip install -r requirements.txt`<br>
`pip install pyinstaller`<br>
`pyinstaller ./Source/build_<sys>.spec`<br>
> Replace \<sys\> with your os

## License
[The MIT License](LICENSE.txt)
