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

class TrackBox(Adw.ActionRow):
    def __init__(self, title, artist, id, year, length, album):
        super(TrackBox, self).__init__()
        self.set_name(f"trackbox_{id}")
        self.set_hexpand(True)
        arLab = Gtk.Label.new(artist)
        yeLab = Gtk.Label.new(str(year))
        leLab = Gtk.Label.new()
        leLab.set_markup(f'<b>{length}</b>')
        leLab.set_halign(Gtk.Align.END)
        leLab.set_hexpand(False)
        arLab.set_ellipsize(3)
        arLab.set_halign(Gtk.Align.END)
        yeLab.set_halign(Gtk.Align.END)
        yeLab.set_hexpand(False)
        arLab.set_hexpand(False)

        formatted = title.replace("&", "&amp;")
        self.set_title(f"<b>{formatted}</b>")
        self.set_subtitle(album.replace("&", "&amp;"))
        self.add_suffix(arLab)
        self.add_suffix(yeLab)
        self.add_suffix(leLab)
        self.set_title_lines(2)
        self.set_margin_end(15)
        self.image = Gtk.Picture.new()
        self.image.set_size_request(65, 65)
        self.image.set_overflow(Gtk.Overflow.HIDDEN)
        self.image = jean(self.image, task="margin", ids=[7, 7, 0, 0])
        self.add_prefix(self.image)

class MainStack(Gtk.Stack):
    def __init__(self, gself):
        super(MainStack, self).__init__()
        _ = gettext.gettext
        self.set_name("mainStack")
        self.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.set_transition_duration(300)
        self.set_vexpand(True)
        self.set_hexpand(True)
        # Page 1
        gself.placeholder = Gtk.Box.new(1, 0)
        gself.topBox = Gtk.Box.new(0, 0)
        gself.playlistBox = Gtk.Box.new(1, 0)
        gself.playlistBox.set_vexpand(True)
        gself.playlistBox.set_hexpand(True)
        gself.playlistBox = jean(gself.playlistBox, task="margin", ids=[10, 0, 10, 0])
        gself.topBox = jean(gself.topBox, task="margin", ids=[5, 10, 10, 10])
        gself.combo_sort = Gtk.ComboBoxText.new()
        gself.combo_sort = jean(gself.combo_sort, [_("Do not sort"), _("Sort by Artist (a-z)"), _("Sort by Artist (z-a)"), _("Sort by Title (a-z)"), _("Sort by Title (z-a)"), _("Sort by Year (0-9)"), _("Sort by Year (9-0)"), _("Sort by Length (0-9)"), _("Sort by Length (9-0)")], "combo", ["0", "1", "2", "3", "4", "5", "6", "7", "8"])
        gself.combo_sort.set_active_id("0")
        gself.combo_sort.set_popup_fixed_width(True)
        gself.combo_sort.set_can_focus(False)
        gself.search_play = Gtk.SearchEntry()
        gself.search_play.set_max_width_chars(100)
        gself.search_play.set_hexpand(True)
        gself.search_play.set_name("search_play")
        gself.order_but = Gtk.Button.new_with_label(_("Save"))
        gself.order_but2 = Gtk.Button.new_with_label(_("Rescan"))
        gself.order_but1 = Gtk.Button.new_with_label(_("Clear"))
        gself.order_but.set_can_focus(False)
        gself.order_but1.set_can_focus(False)
        gself.order_but2.set_can_focus(False)
        gself.order_but.set_tooltip_text(_("Save current order"))
        gself.order_but2.set_tooltip_text(_("Rescan your music library, append new tracks"))
        gself.order_but1.set_tooltip_text(_("Clear saved order"))
        gself.topBox = jean(gself.topBox, [gself.combo_sort, gself.search_play, gself.order_but, gself.order_but2, gself.order_but1])
        gself.topBox.add_css_class("linked")
        gself.placeholder = jean(gself.placeholder, [gself.topBox, gself.playlistBox])
        # Page 2
        gself.strBox = Gtk.Box.new(1, 0)
        gself.strOverlay = Gtk.Overlay.new()
        gself.strOverlay.set_hexpand(True)
        gself.strOverlay.set_vexpand(True)
        gself.strBox.append(gself.strOverlay)
        # Page 3
        gself.rdBox = Gtk.Box.new(1, 0)
        gself.rdBox.set_vexpand(True)
        gself.rdBox.set_hexpand(True)
        gself.rdTitle = Gtk.Label.new()
        gself.rdTitle.add_css_class("title-4")
        gself.rdTitle.set_ellipsize(3)
        gself.rdArtist = Gtk.Label.new()
        gself.rdArtist.set_ellipsize(3)
        gself.rdYear = Gtk.Label.new()
        gself.rdYear.set_valign(Gtk.Align.CENTER)
        gself.rdArtist.set_valign(Gtk.Align.CENTER)
        gself.rdTitle.set_valign(Gtk.Align.CENTER)
        gself.rdBox.set_margin_start(5)
        gself.rdBox.set_margin_end(5)
        gself.rdBox.set_valign(Gtk.Align.CENTER)
        gself.rdBox = jean(gself.rdBox, [gself.rdTitle, gself.rdArtist, gself.rdYear])

        # Add pages
        self.add_named(gself.placeholder, "placeholder")
        self.add_named(gself.strBox, "strBox")
        self.add_named(gself.rdBox, "rdBox")

class PrefWin(Adw.PreferencesWindow):
    def __init__(self, gself):
        super(PrefWin, self).__init__()
        _ = gettext.gettext
        self.set_name("prefwin")
        page = Adw.PreferencesPage.new()
        page.set_title(_("General"))
        page.set_icon_name("user-home-symbolic")
        page_2 = Adw.PreferencesPage.new()
        page_2.set_title(_("System info"))
        page_2.set_icon_name("applications-engineering-symbolic")

        Group = Adw.PreferencesGroup.new()
        Group.set_title(_("Appearance"))
        row, gself.darkew = self.gen_row(0, _("Theme"), Gtk.ComboBoxText.new(), "combo", "", [_("System"), _("Dark"), _("Light")])
        Group.add(row)
        row, gself.colorer = self.gen_row(1, _("Accent color"), Gtk.ColorButton.new(), "color")
        Group.add(row)
        page.add(Group)

        Group = Adw.PreferencesGroup.new()
        Group.set_title(_("Subtitles"))
        row, gself.subSpin = self.gen_row(2, _("Size"), Gtk.SpinButton.new_with_range(10, 99, 1), "spin", _("Default is 30"))
        Group.add(row)
        row, gself.subMarSpin = self.gen_row(3, _("Margin"), Gtk.SpinButton.new_with_range(10, 99, 1), "spin", _("Default is 66"))
        Group.add(row)
        row, gself.bg_switch = self.gen_row(4, _("Dark background"), Gtk.Switch.new(), "switch")
        Group.add(row)
        page.add(Group)

        Group = Adw.PreferencesGroup.new()
        Group.set_title(_("Services"))
        row, gself.mus_switch = self.gen_row(5, _("MusixMatch"), Gtk.Switch.new(), "switch")
        Group.add(row)
        row, gself.az_switch = self.gen_row(6, _("AZLyrics"), Gtk.Switch.new(), "switch")
        Group.add(row)
        row, gself.letr_switch = self.gen_row(7, _("Letras.mus.br"), Gtk.Switch.new(), "switch")
        Group.add(row)
        row, gself.comboSize = self.gen_row(8, _("Preferred album cover quality"), Gtk.ComboBoxText.new(), "combo2", _("Default is High"), [[_("Ultra High (1200px)"), 1200], [_("High (500px)"), 500], [_("Normal (250px)"), 250]])
        Group.add(row)
        page.add(Group)

        Group = Adw.PreferencesGroup.new()
        Group.set_title(_("Behavior"))
        row, gself.scroll_check = self.gen_row(9, _("Auto-scroll"), Gtk.Switch.new(), "switch", _("Automatically scroll to make the current song visible - might be useful, but might be annoying"))
        Group.add(row)
        row, gself.scroll_spin = self.gen_row(10, _("Auto-scroll positioning"), Gtk.SpinButton.new_with_range(5, 250, 1), "spin", _("Default is 5 - increase to make the current song appear further down on the screen"))
        Group.add(row)
        row, gself.lite_switch = self.gen_row(11, _("Minimal mode"), Gtk.Switch.new(), "switch", _("A minimal player mode, better performance and less distraction\nNote: The window will be refreshed after state change"))
        Group.add(row)
        row, gself.hwa_switch = self.gen_row(12, _("Hardware Acceleration"), Gtk.Switch.new(), "switch", _("Whether to use VA for HW acceleration or not\nNote: Turning this off may result in increased stability but worse performance"))
        Group.add(row)
        page.add(Group)

        Group = Adw.PreferencesGroup.new()
        Group.set_title(_("Library versions"))
        row, widget = self.gen_row(99, "GTK", Gtk.Label.new("{}.{}.{}".format(Gtk.get_major_version(), Gtk.get_minor_version(), Gtk.get_micro_version())), "label")
        Group.add(row)
        row, widget = self.gen_row(99, "GStreamer", Gtk.Label.new("{}.{}.{}.{}".format(Gst.version()[0], Gst.version()[1], Gst.version()[2], Gst.version()[3])), "label")
        Group.add(row)
        row, widget = self.gen_row(99, "LibAdwaita", Gtk.Label.new("{}.{}.{}".format(Adw.get_major_version(), Adw.get_minor_version(), Adw.get_micro_version())), "label")
        Group.add(row)
        row, widget = self.gen_row(99, "Python", Gtk.Label.new("{}".format(sys.version.split(" ")[0])), "label")
        Group.add(row)
        page_2.add(Group)

        Group = Adw.PreferencesGroup.new()
        Group.set_title(_("Hardware decoding"))
        gself.present_codecs = {"vah264dec":None, "vah265dec":None, "vampeg2dec":None, "vaav1dec":None, "vavp8dec":None, "vavp9dec":None}
        for c in gself.present_codecs:
            x = Gst.ElementFactory.find(c)
            gself.present_codecs[c] = x
            if x != None: icon = "object-select-symbolic"
            else: icon = "process-stop-symbolic"
            row, widget = self.gen_row(99, c, Gtk.Image.new_from_icon_name(icon), "image")
            Group.add(row)
        page_2.add(Group)

        del widget
        self.add(page)
        self.add(page_2)

    def gen_row(self, uid, title, widget, widtype, subtitle="", extras=None):
        row = Adw.PreferencesRow.new()
        row.set_title(title)
        rowsub = Adw.ActionRow.new()
        rowsub.set_title(title)
        rowsub.set_subtitle(subtitle)
        rowsub.add_suffix(widget)
        if widtype == "combo":
            for i, item in enumerate(extras): widget.append(str(i), item)
        elif widtype == "combo2":
            for i in extras: widget.append(str(i[1]), i[0])
            widget.set_active(500)
        widget.set_valign(Gtk.Align.CENTER)
        widget.set_name(str(uid))
        row.set_child(rowsub)
        return row, widget

class MainWindow(Adw.Window):
    def __init__(self, gself):
        super(MainWindow, self).__init__()
        _ = gettext.gettext
        # Intro
        self.set_name("main")
        self.set_default_size(600, 450)
        gself.mainHeader = Adw.HeaderBar()
        mainbox = Gtk.Box.new(1, 0)
        box = Gtk.Box.new(1, 0)
        gself.mainToast = Adw.ToastOverlay.new()
        gself.mainStack = MainStack(gself)
        gself.prefwin = PrefWin(gself)
        gself.prefwin.set_transient_for(self)
        gself.ev_key_main = Gtk.EventControllerKey.new()
        # Header section
        gself.headBox = Gtk.Box.new(0, 0)
        gself.locBut = Gtk.ToggleButton.new_with_label(_("Audio"))
        gself.locBut.set_name("locBut")
        gself.locBut.set_can_focus(False)
        gself.strBut = Gtk.ToggleButton.new_with_label(_("Video"))
        gself.strBut.set_name("strBut")
        gself.strBut.set_can_focus(False)

        prefbut = Gtk.MenuButton.new()
        prefbut.set_icon_name("open-menu-symbolic")
        prefbut.set_can_focus(False)
        menu = Gio.Menu()
        menu_item = Gio.MenuItem.new(_('Preferences'), "app.pref")
        menu.append_item(menu_item)
        menu_item = Gio.MenuItem.new(_('About'), "app.about")
        menu.append_item(menu_item)
        menu.freeze()
        prefbut.set_menu_model(menu)

        gself.menu = Gio.Menu()
        menu_item = Gio.MenuItem.new(_('Delete from current playqueue'), "app.delete")
        gself.menu.append_item(menu_item)
        menu_item = Gio.MenuItem.new(_('Edit metadata'), "app.edit")
        gself.menu.append_item(menu_item)
        gself.menu.freeze()

        gself.drop_but = Gtk.Button.new_from_icon_name("go-down")
        gself.drop_but.set_tooltip_text(_("More options"))
        gself.drop_but.set_can_focus(False)
        gself.headBox = jean(gself.headBox, [gself.locBut, gself.strBut, gself.drop_but])
        gself.headBox.add_css_class("linked")
        gself.mainHeader.pack_start(gself.headBox)
        gself.mainHeader.pack_end(prefbut)
        # Bottom section
        gself.bottom = Gtk.Box.new(1, 0)
        gself.bottom.set_hexpand(True)
        gself.bottom_motion = Gtk.EventControllerMotion.new()
        gself.bottom.add_controller(gself.bottom_motion)
        gself.slidBox = Gtk.Box.new(0, 0)
        gself.slider = Gtk.Scale.new(Gtk.Orientation.HORIZONTAL, None)
        gself.slider.set_can_focus(False)
        gself.slider = jean(gself.slider, task="margin", ids=[0, 0, 6, 6])
        gself.slider.set_draw_value(False)
        gself.slider.set_increments(1, 10)
        gself.slider.set_has_tooltip(True)
        gself.slider.set_hexpand(True)
        gself.label = Gtk.Label.new()
        gself.label = jean(gself.label, task="margin", ids=[0, 0, 6, 6])
        gself.label_end = Gtk.Label.new()
        gself.label_end = jean(gself.label_end, task="margin", ids=[0, 0, 6, 6])
        gself.slidBox = jean(gself.slidBox, [gself.label, gself.slider, gself.label_end])
        player = Gtk.Box.new(0, 0)
        player.set_homogeneous(True)
        player.set_hexpand(True)
        gself.openFolderBut = Gtk.Button.new_from_icon_name("folder-open")
        gself.openFolderBut.set_can_focus(False)
        gself.prevBut = Gtk.Button.new_from_icon_name("media-skip-backward")
        gself.prevBut.set_can_focus(False)
        gself.plaicon = Gtk.Image.new_from_icon_name("media-playback-start")
        gself.playBut = Gtk.Button.new()
        gself.playBut.set_child(gself.plaicon)
        gself.playBut.set_can_focus(False)
        gself.nextBut = Gtk.Button.new_from_icon_name("media-skip-forward")
        gself.nextBut.set_can_focus(False)
        gself.shuffBut = Gtk.Button.new_from_icon_name("media-playlist-shuffle")
        gself.shuffBut.set_can_focus(False)
        gself.lyrStack = Gtk.Stack()
        gself.karaokeIcon = Gtk.Image.new_from_icon_name("audio-input-microphone")
        gself.karaokeBut = Gtk.Button.new()
        gself.karaokeBut.set_child(gself.karaokeIcon)
        gself.karaokeBut.set_can_focus(False)
        gself.lyrSpin = Gtk.Spinner()
        gself.lyrSpin.set_size_request(-1, 32)
        gself.lyrStack.add_named(gself.karaokeBut, "karaokeBut")
        gself.lyrStack.add_named(gself.lyrSpin, "lyrSpin")
        gself.lyrStack.set_margin_start(7)
        gself.sub_track = Gtk.MenuButton.new()
        gself.sub_track.set_icon_name("media-view-subtitles-symbolic")
        gself.sub_track.set_can_focus(False)
        gself.sub_track.set_sensitive(False)
        sub_pop = Gtk.Popover()
        gself.sub_track.set_popover(sub_pop)
        gself.sub_track.set_margin_start(8)
        gself.sub_track.set_direction(Gtk.ArrowType.UP)
        modularPlayer = Gtk.Box.new(0, 0)
        player = jean(player, [gself.openFolderBut, gself.prevBut, gself.playBut, gself.nextBut, gself.shuffBut])
        player.add_css_class("linked")
        modularPlayer = jean(modularPlayer, [player, gself.sub_track, gself.lyrStack])
        modularPlayer.set_margin_end(5)
        gself.bottom = jean(gself.bottom, [gself.slidBox, modularPlayer])
        gself.bottom = jean(gself.bottom, task="margin", ids=[5, 7, 7, 5])
        # Outro
        gself.mainToast.set_child(gself.mainStack)
        box = jean(box, [gself.mainToast, gself.bottom])
        mainbox = jean(mainbox, [gself.mainHeader, box])
        self.add_controller(gself.ev_key_main)
        handle = Gtk.WindowHandle.new()
        handle.set_child(mainbox)
        self.set_content(handle)

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
        self.comboSize = Gtk.ComboBoxText.new()
        self.comboSize.append("1200", _("Ultra High (1200px)"))
        self.comboSize.append("500", _("High (500px)"))
        self.comboSize.append("250", _("Normal (250px)"))
        self.comboSize.set_active(1)
        self.comboSize.set_active_id("500")
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
        self.window = MainWindow(self)
        self.sub2.set_transient_for(self.window)
        self.sub2.set_modal(True)
        self.about = Adw.AboutWindow(application_name=cn.App.application_name, version=self.build_version, copyright=f"Copyright © {cn.App.app_years}", issue_url=cn.App.help_url, license_type=Gtk.License.GPL_3_0, developer_name="Dániel Kolozsi", developers=["Dániel Kolozsi"], designers=["Seh", "Dániel Kolozsi"], translator_credits=_("Dániel Kolozsi"), application_icon=cn.App.application_id, comments=cn.App.about_comments, website=cn.App.main_url, transient_for=self.window, release_notes=cn.App.release_notes, default_height=450)
        self.switchDict = {"locBut" : [self.placeholder, "audio-input-microphone", "audio", self.strBut], "strBut" : [self.strBox, "view-fullscreen", "video", self.locBut]}
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