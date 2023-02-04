#!/usr/bin/python3

class App:
    application_id = "io.github.swanux.hbud"
    application_name = "HBud"
    application_description = """Simple audio/video player and karaoke app written in Python and GTK4

Features:

    - Audio and video playback
    - Subtitle support
    - Karaoke mode (synced lyrics needed in own srt format, see GitHub repo for instructions)
    - Static lyric automatically from online sources
    - Metadata editor (for audio files)
    - Playlists (from folder structure)
    - Seamlessly switch back and forth between video and audio playback (remembers where to continue)
    - Native, lightweight and simple
    - Minimalistic design
    - Customizable
    - Flatpak package for compatibility and security
"""
    application_version ="0.4.1.1 - Theresa"
    app_years = "2021-2023"
    main_url = "https://github.com/swanux/hbud"
    bug_url = "https://github.com/swanux/hbud/issues/labels/bug"
    help_url = "https://github.com/swanux/hbud/issues"
    about_comments = application_description
    release_notes = """<p>Major pointrelease</p>
    <ul>
        <li>New About window using Adw.AboutWindow</li>
        <li>Added option to edit lyric tag in the metadata editor</li>
        <li>Updated runtime (Gnome 42 -> 43)</li>
        <li>Improved video playback performance (up to 2-3x better with hardware acceleration)</li>
        <li>Improved overall stability and compatibility</li>
        <li>Handle baked in subtitles</li>
        <li>Fixed flatpak related issues</li>
        <li>Added option to disable / enable hardware acceleration</li>
        <li>Switched from Gtk.Video to gtk4paintablesink from gst-rs</li>
        <li>Fixed missing app icon in some cases</li>
        <li>Many smaller bugfixes</li>
        <li>Hotfixes over 0.4.1...</li>
    </ul>"""