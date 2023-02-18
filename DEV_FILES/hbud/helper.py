#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi, locale, os, gettext, sys
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Gst', '1.0')
from gi.repository import Gtk, Gio, GLib, Pango, Adw, Gst
from hbud import constants as cn

APP = "io.github.swanux.hbud"

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
    def __init__(self, gself):
        super().__init__()
        _ = gettext.gettext
        gself.menu = Gio.Menu()
        menu_item = Gio.MenuItem.new(_('Delete from current playqueue'), "app.delete")
        gself.menu.append_item(menu_item)
        menu_item = Gio.MenuItem.new(_('Edit metadata'), "app.edit")
        gself.menu.append_item(menu_item)
        gself.menu.freeze()

        gself.prefwin = PrefWin()
        gself.prefwin.set_transient_for(self)



# class MainWindow(Adw.Window):
#     def __init__(self, gself):
#         super(MainWindow, self).__init__()
#         _ = gettext.gettext
#         # Intro
#         self.set_name("main")
#         self.set_default_size(600, 450)
#         gself.mainHeader = Adw.HeaderBar()
#         mainbox = Gtk.Box.new(1, 0)
#         box = Gtk.Box.new(1, 0)
#         gself.mainToast = Adw.ToastOverlay.new()
#         gself.mainStack = MainStack()
#         gself.prefwin = PrefWin()
#         gself.prefwin.set_transient_for(self)
#         gself.ev_key_main = Gtk.EventControllerKey.new()
#         # Header section
#         gself.headBox = Gtk.Box.new(0, 0)
#         gself.locBut = Gtk.ToggleButton.new_with_label(_("Audio"))
#         gself.locBut.set_name("locBut")
#         gself.locBut.set_can_focus(False)
#         gself.strBut = Gtk.ToggleButton.new_with_label(_("Video"))
#         gself.strBut.set_name("strBut")
#         gself.strBut.set_can_focus(False)

#         prefbut = Gtk.MenuButton.new()
#         prefbut.set_icon_name("open-menu-symbolic")
#         prefbut.set_can_focus(False)
#         menu = Gio.Menu()
#         menu_item = Gio.MenuItem.new(_('Preferences'), "app.pref")
#         menu.append_item(menu_item)
#         menu_item = Gio.MenuItem.new(_('About'), "app.about")
#         menu.append_item(menu_item)
#         menu.freeze()
#         prefbut.set_menu_model(menu)

#         gself.menu = Gio.Menu()
#         menu_item = Gio.MenuItem.new(_('Delete from current playqueue'), "app.delete")
#         gself.menu.append_item(menu_item)
#         menu_item = Gio.MenuItem.new(_('Edit metadata'), "app.edit")
#         gself.menu.append_item(menu_item)
#         gself.menu.freeze()

#         gself.drop_but = Gtk.Button.new_from_icon_name("go-down")
#         gself.drop_but.set_tooltip_text(_("More options"))
#         gself.drop_but.set_can_focus(False)
#         gself.headBox = jean(gself.headBox, [gself.locBut, gself.strBut, gself.drop_but])
#         gself.headBox.add_css_class("linked")
#         gself.mainHeader.pack_start(gself.headBox)
#         gself.mainHeader.pack_end(prefbut)
#         # Bottom section
#         gself.bottom = Gtk.Box.new(1, 0)
#         gself.bottom.set_hexpand(True)
#         gself.bottom_motion = Gtk.EventControllerMotion.new()
#         gself.bottom.add_controller(gself.bottom_motion)
#         gself.slidBox = Gtk.Box.new(0, 0)
#         gself.slider = Gtk.Scale.new(Gtk.Orientation.HORIZONTAL, None)
#         gself.slider.set_can_focus(False)
#         gself.slider = jean(gself.slider, task="margin", ids=[0, 0, 6, 6])
#         gself.slider.set_draw_value(False)
#         gself.slider.set_increments(1, 10)
#         gself.slider.set_has_tooltip(True)
#         gself.slider.set_hexpand(True)
#         gself.label = Gtk.Label.new()
#         gself.label = jean(gself.label, task="margin", ids=[0, 0, 6, 6])
#         gself.label_end = Gtk.Label.new()
#         gself.label_end = jean(gself.label_end, task="margin", ids=[0, 0, 6, 6])
#         gself.slidBox = jean(gself.slidBox, [gself.label, gself.slider, gself.label_end])
#         player = Gtk.Box.new(0, 0)
#         player.set_homogeneous(True)
#         player.set_hexpand(True)
#         gself.openFolderBut = Gtk.Button.new_from_icon_name("folder-open")
#         gself.openFolderBut.set_can_focus(False)
#         gself.prevBut = Gtk.Button.new_from_icon_name("media-skip-backward")
#         gself.prevBut.set_can_focus(False)
#         gself.plaicon = Gtk.Image.new_from_icon_name("media-playback-start")
#         gself.playBut = Gtk.Button.new()
#         gself.playBut.set_child(gself.plaicon)
#         gself.playBut.set_can_focus(False)
#         gself.nextBut = Gtk.Button.new_from_icon_name("media-skip-forward")
#         gself.nextBut.set_can_focus(False)
#         gself.shuffBut = Gtk.Button.new_from_icon_name("media-playlist-shuffle")
#         gself.shuffBut.set_can_focus(False)
#         gself.lyrStack = Gtk.Stack()
#         gself.karaokeIcon = Gtk.Image.new_from_icon_name("audio-input-microphone")
#         gself.karaokeBut = Gtk.Button.new()
#         gself.karaokeBut.set_child(gself.karaokeIcon)
#         gself.karaokeBut.set_can_focus(False)
#         gself.lyrSpin = Gtk.Spinner()
#         gself.lyrSpin.set_size_request(-1, 32)
#         gself.lyrStack.add_named(gself.karaokeBut, "karaokeBut")
#         gself.lyrStack.add_named(gself.lyrSpin, "lyrSpin")
#         gself.lyrStack.set_margin_start(7)
#         gself.sub_track = Gtk.MenuButton.new()
#         gself.sub_track.set_icon_name("media-view-subtitles-symbolic")
#         gself.sub_track.set_can_focus(False)
#         gself.sub_track.set_sensitive(False)
#         sub_pop = Gtk.Popover()
#         gself.sub_track.set_popover(sub_pop)
#         gself.sub_track.set_margin_start(8)
#         gself.sub_track.set_direction(Gtk.ArrowType.UP)
#         modularPlayer = Gtk.Box.new(0, 0)
#         player = jean(player, [gself.openFolderBut, gself.prevBut, gself.playBut, gself.nextBut, gself.shuffBut])
#         player.add_css_class("linked")
#         modularPlayer = jean(modularPlayer, [player, gself.sub_track, gself.lyrStack])
#         modularPlayer.set_margin_end(5)
#         gself.bottom = jean(gself.bottom, [gself.slidBox, modularPlayer])
#         gself.bottom = jean(gself.bottom, task="margin", ids=[5, 7, 7, 5])
#         # Outro
#         gself.mainToast.set_child(gself.mainStack)
#         box = jean(box, [gself.mainToast, gself.bottom])
#         mainbox = jean(mainbox, [gself.mainHeader, box])
#         self.add_controller(gself.ev_key_main)
#         handle = Gtk.WindowHandle.new()
#         handle.set_child(mainbox)
#         self.set_content(handle)

class Sub2(Adw.Window):
    def __init__(self, gself):
        super(Sub2, self).__init__()
        _ = gettext.gettext
        # Intro
        self.set_name("sub2")
        headerbar = Adw.HeaderBar()
        headerbar.add_css_class("flat")
        mainBox = Gtk.Box.new(1, 0)
        gself.sub2Toast = Adw.ToastOverlay()
        dat_grid = Gtk.Grid.new()
        dat_grid.set_row_spacing(5)
        dat_grid.set_column_spacing(5)
        dat_grid = jean(dat_grid, task="margin", ids=[0, 15, 20, 20])
        
        # Main
        gself.yrEnt = Gtk.SpinButton.new_with_range(1400, 2100, 1)
        gself.yrEnt.set_valign(Gtk.Align.CENTER)
        gself.yrEnt.set_numeric(True)
        gself.yrEnt.set_value(1000)
        gself.tiEnt = Gtk.Entry()
        gself.tiEnt.set_valign(Gtk.Align.CENTER)
        gself.tiEnt.set_max_length(50)
        gself.tiEnt.set_placeholder_text(_("Title"))
        gself.alEnt = Gtk.Entry()
        gself.alEnt.set_valign(Gtk.Align.CENTER)
        gself.alEnt.set_max_length(80)
        gself.alEnt.set_placeholder_text(_("Album"))
        gself.arEnt = Gtk.Entry()
        gself.arEnt.set_valign(Gtk.Align.CENTER)
        gself.arEnt.set_max_length(40)
        gself.arEnt.set_input_purpose(Gtk.InputPurpose.NAME)
        gself.arEnt.set_placeholder_text(_("John Doe"))
        gself.lyrEnt = Gtk.TextView(wrap_mode=Gtk.WrapMode.WORD, valign=Gtk.Align.CENTER)
        scroll = Gtk.ScrolledWindow(child=gself.lyrEnt, propagate_natural_width=True)     
        scroll.set_size_request(-1, 150)

        for item in [gself.yrEnt, gself.tiEnt, gself.alEnt, gself.arEnt, scroll]: item.set_vexpand(True)

        for i, item in enumerate([_("Year :"), _("Artist :"), _("Album :"), _("Title :"), _("Lyrics :"), _("Cover art :")]):
            label = Gtk.Label.new(item)
            label.add_css_class("title-4")
            label.set_justify(Gtk.Justification.CENTER)
            dat_grid.attach(label, 0, i, 1, 1)
        
        covBox = Gtk.Box.new(0, 0)
        gself.iChoser = Gtk.Button.new()
        gself.iChoser.set_valign(Gtk.Align.CENTER)
        gself.iChoser.set_halign(Gtk.Align.END)
        gself.iChoser.set_hexpand(True)
        shitBox = jean(Gtk.Box.new(0, 7), [Gtk.Image.new_from_icon_name("folder-open"), Gtk.Label.new(_("Browse"))])
        gself.iChoser.set_child(shitBox)
        gself.metaCover = Gtk.Picture.new()
        gself.metaCover = jean(gself.metaCover, task="margin", ids=[5, 5, 20, 0])
        gself.metaCover.set_halign(Gtk.Align.CENTER)
        gself.metaCover.set_valign(Gtk.Align.CENTER)
        gself.metaCover.set_overflow(Gtk.Overflow.HIDDEN)
        gself.metaCover.set_hexpand(True)
        gself.metaCover.set_size_request(100, 100)
        covBox = jean(covBox, [gself.iChoser, gself.metaCover])

        magBox = Gtk.Box.new(0, 5)
        gself.magiSpin = Gtk.Spinner()
        gself.magiBut = Gtk.Button.new_from_icon_name("sync-synchronizing")
        gself.magiBut.set_valign(Gtk.Align.CENTER)
        gself.magiBut.set_halign(Gtk.Align.CENTER)
        magBox.append(gself.magiSpin)
        magBox.append(Gtk.Label.new(_("Fetch metadata")))
        gself.magiBut.set_child(magBox)
        gself.savBut = Gtk.Button.new_with_label(_("Save"))
        gself.savBut.set_valign(Gtk.Align.CENTER)
        gself.savBut.set_halign(Gtk.Align.END)
        gself.savBut.set_hexpand(True)
        dat_grid.attach(gself.magiBut, 0, 6, 1, 1)

        for i, item in enumerate([gself.yrEnt, gself.arEnt, gself.alEnt, gself.tiEnt, scroll, covBox, gself.savBut]):
            dat_grid.attach(item, 1, i, 1, 1)
        # Outro
        mainBox.append(headerbar)
        mainBox.append(dat_grid)
        gself.sub2Toast.set_child(mainBox)
        # handler.set_child(gself.sub2Toast)
        self.set_content(gself.sub2Toast)
        self.set_size_request(500, 400)
        self.set_resizable(False)
        self.set_title(_("HBud - Metadata editor"))


class Sub(Adw.Window):
    def __init__(self, gself):
        super(Sub, self).__init__()
        _ = gettext.gettext
        self.set_name("sub")
        headerbar = Adw.HeaderBar()
        mainBox = Gtk.Box.new(1, 0)
        gself.ev_key_sub = Gtk.EventControllerKey.new()
        gself.substackhead = Gtk.Stack.new()
        gself.subbox = Gtk.Box.new(0, 0)
        gself.subbox2 = Gtk.Box.new(0, 0)
        gself.subbox = jean(gself.subbox, task="margin", ids=[0, 0, 6, 6])
        gself.subbox2 = jean(gself.subbox2, task="margin", ids=[0, 0, 6, 6])
        gself.off_lab = Gtk.Label.new(_("Offset (ms):"))
        gself.off_lab.set_margin_end(10)
        conf_lab1 = Gtk.Label.new(_("Is this lyrics correct?"))
        conf_lab1.set_margin_end(10)
        gself.subbox.append(gself.off_lab)
        gself.subbox2.append(conf_lab1)
        gself.ye_but = Gtk.Button.new_with_label(_("Yes"))
        gself.no_but = Gtk.Button.new_with_label(_("No"))
        gself.subbox2.append(gself.ye_but)
        gself.subbox2.append(gself.no_but)
        gself.off_spin = Gtk.SpinButton.new_with_range(-99999, 99999, 5)
        gself.off_spin.set_digits(2)
        gself.off_spin.set_numeric(True)
        gself.off_spin.set_can_focus(False)
        gself.subbox.append(gself.off_spin)
        gself.off_but = Gtk.Button.new_with_label(_("Apply"))
        gself.off_but.set_can_focus(False)
        gself.subbox.append(gself.off_but)

        ##########

        gself.karmode = Gtk.ScrolledWindow()
        gself.lyrmode = Gtk.ScrolledWindow()
        gself.lyrmode.set_propagate_natural_width(True)

        req_view = Gtk.Viewport()
        req_view2 = Gtk.Viewport()
        boxForText = Gtk.Box.new(1, 5)
        gself.subStack = Gtk.Stack()

        gself.label1 = Gtk.Label.new()
        gself.label1.set_name("label1")
        gself.label1.set_valign(Gtk.Align.FILL)
        gself.label1.set_halign(Gtk.Align.FILL)
        gself.label1.set_margin_top(5)
        gself.label1.set_margin_bottom(5)
        gself.label1.set_vexpand(True)
        gself.label1.set_hexpand(True)
        gself.label1.set_wrap(True)
        gself.label1.set_wrap_mode(Gtk.WrapMode.WORD)
        gself.label1.set_justify(Gtk.Justification.CENTER)
        gself.label2 = Gtk.Label.new()
        gself.label2.set_name("label2")
        gself.label2.set_margin_top(5)
        gself.label2.set_margin_bottom(5)
        gself.label2.set_wrap(True)
        gself.label2.set_wrap_mode(Gtk.WrapMode.WORD)
        gself.label2.set_justify(Gtk.Justification.CENTER)
        gself.label3 = Gtk.Label.new()
        gself.label3.set_name("label3")
        gself.label3.set_margin_top(5)
        gself.label3.set_margin_bottom(5)
        gself.label3.set_wrap(True)
        gself.label3.set_wrap_mode(Gtk.WrapMode.WORD)
        gself.label3.set_justify(Gtk.Justification.CENTER)

        boxForText.append(gself.label1)
        boxForText.append(gself.label2)
        boxForText.append(gself.label3)
        req_view.set_child(boxForText)
        gself.karmode.set_child(req_view)
        gself.subStack.add_named(gself.karmode, "req_scroll")

        gself.lyrLab = Gtk.Label.new()
        gself.lyrLab = jean(gself.lyrLab, task="margin", ids=[20, 10, 10, 10])
        gself.lyrLab.set_wrap(True)
        gself.lyrLab.set_wrap_mode(Gtk.WrapMode.WORD)
        attrlist = Pango.AttrList()
        attrlist.insert(Pango.attr_weight_new(Pango.Weight.ULTRAHEAVY))
        attrlist.insert(Pango.attr_size_new(22000))
        gself.lyrLab.set_attributes(attrlist)

        req_view2.set_child(gself.lyrLab)
        gself.lyrmode.set_child(req_view2)
        gself.subStack.add_named(gself.lyrmode, "req_scroll2")

        #######

        gself.substackhead.add_named(gself.subbox, "subbox")
        gself.substackhead.add_named(gself.subbox2, "subbox2")
        gself.subbox.add_css_class("linked")
        gself.subbox2.add_css_class("linked")
        headerbar.pack_start(gself.substackhead)
        headerbar.add_css_class("flat")
        mainBox.append(headerbar)
        mainBox.append(gself.subStack)
        handle = Gtk.WindowHandle.new()
        handle.set_child(mainBox)
        self.add_controller(gself.ev_key_sub)
        self.set_content(handle)
        self.set_default_size(560, 360)

class Widgets(Adw.Application):
    def __init__(self):
        super(Widgets, self).__init__()
        _ = gettext.gettext
        Gst.init(None)
        self.application_id = cn.App.application_id
        self.build_version = cn.App.application_version
        self.bug_url = cn.App.bug_url
        self.help_url = cn.App.help_url
        self.useMode = "audio"
        self.supportedList = ['.3gp', '.aa', '.aac', '.aax', '.aiff', '.flac', '.m4a', '.mp3', '.ogg', '.wav', '.wma', '.wv']
        self.searchDict = {"1" : ["artist", False], "2" : ["artist", True], "3" : ["title", False], "4" : ["title", True], "5" : ["year", False], "6" : ["year", True], "7" : ["length", False], "8" : ["length", True]}
        self.playlistPlayer, self.needSub, self.nowIn = False, False, ""
        self.fulle, self.resete, self.keepReset, self.hardReset, self.tnum, self.sorted, self.aborte, self.hardreset2, self.resete2, self.clocking, self.searched = False, False, False, False, 0, False, False, False, False, False, False
        self.sub, self.seekBack, self.playing, self.res, self.title, self.countermove, self.mx, self.my = Sub(self), False, False, False, None, 0, 0, 0
        self.offset = 0
        self.tmpDir = GLib.get_tmp_dir()
        self.lyr_states = [True, True, True]
        self.sub2 = Sub2(self)
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
        self.mainStack = MainStack()
        self.window = MainWindow(self)
        self.sub2.set_transient_for(self.window)
        self.sub2.set_modal(True)
        self.about = Adw.AboutWindow(application_name=cn.App.application_name, version=self.build_version, copyright=f"Copyright © {cn.App.app_years}", issue_url=cn.App.help_url, license_type=Gtk.License.GPL_3_0, developer_name="Dániel Kolozsi", developers=["Dániel Kolozsi"], designers=["Seh", "Dániel Kolozsi"], translator_credits=_("Dániel Kolozsi"), application_icon=cn.App.application_id, comments=cn.App.about_comments, website=cn.App.main_url, transient_for=self.window, release_notes=cn.App.release_notes, default_height=450)
        self.switchDict = {"locBut" : [self.mainStack._placeholder, "audio-input-microphone", "audio", self.window._str_but], "strBut" : [self.mainStack._str_box, "view-fullscreen", "video", self.window._loc_but]}
        self.provider, self.settings = Gtk.CssProvider(), Adw.StyleManager.get_default()

def jean(parent, children=[""], task="append", ids=[]):
    for i, child in enumerate(children):
        if task == "append": parent.append(child)
        elif task == "prepend": parent.prepend(child)
        elif task == "combo": parent.append(ids[i], child)
        elif task == "margin":
            parent.set_margin_top(ids[0])
            parent.set_margin_bottom(ids[1])
            parent.set_margin_start(ids[2])
            parent.set_margin_end(ids[3])
    return parent