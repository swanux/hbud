#!/usr/bin/python3
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

class App:
    application_id = "io.github.swanux.hbud"
    application_name = "HBud"
    application_description = 'Simple audio and video player'
    application_version ="0.4.1 - Theresa"
    app_years = "2021-2023"
    main_url = "https://github.com/swanux/hbud"
    bug_url = "https://github.com/swanux/hbud/issues/labels/bug"
    help_url = "https://github.com/swanux/hbud/issues"
    about_comments = application_description
    release_notes = """<p>Smaller pointrelease</p>
    <ul>
        <li>New About window using Adw.AboiutWindow</li>
        <li>Small improvements, minor bugfixes</li>
        <li>Added option to edit lyric tag in the metadata editor</li>
        <li>Updated runtime (Gnome 42 -> 43) </li>
    </ul>"""