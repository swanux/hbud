#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi, locale, os, gettext, sys
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Gst', '1.0')
from gi.repository import Gtk, Gio, GLib, Adw, Gst
from hbud import constants as cn

APP = cn.App.application_id

WHERE_AM_I = os.path.abspath(os.path.dirname(__file__))
LOCALE_DIR = os.path.join(WHERE_AM_I, 'locale/mo')
locale.setlocale(locale.LC_ALL, locale.getlocale())
locale.bindtextdomain(APP, LOCALE_DIR)
gettext.bindtextdomain(APP, LOCALE_DIR)
gettext.textdomain(APP)

resource_data = Gio.Resource.load("io.github.swanux.hbud.gresource")
Gio.resources_register(resource_data)


@Gtk.Template(resource_path='/io/github/swanux/hbud/ui/trackbox.ui')
class TrackBox(Adw.ActionRow):
    __gtype_name__ = 'TrackBox'
    image = Gtk.Template.Child("_cover_image")
    _artist_label = Gtk.Template.Child()
    _year_label = Gtk.Template.Child()
    _length_label = Gtk.Template.Child()
    _right_click = Gtk.Template.Child()
    _left_click = Gtk.Template.Child()
    def __init__(self, title, artist, id, year, length, album):
        super().__init__()
        self.set_name(f"trackbox_{id}")
        self._artist_label.set_label(artist)
        self._year_label.set_label(str(year))
        self._length_label.set_markup(f'<b>{length}</b>')
        formatted = title.replace("&", "&amp;")
        self.set_title(f"<b>{formatted}</b>")
        self.set_subtitle(album.replace("&", "&amp;"))


@Gtk.Template(resource_path='/io/github/swanux/hbud/ui/mainstack.ui')
class MainStack(Gtk.Stack):
    __gtype_name__ = 'MainStack'
    # Page 1
    _combo_sort = Gtk.Template.Child()
    _placeholder = Gtk.Template.Child()
    _top_box = Gtk.Template.Child()
    _playlist_box = Gtk.Template.Child()
    _search_play = Gtk.Template.Child()
    _order_but = Gtk.Template.Child()
    _order_but1 = Gtk.Template.Child()
    _order_but2 = Gtk.Template.Child()
    # Page 2
    _str_box = Gtk.Template.Child()
    _str_overlay = Gtk.Template.Child()
    # Page 3
    _rd_box = Gtk.Template.Child()
    _rd_title = Gtk.Template.Child()
    _rd_artist = Gtk.Template.Child()
    _rd_year = Gtk.Template.Child()
    def __init__(self): super().__init__()


@Gtk.Template(resource_path='/io/github/swanux/hbud/ui/prefwin.ui')
class PrefWin(Adw.PreferencesWindow):
    __gtype_name__ = 'PrefWin'
    _darkew = Gtk.Template.Child()
    _colorer = Gtk.Template.Child()
    _sub_spin = Gtk.Template.Child()
    _sub_marspin = Gtk.Template.Child()
    _bg_switch = Gtk.Template.Child()
    _mus_switch = Gtk.Template.Child()
    _az_switch = Gtk.Template.Child()
    _letr_switch = Gtk.Template.Child()
    _combo_size = Gtk.Template.Child()
    _scroll_check = Gtk.Template.Child()
    _scroll_spin = Gtk.Template.Child()
    _lite_switch = Gtk.Template.Child()
    _hwa_switch = Gtk.Template.Child()
    _gtk_ver = Gtk.Template.Child()
    _gst_ver = Gtk.Template.Child()
    _adw_ver = Gtk.Template.Child()
    _py_ver = Gtk.Template.Child()
    _vah264dec = Gtk.Template.Child()
    _vah265dec = Gtk.Template.Child()
    _vampeg2dec = Gtk.Template.Child()
    _vaav1dec = Gtk.Template.Child()
    _vavp8dec = Gtk.Template.Child()
    _vavp9dec = Gtk.Template.Child()
    def __init__(self):
        super().__init__()
        self._gtk_ver.set_label("{}.{}.{}".format(Gtk.get_major_version(), Gtk.get_minor_version(), Gtk.get_micro_version()))
        self._gst_ver.set_label("{}.{}.{}.{}".format(Gst.version()[0], Gst.version()[1], Gst.version()[2], Gst.version()[3]))
        self._adw_ver.set_label("{}.{}.{}".format(Adw.get_major_version(), Adw.get_minor_version(), Adw.get_micro_version()))
        self._py_ver.set_label("{}".format(sys.version.split(" ")[0]))
        self.present_codecs = {"vah264dec":[None, self._vah264dec], "vah265dec":[None, self._vah265dec], "vampeg2dec":[None, self._vampeg2dec], "vaav1dec":[None, self._vaav1dec], "vavp8dec":[None, self._vavp8dec], "vavp9dec":[None, self._vavp9dec]}
        for c in self.present_codecs:
            x = Gst.ElementFactory.find(c)
            self.present_codecs[c][0] = x
            if x != None: icon = "object-select-symbolic"
            else: icon = "process-stop-symbolic"
            self.present_codecs[c][1].set_from_icon_name(icon)


@Gtk.Template(resource_path='/io/github/swanux/hbud/ui/mainwindow.ui')
class MainWindow(Adw.Window):
    __gtype_name__ = 'MainWindow'
    _main_stack = Gtk.Template.Child()
    _main_header = Gtk.Template.Child()
    _title = Gtk.Template.Child()
    _main_toast = Gtk.Template.Child()
    _ev_key_main = Gtk.Template.Child()
    _head_box = Gtk.Template.Child()
    _str_but = Gtk.Template.Child()
    _loc_but = Gtk.Template.Child()
    _drop_but = Gtk.Template.Child()
    _bottom = Gtk.Template.Child()
    _bottom_motion = Gtk.Template.Child()
    _slider = Gtk.Template.Child()
    _label = Gtk.Template.Child()
    _label_end = Gtk.Template.Child()
    _ofo_but = Gtk.Template.Child()
    _prev_but = Gtk.Template.Child()
    _next_but = Gtk.Template.Child()
    _play_but = Gtk.Template.Child()
    _shuff_but = Gtk.Template.Child()
    _lyr_stack = Gtk.Template.Child()
    _karaoke_but = Gtk.Template.Child()
    _lyr_spin = Gtk.Template.Child()
    _sub_track = Gtk.Template.Child()
    _prefbut = Gtk.Template.Child()
    def __init__(self, gself):
        super().__init__()
        _ = gettext.gettext

        menu = Gio.Menu()
        menu_item = Gio.MenuItem.new(_('Preferences'), "app.pref")
        menu.append_item(menu_item)
        menu_item = Gio.MenuItem.new(_('About'), "app.about")
        menu.append_item(menu_item)
        menu.freeze()
        self._prefbut.set_menu_model(menu)

        gself.menu = Gio.Menu()
        menu_item = Gio.MenuItem.new(_('Delete from current playqueue'), "app.delete")
        gself.menu.append_item(menu_item)
        menu_item = Gio.MenuItem.new(_('Edit metadata'), "app.edit")
        gself.menu.append_item(menu_item)
        gself.menu.freeze()


@Gtk.Template(resource_path='/io/github/swanux/hbud/ui/sub2.ui')
class Sub2(Adw.Window):
    __gtype_name__ = 'Sub2'
    _sub2_toast = Gtk.Template.Child()
    _yr_ent = Gtk.Template.Child()
    _ti_ent = Gtk.Template.Child()
    _al_ent = Gtk.Template.Child()
    _ar_ent = Gtk.Template.Child()
    _lyr_ent = Gtk.Template.Child()
    _ichoser = Gtk.Template.Child()
    _meta_cover = Gtk.Template.Child()
    _mag_spin = Gtk.Template.Child()
    _magi_but = Gtk.Template.Child()
    _sav_but = Gtk.Template.Child()
    def __init__(self): super().__init__()


@Gtk.Template(resource_path='/io/github/swanux/hbud/ui/sub.ui')
class Sub(Adw.Window):
    __gtype_name__ = 'Sub'
    _ev_key_sub = Gtk.Template.Child()
    _sub_stackhead = Gtk.Template.Child()
    _sub_box = Gtk.Template.Child()
    _sub_box2 = Gtk.Template.Child()
    _off_lab = Gtk.Template.Child()
    _ye_but = Gtk.Template.Child()
    _no_but = Gtk.Template.Child()
    _off_spin = Gtk.Template.Child()
    _off_but = Gtk.Template.Child()
    _sub_stack = Gtk.Template.Child()
    _lyr_lab = Gtk.Template.Child()
    _label1 = Gtk.Template.Child()
    _label2 = Gtk.Template.Child()
    _label3 = Gtk.Template.Child()
    def __init__(self): super().__init__()


class UI(Adw.Application):
    build_version = cn.App.application_version
    def __init__(self):
        super().__init__()
        Gst.init(None)
        Adw.init()
        _ = gettext.gettext
        self.useMode = "audio"
        self.supportedList = ['.3gp', '.aa', '.aac', '.aax', '.aiff', '.flac', '.m4a', '.mp3', '.ogg', '.wav', '.wma', '.wv']
        self.searchDict = {"1" : ["artist", False], "2" : ["artist", True], "3" : ["title", False], "4" : ["title", True], "5" : ["year", False], "6" : ["year", True], "7" : ["length", False], "8" : ["length", True]}
        self.playlistPlayer, self.needSub, self.nowIn = False, False, ""
        self.fulle, self.resete, self.keepReset, self.hardReset, self.tnum, self.sorted, self.aborte, self.hardreset2, self.resete2, self.clocking, self.searched = False, False, False, False, 0, False, False, False, False, False, False
        self.sub, self.seekBack, self.playing, self.res, self.title, self.countermove, self.mx, self.my = Sub(), False, False, False, None, 0, 0, 0
        self.offset = 0
        self.tmpDir = GLib.get_tmp_dir()
        self.lyr_states = [True, True, True]
        self.sub2 = Sub2()
        self.choser_window = Adw.Window()
        self.choser_window.set_transient_for(self.sub2)
        self.choser_window.set_modal(True)
        self.choser_window.set_resizable(False)
        self.headerbar = Adw.HeaderBar()
        self.headerbar.set_show_end_title_buttons(False)
        self.headerbar.add_css_class("flat")
        self.chosBox = Gtk.Box.new(1, 0)
        self.chosBox.append(self.headerbar)
        handle = Gtk.WindowHandle.new()
        handle.set_child(self.chosBox)
        self.choser_window.set_content(handle)
        self.choser_window.set_title(_("Which one is correct?"))
        self.seeking = False
        self.theTitle = Gtk.Label.new()
        self.theTitle.set_name("thetitle")
        self.theTitle.set_valign(Gtk.Align.END)
        self.header = Adw.HeaderBar()
        self.header.set_show_end_title_buttons(True)
        self.window = MainWindow(self)
        self.prefwin = PrefWin()
        self.prefwin.set_transient_for(self.window)
        self.sub2.set_transient_for(self.window)
        self.sub2.set_modal(True)
        self.about = Adw.AboutWindow(application_name=cn.App.application_name, version=self.build_version, copyright=f"Copyright © {cn.App.app_years}", issue_url=cn.App.help_url, license_type=Gtk.License.GPL_3_0, developer_name="Dániel Kolozsi", developers=["Dániel Kolozsi"], designers=["Seh", "Dániel Kolozsi"], translator_credits=_("Dániel Kolozsi"), application_icon=cn.App.application_id, comments=cn.App.about_comments, website=cn.App.main_url, transient_for=self.window, release_notes=cn.App.release_notes, default_height=450)
        self.switchDict = {"locBut" : [self.window._main_stack._placeholder, "audio-input-microphone", "audio", self.window._str_but], "strBut" : [self.window._main_stack._str_box, "view-fullscreen", "video", self.window._loc_but]}
        self.provider, self.settings = Gtk.CssProvider(), Adw.StyleManager.get_default()