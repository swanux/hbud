#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi, gettext, sys, os
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Gst', '1.0')
from gi.repository import Gtk, Gio, GLib, Adw, Gst, Gdk, GObject
from hbud import CONSTANTS


if os.getenv('container', '') != 'flatpak':
    if os.getenv("HDIR", "") == "":
        Gio.resources_register(Gio.Resource.load("../io.github.swanux.hbud.gresource"))
        schema_source = Gio.SettingsSchemaSource.new_from_directory("../schemas", None, None)
    else:
        Gio.resources_register(Gio.Resource.load("DEV_FILES/io.github.swanux.hbud.gresource"))
        schema_source = Gio.SettingsSchemaSource.new_from_directory("DEV_FILES/schemas", None, None)
    schema = schema_source.lookup("io.github.swanux.hbud", True)
    settings = Gio.Settings.new_full(schema, None, None)
else:
    Gio.resources_register(Gio.Resource.load("/app/share/hbud/io.github.swanux.hbud.gresource"))
    settings = Gio.Settings(schema_id="io.github.swanux.hbud")


@Gtk.Template(resource_path='/io/github/swanux/hbud/DEV_FILES/source/ui/trackbox.ui')
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
        self._year_label.set_label("| {} |".format(str(year)))
        self._length_label.set_markup(f'<b>{length}</b>')
        formatted = title.replace("&", "&amp;")
        self.set_title(f"<b>{formatted}</b>")
        self.set_subtitle(album.replace("&", "&amp;"))


@Gtk.Template(resource_path='/io/github/swanux/hbud/DEV_FILES/source/ui/playlistbox.ui')
class PlayListBox(Adw.ActionRow):
    __gtype_name__ = 'PlayListBox'
    _start_but = Gtk.Template.Child()
    _ed_but = Gtk.Template.Child()
    _del_but = Gtk.Template.Child()
    def __init__(self, title, subtitle, id):
        super().__init__()
        self.set_title(title)
        self.set_subtitle(subtitle)
        self.set_name(f"playlistbox_{id}")
        self._del_but.set_name(f"del_but_{id}")
        self._ed_but.set_name(f"ed_but_{id}")
        self._start_but.set_name(f"start_but_{id}")


@Gtk.Template(resource_path='/io/github/swanux/hbud/DEV_FILES/source/ui/deldialog.ui')
class DeleteDialog(Adw.MessageDialog):
    __gtype_name__ = 'DeleteDialog'
    def __init__(self, ogname):
        super().__init__()
        _ = gettext.gettext
        self.set_heading(_("Delete Playlist \"{}\"?".format(ogname)))


@Gtk.Template(resource_path='/io/github/swanux/hbud/DEV_FILES/source/ui/renamedialog.ui')
class RenameDialog(Adw.MessageDialog):
    __gtype_name__ = 'RenameDialog'
    _rename_entry = Gtk.Template.Child()
    def __init__(self, ogname):
        super().__init__()
        _ = gettext.gettext
        self.set_heading(_("Rename Playlist ({})".format(ogname)))
        self._rename_entry.connect('notify::text', self.on_rename_entry_text_changed)
    
    def on_rename_entry_text_changed(self, entry, _):
        text = entry.get_text()
        self.set_response_enabled("save", len(text) > 0)


@Gtk.Template(resource_path='/io/github/swanux/hbud/DEV_FILES/source/ui/mainstack.ui')
class MainStack(Gtk.Stack):
    __gtype_name__ = 'MainStack'
    # Page 1
    _combo_sort = Gtk.Template.Child()
    _placeholder = Gtk.Template.Child()
    _top_reveal = Gtk.Template.Child()
    _sup_box = Gtk.Template.Child()
    _sup_scroll = Gtk.Template.Child()
    _sup_spinbox = Gtk.Template.Child()
    _sup_stack = Gtk.Template.Child()
    _search_play = Gtk.Template.Child()
    _order_but = Gtk.Template.Child()
    _order_but2 = Gtk.Template.Child()
    _side_flap = Gtk.Template.Child()
    _play_list_box = Gtk.Template.Child()
    _flap_stack = Gtk.Template.Child()
    _nope_lab = Gtk.Template.Child()
    # Page 2
    _str_box = Gtk.Template.Child()
    _video_picture = Gtk.Template.Child()
    _video_click = Gtk.Template.Child()
    _subtitles = Gtk.Template.Child()
    _overlay_full = Gtk.Template.Child()
    _overlay_play = Gtk.Template.Child()
    _overlay_subs = Gtk.Template.Child()
    _overlay_time = Gtk.Template.Child()
    _overlay_scale = Gtk.Template.Child()
    _overlay_revealer = Gtk.Template.Child()
    _overlay_motion = Gtk.Template.Child()
    _hub_motion = Gtk.Template.Child()
    _hub_motion2 = Gtk.Template.Child()
    _overlay_hub = Gtk.Template.Child()
    _current_time = Gtk.Template.Child()
    _end_time = Gtk.Template.Child()
    # Page 3
    _rd_box = Gtk.Template.Child()
    _rd_title = Gtk.Template.Child()
    _rd_artist = Gtk.Template.Child()
    _rd_year = Gtk.Template.Child()
    def __init__(self):
        super().__init__()
        content = Gdk.ContentFormats.new_for_gtype(Gdk.FileList)
        self._drop_music = Gtk.DropTarget(formats=content, actions=Gdk.DragAction.COPY)
        self.add_controller(self._drop_music)

        controllers = self._overlay_scale.observe_controllers()
        for controller in controllers:
            if isinstance(controller, gi.repository.Gtk.GestureClick):
                self._overlay_click = controller
                break


@Gtk.Template(resource_path='/io/github/swanux/hbud/DEV_FILES/source/ui/hbudshortcuts.ui')
class HbudShortcuts(Gtk.ShortcutsWindow):
    __gtype_name__ = 'HbudShortcuts'
    def __init__(self): super().__init__()


@Gtk.Template(resource_path='/io/github/swanux/hbud/DEV_FILES/source/ui/prefwin.ui')
class PrefWin(Adw.PreferencesWindow):
    __gtype_name__ = 'PrefWin'
    _darkew = Gtk.Template.Child()
    _colorer = Gtk.Template.Child()
    _sub_spin = Gtk.Template.Child()
    _opac_spin = Gtk.Template.Child()
    _sub_marspin = Gtk.Template.Child()
    _bg_switch = Gtk.Template.Child()
    _mus_switch = Gtk.Template.Child()
    _az_switch = Gtk.Template.Child()
    _letr_switch = Gtk.Template.Child()
    _combo_size = Gtk.Template.Child()
    _scroll_check = Gtk.Template.Child()
    _scroll_spin = Gtk.Template.Child()
    _clear_cache = Gtk.Template.Child()
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
        settings.bind("theme", self._darkew, "active-id", Gio.SettingsBindFlags.DEFAULT)
        settings.bind("relative-size", self._sub_spin, "value", Gio.SettingsBindFlags.DEFAULT)
        settings.bind("opacity", self._opac_spin, "value", Gio.SettingsBindFlags.DEFAULT)
        settings.bind("relative-margin", self._sub_marspin, "value", Gio.SettingsBindFlags.DEFAULT)
        settings.bind("dark-background", self._bg_switch, "active", Gio.SettingsBindFlags.DEFAULT)
        settings.bind("musixmatch", self._mus_switch, "active", Gio.SettingsBindFlags.DEFAULT)
        settings.bind("azlyrics", self._az_switch, "active", Gio.SettingsBindFlags.DEFAULT)
        settings.bind("letrasbr", self._letr_switch, "active", Gio.SettingsBindFlags.DEFAULT)
        settings.bind("cover-size", self._combo_size, "active-id", Gio.SettingsBindFlags.DEFAULT)
        settings.bind("autoscroll", self._scroll_check, "active", Gio.SettingsBindFlags.DEFAULT)
        settings.bind("positioning", self._scroll_spin, "value", Gio.SettingsBindFlags.DEFAULT)
        settings.bind("minimal-mode", self._lite_switch, "active", Gio.SettingsBindFlags.DEFAULT)
        settings.bind("hwa-enabled", self._hwa_switch, "active", Gio.SettingsBindFlags.DEFAULT)

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


@Gtk.Template(resource_path='/io/github/swanux/hbud/DEV_FILES/source/ui/mainwindow.ui')
class MainWindow(Adw.Window):
    __gtype_name__ = 'MainWindow'
    _main_stack = Gtk.Template.Child()
    _toggle_pane_button = Gtk.Template.Child()
    _head_reveal = Gtk.Template.Child()
    _main_toast = Gtk.Template.Child()
    _ev_key_main = Gtk.Template.Child()
    _head_box = Gtk.Template.Child()
    _str_but = Gtk.Template.Child()
    _loc_but = Gtk.Template.Child()
    _drop_but = Gtk.Template.Child()
    _main_motion = Gtk.Template.Child()
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
    def __init__(self):
        super().__init__()
        _ = gettext.gettext
        settings.bind("width", self, "default-width", Gio.SettingsBindFlags.DEFAULT)
        settings.bind("height", self, "default-height", Gio.SettingsBindFlags.DEFAULT)
        settings.bind("is-maximized", self, "maximized", Gio.SettingsBindFlags.DEFAULT)
        settings.bind("is-fullscreen", self, "fullscreened", Gio.SettingsBindFlags.DEFAULT)

        _adj_over = self._main_stack._overlay_scale.get_adjustment()
        _adj_win = self._slider.get_adjustment()
        self._main_stack._side_flap.bind_property(
            "reveal-flap", self._toggle_pane_button, "active",
            GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.BIDIRECTIONAL)
        self._main_stack._overlay_play.bind_property(
            "icon-name", self._play_but, "icon-name",
            GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.BIDIRECTIONAL)
        self._main_stack._overlay_subs.bind_property(
            "sensitive", self._sub_track, "sensitive",
            GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.BIDIRECTIONAL)
        _adj_over.bind_property("lower", _adj_win, "lower",
            GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.BIDIRECTIONAL)
        _adj_over.bind_property("upper", _adj_win, "upper",
            GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.BIDIRECTIONAL)
        _adj_over.bind_property("value", _adj_win, "value",
            GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.BIDIRECTIONAL)

        controllers = self._slider.observe_controllers()
        for controller in controllers:
            if isinstance(controller, gi.repository.Gtk.GestureClick):
                self._slider_click = controller
                break

        menu = Gio.Menu()
        menu_item = Gio.MenuItem.new(_('Preferences'), "app.pref")
        menu.append_item(menu_item)
        menu_item = Gio.MenuItem.new(_('Keyboard Shortcuts'), "app.shortcuts")
        menu.append_item(menu_item)
        menu_item = Gio.MenuItem.new(_('About'), "app.about")
        menu.append_item(menu_item)
        menu.freeze()
        self._prefbut.set_menu_model(menu)


@Gtk.Template(resource_path='/io/github/swanux/hbud/DEV_FILES/source/ui/sub2.ui')
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


@Gtk.Template(resource_path='/io/github/swanux/hbud/DEV_FILES/source/ui/sub.ui')
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
    build_version = CONSTANTS["version"]
    def __init__(self):
        super().__init__(flags=Gio.ApplicationFlags.HANDLES_OPEN)
        self._ = gettext.gettext
        Gst.init(None)
        Adw.init()
        self.useMode, self.duration_nanosecs, self.remaining = "audio", 0, 0
        self.searchDict = {"1" : ["artist", False], "2" : ["artist", True], "3" : ["title", False], "4" : ["title", True], "5" : ["year", False], "6" : ["year", True], "7" : ["length", False], "8" : ["length", True]}
        self.playlistPlayer, self.needSub, self.nowIn = False, False, ""
        self.fulle, self.resete, self.keepReset, self.hardReset, self.tnum, self.sorted, self.aborte, self.hardreset2, self.resete2, self.clocking, self.searched = False, False, False, False, 0, False, False, False, False, False, False
        self.playing, self.res, self.title, self.countermove, self.mx, self.my = False, False, None, 0, 0, 0
        self.offset = 0
        self.cacheDir = GLib.get_user_cache_dir()
        if os.path.isdir(f"{self.cacheDir}/hbud") is False: os.mkdir(f"{self.cacheDir}/hbud")
        self.lyr_states = [True, True, True]
        self.choser_window = Adw.Window()
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
        self.choser_window.set_title(self._("Which one is correct?"))
        self.seeking = False
        self.menu = Gio.Menu()
        menu_item = Gio.MenuItem.new(self._('Delete from current playqueue'), "app.delete")
        self.menu.append_item(menu_item)
        menu_item = Gio.MenuItem.new(self._('Edit metadata'), "app.edit")
        self.menu.append_item(menu_item)
        self.menu.freeze()
        self.about = Adw.AboutWindow(application_name=CONSTANTS["name"],
                    version=self.build_version, copyright="Copyright © {}".format(CONSTANTS["years"]),
                    issue_url=CONSTANTS["help_url"], license_type=Gtk.License.GPL_3_0,
                    developer_name="Dániel Kolozsi", developers=["Dániel Kolozsi"],
                    designers=["Seh", "Dániel Kolozsi"],
                    translator_credits=self._("Dániel Kolozsi"),
                    application_icon=CONSTANTS["app_id"],
                    comments=CONSTANTS["app_desc"],
                    website=CONSTANTS["main_url"],
                    release_notes=CONSTANTS["rel_notes"], default_height=650)
        self.provider, self.styles = Gtk.CssProvider(), Adw.StyleManager.get_default()
        self.settings = settings
        self.window = MainWindow()
        self.sub = Sub()
        self.sub2 = Sub2()
        self.sub2.set_transient_for(self.window)
        self.choser_window.set_transient_for(self.sub2)
        self.shortcuts = HbudShortcuts()
        self.shortcuts.set_transient_for(self.window)
        self.prefwin = PrefWin()
        self.prefwin.set_transient_for(self.window)
        self.about.set_transient_for(self.window)
        self.switchDict = {"locBut" : [self.window._main_stack._side_flap, "audio-input-microphone", "audio", self.window._str_but],
                           "strBut" : [self.window._main_stack._str_box, "view-fullscreen", "video", self.window._loc_but]}