#!/usr/bin/python3
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

class App:
    # application_shortname = "hbud"
    application_id = "io.github.swanux.hbud"
    application_name = "HBud"
    application_description = 'Simple music and video player'
    application_version ="0.4.0 - CODENAME?"
    app_years = "2021-2022"
    main_url = "https://github.com/swanux/hbud"
    bug_url = "https://github.com/swanux/hbud/issues/labels/bug"
    help_url = "https://github.com/swanux/hbud/issues"
    about_comments = application_description
    # about_license_type = Gtk.License.GPL_3_0