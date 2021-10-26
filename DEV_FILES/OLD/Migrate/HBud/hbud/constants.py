#!/usr/bin/python3
import gi, os, locale, gettext
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

try:
    current_locale, encoding = locale.getdefaultlocale()
    locale_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
    translate = gettext.translation("hbud", locale_path, [current_locale])
    _ = translate.gettext
except FileNotFoundError:
    _ = str

class App:
    '''Here we are defining our Application infos, so we can easily
    use in all our application files'''
    application_shortname = "hbud"
    application_id = "com.github.swanux.hbud"
    application_name = "HBud"
    application_description = _('Simple music and video player')
    application_version ="0.2.4"
    app_years = "2021"
    main_url = "https://github.com/swanux/hbud"
    bug_url = "https://github.com/swanux/hbud/issues/labels/bug"
    help_url = "https://github.com/swanux/hbud/issues"
    about_comments = application_description
    about_license_type = Gtk.License.GPL_3_0
