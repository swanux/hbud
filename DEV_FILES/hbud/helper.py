#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio
from hbud import constants as cn

APP = "com.github.swanux.hbud"
UI_FILE = "hbud/hbud.glade"

class TrackBox(Gtk.EventBox):
    def __init__(self, title, artist, id, year, length, album):
        super(TrackBox, self).__init__()
        self.set_can_focus(False)
        self.set_name(f"trackbox_{id}")
        self.set_size_request(-1, 60)
        subBox = Gtk.Box.new(0, 5)
        comboBox = Gtk.Box.new(1, 5)
        tiLab = Gtk.Label.new()
        alLab = Gtk.Label.new(album)
        arLab = Gtk.Label.new(artist)
        yeLab = Gtk.Label.new(str(year))
        leLab = Gtk.Label.new()
        leLab.set_markup(f'<b>{length}</b>')
        tiLab.set_ellipsize(3)
        tiLab.set_halign(Gtk.Align(1))
        tiLab.set_margin_top(15)
        tiLab.set_markup(f"<b><span size='12000'>{title}</span></b>")
        alLab.set_ellipsize(3)
        alLab.set_halign(Gtk.Align(1))
        alLab.set_margin_bottom(15)
        arLab.set_ellipsize(3)
        arLab.set_halign(Gtk.Align(1))
        comboBox.pack_start(tiLab, False, False, 0)
        comboBox.pack_start(alLab, False, False, 0)
        subBox.pack_start(comboBox, True, True, 15)
        subBox.pack_end(leLab, False, False, 10)
        subBox.pack_end(yeLab, False, False, 20)
        subBox.pack_end(arLab, False, False, 20)
        self.add(subBox)
        self.set_margin_end(15)
        targs = [Gtk.TargetEntry.new("dummy", Gtk.TargetFlags.SAME_APP, 1)]
        self.drag_source_set(Gdk.ModifierType.BUTTON1_MASK, targs, Gdk.DragAction.MOVE)
        self.drag_dest_set(Gtk.DestDefaults.HIGHLIGHT | Gtk.DestDefaults.DROP | Gtk.DestDefaults.MOTION, targs, Gdk.DragAction.MOVE)

class Widgets(Gtk.Application):
    application_id = cn.App.application_id
    flags = Gio.ApplicationFlags.FLAGS_NONE
    program_name = cn.App.application_name
    build_version = cn.App.application_version
    about_comments = cn.App.about_comments
    app_years = cn.App.app_years
    build_version = cn.App.application_version
    app_icon = cn.App.application_id
    main_url = cn.App.main_url
    bug_url = cn.App.bug_url
    help_url = cn.App.help_url
    useMode = "audio"
    supportedList = ['.3gp', '.aa', '.aac', '.aax', '.aiff', '.flac', '.m4a', '.mp3', '.ogg', '.wav', '.wma', '.wv']
    searchDict = {"1" : ["artist", False], "2" : ["artist", True], "3" : ["title", False], "4" : ["title", True], "5" : ["year", False], "6" : ["year", True], "7" : ["length", False], "8" : ["length", True]}
    builder = Gtk.Builder()
    builder.set_translation_domain(APP)
    builder.add_from_file(UI_FILE)
    playlistPlayer, needSub, nowIn = False, False, ""
    fulle, resete, keepReset, hardReset, tnum, sorted = False, False, False, False, 0, False
    sub, seekBack, playing, res, title = builder.get_object('sub'), False, False, False, None
    comboSize = builder.get_object("comboSize")
    slider = Gtk.HScale()
    slider.set_can_focus(False)
    slider.set_margin_start(6)
    slider.set_margin_end(6)
    slider.set_draw_value(False)
    slider.set_increments(1, 10)
    box = builder.get_object("slidBox")
    label = Gtk.Label(label='0:00')
    label.set_margin_start(6)
    label.set_margin_end(6)
    label_end = Gtk.Label(label='0:00')
    label_end.set_margin_start(6)
    label_end.set_margin_end(6)
    box.pack_start(label, False, False, 0)
    box.pack_start(slider, True, True, 0)
    box.pack_start(label_end, False, False, 0)
    trackCover = builder.get_object("cover_img")
    trackCover.set_name("cover_img")
    metaCover = builder.get_object("metaCover")
    plaicon = builder.get_object("play")
    playlistBox = builder.get_object("expanded")
    exBot = builder.get_object("extendedBottom")
    header = builder.get_object("header")
    label1 = builder.get_object('label1')
    label2 = builder.get_object('label2')
    label3 = builder.get_object('label3')
    yrEnt = builder.get_object("yrEnt")
    tiEnt = builder.get_object("tiEnt")
    infBut = builder.get_object("infBut")
    alEnt = builder.get_object("alEnt")
    arEnt = builder.get_object("arEnt")
    karaokeIcon = builder.get_object("kar")
    karaokeBut = builder.get_object("karaokeBut")
    sub2 = builder.get_object("sub2")
    shuffBut = builder.get_object("shuffBut")
    locBut = builder.get_object("locBut")
    strBut = builder.get_object("strBut")
    mainStack = builder.get_object("mainStack")
    strOverlay = builder.get_object("strOverlay")
    theTitle = builder.get_object("theTitle")
    subSpin = builder.get_object("subSpin")
    subMarSpin = builder.get_object("subSpin1")
    subcheck = builder.get_object("sub_check")
    lyrSpin = builder.get_object("lyrSpin")
    nosub = builder.get_object("nosub")
    iChoser = builder.get_object("iChoser")
    roundSpin = builder.get_object("round_spin")
    colorer = builder.get_object("colorer")
    magiSpin = builder.get_object("magiSpin")
    magiStack = builder.get_object("magiStack")
    lyrStack = builder.get_object("lyrStack")
    magiBut = builder.get_object("magiBut")
    dark_switch, bg_switch = builder.get_object("dark_switch"), builder.get_object("bg_switch")
    mus_switch, az_switch, letr_switch = builder.get_object("mus_switch"), builder.get_object("az_switch"), builder.get_object("letr_switch")
    topBox = builder.get_object("topBox")
    drop_but = builder.get_object("drop_but")
    subStack = builder.get_object("subStack")
    lyrLab = builder.get_object("lyrLab")
    karmode = builder.get_object("req_scroll")
    lyrmode = builder.get_object("req_scroll2")
    search_play = builder.get_object("search_play")
    window = builder.get_object('main')
    switchDict = {"locBut" : [builder.get_object("placeholder"), "audio-input-microphone", "audio", strBut, infBut], "strBut" : [builder.get_object("strBox"), "view-fullscreen", "video", locBut, infBut], "infBut" : [builder.get_object("infBook"), "", "", locBut, strBut]}
    provider, settings = Gtk.CssProvider(), Gtk.Settings.get_default()
    window.set_wmclass ("hbud", "HBud")