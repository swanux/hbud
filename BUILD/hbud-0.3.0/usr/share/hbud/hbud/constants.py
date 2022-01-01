#!/usr/bin/python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class App:
    application_shortname = "hbud"
    application_id = "com.github.swanux.hbud"
    application_name = "HBud"
    application_description = 'Simple music and video player'
    application_version ="0.3.0"
    app_years = "2021-2022"
    main_url = "https://github.com/swanux/hbud"
    bug_url = "https://github.com/swanux/hbud/issues/labels/bug"
    help_url = "https://github.com/swanux/hbud/issues"
    about_comments = application_description
    about_license_type = Gtk.License.GPL_3_0
