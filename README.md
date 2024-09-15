
Simple wrapper of OpenAI tts API, support third parties' hosts.

## Using the Pre-built Executable

1. Download the release `.exe` file.
2. Run the `.exe` file to get started!

## Building Your Own Executable

1. Download the `ffmpeg.zip` file from the release.
2. Extract the contents of `ffmpeg.zip` into the `bin/` directory.
3. Use the `PyInstaller` to generate a single executable file

``` bash
pip install PyInstaller
python -m PyInstaller --onefile --add-binary "bin/*:." --windowed --name TTSWrapper tts.py

# with debug info
# python -m PyInstaller --onefile --add-binary "bin/*:." --name TTSWrapper tts.py
```
