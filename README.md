# MxMDL
> Latest version: [v1.2](https://github.com/ElliotCHEN37/RMxLRC/releases/latest)

# History
The project was gradually derived from GMxLRC.<br>
GMxLRC was designed to provide a GUI interface for MxLRC. Over time GMxLRC was rewritten and renamed RMxLRC. However, RMxLRC still requires MxLRC as a dependency.<br>
Now, MxMDL is a new beginning. It can work independently without MxLRC and has richer functions than MxLRC!<br>

## Changelog
v1.2
NEW:<br>
    1. Add support for direct file input.<br>
FIX:<br>
    1. Error when downloading Instrumental songs.
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
