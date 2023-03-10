# HBud
Simple audio / video player and karaoke app written in Python and GTK4

<p align="center"><a href="https://beta.flathub.org/apps/io.github.swanux.hbud" align="center"><img width="250" alt='Download on Flathub' src='https://raw.githubusercontent.com/swanux/hbud/master/Screenshots/flatpak-badge-new.svg'/></a></p>
<p align="center">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/flathub/v/io.github.swanux.hbud?label=HBud&style=for-the-badge">
  <source media="(prefers-color-scheme: light)" srcset="https://img.shields.io/flathub/v/io.github.swanux.hbud?label=HBud&style=for-the-badge">
  <img alt="Latest published version" src="https://img.shields.io/flathub/v/io.github.swanux.hbud?label=HBud&style=for-the-badge">
</picture>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/flathub/downloads/io.github.swanux.hbud?logo=Flatpak&logoColor=white&style=for-the-badge">
  <source media="(prefers-color-scheme: light)" srcset="https://img.shields.io/flathub/downloads/io.github.swanux.hbud?logo=Flatpak&logoColor=white&style=for-the-badge">
  <img alt="Number of installs" src="https://img.shields.io/flathub/downloads/io.github.swanux.hbud?logo=Flatpak&logoColor=white&style=for-the-badge">
</picture>
</p>

## Features
- Audio and video playback
- Subtitle support
- Karaoke mode (synced lyrics needed in own srt format, see below for instructions)
- Static lyric automatically from online sources
- Metadata editor (for audio files)
- Playlists (from folder structure)
- Seamlessly switch back and forth between video and audio playback (remembers where to continue)
- Native, lightweight and simple
- Minimalistic design
- Customizable
- Flatpak package for compatibility and security

## Translation

First you have to clone this repo, then change directory into it's root (where the `Makefile` is).

You can then use the `make` command with the provided flags:

- Add new translation: `make translate-new en`
- Generate `.mo` files: `make translate-add en`
- Update `.po` files: `make translate-update en`
- Update `.mo` files: `make translate-upgrade en`

It's important to use UTF-8 charset when needed (instead of ASCII).

## Downloading music

I recommend using one of these tools:
* [spotDL](https://github.com/spotDL/spotify-downloader) - Spotify
* [Freyr](https://github.com/miraclx/freyr-js) - Spotify, Apple Music, Deezer

# Credits
* [GTK4](https://www.gtk.org) - For the GUI framework
* [GStreamer](https://gstreamer.freedesktop.org/) - For the multimedia backend
* [Amolenaar](https://amolenaar.github.io/pgi-docgen/) - For the PyGObject documentation
* [AutoLyrixAlign](https://github.com/chitralekha18/AutoLyrixAlign) - For the neural network to align lyrics to music
* [srt](https://github.com/cdown/srt) - For the Python srt module
* [mediafile](https://github.com/beetbox/mediafile) - For the handy wrapper around mutagen
* [azapi](https://github.com/elmoiv/azapi) - For the AZLyrics API
* [PyICU](https://gitlab.pyicu.org/main/pyicu) - For providing proper name of a language from language code
* [gst-plugins-rs](https://gitlab.freedesktop.org/gstreamer/gst-plugins-rs) - For `gtk4paintablesink` for video playback
* [pyacoustid](https://github.com/beetbox/pyacoustid) and [musicbrainzngs](https://github.com/alastair/python-musicbrainzngs) - For the AcoustID and MusicBrainz bindings
* [MusicBrainz](https://beta.musicbrainz.org/) and [AcoustID](https://acoustid.org/) - For the open databases
* [mpris_server](https://github.com/alexdelorenzo/mpris_server) - For the MPRIS server (although I'm using a slightly modified version)
* [Flatpak](https://flatpak.org/) - For this awesome distribution system

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

### Other methods

You can try to generate a word by word .lrc file ([here](https://lrcgenerator.com) for example), and you can try my experimental enhanced-lrc converter like this: `python3 lrc2srt.py lyric.lrc output.srt`

## Generate subtitles

You can use [AutoSub](https://github.com/abhirooptalasila/AutoSub) which is a nice tool if you want to generate your own subtitles.

A manual alternative is the GTK program [Gnome Subtitles](https://gnomesubtitles.org)

*Note: You can also use this program, to adjust already generated synced lyrics to different audio files of the same song.*
