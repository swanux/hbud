#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi, dbus, srt, azapi, dbus.mainloop.glib, json, os, sys, gettext, locale
from concurrent import futures
from time import sleep, time
from operator import itemgetter
from collections import deque
from datetime import timedelta
from random import sample
from configparser import ConfigParser
from mediafile import MediaFile
gi.require_version('Gtk', '3.0')
gi.require_version('Gst', '1.0')
from gi.repository import Gtk, Gst, GLib, GdkPixbuf, Gdk, Gio
from hbud import constants as cn

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

class GUI(Gtk.Application):
    def __init__(self):
        APP = "com.github.swanux.hbud"
        WHERE_AM_I = os.path.abspath(os.path.dirname(__file__))
        LOCALE_DIR = os.path.join(WHERE_AM_I, 'locale/mo')
        print(LOCALE_DIR, locale.getlocale())
        locale.setlocale(locale.LC_ALL, locale.getlocale())
        locale.bindtextdomain(APP, LOCALE_DIR)
        gettext.bindtextdomain(APP, LOCALE_DIR)
        gettext.textdomain(APP)
        self._ = gettext.gettext

        UI_FILE, version = "hbud/hbud.glade", "HBud 0.2.4 Yennefer"
        self.useMode = "audio"
        self.supportedList = ['.3gp', '.aa', '.aac', '.aax', '.aiff', '.flac', '.m4a', '.mp3', '.ogg', '.wav', '.wma', '.wv']
        try:
            self.clickedE = sys.argv[1].replace("file://", "")
            if os.path.splitext(self.clickedE)[-1] not in self.supportedList and os.path.splitext(self.clickedE)[-1] != "":
                self.useMode = "video" 
                print("video, now", self.clickedE)
        except:
            self.clickedE = False
        self.builder = Gtk.Builder()
        self.builder.set_translation_domain(APP)
        self.builder.add_from_file(UI_FILE)
        self.builder.connect_signals(self)
        whview = self.builder.get_object("whView")
        buffer = Gtk.TextBuffer()
        buffer.set_text(self._("""
 v0.2.4 - Oct ?? 2021 :

        * Added translation support
        * Added focus on currently playing track
        * Added Ctrl+F to search
        * Added option to load lyric / subtitle from 'misc' subfolder - to keep things orderly
        * Fixed several bugs
        * Polished the GUI"""))
        whview.set_buffer(buffer)
        self.playlistPlayer, self.needSub, self.nowIn = False, False, ""
        self.DAPI = azapi.AZlyrics('duckduckgo', accuracy=0.65)
        self.fulle, self.resete, self.keepReset, self.hardReset, self.tnum, self.sorted = False, False, False, False, 0, False
        self.sSize, self.sMarg = int(float(sSize)), int(float(sMarg))
        self.size, self.size2, self.size3, self.size4 = 35000, 15000, self.sSize*450, float(f"0.0{self.sMarg}")*450
        self.sub, self.seekBack, self.playing, self.res = self.builder.get_object('sub'), False, False, False
        if dark == "False": self.darke = False
        else: self.darke = True
        if bg == "False": self.bge = False
        else: self.bge = True
        self.slider = Gtk.HScale()
        self.slider.set_can_focus(False)
        self.slider.set_margin_start(6)
        self.slider.set_margin_end(6)
        self.slider.set_draw_value(False)
        self.slider.set_increments(1, 10)
        self.slider_handler_id = self.slider.connect("value-changed", self.on_slider_seek)
        self.box = self.builder.get_object("slidBox")
        self.label = Gtk.Label(label='0:00')
        self.label.set_margin_start(6)
        self.label.set_margin_end(6)
        self.label_end = Gtk.Label(label='0:00')
        self.label_end.set_margin_start(6)
        self.label_end.set_margin_end(6)
        self.box.pack_start(self.label, False, False, 0)
        self.box.pack_start(self.slider, True, True, 0)
        self.box.pack_start(self.label_end, False, False, 0)
        self.trackCover = self.builder.get_object("cover_img")
        self.trackCover.set_name("cover_img")
        self.plaicon = self.builder.get_object("play")
        self.slider.connect("enter-notify-event", self.mouse_enter)
        self.slider.connect("leave-notify-event", self.mouse_leave)
        self.playlistBox = self.builder.get_object("expanded")
        self.exBot = self.builder.get_object("extendedBottom")
        self.header = self.builder.get_object("header")
        self.label1 = self.builder.get_object('label1')
        self.label2 = self.builder.get_object('label2')
        self.label3 = self.builder.get_object('label3')
        self.yrEnt = self.builder.get_object("yrEnt")
        self.tiEnt = self.builder.get_object("tiEnt")
        self.infBut = self.builder.get_object("infBut")
        self.alEnt = self.builder.get_object("alEnt")
        self.arEnt = self.builder.get_object("arEnt")
        self.karaokeBut = self.builder.get_object("kar")
        self.sub2 = self.builder.get_object("sub2")
        self.shuffBut = self.builder.get_object("shuffBut")
        self.locBut = self.builder.get_object("locBut")
        self.strBut = self.builder.get_object("strBut")
        self.mainStack = self.builder.get_object("mainStack")
        self.strOverlay = self.builder.get_object("strOverlay")
        self.theTitle = self.builder.get_object("theTitle")
        self.subSpin = self.builder.get_object("subSpin")
        self.subMarSpin = self.builder.get_object("subSpin1")
        self.subcheck = self.builder.get_object("sub_check")
        self.nosub = self.builder.get_object("nosub")
        self.iChoser = self.builder.get_object("iChoser")
        self.roundSpin = self.builder.get_object("round_spin")
        self.colorer = self.builder.get_object("colorer")
        self.color = color
        coco = Gdk.RGBA()
        coco.parse(self.color)
        self.colorer.set_rgba(coco)
        self.roundSpin.set_value(int(rounded))
        self.dark_switch, self.bg_switch = self.builder.get_object("dark_switch"), self.builder.get_object("bg_switch")
        self.dark_switch.set_state(self.darke)
        self.bg_switch.set_state(self.bge)
        self.topBox = self.builder.get_object("topBox")
        self.drop_but = self.builder.get_object("drop_but")
        image_filter = Gtk.FileFilter()
        image_filter.set_name(self._("Image files"))
        image_filter.add_mime_type("image/*")
        self.iChoser.add_filter(image_filter)
        GLib.idle_add(self.subcheck.hide)
        GLib.idle_add(self.builder.get_object("oplink").set_label, self._("Visit OpenSubtitles"))
        GLib.idle_add(self.builder.get_object("sublink").set_label, self._("Visit Subscene"))
        self.subSpin.set_value(self.sSize)
        self.subStack = self.builder.get_object("subStack")
        self.lyrLab = self.builder.get_object("lyrLab")
        self.karmode = self.builder.get_object("req_scroll")
        self.lyrmode = self.builder.get_object("req_scroll2")
        self.search_play = self.builder.get_object("search_play")
        self.subMarSpin.set_value(self.sMarg)
        self.window = self.builder.get_object('main')
        self.sub.connect('size-allocate', self._on_size_allocated)
        self.window.connect('size-allocate', self._on_size_allocated0)
        self.switchDict = {"locBut" : [self.builder.get_object("placeholder"), "audio-input-microphone", "audio", self.strBut, self.infBut], "strBut" : [self.builder.get_object("strBox"), "view-fullscreen", "video", self.locBut, self.infBut], "infBut" : [self.builder.get_object("infBook"), "", "", self.locBut, self.strBut]}
        self.provider, self.settings = Gtk.CssProvider(), Gtk.Settings.get_default()
        self.themer(str(rounded))
        self.settings.set_property("gtk-application-prefer-dark-theme", self.darke)
        # Display the program
        self.window.set_title(version)
        self.window.set_wmclass ("hbud", "HBud")
        self.window.show_all()
        self.createPipeline("local")
        self.topBox.hide()
        self.drop_but.hide()
        self.locBut.set_active(True)
        if self.clickedE:
            if self.useMode == "audio":
                self.loader("xy")
                self.on_playBut_clicked("xy")
            else:
                self.strBut.set_active(True)
                self.on_playBut_clicked("xy")
        self.listener() # Do not write anything after this in init

    def highlight(self, widget, event):
        if event.button == 3:
            self.ednum = int(widget.get_name().replace("trackbox_", ""))
            menu = Gtk.Menu()
            menu.set_can_focus(False)
            menu_item = Gtk.MenuItem.new_with_label(self._('Delete from current playqueue'))
            menu_item.set_can_focus(False)
            menu_item.connect("activate", self.del_cur)
            menu.add(menu_item)
            menu_item = Gtk.MenuItem.new_with_label(self._('Edit metadata'))
            menu_item.set_can_focus(False)
            menu_item.connect("activate", self.ed_cur)
            menu.add(menu_item)
            menu.show_all()
            menu.popup_at_pointer()
        else:
            self.tnum = int(widget.get_name().replace("trackbox_", ""))
            self.themer(self.roundSpin.get_value(), self.tnum)
            self.on_next("clickMode")

    def on_search(self, widget):
        term = widget.get_text().lower()
        GLib.idle_add(self.supBox.show_all)
        if term != "":
            results = []
            for i, item in enumerate(self.playlist):
                if term in item["title"].lower() or term in item["artist"].lower() or term in item["album"].lower():
                    results.append(i)
            for i, item in enumerate(self.supBox.get_children()):
                if i not in results: GLib.idle_add(item.hide)

    def on_sort_change(self, widget):
        aid = int(widget.get_active_id())
        if self.sorted == False: self.archive = self.playlist
        self.sorted = True
        if aid == 0 and self.sorted == True:
            self.playlist = self.archive
            self.sorted = False
        elif aid == 1: self.playlist = sorted(self.archive, key=itemgetter('artist'),reverse=False)
        elif aid == 2: self.playlist = sorted(self.archive, key=itemgetter('artist'),reverse=True)
        elif aid == 3: self.playlist = sorted(self.archive, key=itemgetter('title'),reverse=False)
        elif aid == 4: self.playlist = sorted(self.archive, key=itemgetter('title'),reverse=True)
        elif aid == 5: self.playlist = sorted(self.archive, key=itemgetter('year'),reverse=False)
        elif aid == 6: self.playlist = sorted(self.archive, key=itemgetter('year'),reverse=True)
        elif aid == 7: self.playlist = sorted(self.archive, key=itemgetter('length'),reverse=False)
        elif aid == 8: self.playlist = sorted(self.archive, key=itemgetter('length'),reverse=True)
        self.neo_playlist_gen()
        old = self.archive[self.tnum]["title"]
        num = 0
        for item in self.playlist:
            if item["title"] == old: break
            else: num += 1
        self.tnum = num
        self.themer(self.roundSpin.get_value(), self.tnum)

    def on_clear_order(self, _): os.system(f"rm {self.folderPath}/.saved.order")

    def on_rescan_order(self, _):
        GLib.idle_add(self.loader, self.folderPath, True)

    def on_order_save(self, _):
        f = open(f"{self.folderPath}/.saved.order", "w+")
        f.write(json.dumps(self.playlist))
        f.close()

    def themer(self, v, w=""):
        css = """#cover_img {
            padding-bottom: %spx;
        }
        menu, .popup {
            border-radius: %spx;
        }
        decoration, headerbar{
            border-radius: %spx;
        }
        button, menuitem, entry {
            border-radius: %spx;
            margin: 5px;
        }
        .titlebar {
            border-top-left-radius: %spx;
            border-top-right-radius: %spx;
            border-bottom-left-radius: 0px;
            border-bottom-right-radius: 0px;
        }
        window, notebook, stack, box, scrolledwindow, viewport {
            border-top-left-radius: 0px;
            border-top-right-radius: 0px;
            border-bottom-left-radius: %spx;
            border-bottom-right-radius: %spx;
            border-width: 0px;
            border-image: none;
            box-shadow: none;
        }
        switch:checked, highlight, selection, menuitem:hover {
            background-color: %s;
        }
        #trackbox_%s{
            background: %s;
            color: #000;
            border-radius: %spx;
        }
        .maximized, .fullscreen, .maximized .titlebar {
            border-radius: 0px;
        }""" % (int(v)/2.6,int(v)/1.5,v,v,v,v,v,v,self.color,w,self.color,v) # decoration, window, window.background, window.titlebar, .titlebar
        css = str.encode(css)
        self.provider.load_from_data(css)
        self.window.get_style_context().add_provider_for_screen(Gdk.Screen.get_default(), self.provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def createPipeline(self, mode):
        if mode == "local":
            self.videoPipe, self.audioPipe = Gst.ElementFactory.make("playbin3"), Gst.ElementFactory.make("playbin3")
            # self.audioPipe = Gst.parse_launch('filesrc  ! decodebin ! audioconvert ! rgvolume ! audioconvert ! audioresample ! alsasink')
            playerFactory = self.videoPipe.get_factory()
            gtksink = playerFactory.make('gtksink')
            self.videoPipe.set_property("video-sink", gtksink)
            gtksink.props.widget.set_valign(Gtk.Align.FILL)
            gtksink.props.widget.set_halign(Gtk.Align.FILL)
            gtksink.props.widget.connect("button_press_event", self.mouse_click0)
            self.strOverlay.add(gtksink.props.widget)
            gtksink.props.widget.show()
            self.strOverlay.add_overlay(self.theTitle)
            bus = self.videoPipe.get_bus()
            bus.add_signal_watch()
            bus.connect("message", self.on_message)
            bus = self.audioPipe.get_bus()
            bus.add_signal_watch()
            bus.connect("message", self.on_message)
        # elif mode == "stream":
            # self.player = Gst.parse_launch(f"souphttpsrc is-live=false location={self.url} ! decodebin ! audioconvert ! autoaudiosink")

    def on_dropped(self, _):
        if self.drop_but.get_visible() == True:
            if self.topBox.get_visible() == True:
                GLib.idle_add(self.drop_but.get_image().set_from_icon_name, "gtk-go-down", Gtk.IconSize.BUTTON)
                GLib.idle_add(self.topBox.hide)
            else:
                GLib.idle_add(self.drop_but.get_image().set_from_icon_name, "gtk-go-up", Gtk.IconSize.BUTTON)
                GLib.idle_add(self.topBox.show)
                self.search_play.grab_focus()

    def allToggle(self, button):
        btn = Gtk.Buildable.get_name(button)
        if self.mainStack.get_visible_child() != self.switchDict[btn][0] and button.get_active() == True:
            self.mainStack.set_visible_child(self.switchDict[btn][0])
            if btn != "infBut":
                GLib.idle_add(self.exBot.show)
                if btn == "locBut":
                    GLib.idle_add(self.trackCover.show)
                    GLib.idle_add(self.shuffBut.show)
                    if self.playlistPlayer == True: GLib.idle_add(self.drop_but.show)
                    GLib.idle_add(self.subcheck.hide)
                else:
                    GLib.idle_add(self.trackCover.hide)
                    GLib.idle_add(self.shuffBut.hide)
                    GLib.idle_add(self.drop_but.hide)
                    GLib.idle_add(self.subcheck.show)
                GLib.idle_add(self.karaokeBut.set_from_icon_name, self.switchDict[btn][1], Gtk.IconSize.BUTTON)
                if self.playing == True and self.switchDict[btn][2] == "video": self.on_playBut_clicked("xy")
                self.useMode = self.switchDict[btn][2]
            else:
                GLib.idle_add(self.exBot.hide)
                GLib.idle_add(self.subcheck.hide)
                GLib.idle_add(self.drop_but.hide)
            self.needSub = False
            GLib.idle_add(self.subcheck.set_state, False)
            GLib.idle_add(self.switchDict[btn][3].set_active, False)
            GLib.idle_add(self.switchDict[btn][4].set_active, False)
        elif self.mainStack.get_visible_child() == self.switchDict[btn][0]: GLib.idle_add(button.set_active, True) 

    def cleaner(self, lis):
        if lis == []: pass
        else: [i.destroy() for i in lis]
    
    def neo_playlist_gen(self, name="", src=0, dst=0):
        if name == 'shuffle':
            if self.playlistPlayer == True:
                playlistLoc = sample(self.playlist, len(self.playlist))
                self.playlist, self.tnum = playlistLoc, 0
                self.neo_playlist_gen()
                self.on_next('clickMode')
        elif name == "rename":
            srcBox = self.supBox.get_children()[src]
            self.supBox.reorder_child(srcBox, dst)
            tmpList = self.supBox.get_children()
            for i in range(len(self.playlist)):
                tmpList[i].set_name(f"trackbox_{i}")
            if self.tnum == src or self.tnum == dst:
                if self.tnum == src: self.tnum = dst
                elif src > dst: self.tnum += 1
                elif src < dst: self.tnum -= 1
            else:
                if src > self.tnum and dst < self.tnum: self.tnum += 1
                elif src < self.tnum and dst > self.tnum: self.tnum -= 1
            self.themer(self.roundSpin.get_value(), self.tnum)
        else:
            self.cleaner(self.playlistBox.get_children())
            self.supBox = Gtk.Box.new(1, 0)
            self.supBox.set_can_focus(False)
            for i, item in enumerate(self.playlist):
                trBox = TrackBox(item["title"].replace("&", "&amp;"), item["artist"], i, item["year"], item["length"], item["album"])
                trBox.connect("button_release_event", self.highlight)
                trBox.connect('drag-begin', self.pause)
                trBox.connect('drag-drop', self._sig_drag_drop)
                trBox.connect('drag-end', self._sig_drag_end)
                self.supBox.pack_start(trBox, False, False, 0)
            yetScroll = Gtk.ScrolledWindow()
            yetScroll.set_can_focus(False)
            yetScroll.set_vexpand(True)
            yetScroll.set_hexpand(True)
            yetScroll.set_margin_end(10)
            yetScroll.add(self.supBox)
            self.playlistBox.pack_end(yetScroll, True, True, 0)
            yetScroll.show_all()
            self.adj = yetScroll.get_vadjustment()
            self.playlistPlayer = True
            GLib.idle_add(self.drop_but.show)

    def metas(self, location, extrapath, misc=False):
        f = MediaFile(location)
        title, artist, album, year, length = f.title, f.artist, f.album, f.year, str(timedelta(seconds=round(f.length))).replace("0:", "")
        if not title: title = os.path.splitext(extrapath)[0]
        if not artist: artist = self._("Unknown")
        if not album: album = self._("Unknown")
        if not year: year = 0
        itmp = {"uri" : location, "title" : title, "artist" : artist, "year" : year, "album" : album, "length" : length}
        if misc == True:
            if itmp not in self.playlist: self.pltmp.append(itmp)
        else: self.pltmp.append(itmp)

    def loader(self, path, misc=False):
        self.pltmp = []
        if self.clickedE:
            self.metas(self.clickedE, self.clickedE.split("/")[-1])
        else:
            pltmpin = os.listdir(path)
            for i in pltmpin:
                ityp = os.path.splitext(i)[1]
                if ityp in self.supportedList:
                    self.metas(f"{path}/{i}", i, misc)
        if misc == False: self.playlist = self.pltmp
        else: [self.playlist.append(item) for item in self.pltmp]
        GLib.idle_add(self.neo_playlist_gen)

    def on_openFolderBut_clicked(self, *_):
        if self.playing == True: self.pause()
        if self.useMode == "audio":
            self.fcconstructer(self._("Please choose a folder"), Gtk.FileChooserAction.SELECT_FOLDER, self._("Music"))
        else:
            self.fcconstructer(self._("Please choose a video file"), Gtk.FileChooserAction.OPEN, self._("Videos"))     

    def fcconstructer(self, title, action, folder):
        filechooserdialog = Gtk.FileChooserDialog(title=title, parent=self.window, action=action)
        if folder == self._("Videos"):
            filterr = Gtk.FileFilter()
            filterr.set_name(self._("Video files"))
            filterr.add_mime_type("video/*")
            filechooserdialog.add_filter(filterr)
        filechooserdialog.add_button(self._("_Cancel"), Gtk.ResponseType.CANCEL)
        filechooserdialog.add_button(self._("_Open"), Gtk.ResponseType.OK)
        filechooserdialog.set_default_response(Gtk.ResponseType.OK)
        filechooserdialog.set_current_folder(f"/home/{user}/{folder}")
        response = filechooserdialog.run()
        if response == Gtk.ResponseType.OK:
            if folder == self._("Music"):
                self.folderPath = filechooserdialog.get_uri().replace("file://", "")
                print("Folder selected: " + self.folderPath)
                if os.path.isfile(f"{self.folderPath}/.saved.order"):
                    f = open(f"{self.folderPath}/.saved.order", "r")
                    self.playlist = json.loads(f.read())
                    f.close()
                    for item in self.playlist[:]:
                        if os.path.isfile(f"{item['uri']}") == False: self.playlist.remove(item)
                    GLib.idle_add(self.neo_playlist_gen)
                else:
                    d_pl = futures.ThreadPoolExecutor(max_workers=4)
                    d_pl.submit(self.loader, self.folderPath)
            else:
                videoPath = filechooserdialog.get_filename()
                print("File selected: " + videoPath)
                self.on_playBut_clicked(videoPath)
        elif response == Gtk.ResponseType.CANCEL: print("Cancel clicked")
        filechooserdialog.destroy()

    def on_save(self, *_):
        f = MediaFile(self.editingFile)
        f.year, f.artist, f.album, f.title, newCover = self.yrEnt.get_value_as_int(), self.arEnt.get_text(), self.alEnt.get_text(), self.tiEnt.get_text(), self.iChoser.get_filename()
        try:
            if os.path.isfile(newCover):
                tf = open(newCover, "rb")
                binary = tf.read()
                tf.close()
                f.art = binary
        except: pass
        f.save()
        self.playlist[self.ednum]["year"] = self.yrEnt.get_value_as_int()
        self.playlist[self.ednum]["artist"] = self.arEnt.get_text()
        self.playlist[self.ednum]["album"] = self.alEnt.get_text()
        self.playlist[self.ednum]["title"] = self.tiEnt.get_text()
        self.sub2_hide("xy")
        self.neo_playlist_gen()

    def sub2_hide(self, *_):
        self.sub2.hide()
        return True

    def ed_cur(self, *_):
        self.editingFile = self.playlist[self.ednum]["uri"].replace("file://", "")
        self.yrEnt.set_value(self.playlist[self.ednum]["year"])
        self.arEnt.set_text(self.playlist[self.ednum]["artist"])
        self.alEnt.set_text(self.playlist[self.ednum]["album"])
        self.tiEnt.set_text(self.playlist[self.ednum]["title"])
        self.sub2.set_title(self._("Edit metadata for")+{self.editingFile.split('/')[-1]})
        self.sub2.show_all()

    def mouse_click0(self, _, event):
        if event.type == Gdk.EventType._2BUTTON_PRESS: 
            if self.useMode == "video": self.on_karaoke_activate(0)
        elif event.type == Gdk.EventType.BUTTON_PRESS: self.on_playBut_clicked(0)

    def del_cur(self, *_):
        self.playlist.remove(self.playlist[self.ednum])
        self.neo_playlist_gen()
        if self.tnum == self.ednum: self.play()

    def on_next(self, button):
        self.stopKar = True
        if self.nowIn == self.useMode or button == "clickMode":
            if self.nowIn == "audio" or button == "clickMode":
                if button != "clickMode":
                    self.tnum += 1
                    if self.tnum >= len(self.playlist): self.tnum = 0
                try:
                    self.stop()
                except: print("No playbin yet to stop.")
                self.play()
                if self.sub.get_visible(): self.on_karaoke_activate("xy")
            elif self.nowIn == "video":
                seek_time_secs = self.player.query_position(Gst.Format.TIME)[1] + 10 * Gst.SECOND
                self.player.seek_simple(Gst.Format.TIME,  Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, seek_time_secs)

    def load_cover(self):
        binary = MediaFile(self.url.replace('file://', '')).art
        if not binary: tmpLoc = "icons/track.png"
        else:
            tmpLoc = "/tmp/cacheCover.jpg"
            f = open(tmpLoc, "wb")
            f.write(binary)
            f.close()
        coverBuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(tmpLoc, 80, 80, True)
        GLib.idle_add(self.trackCover.set_from_pixbuf, coverBuf)

    def on_prev(self, *_):
        self.stopKar = True
        if self.nowIn == self.useMode:
            if self.nowIn == "audio":
                self.tnum -= 1
                if self.tnum < 0: self.tnum = len(self.playlist)-1
                try:
                    self.pause()
                    self.stop()
                except: print("No playbin yet to stop.")
                self.play()
                if self.sub.get_visible(): self.on_karaoke_activate("xy")
            elif self.nowIn == "video":
                seek_time_secs = self.player.query_position(Gst.Format.TIME)[1] - 10 * Gst.SECOND
                self.player.seek_simple(Gst.Format.TIME,  Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, seek_time_secs)

    def stop(self):
        print("Stop")
        self.player.set_state(Gst.State.PAUSED)
        if self.nowIn == "audio": self.audioPipe = self.player
        elif self.nowIn == "video": self.videoPipe = self.player
        self.res = False
        self.playing = False
        self.label.set_text("0:00")
        self.label_end.set_text("0:00")
        GLib.idle_add(self.plaicon.set_from_icon_name, "media-playback-start", Gtk.IconSize.BUTTON)
        self.slider.handler_block(self.slider_handler_id)
        self.slider.set_value(0)
        self.slider.handler_unblock(self.slider_handler_id)
        self.player.set_state(Gst.State.NULL)

    def pause(self, *_): 
        print("Pause")
        self.playing = False
        try:
            GLib.idle_add(self.plaicon.set_from_icon_name, "media-playback-start", Gtk.IconSize.BUTTON)
            self.player.set_state(Gst.State.PAUSED)
        except: print("Pause exception")
    
    def resume(self):
        print("Resume")
        self.playing = True
        self.player.set_state(Gst.State.PLAYING)
        GLib.idle_add(self.plaicon.set_from_icon_name, "media-playback-pause", Gtk.IconSize.BUTTON)
        GLib.timeout_add(50, self.updateSlider)

    def on_slider_seek(self, *_):
        if self.useMode == self.nowIn:
            seek_time_secs = self.slider.get_value()
            if seek_time_secs < self.position:
                self.seekBack = True
                print('back')
            self.player.seek_simple(Gst.Format.TIME,  Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, seek_time_secs * Gst.SECOND)

    def updateSlider(self):
        if(self.playing == False): return False # cancel timeout
        try:
            duration_nanosecs = self.player.query_duration(Gst.Format.TIME)[1]
            position_nanosecs = self.player.query_position(Gst.Format.TIME)[1]
            if duration_nanosecs == -1: return True
            # block seek handler so we don't seek when we set_value()
            self.slider.handler_block(self.slider_handler_id)
            duration = float(duration_nanosecs) / Gst.SECOND
            self.position = float(position_nanosecs) / Gst.SECOND
            remaining = float(duration_nanosecs - position_nanosecs) / Gst.SECOND
            self.slider.set_range(0, duration)
            self.slider.set_value(self.position)
            fvalue, svalue = str(timedelta(seconds=round(self.position))), str(timedelta(seconds=int(remaining)))
            self.label.set_text(fvalue)
            self.label_end.set_text(svalue)
            self.slider.handler_unblock(self.slider_handler_id)
        except Exception as e:
            print (f'W: {e}')
            pass
        return True

    def on_shuffBut_clicked(self, *_): self.neo_playlist_gen(name='shuffle')

    def nosub_hide(self, *_):
        self.nosub.hide()
        return True

    def on_act_sub(self, _, state):
        if state == True and self.nowIn == "video":
            filename = self.url.replace("file://", "").split("/")[-1]
            neo_tmpdbnow = os.listdir(self.url.replace("file://", "").replace(filename, "")+"misc/")
            tmpdbnow = os.listdir(self.url.replace("file://", "").replace(filename, ""))
            if os.path.splitext(filename)[0]+".srt" in tmpdbnow or os.path.splitext(filename)[0]+".srt" in neo_tmpdbnow:
                print("Subtitle found!")
                srfile = os.path.splitext(self.url.replace("file://", ""))[0]+".srt"
                neo_srfile = self.url.replace("file://", "").replace(filename, "")+"misc/"+os.path.splitext(filename)[0]+".srt"
                print(srfile, neo_srfile)
                try:
                    with open (srfile, 'r') as subfile: presub = subfile.read()
                except:
                    with open (neo_srfile, 'r') as subfile: presub = subfile.read()
                subtitle_gen = srt.parse(presub)
                subtitle = list(subtitle_gen)
                self.needSub = True
                subs = futures.ThreadPoolExecutor(max_workers=2)
                subs.submit(self.subShow, subtitle)
            else:
                self.nosub.set_title(self._("Subtitle file not found"))
                self.nosub.show_all()
                GLib.idle_add(self.subcheck.set_state, False)
                self.pause()
        else: self.needSub = False

    def play(self, misc=""):
        if self.clickedE:
            self.url, self.nowIn = "file://"+self.clickedE, self.useMode
            if self.useMode == "audio": self.player = self.audioPipe
            else: self.player = self.videoPipe
        elif "/" in misc:
            self.url, self.nowIn, self.player = "file://"+misc, "video", self.videoPipe
            GLib.idle_add(self.subcheck.set_state, False)
        elif misc == "continue":
            if self.useMode == "audio":
                if self.audioPipe.get_state(1)[1] == Gst.State.NULL: return
                self.player, self.nowIn = self.audioPipe, "audio"
            else:
                if self.videoPipe.get_state(1)[1] == Gst.State.NULL: return
                self.player, self.nowIn = self.videoPipe, "video"
        else:
            try: self.url, self.nowIn, self.player = "file://"+self.playlist[self.tnum]["uri"], "audio", self.audioPipe
            except: return
        print("Play")
        self.res, self.playing, self.position = True, True, 0
        if self.useMode == "audio":
            self.themer(self.roundSpin.get_value(), self.tnum)
        if misc != "continue":
            self.player.set_state(Gst.State.NULL)
            self.player.set_property("uri", self.url)
        self.player.set_state(Gst.State.PLAYING)
        GLib.idle_add(self.header.set_subtitle, self.url.replace("file://", "").split("/")[-1])
        GLib.idle_add(self.plaicon.set_from_icon_name, "media-playback-pause", Gtk.IconSize.BUTTON)
        GLib.timeout_add(50, self.updateSlider)
        if self.useMode == "audio" and misc != "continue":
            ld_cov = futures.ThreadPoolExecutor(max_workers=1)
            ld_cov.submit(self.load_cover)

    def diabuilder (self, text, title, mtype, buts):
        x, y = self.window.get_position()
        sx, sy = self.window.get_size()
        dialogWindow = Gtk.MessageDialog(parent=self.window, modal=True, destroy_with_parent=True, message_type=mtype, buttons=buts, text=text, title=title)
        dsx, dsy = dialogWindow.get_size()
        dialogWindow.move(x+((sx-dsx)/2), y+((sy-dsy)/2))
        dialogWindow.show_all()
        dialogWindow.run()
        dialogWindow.destroy()

    def on_playBut_clicked(self, button):
        if self.useMode == "audio" and self.nowIn != "video": self.adj.set_value(self.tnum*70-140)
        if self.nowIn == self.useMode or self.nowIn == "" or "/" in button:
            if not self.playing:
                if not self.res or "/" in str(button): self.play(button)
                else: self.resume()
            else: self.pause()
        else: self.play("continue")

    def on_main_delete_event(self, window, e):
        try: self.mainloop.quit()
        except: pass
        self.force, self.stopKar, self.needSub, self.hardReset = True, True, False, True
        raise SystemExit

    def listener(self):
        try:
            APP_ID = "hbud"
            dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
            bus = dbus.Bus(dbus.Bus.TYPE_SESSION)
            bus_object = bus.get_object('org.gnome.SettingsDaemon', '/org/gnome/SettingsDaemon/MediaKeys')
            dbus_interface='org.gnome.SettingsDaemon.MediaKeys'
            bus_object.GrabMediaPlayerKeys(APP_ID, 0, dbus_interface=dbus_interface)
            bus_object.connect_to_signal('MediaPlayerKeyPressed', self.on_media)
            self.mainloop = GLib.MainLoop()
            self.mainloop.run()
        except:
            print("I: Not compatible with Gnome MediaKeys daemon")
    
    def on_media(self, app, action):
        print(app, action)
        if app == "hbud" and self.url:
            if action == "Next": self.on_next("xy")
            elif action == "Previous": self.on_prev("xy")
            elif not self.playing: self.resume()
            elif self.playing: self.pause()
    
    def _sig_drag_drop(self, widget, *_): self.dst = int(widget.get_name().replace("trackbox_", ""))

    def _sig_drag_end(self, widget, _): self.reorderer(int(widget.get_name().replace("trackbox_", "")), self.dst)

    def reorderer(self, src, dst):
        playlistLoc, cutList = self.playlist, []
        if dst < src:
            [cutList.append(playlistLoc[i]) for i in range(dst, src+1)]
            rby, corrector = 1, dst
        elif dst > src:
            [cutList.append(playlistLoc[i]) for i in range(src, dst+1)]
            rby, corrector = -1, src
        cutList = deque(cutList)
        cutList.rotate(rby)
        cutList = list(cutList)
        for i in range(len(cutList)):
            self.playlist[i+corrector] = cutList[i]
        GLib.idle_add(self.neo_playlist_gen, "rename", src, dst)

    def on_key(self, _, key):
        # Add on_key as key_press signal to the ui file - main window preferably
        # print(key.keyval)
        try:
            if Gdk.ModifierType.CONTROL_MASK & key.state: # Ctrl combo
                if key.keyval == 102: self.on_dropped(None)
            elif key.keyval == 32 and self.url: self.on_playBut_clicked(0) # Space
            elif key.keyval == 65307 or key.keyval == 65480:
                if self.useMode == "video": self.on_karaoke_activate(0) # ESC and F11
            elif key.keyval == 65363: self.on_next("") # Right
            elif key.keyval == 65361: self.on_prev("") # Left
            elif key.keyval == 65535 and self.useMode == "audio": # Delete
                self.ednum = self.tnum
                self.del_cur()
            elif key.keyval == 65362 and self.useMode == "audio": # Up
                self.reorderer(self.tnum, self.tnum-1)
            elif key.keyval == 65364 and self.useMode == "audio": # Down
                self.reorderer(self.tnum, self.tnum+1)
        except: pass

    def on_message(self, _, message):
        t = message.type
        if t == Gst.MessageType.EOS and self.nowIn == "audio": self.on_next("xy")
        elif t == Gst.MessageType.ERROR:
            self.player.set_state(Gst.State.NULL)
            err, debug = message.parse_error()
            print (f"Error: {err}", debug)

    def _on_size_allocated(self, *_):
        sleep(0.01)
        x, y = self.sub.get_size()
        self.size, self.size2 = 50*x, 21.4285714*x
    
    def _on_size_allocated0(self, *_):
        sleep(0.01)
        if self.needSub == True:
            x, y = self.window.get_size()
            self.size3, self.size4 = self.sSize*y, float(f"0.0{self.sMarg}")*y

    def get_lyrics(self, title, artist):
        self.DAPI.title, self.DAPI.artist = title, artist
        try: result = self.DAPI.getLyrics()
        except: result = 0
        return result

    def on_karaoke_activate(self, *_):
        if self.nowIn == "audio":
            if self.playing == True or self.res == True:
                print('Karaoke')
                self.stopKar = False
                track = self.playlist[self.tnum]["title"]
                try:
                    artist = self.playlist[self.tnum]["artist"].split("/")[0]
                    if artist == "AC": artist = self.playlist[self.tnum]["artist"]
                except: artist = self.playlist[self.tnum]["artist"]
                dbnow, neo_dbnow = [], []
                if self.clickedE:
                    folPathClick = self.clickedE.replace(self.clickedE.split("/")[-1], "")
                    tmpdbnow = os.listdir(folPathClick)
                else:
                    tmpdbnow = os.listdir(self.folderPath)
                    neo_tmpdbnow = os.listdir(self.folderPath+"/misc/")
                for i in tmpdbnow:
                    if ".srt" in i or ".txt" in i:
                        x = i
                        if self.clickedE: dbnow.append(f"{folPathClick}{x}")
                        else: dbnow.append(f"{self.folderPath}/{x}")
                for i in neo_tmpdbnow:
                    if ".srt" in i or ".txt" in i:
                        x = i
                        neo_dbnow.append(f"{self.folderPath}/misc/{x}")
                self.sub.set_title(f'{track} - {artist}')
                tmp = os.path.splitext(self.playlist[self.tnum]["uri"])[0]
                neo_tmp = os.path.splitext(self.playlist[self.tnum]["uri"].split("/")[-1])[0]
                if f"{tmp}.srt" not in dbnow and f"{self.folderPath}/misc/{neo_tmp}.srt" not in neo_dbnow:
                    if f"{tmp}.txt" in dbnow or f"{self.folderPath}/misc/{neo_tmp}.txt" in neo_dbnow:
                        try: f = open(f"{tmp}.txt", "r")
                        except: f = open(f"{self.folderPath}/misc/{neo_tmp}.txt", "r")
                        lyric = f.read()
                        f.close()
                        self.lyrLab.set_label(lyric)
                        self.subStack.set_visible_child(self.lyrmode)
                        self.sub.show_all()
                    else:
                        lyric = self.get_lyrics(track, artist)
                        if lyric == 0:
                            self.diabuilder(self._('Can not get lyrics for the current track. Please place the synced .srt file  or the raw .txt file alongside the audio file, with the same name as the audio file.'), self._("Information"), Gtk.MessageType.INFO, Gtk.ButtonsType.OK)
                        else:
                            f = open(f"{tmp}.txt", "w+")
                            f.write(lyric)
                            f.close()
                            self.lyrLab.set_label(lyric)
                            self.subStack.set_visible_child(self.lyrmode)
                            self.sub.show_all()
                else:
                    print("FOUND")
                    try:
                        with open (f"{tmp}.srt", "r") as subfile: presub = subfile.read()
                    except:
                        with open (f"{self.folderPath}/misc/{neo_tmp}.srt", "r") as subfile: presub = subfile.read()
                    subtitle_gen = srt.parse(presub)
                    subtitle, lyrs = list(subtitle_gen), futures.ThreadPoolExecutor(max_workers=2)
                    lyrs.submit(self.slideShow, subtitle)
                    self.subStack.set_visible_child(self.karmode)
                    self.sub.show_all()
        elif self.useMode == "video":
            if self.fulle == False:
                GLib.idle_add(self.karaokeBut.set_from_icon_name, "view-restore", Gtk.IconSize.BUTTON)
                self.window.fullscreen()
                ld_clock = futures.ThreadPoolExecutor(max_workers=1)
                ld_clock.submit(self.clock)
            else:
                GLib.idle_add(self.karaokeBut.set_from_icon_name, "view-fullscreen", Gtk.IconSize.BUTTON)
                self.resete, self.keepReset = False, False
                self.window.unfullscreen()
                self.mage()

    def mouse_enter(self, *_):
        if self.fulle == True: self.keepReset = True
    
    def mouse_leave(self, *_):
        if self.fulle == True: self.keepReset = False
    
    def mage(self):
        GLib.idle_add(self.exBot.show)
        cursor = Gdk.Cursor.new_from_name(self.window.get_display(), 'default')
        self.window.get_window().set_cursor(cursor)

    def mouse_moving(self, *_):
        if self.fulle == True:
            self.resete = True
            if self.exBot.get_visible() == False:
                self.mage()
                ld_clock = futures.ThreadPoolExecutor(max_workers=1)
                ld_clock.submit(self.clock)

    def clock(self):
        start = time()
        while time() - start < 2:
            sleep(0.00001)
            if self.hardReset == True: return
            if self.keepReset == True: start = time()
            elif self.resete == True: start, self.resete = time(), False    
        if self.fulle == True:
            GLib.idle_add(self.exBot.hide)
            cursor = Gdk.Cursor.new_for_display(self.window.get_display(), Gdk.CursorType.BLANK_CURSOR)
            self.window.get_window().set_cursor(cursor)

    def on_state_change(self, _, event):
        if event.changed_mask & Gdk.WindowState.FULLSCREEN:
            self.fulle = bool(event.new_window_state & Gdk.WindowState.FULLSCREEN)
            print(self.fulle)

    def subShow(self, subtitle):
        while self.needSub == True:
            sleep(0.001)
            for line in subtitle:
                if self.position >= line.start.total_seconds() and self.position <= line.end.total_seconds():
                    if self.bge == True: GLib.idle_add(self.theTitle.set_markup, f"<span size='{int(self.size3)}' color='white' background='black'>{line.content}</span>")
                    else: GLib.idle_add(self.theTitle.set_markup, f"<span size='{int(self.size3)}' color='white'>{line.content}</span>")
                    self.theTitle.set_margin_bottom(self.size4)
                    GLib.idle_add(self.theTitle.show)
                    while self.needSub == True and self.position <= line.end.total_seconds() and self.position >= line.start.total_seconds():
                        sleep(0.001)
                        pass
                    GLib.idle_add(self.theTitle.hide)
                    GLib.idle_add(self.theTitle.set_label, "")

    def start_karaoke(self, sfile):
        with open (sfile, "r") as subfile: presub = subfile.read()
        subtitle_gen = srt.parse(presub)
        subtitle, lyrs = list(subtitle_gen), futures.ThreadPoolExecutor(max_workers=2)
        lyrs.submit(self.slideShow, subtitle)

    def slideShow(self, subtitle):
        self.lenlist = len(subtitle)-1
        while not self.stopKar:
            self.line1, self.line2, self.line3, self.buffer = [], [], [], []
            self.hav1, self.hav2, self.hav3, self.where = False, False, False, -1
            for word in subtitle:
                if '#' in word.content:
                    self.buffer.append(word)
                    if not self.hav1: self.to1()
                    elif not self.hav2: self.to2()
                    else: self.to3()
                else: self.buffer.append(word)
                if self.stopKar or self.seekBack: break
                self.where += 1
            if not self.seekBack:
                self.to2()
                self.to1()
                self.line2 = []
                self.sync()
                self.stopKar = True
            else: self.seekBack = False
    
    def to1(self):
        if self.hav2: self.line1 = self.line2
        else:
            self.line1 = self.buffer
            self.buffer = []
        self.hav1 = True

    def to2(self):
        if self.where+1 <= self.lenlist:
            if self.hav3: self.line2 = self.line3
            else:
                self.line2 = self.buffer
                self.buffer = []
            self.hav2 = True
        else:
            if self.hav1 and not self.hav3: self.to1()
            self.line2 = self.line3
            self.line3 = []
            self.sync()

    def to3(self):
        if self.where+2 <= self.lenlist:
            if self.hav1 and self.hav3: self.to1()
            if self.hav2 and self.hav3: self.to2()
            self.line3 = self.buffer
            self.buffer, self.hav3 = [], True
        else:
            if self.hav1: self.to1()
            if self.hav2: self.to2()
            self.line3 = self.buffer
            self.buffer, self.hav3 = [], False
        self.sync()

    def sync(self):
        simpl2, simpl3 = "", ""
        if self.line2 != []:
            for z in self.line2:
                if self.stopKar or self.seekBack: break
                simpl2 += f"{z.content.replace('#', '')} "
        else: simpl2 = ""
        if self.line3 != []:
            for z in self.line3:
                if self.stopKar or self.seekBack: break
                simpl3 += f"{z.content.replace('#', '')} "
        else: simpl3 = ""
        GLib.idle_add(self.label2.set_markup, f"<span size='{int(self.size2)}'>{simpl2}</span>")
        GLib.idle_add(self.label3.set_markup, f"<span size='{int(self.size2)}'>{simpl3}</span>")
        done, tmpline, first, tl1, it = "", self.line1[:], True, self.line1, 1
        tl1.insert(0, "")
        maxit = len(tl1)-1
        for xy in tl1:
            if self.stopKar or self.seekBack: break
            if first: first = False
            else: tmpline = tmpline[1:]
            leftover = ""
            for y in tmpline:
                if self.stopKar or self.seekBack: break
                leftover += f"{y.content.replace('#', '')} "
            try: GLib.idle_add(self.label1.set_markup, f"<span size='{self.size}' color='green'>{done}</span> <span size='{self.size}' color='green'> {xy.content.replace('#', '')}</span> <span size='{self.size}'> {leftover}</span>")
            except: GLib.idle_add(self.label1.set_markup, f"<span size='{self.size}' color='green'>{done}</span> <span size='{self.size}' color='green'> {xy}</span> <span size='{self.size}'> {leftover}</span>")
            while not self.stopKar:
                sleep(0.01)
                if it > maxit:
                    if self.position >= xy.end.total_seconds()-0.05 and self.position >= 0.5: break
                else:
                    xz = tl1[it]
                    if self.position >= xz.start.total_seconds()-0.1 and self.position >= 0.5: break
                if self.seekBack: break
            it += 1
            try:
                if done == "": done += f"{xy.content.replace('#', '')}"
                else: done += f" {xy.content.replace('#', '')}"
            except: pass

    def config_write(self, *_):
        self.darke, self.bge, self.color = self.dark_switch.get_state(), self.bg_switch.get_state(), self.colorer.get_rgba().to_string()
        tmp1, tmp2, tmp3 = int(self.subSpin.get_value()), int(self.subMarSpin.get_value()), int(self.roundSpin.get_value())
        parser.set('subtitles', 'margin', str(tmp2))
        parser.set('subtitles', 'size', str(tmp1))
        parser.set('subtitles', 'bg', str(self.bge))
        parser.set('gui', 'rounded', str(tmp3))
        parser.set('gui', 'dark', str(self.darke))
        parser.set('gui', 'color', self.color)
        file = open(confP, "w+")
        parser.write(file)
        file.close()
        self.settings.set_property("gtk-application-prefer-dark-theme", self.darke)
        self.themer(str(tmp3), self.tnum)
        self.sSize, self.sMarg = tmp1, tmp2

    def on_hide(self, *_):
        self.stopKar = True
        self.sub.hide()
        return True

user = os.popen("who|awk '{print $1}'r").read().rstrip().split('\n')[0]
parser, confP = ConfigParser(), f"/home/{user}/.config/hbud.ini"
if os.path.isfile(confP): parser.read(confP)
else:
    os.system(f"touch {confP}")
    parser.add_section('subtitles')
    parser.set('subtitles', 'margin', str(66))
    parser.set('subtitles', 'size', str(30))
    parser.set('subtitles', 'bg', "False")
    parser.add_section('gui')
    parser.set('gui', 'rounded', "10")
    parser.set('gui', 'dark', "False")
    parser.set('gui', 'color', "rgb(17, 148, 156)")
    file = open(confP, "w+")
    parser.write(file)
    file.close()
sSize, sMarg, bg = parser.get('subtitles', 'size'), parser.get('subtitles', 'margin'), parser.get('subtitles', 'bg')
rounded, dark, color = parser.get('gui', 'rounded'), parser.get('gui', 'dark'), parser.get('gui', 'color')
Gst.init(None)
app = GUI()
app.application_id = cn.App.application_id
app.flags = Gio.ApplicationFlags.FLAGS_NONE
app.program_name = cn.App.application_name
app.build_version = cn.App.application_version
app.about_comments = cn.App.about_comments
app.app_years = cn.App.app_years
app.build_version = cn.App.application_version
app.app_icon = cn.App.application_id
app.main_url = cn.App.main_url
app.bug_url = cn.App.bug_url
app.help_url = cn.App.help_url
app.run()

# GTK_DEBUG=interactive
# to debug