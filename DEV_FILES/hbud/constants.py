#!/usr/bin/python3
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

class App:
    application_id = "io.github.swanux.hbud"
    application_name = "HBud"
    application_description = 'Simple audio and video player'
    application_version ="0.4.0 - Theresa"
    app_years = "2021-2022"
    main_url = "https://github.com/swanux/hbud"
    bug_url = "https://github.com/swanux/hbud/issues/labels/bug"
    help_url = "https://github.com/swanux/hbud/issues"
    about_comments = application_description