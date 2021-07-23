# HBud
Simple music / video player and karaoke app written in Python and GTK - Because why not

# [Website](https://swanux.github.io/hbud.html)

# Features
- Video and audio playback (for supported formats, refer to GStreamer docs)
- Subtitle support
- Karaoke mode (synced lyrics needed in own srt format, I'll provide instructions on that later)
- Metadata editor (for audio files)
- Playlists (from folder structure)
- Seamlessly switch back and forth between video and audio playback (remembers where to continue)
- Native, lightweight and simple

# Generate synced lyrics

Here I'll show you how to generate synced lyrics for yourslef

### Requirements

* ~20GB of RAM (you can use swap to extend your memory)
* ~20GB of disk space
* node v12 or above (for ubuntu/debian based distros you can use [this](https://github.com/nodesource/distributions) repo)

### Installation

1. Install [AutoLyrixAlignService](https://github.com/gazugafan/AutoLyrixAlignService)
    - It'll guide you through downloading the neural network and the dependencies
2. Run the server as described above, connect to it and set things up
3. Select RAW output format, save to `aligned.txt` when ready (DO NOT copy into a file, use Ctrl+S to save it)
4. Save the plain lyrics to `lyrics.txt`
5. Run [tosrt.py](https://github.com/swanux/hbud/blob/master/tools/) from this repo like this: `python3 tosrt.py aligned.txt lyrics.txt output.srt`
7. Move and rename the resulted output file alongside your audio file

# Credits
* [GTK](https://www.gtk.org) - For the GUI framework
* [GStreamer](https://gstreamer.freedesktop.org) - For the multimedia framework
* [PyGObject](https://pygobject.readthedocs.io/en/latest/) - For the Python bindings
* [Lazka](https://lazka.github.io/pgi-docs/) - For the documentation
* [AutoLyrixAlign](https://github.com/chitralekha18/AutoLyrixAlign) - For the neural network to align text to lyrics
* [srt](https://pypi.org/project/srt/) - For the Python srt module
* [mediafile](https://pypi.org/project/mediafile/) - For the wrapper around mutagen
* [mutagen](https://pypi.org/project/mutagen/) - For this extensive module
* [Nuitka](https://nuitka.net) - For the compiler
