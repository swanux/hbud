#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from copy import copy
import gi, srt, azapi, json, os, sys, gettext, locale, acoustid, musicbrainzngs#, ctypes
from concurrent import futures
from time import sleep, time
from operator import itemgetter
from collections import deque
from datetime import timedelta
from random import sample
from mediafile import MediaFile, MediaField, MP3DescStorageStyle, StorageStyle
gi.require_version('Gtk', '4.0')
gi.require_version('Gst', '1.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, GLib, GdkPixbuf, Gdk, Gst, Adw, Gio
from hbud import letrasapi, musixapi, helper, tools

class Main(helper.Widgets):
    def __init__(self):
        super(Main, self).__init__()
    
    def on_activate(self, app):
        self.confDir = GLib.get_user_config_dir()
        APP = "io.github.swanux.hbud"
        WHERE_AM_I = os.path.abspath(os.path.dirname(__file__))
        LOCALE_DIR = os.path.join(WHERE_AM_I, 'locale/mo')
        print(LOCALE_DIR, locale.getlocale())
        print(self.tmpDir, confP)
        locale.setlocale(locale.LC_ALL, locale.getlocale())
        locale.bindtextdomain(APP, LOCALE_DIR)
        gettext.bindtextdomain(APP, LOCALE_DIR)
        gettext.textdomain(APP)
        self._ = gettext.gettext
        self.API_KEY = "Erv1I6jCqZ"
        musicbrainzngs.set_useragent("hbud", "0.4.0", "https://github.com/swanux/hbud")
        try:
            self.clickedE = sys.argv[1].replace("file://", "")
            if os.path.splitext(self.clickedE)[-1] not in self.supportedList and os.path.splitext(self.clickedE)[-1] != "":
                self.useMode = "video" 
                print("video, now", self.clickedE)
        except:
            self.clickedE = False
        self.createPipeline("local")
        self.connect_signals()
        self.DAPI = azapi.AZlyrics('duckduckgo', accuracy=0.65)

        self.canwriteconf = False
        self.sSize, self.sMarg = int(float(sSize)), int(float(sMarg))
        self.size3, self.size4 = self.sSize*450, float(f"0.0{self.sMarg}")*450
        self.subSpin.set_value(self.sSize)
        self.subMarSpin.set_value(self.sMarg)
        self.darkew.set_active(int(theme))
        self.size, self.size2 = 35000, 15000
        if theme == "0": self.theme = 0
        elif theme == "1": self.theme = 4
        elif theme == "2": self.theme = 1
        self.bge = bg == "True"
        self.musixe = musix == "True"
        self.azlyre = azlyr == "True"
        self.letrase = letras == "True"
        self.autoscroll = autoscroll == "True"
        self.lite = minimal_mode == "True"
        self.scroll_val = int(positioning)
        self.cover_size = coverSize
        self.color = color
        coco = Gdk.RGBA()
        coco.parse(self.color)
        self.colorer.set_rgba(coco)
        self.bg_switch.set_state(self.bge)
        self.mus_switch.set_state(self.musixe)
        self.az_switch.set_state(self.azlyre)
        self.comboSize.set_active_id(str(self.cover_size))
        self.letr_switch.set_state(self.letrase)
        self.scroll_check.set_state(self.autoscroll)
        self.scroll_spin.set_value(self.scroll_val)
        self.lite_switch.set_state(self.lite)
        self.canwriteconf = True

        self.off_but.connect("clicked", self.on_off_but_clicked)
        click = Gtk.GestureClick.new()
        motion = Gtk.EventControllerMotion.new()
        self.slider.add_controller(motion)
        click.connect("pressed", self.on_slider_grab)
        self.slider.connect("value-changed", self.on_slider_grabbed)
        self.bottom_motion.connect("enter", self.mouse_enter)
        self.bottom_motion.connect("leave", self.mouse_leave)
        motion.connect("motion", self.sliding)
        self.slider.add_controller(click)

        GLib.idle_add(self.subcheck.hide)
        self.window.connect('notify', self._on_notify)
        self.sub.connect('notify', self._on_notify)
        tools.themer(self.provider, self.window, self.color)
        self.settings.set_color_scheme(self.theme)
        # Display the program
        title = Adw.WindowTitle()
        title.set_title("HBud")
        if self.lite == False: title.set_subtitle(self.build_version)
        self.mainHeader.set_title_widget(title)
        self.window.set_application(app)
        self.window.present()
        self.topBox.hide()
        self.drop_but.hide()
        if self.lite == True:
            GLib.idle_add(self.headBox.set_visible, False)
            GLib.idle_add(self.mainStack.set_visible_child, self.rdBox)
            GLib.idle_add(self.window.set_default_size, 1, 1)
            GLib.idle_add(self.mainHeader.add_css_class, "flat")
            self.window.set_resizable(False)
        self.locBut.set_active(True)
        if self.clickedE:
            if self.useMode == "audio":
                self.loader("xy")
                self.on_playBut_clicked("xy")
            else:
                self.strBut.set_active(True)
                self.on_playBut_clicked("xy")

    def connect_signals(self):
        self.window.connect("close-request", self.on_main_delete_event)
        self.prefwin.connect("close-request", self.on_pref_close)
        self.sub.connect("close-request", self.on_hide)
        self.sub2.connect("close-request", self.sub2_hide)
        self.about.connect("close-request", self.about_hide)

        self.ev_key_main.connect("key-pressed", self.on_key_local)
        self.ev_key_main.connect("key-released", self.on_key_local_release)
        self.ev_key_sub.connect("key-pressed", self.on_key_local)
        self.ev_key_sub.connect("key-released", self.on_key_local_release)

        action = Gio.SimpleAction.new("pref", None)
        action.connect("activate", self.on_infBut_clicked)
        self.add_action(action)
        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.on_about_clicked)
        self.add_action(action)
        action = Gio.SimpleAction.new("delete", None)
        action.connect("activate", self.del_cur)
        self.add_action(action)
        action = Gio.SimpleAction.new("edit", None)
        action.connect("activate", self.ed_cur)
        self.add_action(action)
        self.openFolderBut.connect("clicked", self.on_openFolderBut_clicked)
        self.locBut.connect("toggled", self.allToggle)
        self.strBut.connect("toggled", self.allToggle)
        self.playBut.connect("clicked", self.on_playBut_clicked)
        self.prevBut.connect("clicked", self.on_prev)
        self.nextBut.connect("clicked", self.on_next)
        self.shuffBut.connect("clicked", self.on_shuffBut_clicked)
        self.karaokeBut.connect("clicked", self.on_karaoke_activate)
        self.drop_but.connect("clicked", self.on_dropped)
        self.magiBut.connect("clicked", self.on_magiBut_clicked)
        self.iChoser.connect("clicked", self.on_iChoser_clicked)
        self.savBut.connect("clicked", self.on_save)
        self.combo_sort.connect("changed", self.on_sort_change)
        self.search_play.connect("activate", self.on_search)
        self.order_but.connect("clicked", self.on_order_save)
        self.order_but1.connect("clicked", self.on_clear_order)
        self.order_but2.connect("clicked", self.on_rescan_order)
        self.ye_but.connect("clicked", self.on_correct_lyr)
        self.no_but.connect("clicked", self.on_wrong_lyr)
        self.subcheck.connect("state-set", self.on_act_sub)

        self.darkew.connect("changed", self.config_write)
        self.colorer.connect("color-set", self.config_write)
        self.subSpin.connect("value-changed", self.config_write)
        self.subMarSpin.connect("value-changed", self.config_write)
        self.bg_switch.connect("state-set", self.config_write)
        self.mus_switch.connect("state-set", self.config_write)
        self.az_switch.connect("state-set", self.config_write)
        self.letr_switch.connect("state-set", self.config_write)
        self.comboSize.connect("changed", self.config_write)
        self.scroll_check.connect("state-set", self.config_write)
        self.scroll_spin.connect("value-changed", self.config_write)
        self.lite_switch.connect("state-set", self.config_write)
    
    def on_about_clicked(self, *_): self.about.show()

    def about_hide(self, *_): self.about.hide()

    def on_infBut_clicked(self, *_): self.prefwin.present()
    
    def on_pref_close (self, *_): self.prefwin.hide()

    def highlight(self, widget, *_):
        print(widget.get_button())
        if widget.get_button() == 3:
            self.ednum = int(widget.get_widget().get_name().replace("trackbox_", ""))
            self.popover = Gtk.PopoverMenu.new_from_model(self.menu)
            self.popover.set_autohide(True)
            self.popover.set_parent(widget.get_widget())
            self.popover.popup()
        else:
            self.tnum = int(widget.get_widget().get_name().replace("trackbox_", ""))
            tools.themer(self.provider, self.window, self.color, self.tnum)
            self.on_next("clickMode")

    def on_search(self, widget):
        print("Searching...")
        self.searched = True
        term = widget.get_text().lower()
        for i, item in enumerate(self.playlist): self.playlist[i]["hidden"] = False
        if term != "":
            for i, item in enumerate(self.playlist):
                if term in item["title"].lower() or term in item["artist"].lower() or term in item["album"].lower(): self.playlist[i]["hidden"] = False
                else: self.playlist[i]["hidden"] = True
        else: self.searched = False
        self.neo_playlist_gen("shuff_2nd_stage")

    def on_sort_change(self, widget):
        print("Sorting")
        aid = int(widget.get_active_id())
        if self.sorted == False: self.archive = self.playlist.copy()
        self.sorted = True
        if aid == 0 and self.sorted == True:
            self.playlist = self.archive.copy()
            self.archive = []
            self.sorted = False
        else: self.playlist = sorted(self.archive, key=itemgetter(self.searchDict[str(aid)][0]),reverse=self.searchDict[str(aid)][1])
        self.neo_playlist_gen("shuff_2nd_stage")
        num = 0
        for item in self.playlist:
            if item["title"] == self.title: break
            else: num += 1
        self.tnum = num
        tools.themer(self.provider, self.window, self.color, self.tnum)

    def on_clear_order(self, _):
        tmname = self.folderPath.replace("/", ">")
        os.system(f"rm '{self.confDir}/{tmname}.saved.order'")
        self.mainToast.add_toast(Adw.Toast.new(self._('Cleared saved order successfully!')))

    def on_rescan_order(self, _): GLib.idle_add(self.loader, self.folderPath, True)

    def on_order_save(self, _):
        tmname = self.folderPath.replace("/", ">")
        f = open(f"{self.confDir}/{tmname}.saved.order", "w+")
        data = []
        for i in range(len(self.playlist)): data.append(self.playlist[i].copy())
        for i in range(len(data)): data[i]["widget"] = None
        f.write(json.dumps(data))
        f.close()
        self.mainToast.add_toast(Adw.Toast.new(self._('Saved order successfully!')))

    def createPipeline(self, mode):
        if mode == "local":
            self.videoPipe, self.audioPipe = Gst.ElementFactory.make("playbin3"), Gst.ElementFactory.make("playbin3")
            # self.audioPipe = Gst.parse_launch('filesrc  ! decodebin ! audioconvert ! rgvolume ! audioconvert ! audioresample ! alsasink')
            playerFactory = self.videoPipe.get_factory()
            gtksink = playerFactory.make('gtk4paintablesink')
            videosink = gtksink.props.paintable
            self.videoPipe.set_property("video-sink", gtksink)
            self.videosink = Gtk.Picture.new_for_paintable(videosink)
            self.videosink.set_valign(Gtk.Align.FILL)
            self.videosink.set_halign(Gtk.Align.FILL)
            self.videosink.set_name("videosink")
            click = Gtk.GestureClick.new()
            motion = Gtk.EventControllerMotion.new()
            self.videosink.add_controller(click)
            self.window.add_controller(motion)
            motion.connect("motion", self.mouse_moving)
            click.connect("pressed", self.on_playBut_clicked)
            self.strOverlay.set_child(self.videosink)
            self.videosink.show()
            self.strOverlay.add_overlay(self.theTitle)
            bus = self.videoPipe.get_bus()
            bus.add_signal_watch()
            bus.connect("message", self.on_message)
            bus = self.audioPipe.get_bus()
            bus.add_signal_watch()
            bus.connect("message", self.on_message)

    def on_dropped(self, button):
        if self.drop_but.get_visible() == True:
            if self.topBox.get_visible() == False:
                GLib.idle_add(self.drop_but.set_icon_name, "go-up")
                GLib.idle_add(self.topBox.show)
                self.search_play.grab_focus()
            elif button != "key":
                GLib.idle_add(self.drop_but.set_icon_name, "go-down")
                GLib.idle_add(self.topBox.hide)

    def allToggle(self, button):
        btn = button.get_name()
        if self.mainStack.get_visible_child() != self.switchDict[btn][0] and button.get_active() == True:
            self.mainStack.set_visible_child(self.switchDict[btn][0])
            GLib.idle_add(self.bottom.show)
            if btn == "locBut":
                GLib.idle_add(self.shuffBut.show)
                if self.playlistPlayer == True: GLib.idle_add(self.drop_but.show)
                GLib.idle_add(self.subcheck.hide)
            else:
                GLib.idle_add(self.shuffBut.hide)
                GLib.idle_add(self.drop_but.hide)
                GLib.idle_add(self.subcheck.show)
            GLib.idle_add(self.karaokeIcon.set_from_icon_name, self.switchDict[btn][1])
            if self.playing == True:
                if self.switchDict[btn][2] == "video" and self.nowIn == "audio": self.on_playBut_clicked("xy")
                elif self.nowIn == "video" and self.switchDict[btn][2] != "video": self.on_playBut_clicked("xy")
            self.useMode = self.switchDict[btn][2]
            self.needSub = False
            GLib.idle_add(self.subcheck.set_state, False)
            GLib.idle_add(self.switchDict[btn][3].set_active, False)
        elif self.mainStack.get_visible_child() == self.switchDict[btn][0]: GLib.idle_add(button.set_active, True) 
    
    def neo_playlist_gen(self, name="", srBox=None, dsBox=None, src=0, dst=0):
        print("neo start", time())
        if self.lite == True:
            self.tnum = 0
            self.on_next("clickMode")
            return
        if self.lite == False:
            if name == "reorder":
                self.supBox.reorder_child_after(srBox, dsBox)
                for i, item in enumerate(self.playlist):
                    item["widget"].set_name(f"trackbox_{i}")
                if self.tnum == src or self.tnum == dst:
                    if self.tnum == src: self.tnum = dst
                    elif src > dst: self.tnum += 1
                    elif src < dst: self.tnum -= 1
                else:
                    if src > self.tnum and dst < self.tnum: self.tnum += 1
                    elif src < self.tnum and dst > self.tnum: self.tnum -= 1
                tools.themer(self.provider, self.window, self.color, self.tnum)
            else:
                if name != "modular" and name != "append":
                    try: self.playlistBox.remove(self.playlistBox.get_first_child())
                    except: print("no child")
                    self.supBox = Gtk.Box.new(1, 0)
                    self.supBox.set_can_focus(False)
                for i, item in enumerate(self.playlist):
                    trBox = None
                    if name == "shuff_2nd_stage":
                        if item["hidden"] == False:
                            trBox = item["widget"]
                            trBox.set_name(f"trackbox_{i}")
                    elif name != "modular" or i == self.ednum:
                        if name != "append" or self.playlist[i]["widget"] == None:
                            trBox = helper.TrackBox(item["title"].replace("&", "&amp;"), item["artist"], i, item["year"], item["length"], item["album"])
                            self.playlist[i]["widget"] = trBox
                            left_click = Gtk.GestureClick.new()
                            trBox.add_controller(left_click)
                            left_click.connect("pressed", self.highlight)
                            right_click = Gtk.GestureClick.new()
                            right_click.set_button(3)
                            trBox.add_controller(right_click)
                            right_click.connect("pressed", self.highlight)
                            self.load_cover(item["uri"], trBox.image)
                        if name == "modular" and i == self.ednum: GLib.idle_add(self.supBox.insert_child_after, trBox, self.playlist[i-1]["widget"])
                    if name != "modular" and trBox != None: self.supBox.append(trBox)
                if name != "modular" and name != "append":
                    yetScroll = Gtk.ScrolledWindow()
                    yetScroll.set_can_focus(False)
                    yetScroll.set_vexpand(True)
                    yetScroll.set_hexpand(True)
                    yetScroll.set_child(self.supBox)
                    GLib.idle_add(self.playlistBox.append, yetScroll)
                    self.adj = yetScroll.get_vadjustment()
                    self.playlistPlayer = True
                    if self.title != None:
                        num = 0
                        for item in self.playlist:
                            if item["title"] == self.title: break
                            else: num += 1
                        self.tnum = num
                        tools.themer(self.provider, self.window, self.color, self.tnum)
                    GLib.idle_add(self.drop_but.show)
        print("neo end", time())

    def metas(self, location, extrapath, misc=False):
        f = MediaFile(f"{location}")
        title, artist, album, year, length = f.title, f.artist, f.album, f.year, ":".join(str(timedelta(seconds=round(f.length))).split(":")[1:])
        if not title: title = os.path.splitext(extrapath)[0]
        if not artist: artist = self._("Unknown")
        if not album: album = self._("Unknown")
        if not year: year = 0
        itmp = {"uri" : location, "title" : title, "artist" : artist, "year" : year, "album" : album, "length" : length, "widget" : None, "hidden" : False}
        if misc == True:
            if itmp not in self.playlist: self.pltmp.append(itmp)
        else: self.pltmp.append(itmp)

    def loader(self, path, misc=False):
        print("loader start", time())
        self.pltmp = []
        if self.clickedE:
            self.metas(self.clickedE, self.clickedE.split("/")[-1])
        else:
            pltmpin = os.listdir(path)
            for i in pltmpin:
                ityp = os.path.splitext(i)[1]
                if ityp in self.supportedList:
                    self.metas(f"{path}/{i}", i, misc)
        d_pl = futures.ThreadPoolExecutor(max_workers=4)
        if misc == False:
            self.playlist = self.pltmp
            d_pl.submit(self.neo_playlist_gen)
        else:
            uristmp = []
            for item in self.playlist: uristmp.append(item["uri"])
            i = 0
            for item in self.pltmp:
                if item["uri"] not in uristmp:
                    self.playlist.append(item)
                    i += 1
            d_pl.submit(self.neo_playlist_gen, name="append")
            self.mainToast.add_toast(Adw.Toast.new(self._('Rescan complete. {} tracks added.').format(i)))
        print("loader end", time())

    def on_openFolderBut_clicked(self, *_):
        if self.playing == True: self.pause()
        if self.useMode == "audio": self.fcconstructer(self._("Please choose a folder"), Gtk.FileChooserAction.SELECT_FOLDER, self._("Music"), self.window)
        else: self.fcconstructer(self._("Please choose a video file"), Gtk.FileChooserAction.OPEN, self._("Videos"), self.window)

    def on_response(self, dialog, response, _dialog, folder):
        if response == Gtk.ResponseType.ACCEPT:
            if folder == self._("Music"):
                self.folderPath = dialog.get_files()[0].get_path()
                print("Folder selected: " + self.folderPath)
                tmname = self.folderPath.replace("/", ">")
                if os.path.isfile(f"{self.confDir}/{tmname}.saved.order"):
                    f = open(f"{self.confDir}/{tmname}.saved.order", "r")
                    self.playlist = json.loads(f.read())
                    f.close()
                    for item in self.playlist[:]:
                        if os.path.isfile(f"{item['uri']}") == False: self.playlist.remove(item)
                    d_pl = futures.ThreadPoolExecutor(max_workers=4)
                    d_pl.submit(self.neo_playlist_gen)
                else: GLib.idle_add(self.loader, self.folderPath)
            elif folder == self._("Pictures"):
                path = dialog.get_file().get_path()
                tf = open(path, "rb")
                tmBin = tf.read()
                tf.close()
                GLib.idle_add(self.load_cover, "brainz", tmBin)
            else:
                videoPath = dialog.get_file().get_path()
                print("File selected: " + videoPath)
                self.res = False
                try: self.player.set_state(Gst.State.NULL)
                except: print("Nothing to stop yet")
                self.on_playBut_clicked(videoPath)
        elif response == Gtk.ResponseType.CANCEL: print("Cancel clicked")

    def fcconstructer(self, title, action, folder, parent):
        filechooserdialog = Gtk.FileChooserNative.new(title, parent, action, self._("Open"), self._("Cancel"))
        if folder == self._("Videos"):
            filterr = Gtk.FileFilter()
            filterr.set_name(self._("Video files"))
            filterr.add_mime_type("video/*")
            filechooserdialog.add_filter(filterr)
        elif folder == self._("Pictures"):
            filterr = Gtk.FileFilter()
            filterr.set_name(self._("Image files"))
            filterr.add_mime_type("image/*")
            filechooserdialog.add_filter(filterr)
        filechooserdialog.connect("response", self.on_response, filechooserdialog, folder)
        filechooserdialog.set_transient_for(parent)
        filechooserdialog.set_modal(True)
        filechooserdialog.show()

    def on_iChoser_clicked(self, *_):
        self.fcconstructer(self._("Please choose an image file"), Gtk.FileChooserAction.OPEN, self._("Pictures"), self.sub2)

    def on_save(self, *_):
        tmname = self.folderPath.replace("/", ">")
        self.yrEnt.update()
        f = MediaFile(self.editingFile)
        f.year, f.artist, f.album, f.title, f.art = self.yrEnt.get_value_as_int(), self.arEnt.get_text(), self.alEnt.get_text(), self.tiEnt.get_text(), self.binary
        f.save()
        self.playlist[self.ednum]["year"] = self.yrEnt.get_value_as_int()
        self.playlist[self.ednum]["artist"] = self.arEnt.get_text()
        self.playlist[self.ednum]["album"] = self.alEnt.get_text()
        self.playlist[self.ednum]["title"] = self.tiEnt.get_text()
        if os.path.isfile(f"{self.confDir}/{tmname}.saved.order"):
            self.on_order_save()
        self.sub2_hide("xy")
        GLib.idle_add(self.supBox.remove, self.playlist[self.ednum]["widget"])
        self.neo_playlist_gen("modular")

    def sub2_hide(self, *_):
        self.sub2.hide()
        if self.magiSpin.get_spinning() == True: self.aborte = True
        GLib.idle_add(self.magiSpin.stop)

    def ed_cur(self, *_):
        self.popover.unparent()
        self.editingFile = self.playlist[self.ednum]["uri"].replace("file://", "")
        self.yrEnt.set_value(self.playlist[self.ednum]["year"])
        self.arEnt.set_text(self.playlist[self.ednum]["artist"])
        self.alEnt.set_text(self.playlist[self.ednum]["album"])
        self.tiEnt.set_text(self.playlist[self.ednum]["title"])
        self.load_cover(mode="meta")
        self.sub2.present()

    def on_magiBut_clicked(self, _):
        GLib.idle_add(self.magiSpin.start)
        thread = futures.ThreadPoolExecutor(max_workers=2)
        thread.submit(self.fetch_cur)

    def chose_one(self):
        print("Chose one")
        liststore = Gtk.ListStore(str, str, str, int)
        for item in self.chosefrom:
            liststore.append([item["title"], item["artist"], item["album"], item["year"]])
        liststore.append([self._("None of the above"), "", "", 0])
        treeview = Gtk.TreeView(model=liststore)
        treeview.set_headers_visible(True)
        treeview.connect("row-activated", self.on_tree_row_activated)
        rendererText = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Title", rendererText, text=0)
        treeview.append_column(column)
        column = Gtk.TreeViewColumn("Artist", rendererText, text=1)
        treeview.append_column(column)
        column = Gtk.TreeViewColumn("Album", rendererText, text=2)
        treeview.append_column(column)
        column = Gtk.TreeViewColumn("Year", rendererText, text=3)
        treeview.append_column(column)
        self.chosBox.append(treeview)
        GLib.idle_add(self.choser_window.present)
    
    def on_tree_row_activated(self, widget, row, _):
        row = row.get_indices()[0]
        if row != len(self.chosefrom):
            data = [self.chosefrom[row]["artist"], self.chosefrom[row]["title"], self.chosefrom[row]["rid"], self.chosefrom[row]["year"], self.chosefrom[row]["album"], self.chosefrom[row]["album_ids"]]
            thread = futures.ThreadPoolExecutor(max_workers=2)
            thread.submit(self.next_fetch, data)
        else: GLib.idle_add(self.magiSpin.stop)
        GLib.idle_add(self.choser_window.hide)
        GLib.idle_add(self.chosBox.remove, self.chosBox.get_last_child())

    def fetch_cur(self):
        path = self.playlist[self.ednum]["uri"].replace("file://", "")
        try:
            results = acoustid.match(self.API_KEY, path, force_fpcalc=True)
        except acoustid.NoBackendError as e:
            print("chromaprint library/tool not found", file=sys.stderr)
            print(e)
        except acoustid.FingerprintGenerationError:
            print("fingerprint could not be calculated", file=sys.stderr)
        except acoustid.WebServiceError as exc:
            print("web service request failed:", exc.message, file=sys.stderr)
        self.chosefrom, i = [], 0
        try:
            for score, rid, title, artist in results:
                if self.aborte == True:
                    print("Aborted")
                    break
                if artist != None and title != None and i <= 10:
                    tmpData = musicbrainzngs.get_recording_by_id(rid, includes=["releases"])["recording"]["release-list"]
                    sleep(1.1)
                    i += 1
                    if len(tmpData) > 2:
                        tmpDir = {"score": score, "rid": rid, "title": title, "artist": artist, 'year' : int(tmpData[0]["date"].split("-")[0]), "album" : tmpData[0]["title"], "album_ids" : [d['id'] for d in tmpData if 'id' in d]}
                        for item in self.chosefrom:
                            if item["title"] == tmpDir["title"] and item["artist"] == tmpDir["artist"] and item["year"] == tmpDir["year"]: break
                        else: self.chosefrom.append(tmpDir)
        except: print("Something bad happened...")
        if self.aborte == True:
            print("Aborted")
            self.aborte = False
            return
        if len(self.chosefrom) == 0:
            self.sub2Toast.add_toast(Adw.Toast.new(self._('Did not find any match online.')))
            GLib.idle_add(self.magiSpin.stop)
        elif len(self.chosefrom) == 1:
            data = [self.chosefrom[0]["artist"], self.chosefrom[0]["title"], self.chosefrom[0]["rid"], self.chosefrom[0]["year"], self.chosefrom[0]["album"], self.chosefrom[0]["album_ids"]]
            thread = futures.ThreadPoolExecutor(max_workers=2)
            thread.submit(self.next_fetch, data)
        else: self.chose_one()
            
    def next_fetch(self, data):
        for i in range(10):
            if self.aborte == True:
                print("Aborted")
                self.aborte = False
                break
            print("Trying to get cover: "+str(i))
            try:
                release = musicbrainzngs.get_image_front(data[5][i], self.cover_size)
                sleep(1.2)
                print("Cover found")
                break
            except: release = None
        GLib.idle_add(self.yrEnt.set_value, data[3])
        GLib.idle_add(self.arEnt.set_text, data[0])
        GLib.idle_add(self.alEnt.set_text, data[4])
        GLib.idle_add(self.tiEnt.set_text, data[1])
        if release != None: GLib.idle_add(self.load_cover, "brainz", release)
        GLib.idle_add(self.magiSpin.stop)
        self.sub2Toast.add_toast(Adw.Toast.new(self._('Metadata fetched successfully!')))

    def del_cur(self, *_):
        print(self.playlist[self.ednum])
        try: self.popover.unparent()
        except: print("huh")
        torem = self.playlist[self.ednum]["widget"]
        GLib.idle_add(self.supBox.remove, torem)
        self.playlist.remove(self.playlist[self.ednum])
        for i, item in enumerate(self.playlist):
            item["widget"].set_name(f"trackbox_{i}")
        self.visnum = 0
        for i, item in enumerate(self.playlist):
            if item["hidden"] == False and i<self.tnum: self.visnum += 1
        if self.tnum == self.ednum: self.play()

    def on_next(self, button):
        self.stopKar = True
        if self.nowIn == self.useMode or "clickMode" in button:
            if self.nowIn == "audio" or "clickMode" in button:
                if "clickMode" not in button:
                    self.tnum += 1
                    if self.tnum >= len(self.playlist): self.tnum = 0
                    while self.playlist[self.tnum]["hidden"] == True:
                        self.tnum += 1
                        if self.tnum >= len(self.playlist): self.tnum = 0
                elif button == "clickMode0": self.tnum = 0
                try: self.stop()
                except: print("No playbin yet to stop.")
                self.play()
                if self.sub.get_visible(): self.on_karaoke_activate("xy")
                if self.useMode == "audio" and button != "clickMode" and self.autoscroll == True and self.lite == False: self.adj.set_value(self.visnum*79-self.scroll_val)
            elif self.nowIn == "video":
                self.seeking = True
                self.resete2 = time()
                GLib.idle_add(self.slider.set_value, self.slider.get_value() + 10)

    def load_cover(self, mode="", bitMage=""):
        if mode == "meta": self.binary = MediaFile(self.editingFile).art
        elif mode == "brainz": self.binary = bitMage
        else: self.binary = MediaFile(mode.replace('file://', '')).art
        if not self.binary: tmpLoc = "hbud/icons/track.png"
        else:
            tmpLoc = f"{self.tmpDir}/cacheCover.jpg"
            f = open(tmpLoc, "wb")
            f.write(self.binary)
            f.close()
        if mode == "meta" or mode == "brainz":
            coverBuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(tmpLoc, 100, 100, True)
            GLib.idle_add(self.metaCover.set_pixbuf, coverBuf)
        else:
            coverBuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(tmpLoc, 60, 60, True)
            GLib.idle_add(bitMage.set_pixbuf, coverBuf)

    def on_prev(self, *_):
        self.stopKar = True
        if self.nowIn == self.useMode:
            if self.nowIn == "audio":
                self.tnum -= 1
                if self.tnum < 0: self.tnum = len(self.playlist)-1
                while self.playlist[self.tnum]["hidden"] == True:
                    self.tnum -= 1
                    if self.tnum < 0: self.tnum = len(self.playlist)-1
                try:
                    self.pause()
                    self.stop()
                except: print("No playbin yet to stop.")
                self.play()
                if self.sub.get_visible(): self.on_karaoke_activate("xy")
                if self.useMode == "audio" and self.autoscroll == True and self.lite == False: self.adj.set_value(self.visnum*79-self.scroll_val)
            elif self.nowIn == "video":
                self.seeking = True
                self.resete2 = time()
                GLib.idle_add(self.slider.set_value, self.slider.get_value() - 10)

    def stop(self, arg=False):
        print("Stop")
        self.player.set_state(Gst.State.PAUSED)
        if self.nowIn == "audio": self.audioPipe = self.player
        elif self.nowIn == "video": self.videoPipe = self.player
        self.playing = False
        if self.lite == True: self.label.set_text("00:00")
        else: self.label.set_text("0:00:00")
        GLib.idle_add(self.plaicon.set_from_icon_name, "media-playback-start")
        if arg == False:
            self.slider.set_value(0)
            self.res = False
            del self.player
        else:
            self.slider.set_value(0)
            self.player.seek_simple(Gst.Format.TIME,  Gst.SeekFlags.FLUSH | Gst.SeekFlags.ACCURATE, 0 * Gst.SECOND)

    def pause(self, *_): 
        print("Pause")
        self.playing = False
        try:
            GLib.idle_add(self.plaicon.set_from_icon_name, "media-playback-start")
            self.player.set_state(Gst.State.PAUSED)
        except: print("Pause exception")
    
    def resume(self):
        print("Resume")
        self.playing = True
        self.player.set_state(Gst.State.PLAYING)
        GLib.idle_add(self.plaicon.set_from_icon_name, "media-playback-pause")
        GLib.timeout_add(400, self.updateSlider)
        GLib.timeout_add(5, self.updatePos)

    def sliding(self, *_): self.resete2 = time()

    def on_slider_grab(self, *_):
        print("grabbed")
        self.seeking = True
        self.resete2 = time()
        if not self.clocking:
            self.clocking = True
            ld_clock = futures.ThreadPoolExecutor(max_workers=1)
            ld_clock.submit(self.clock, "seek")
    
    def on_slider_grabbed(self, *_):
        current_time = str(timedelta(seconds=round(self.slider.get_value())))
        GLib.idle_add(self.slider.set_tooltip_text, f"{current_time}")

    def on_slider_seek(self, *_):
        print("seeked")
        if self.useMode == self.nowIn:
            seek_time_secs = self.slider.get_value()
            print(seek_time_secs)
            if seek_time_secs < self.position:
                self.seekBack = True
            self.player.seek_simple(Gst.Format.TIME,  Gst.SeekFlags.FLUSH | Gst.SeekFlags.ACCURATE, seek_time_secs * Gst.SECOND)
            self.seeking = False

    def updatePos(self):
        if(self.playing == False): return False
        try:
            position_nanosecs = self.player.query_position(Gst.Format.TIME)[1]
            self.position = float(position_nanosecs) / Gst.SECOND
        except Exception as e:
            print (f'W: {e}')
            pass
        return True

    def updateSlider(self):
        if(self.playing == False): return False
        try:
            duration_nanosecs = self.player.query_duration(Gst.Format.TIME)[1]
            position_nanosecs = self.player.query_position(Gst.Format.TIME)[1]
            if duration_nanosecs == -1: return True
            duration = float(duration_nanosecs) / Gst.SECOND
            remaining = float(duration_nanosecs - position_nanosecs) / Gst.SECOND
            if self.seeking == False:
                self.slider.set_range(0, duration)
                self.slider.set_value(self.position)
            fvalue, svalue = str(timedelta(seconds=round(self.position))), str(timedelta(seconds=int(remaining)))
            if self.lite == True: fvalue, svalue = ":".join(fvalue.split(":")[1:]), ":".join(svalue.split(":")[1:])
            self.label.set_text(fvalue)
            self.label_end.set_text(svalue)
        except Exception as e:
            print (f'W: {e}')
            pass
        return True

    def on_shuffBut_clicked(self, *_):
        try:
            playlistLoc = sample(self.playlist, len(self.playlist))
            self.playlist, self.tnum = playlistLoc, 0
            self.neo_playlist_gen("shuff_2nd_stage")
            self.on_next('clickMode0')
        except: print("pass")

    def on_act_sub(self, _, state):
        if state == True and self.nowIn == "video":
            filename = self.url.replace("file://", "").split("/")[-1]
            try: neo_tmpdbnow = os.listdir(self.url.replace("file://", "").replace(filename, "")+"misc/")
            except: neo_tmpdbnow = []
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
                self.mainToast.add_toast(Adw.Toast.new(self._('Could not find subtitle for the current video.\nYou may provide it manually (OpenSubtitles, Subscene).')))
                GLib.idle_add(self.subcheck.set_state, False)
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
        if self.useMode == "audio" and self.nowIn != "video" and self.autoscroll == True:
            self.visnum = 0
            for i, item in enumerate(self.playlist):
                if item["hidden"] == False and i<self.tnum: self.visnum += 1
        if self.useMode == "audio":
            self.title = self.playlist[self.tnum]["title"]
            if self.lite == True:
                self.rdTitle.set_text(self.playlist[self.tnum]["title"])
                self.rdArtist.set_text(self.playlist[self.tnum]["artist"])
                self.rdYear.set_text(str(self.playlist[self.tnum]["year"]))
            else: tools.themer(self.provider, self.window, self.color, self.tnum)
        if misc != "continue":
            self.player.set_state(Gst.State.NULL)
            self.player.set_property("uri", self.url)
        self.player.set_state(Gst.State.PLAYING)
        GLib.idle_add(self.plaicon.set_from_icon_name, "media-playback-pause")
        GLib.timeout_add(300, self.updateSlider)
        GLib.timeout_add(5, self.updatePos)

    def on_playBut_clicked(self, button, *_):
        if self.plaicon.is_visible() == False and self.videosink.is_visible() == False: return
        if self.useMode == "audio" and self.nowIn != "video" and self.autoscroll == True and self.lite == False:
            self.visnum = 0
            for i, item in enumerate(self.playlist):
                if item["hidden"] == False and i<self.tnum: self.visnum += 1
            self.adj.set_value(self.visnum*79-self.scroll_val)
        if self.nowIn == self.useMode or self.nowIn == "" or "/" in str(button):
            if not self.playing:
                if not self.res or "/" in str(button): self.play(button)
                else: self.resume()
            else: self.pause()
        else: self.play("continue")

    def on_main_delete_event(self, *_):
        print("Quitting...")
        self.stopKar, self.hardReset, self.needSub, self.hardreset2 = True, True, False, True
        raise SystemExit

    def reorderer(self, src, dst):
        if self.sorted == True or self.searched == True: return
        else:
            srcBox = self.playlist[src]["widget"]
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
            for i in range(len(cutList)): self.playlist[i+corrector] = cutList[i]
            for i, item in enumerate(self.playlist):
                if item["widget"] == srcBox:
                    if i == 0: dstBox = None
                    else: dstBox = self.playlist[i-1]["widget"]
                    break
            GLib.idle_add(self.neo_playlist_gen, "reorder", srcBox, dstBox, src, dst)

    def on_key_local_release(self, _controller, keyval, *_):
        del _controller
        if keyval == 65363 or keyval == 65361:
            if not self.clocking:
                self.clocking = True
                ld_clock = futures.ThreadPoolExecutor(max_workers=1)
                ld_clock.submit(self.clock, "seek")

    def on_key_local(self, _controller, keyval, _keycode, modifier):
        del _controller, _keycode
        # Add on_key_local as key-pressed signal to eventcontrollerkey
        # print(keyval)
        try:
            if Gdk.ModifierType.CONTROL_MASK & modifier: # Ctrl combo
                if keyval == 102 and self.lite == False: self.on_dropped("key")
                elif keyval == 111: self.on_openFolderBut_clicked(None)
            elif keyval == 32 and self.url: self.on_playBut_clicked(0) # Space
            elif keyval == 65307 or keyval == 65480:
                if self.useMode == "video": self.on_karaoke_activate(0) # ESC and F11
            elif keyval == 65363: self.on_next("") # Right
            elif keyval == 65361: self.on_prev("") # Left
            elif keyval == 65535 and self.useMode == "audio" and self.lite == False: # Delete
                self.ednum = self.tnum
                self.del_cur()
            elif keyval == 65362 and self.useMode == "audio" and self.lite == False: # Up
                if self.tnum-1 < 0: self.reorderer(self.tnum, len(self.playlist)-1)
                else: self.reorderer(self.tnum, self.tnum-1)
            elif keyval == 65364 and self.useMode == "audio" and self.lite == False: # Down
                if self.tnum+1 > len(self.playlist)-1: self.reorderer(self.tnum, 0)
                else: self.reorderer(self.tnum, self.tnum+1)
        except: print("No key local mate")

    def on_message(self, _, message):
        t = message.type
        if t == Gst.MessageType.EOS and self.nowIn == "audio": self.on_next("xy")
        elif t == Gst.MessageType.EOS and self.nowIn == "video": self.stop(arg=True)
        elif t == Gst.MessageType.ERROR:
            self.player.set_state(Gst.State.NULL)
            err, debug = message.parse_error()
            print (f"Error: {err}", debug)
    
    def _on_notify(self, emitter, param):
        if param.name in ["default-width", "default-height"]:
            x, y = emitter.get_size(Gtk.Orientation.HORIZONTAL), emitter.get_size(Gtk.Orientation.VERTICAL)
            if emitter == self.window:
                if self.needSub == True:
                    self.size3, self.size4 = self.sSize*y, float(f"0.0{int(self.sMarg)}")*y
            else: self.size, self.size2 = 50*x, 21.4285714*x
        elif param.name == "maximized":
            sizThread = futures.ThreadPoolExecutor(max_workers=1)
            sizThread.submit(self.different_resize, emitter)
        elif param.name == "fullscreened":
            self.fulle = self.window.is_fullscreen()
            if self.fulle == True: GLib.idle_add(self.mainHeader.hide)
            else: GLib.idle_add(self.mainHeader.show)
            sizThread = futures.ThreadPoolExecutor(max_workers=1)
            sizThread.submit(self.different_resize, emitter)

    def different_resize(self, emitter):
        sleep(0.3)
        x, y = emitter.get_size(Gtk.Orientation.HORIZONTAL), emitter.get_size(Gtk.Orientation.VERTICAL)
        if emitter == self.window: self.size3, self.size4 = self.sSize*y, float(f"0.0{int(self.sMarg)}")*y
        else: self.size, self.size2 = 50*x, 21.4285714*x

    def on_off_but_clicked(self, _):
        self.off_spin.update()
        self.offset = int(self.off_spin.get_value())
        f = MediaFile(self.playlist[self.tnum]["uri"])
        f.offset = self.offset
        f.save()
        self.sub.set_focus(None)

    def on_correct_lyr(self, _):
        f = MediaFile(self.playlist[self.tnum]["uri"])
        f.lyrics = self.tmp_lyric
        f.save()
        GLib.idle_add(self.substackhead.hide)
    
    def on_wrong_lyr(self, _): self.on_karaoke_activate()

    def on_karaoke_activate(self, *_):
        if self.useMode == "audio" and self.nowIn == "audio":
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
                    try: neo_tmpdbnow = os.listdir(self.folderPath+"/misc/")
                    except: neo_tmpdbnow = []
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
                    GLib.idle_add(self.off_but.hide)
                    GLib.idle_add(self.off_lab.hide)
                    GLib.idle_add(self.off_spin.hide)
                    if f"{tmp}.txt" in dbnow or f"{self.folderPath}/misc/{neo_tmp}.txt" in neo_dbnow:
                        try: f = open(f"{tmp}.txt", "r")
                        except: f = open(f"{self.folderPath}/misc/{neo_tmp}.txt", "r")
                        lyric = f.read()
                        f.close()
                        self.lyrLab.set_label(lyric)
                        self.subStack.set_visible_child(self.lyrmode)
                        self.sub.present()
                        GLib.idle_add(self.substackhead.hide)
                    else:
                        try:
                            print("Dikk")
                            f = MediaFile(self.playlist[self.tnum]["uri"])
                            lyric = f.lyrics
                            print(lyric)
                            self.lyrLab.set_label(lyric)
                            self.subStack.set_visible_child(self.lyrmode)
                            self.sub.present()
                            GLib.idle_add(self.substackhead.hide)
                        except:
                            self.substackhead.set_visible_child(self.subbox2)
                            GLib.idle_add(self.substackhead.show)
                            thread = futures.ThreadPoolExecutor(max_workers=2)
                            thread.submit(self.lyr_fetcher, artist, track)
                else:
                    GLib.idle_add(self.off_but.show)
                    GLib.idle_add(self.off_lab.show)
                    GLib.idle_add(self.off_spin.show)
                    f = MediaFile(self.playlist[self.tnum]["uri"])
                    try:
                        field = MediaField(MP3DescStorageStyle(u'offset'), StorageStyle(u'offset'))
                        f.add_field(u'offset', field)
                    except: pass
                    if f.offset == None: f.offset = 0
                    self.offset = int(f.offset)
                    GLib.idle_add(self.off_spin.set_value, self.offset)
                    f.save()
                    print("FOUND")
                    try:
                        with open (f"{tmp}.srt", "r") as subfile: presub = subfile.read()
                    except:
                        with open (f"{self.folderPath}/misc/{neo_tmp}.srt", "r") as subfile: presub = subfile.read()
                    subtitle_gen = srt.parse(presub)
                    subtitle, lyrs = list(subtitle_gen), futures.ThreadPoolExecutor(max_workers=2)
                    lyrs.submit(self.slideShow, subtitle)
                    self.subStack.set_visible_child(self.karmode)
                    self.substackhead.set_visible_child(self.subbox)
                    GLib.idle_add(self.substackhead.show)
                    self.sub.present()
        elif self.useMode == "video":
            if self.fulle == False:
                GLib.idle_add(self.karaokeIcon.set_from_icon_name, "view-restore")
                self.window.fullscreen()
                ld_clock = futures.ThreadPoolExecutor(max_workers=1)
                ld_clock.submit(self.clock, "full")
            else:
                GLib.idle_add(self.karaokeIcon.set_from_icon_name, "view-fullscreen")
                self.resete, self.keepReset = False, False
                self.window.unfullscreen()
                self.mage()

    def lyr_fetcher(self, artist, track):
        print("Fetcher...")
        GLib.idle_add(self.lyrStack.set_visible_child, self.lyrSpin)
        GLib.idle_add(self.lyrSpin.start)
        lyric = None
        if self.musixe == True and self.lyr_states[0] == True:
            print("musix")
            lyric, self.lyr_states = musixapi.get_lyric(artist, track), [False, True, True]
        if self.letrase == True and lyric == None and self.lyr_states[1] == True:
            print("letras")
            lyric, self.lyr_states = letrasapi.get_lyric(artist, track), [False, False, True]
        if self.azlyre == True and lyric == None and self.lyr_states[2] == True:
            print("AZ")
            lyric, self.lyr_states = tools.get_lyric(track, artist, self.DAPI), [False, False, False]
        print("end")
        GLib.idle_add(self.lyrStack.set_visible_child, self.karaokeBut)
        if lyric == 0:
            self.mainToast.add_toast(Adw.Toast.new(self._('Could not fetch lyrics for the current track.\nYou may provide it manually.')))
            self.lyr_states = [True, True, True]
        else:
            self.tmp_lyric = lyric
            GLib.idle_add(self.lyrLab.set_label, lyric)
            GLib.idle_add(self.subStack.set_visible_child, self.lyrmode)
            GLib.idle_add(self.sub.present)

    def mouse_enter(self, *_):
        if self.fulle == True: self.keepReset = True
    
    def mouse_leave(self, *_):
        if self.fulle == True: self.keepReset = False
    
    def mage(self):
        GLib.idle_add(self.bottom.show)
        cursor = Gdk.Cursor.new_from_name('default')
        self.window.set_cursor(cursor)

    def mouse_moving(self, _, x, y):
        if self.fulle == True: 
            self.countermove += 1
            if self.countermove >= 2 and self.mx != x and self.my != y:
                self.countermove = 0
                self.resete = True
                self.mx, self.my = x, y
                if self.bottom.get_visible() == False:
                    self.mage()
                    ld_clock = futures.ThreadPoolExecutor(max_workers=1)
                    ld_clock.submit(self.clock, "full")

    def clock(self, ltype):
        start = time()
        if ltype == "full":
            while time() - start < 2:
                if self.hardReset == True: return
                if self.keepReset == True: start = time()
                elif self.resete == True: start, self.resete = time(), False    
                sleep(0.001)
            if self.fulle == True:
                cursor = Gdk.Cursor.new_from_name('none')
                self.window.set_cursor(cursor)
                GLib.idle_add(self.bottom.hide)
                self.countermove = 0
        elif ltype == "seek":
            while time() - start < 0.3:
                if self.hardreset2 == True: return
                start = self.resete2
                sleep(0.001)
            self.on_slider_seek()
            self.clocking = False

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
                    if self.position >= xy.end.total_seconds()+self.offset/1000 and self.position >= 0.5: break
                else:
                    xz = tl1[it]
                    if self.position >= xz.start.total_seconds()+self.offset/1000 and self.position >= 0.5: break
                if self.seekBack: break
            it += 1
            try:
                if done == "": done += f"{xy.content.replace('#', '')}"
                else: done += f" {xy.content.replace('#', '')}"
            except: pass

    def config_write(self, widget, *_):
        if self.canwriteconf == True:
            uid = int(widget.get_name())
            if uid == 0:
                theme = self.darkew.get_active_id()
                if theme == "0": self.theme = 0
                elif theme == "1": self.theme = 4
                elif theme == "2": self.theme = 1
                self.settings.set_color_scheme(self.theme)
                parser.set("gui", "theme", str(self.theme))
            elif uid == 1:
                self.color = self.colorer.get_rgba().to_string()
                parser.set('gui', 'color', self.color)
            elif uid == 2:
                self.sSize = self.subSpin.get_value()
                parser.set('subtitles', 'size', str(self.sSize))
            elif uid == 3:
                self.sMarg = self.subMarSpin.get_value()
                parser.set('subtitles', 'margin', str(self.sMarg))
            elif uid == 4:
                self.bge = self.bg_switch.get_active()
                parser.set('subtitles', 'bg', str(self.bge))
            elif uid == 5:
                self.musixe = self.mus_switch.get_active()
                parser.set('services', 'MusixMatch', str(self.musixe))
            elif uid == 6:
                self.azlyre = self.az_switch.get_active()
                parser.set('services', 'AZLyrics', str(self.azlyre))
            elif uid == 7:
                self.letrase = self.letr_switch.get_active()
                parser.set('services', 'Letras.br', str(self.letrase))
            elif uid == 8:
                self.cover_size = int(self.comboSize.get_active_id())
                parser.set('services', 'CoverSize', str(self.cover_size))
            elif uid == 9:
                self.autoscroll = self.scroll_check.get_active()
                parser.set('misc', 'autoscroll', str(self.autoscroll))
            elif uid == 10:
                self.scroll_val = int(self.scroll_spin.get_value())
                parser.set('misc', 'positioning', str(self.autoscroll))
            elif uid == 11:
                self.lite = self.lite_switch.get_active()
                parser.set('misc', 'minimal_mode', str(self.lite))
                title = Adw.WindowTitle()
                title.set_title("HBud")
                if self.lite == False:
                    GLib.idle_add(self.headBox.set_visible, True)
                    title.set_subtitle(self.build_version)
                    GLib.idle_add(self.mainStack.set_visible_child, self.placeholder)
                    GLib.idle_add(self.window.set_default_size, 600, 450)
                    GLib.idle_add(self.mainHeader.remove_css_class, "flat")
                    self.window.set_resizable(True)
                    d_pl = futures.ThreadPoolExecutor(max_workers=4)
                    d_pl.submit(self.neo_playlist_gen)
                else:
                    GLib.idle_add(self.headBox.set_visible, False)
                    self.locBut.set_active(True)
                    GLib.idle_add(self.mainStack.set_visible_child, self.rdBox)
                    GLib.idle_add(self.window.set_default_size, 1, 1)
                    GLib.idle_add(self.mainHeader.add_css_class, "flat")
                    try:
                        GLib.idle_add(self.rdTitle.set_text, self.playlist[self.tnum]["title"])
                        GLib.idle_add(self.rdArtist.set_text, self.playlist[self.tnum]["artist"])
                        GLib.idle_add(self.rdYear.set_text, str(self.playlist[self.tnum]["year"]))
                    except: pass
                    self.window.set_resizable(False)
                GLib.idle_add(self.mainHeader.set_title_widget, title)
                GLib.idle_add(self.on_pref_close)
                GLib.idle_add(self.window.hide)
                GLib.idle_add(self.window.present)

            file = open(confP, "w+")
            parser.write(file)
            file.close()
            tools.themer(self.provider, self.window, self.color, self.tnum)

    def on_hide(self, *_):
        self.stopKar = True
        self.lyr_states = [True, True, True]
        self.sub.hide()

parser, confP, theme, color, musix, azlyr, letras, coverSize, sSize, sMarg, bg, autoscroll, positioning, minimal_mode = tools.real_init()
Gst.init(None)
app = Main()
app.connect('activate', app.on_activate)
app.run(None)

# GTK_DEBUG=interactive
# top | grep xy
# to debug