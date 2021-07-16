# HBud
Simple music / video player and karaoke app written in Python and GTK - Because why not

# [Website](https://swanux.github.io/hbud.html)

# Features
- Video and audio playback (for supported formats, refer to GStreamer docs)
- Subtitle support (automatically)
- Karaoke mode (synced lyrics needed in own srt format, I'll provide instructions on that later)
- Metadata editor (for audio files)
- Playlists (from folder structure)
- Seamlessly switch back and forth between video and audio playback (remembers where to continue)
- Native, lightweight and simple

# Credits
* [GTK](https://www.gtk.org) - For the GUI framework
* [GStreamer](https://gstreamer.freedesktop.org) - For the multimedia framework
* [PyGObject](https://pygobject.readthedocs.io/en/latest/) - For the Python bindings
* [Lazka](https://lazka.github.io/pgi-docs/) - For the documentation
* [AutoLyrixAlign](https://github.com/chitralekha18/AutoLyrixAlign) - For the neural network to align text to lyrics
* [srt](https://pypi.org/project/srt/) - For the Python srt module
* [mediafile](https://pypi.org/project/mediafile/) - For the wrapper around mutagen
* [mutagen](https://pypi.org/project/mutagen/) - For this extensive module
