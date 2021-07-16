#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, gi, dbus, random, dbus.mainloop.glib, dbus.service, time, sys
if os.path.exists('/home/daniel/GitRepos/hbud'):
    fdir = "/home/daniel/GitRepos/hbud/DEV_FILES/"
    print(fdir)
    os.chdir(fdir)
    print('Running in development mode.')
else:
    fdir = "/usr/share/hbud/"
    print(fdir)
    os.chdir(fdir)
    print('Running in production mode.')
sys.path.append("tools")
from concurrent import futures
from configparser import ConfigParser
from mediafile import MediaFile
import srt
gi.require_version('Gtk', '3.0')
gi.require_version('Gst', '1.0')
from gi.repository import Gtk, Gst, GLib, GdkPixbuf, Gdk

class GUI:
    def __init__(self):
        UI_FILE = "hbud.glade"
        self.useMode = "audio"
        self.supportedList = ['.3gp', '.aa', '.aac', '.aax', '.aiff', '.flac', '.m4a', '.m4p', '.mp3', '.ogg', '.wav', '.wma', '.wv']
        try:
            self.clickedE = sys.argv[1]
            if os.path.splitext(self.clickedE.split("/")[-1])[-1] not in self.supportedList:
                self.useMode = "video"
                print("video click")
            print(self.clickedE)
        except:
            self.clickedE = False
        version = 'HBud Alpha 0.1-S5'
        print('Init here')
        self.builder = Gtk.Builder()
        self.builder.add_from_file(UI_FILE)
        self.builder.connect_signals(self)
        self.position = 0
        self.playlistPlayer = False
        self.playlist = []
        self.relPos = 0
        self.tnum = 0
        self.player = ""
        self.needSub = False
        self.nowIn = ""
        self.fulle = False
        self.resete = False
        self.hardReset = False
        self.sSize = int(float(sSize))
        self.sMarg = int(float(sMarg))
        self.size = 35000
        self.size2 = 15000
        self.size3 = self.sSize*450
        self.size4 = float(f"0.0{self.sMarg}")*450
        self.globSeek = True
        self.seekBack = False
        self.sub = self.builder.get_object('sub')
        self.slider = Gtk.HScale()
        self.slider.set_can_focus(False)
        self.slider.set_margin_start(6)
        self.slider.set_margin_end(6)
        self.slider.set_draw_value(False)
        self.slider.set_increments(1, 10)
        self.slider_handler_id = self.slider.connect("value-changed", self.on_slider_seek)
        self.box = self.builder.get_object("slidBox")
        self.box.pack_start(self.slider, True, True, 0)
        self.label = Gtk.Label(label='0:00')
        self.label.set_margin_start(6)
        self.label.set_margin_end(6)
        self.trackCover = self.builder.get_object("coverImg")
        self.box.pack_start(self.label, False, False, 0)
        self.plaicon = self.builder.get_object("play")
        self.slider.connect("enter-notify-event", self.mouse_enter)
        self.slider.connect("leave-notify-event", self.mouse_leave)
        self.label.connect("enter-notify-event", self.mouse_enter)
        self.label.connect("leave-notify-event", self.mouse_leave)
        self.storePlaylist = Gtk.ListStore(str, str, str, int, int)
        self.tree = Gtk.TreeView.new_with_model(self.storePlaylist)
        self.tree.set_can_focus(False)
        self.tree.connect("row-activated", self.row_activated)
        self.tree.connect("button_press_event", self.mouse_click)
        self.tree.set_reorderable(True)
        self.tree.set_grid_lines(Gtk.TreeViewGridLines(1))
        self.playlistBox = self.builder.get_object("expanded")
        self.scrollable_treelist = Gtk.ScrolledWindow()
        self.scrollable_treelist.set_can_focus(False)
        self.scrollable_treelist.set_vexpand(True)
        self.exBot = self.builder.get_object("extendedBottom")
        self.scrollable_treelist.add(self.tree)
        self.playlistBox.pack_start(self.scrollable_treelist, True, True, 0)
        self.playing = False
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
        self.strBox= self.builder.get_object("strBox")
        self.strOverlay = self.builder.get_object("strOverlay")
        self.theTitle = self.builder.get_object("theTitle")
        self.infBook = self.builder.get_object("infBook")
        self.subSpin = self.builder.get_object("subSpin")
        self.subMarSpin = self.builder.get_object("subSpin1")
        self.subSpin.set_value(self.sSize)
        self.subMarSpin.set_value(self.sMarg)
        self.res = False
        self.opener = self.builder.get_object('openFolderBut')
        self.window = self.builder.get_object('main')
        if os.geteuid() == 0:
            self.window.set_title(version+' (as superuser)')
        else:
            self.window.set_title(version)
        self.sub.connect('size-allocate', self._on_size_allocated)
        self.window.connect('size-allocate', self._on_size_allocated0)
        # Display the program
        self.window.show_all()
        self.createPipeline("local")
        self.locBut.set_active(True)
        if self.clickedE:
            if self.useMode == "audio":
                self.loader("xy")
                self.on_playBut_clicked("xy")
            else:
                self.strBut.set_active(True)
                self.on_playBut_clicked("xy")
        self.listener() # Do not write anything after this in init

    def createPipeline(self, mode):
        if mode == "local":
            self.videoPipe = Gst.ElementFactory.make("playbin")
            self.audioPipe = Gst.ElementFactory.make("playbin")
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

    def checker(self, widget):
        if widget.get_active() == True:
            widget.set_active(True)
            return False
        else:
            return True

    def lcToggle(self, button):
        if self.mainStack.get_visible_child() != self.playlistBox and button.get_active() == True:
            self.mainStack.set_visible_child(self.playlistBox)
            GLib.idle_add(self.exBot.show)
            GLib.idle_add(self.trackCover.show)
            GLib.idle_add(self.shuffBut.show)
            GLib.idle_add(self.karaokeBut.set_from_icon_name, "audio-x-generic", Gtk.IconSize.BUTTON)
            if self.nowIn == "video" and self.playing == True:
                self.on_playBut_clicked("xy")
            self.useMode = "audio"
            self.needSub = False
            GLib.idle_add(self.strBut.set_active, False)
            GLib.idle_add(self.infBut.set_active, False)
        elif self.mainStack.get_visible_child() == self.playlistBox:
            GLib.idle_add(button.set_active, True)

    def strToggle(self, button):
        if self.mainStack.get_visible_child() != self.strBox and button.get_active() == True:
            self.mainStack.set_visible_child(self.strBox)
            GLib.idle_add(self.exBot.show)
            GLib.idle_add(self.trackCover.hide)
            GLib.idle_add(self.shuffBut.hide)
            GLib.idle_add(self.karaokeBut.set_from_icon_name, "view-fullscreen", Gtk.IconSize.BUTTON)
            if self.nowIn == "audio" and self.playing == True:
                self.on_playBut_clicked("xy")
            self.useMode = "video"
            GLib.idle_add(self.locBut.set_active, False)
            GLib.idle_add(self.infBut.set_active, False)
        elif self.mainStack.get_visible_child() == self.strBox:
            GLib.idle_add(button.set_active, True)
    
    def infToggle(self, button):
        if self.mainStack.get_visible_child() != self.infBook and button.get_active() == True:
            self.mainStack.set_visible_child(self.infBook)
            GLib.idle_add(self.exBot.hide)
            if self.playing == True:
                self.on_playBut_clicked("xy")
            GLib.idle_add(self.locBut.set_active, False)
            GLib.idle_add(self.strBut.set_active, False)
        elif self.mainStack.get_visible_child() == self.infBook:
            GLib.idle_add(button.set_active, True)

    def gen_playlist_view(self, playlistLoc='', name='', again=False, allPos=''):
        if name == 'shuffle':
            if self.playlistPlayer == True:
                self.relPos = 0
                playlistLoc = random.sample(self.playlist, len(self.playlist))
                self.playlist = playlistLoc
                self.gen_playlist_view(name='playlistPlayer', again=self.playlistPlayer, allPos='regen')
                self.on_next('clickModel')
        elif name == 'playlistPlayer':
            if allPos == 'regen':
                print('Regenerate only')
            else:
                print('Passing in generator')
            playlistLoc = self.playlist
            self.storePlaylist = Gtk.ListStore(str, str, str, int, int)
            self.tree.set_model(self.storePlaylist)
            def doapp():
                for x in range(len(playlistLoc)):
                    self.storePlaylist.append([t[x], a[x], al[x], y[x], il[x]])
                return False
            t = []
            a = []
            al = []
            y = []
            il = []
            for i in range(len(playlistLoc)):
                t.append(playlistLoc[i]["title"])
                a.append(playlistLoc[i]["artist"])
                al.append(playlistLoc[i]["album"])
                y.append(playlistLoc[i]["year"])
                il.append(i)
            GLib.idle_add(doapp)
            if not again:
                print("First time")
                for i, column_title in enumerate(["Title", "Artist", "Album", "Year", "ID"]):
                    renderer = Gtk.CellRendererText(xalign=0)
                    renderer.set_property("ellipsize", 3)
                    renderer.set_fixed_size(-1, 50)
                    column = Gtk.TreeViewColumn(column_title, renderer, text=i)
                    if column_title == "Title" or column_title == "Album":
                        column.set_resizable(True)
                        column.set_expand(True)
                    elif column_title == "Artist":
                        column.set_max_width(150)
                        column.set_resizable(True)
                        column.set_expand(True)
                    elif column_title == "ID" or column_title == "Year":
                        column.set_max_width(60)
                        column.set_resizable(False)
                        column.set_expand(False)
                    column.set_sort_column_id(i)
                    column.set_sort_indicator(False)
                    self.tree.append_column(column)
            self.playlistPlayer = True

    def loader(self, path):
        pltmp = []
        if self.clickedE:
            f = MediaFile(self.clickedE)
            title, artist, album, year = f.title, f.artist, f.album, f.year
            if not title:
                title = os.path.splitext(self.clickedE.split("/")[-1])[0]
            if not artist:
                artist = "Unknown"
            if not album:
                album = "Unknown"
            if not year:
                year = 0
            itmp = {"uri" : self.clickedE, "title" : title, "artist" : artist, "year" : year, "album" : album}
            pltmp.append(itmp)
        else:
            pltmpin = os.listdir(path)
            for i in pltmpin:
                ityp = os.path.splitext(i)[1]
                if ityp in self.supportedList:
                    f = MediaFile(f"{path}/{i}")
                    title, artist, album, year = f.title, f.artist, f.album, f.year
                    if not title:
                        title = os.path.splitext(i)[0]
                    if not artist:
                        artist = "Unknown"
                    if not album:
                        album = "Unknown"
                    if not year:
                        year = 0
                    itmp = {"uri" : f"{path}/{i}", "title" : title, "artist" : artist, "year" : year, "album" : album}
                    pltmp.append(itmp)
        self.playlist = pltmp
        self.gen_playlist_view(name="playlistPlayer")

    def on_openFolderBut_clicked(self, button):
        if self.playing == True:
            self.pause()
        if self.useMode == "audio":
            filechooserdialog = Gtk.FileChooserDialog(title="Please choose a folder",
                parent=self.window,
                action=Gtk.FileChooserAction.SELECT_FOLDER)
            filechooserdialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)
            filechooserdialog.add_button("_Open", Gtk.ResponseType.OK)
            filechooserdialog.set_default_response(Gtk.ResponseType.OK)
            filechooserdialog.set_current_folder(f"/home/{user}/Music")
            response = filechooserdialog.run()
            if response == Gtk.ResponseType.OK:
                self.folderPath = filechooserdialog.get_uri().replace("file://", "")
                print("Select clicked")
                print("Folder selected: " + self.folderPath)
                d_pl = futures.ThreadPoolExecutor(max_workers=4)
                d_pl.submit(self.loader, self.folderPath)
            elif response == Gtk.ResponseType.CANCEL:
                print("Cancel clicked")
        else:
            filechooserdialog = Gtk.FileChooserDialog(title="Please choose a video file",
                parent=self.window,
                action=Gtk.FileChooserAction.OPEN)
            filterr = Gtk.FileFilter()
            filterr.set_name("Video files")
            filterr.add_mime_type("video/*")
            filechooserdialog.add_filter(filterr)
            filechooserdialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)
            filechooserdialog.add_button("_Open", Gtk.ResponseType.OK)
            filechooserdialog.set_default_response(Gtk.ResponseType.OK)
            filechooserdialog.set_current_folder(f"/home/{user}/Videos")
            response = filechooserdialog.run()
            if response == Gtk.ResponseType.OK:
                print("Open clicked")
                videoPath = filechooserdialog.get_filename()
                print("File selected: " + videoPath)
                self.on_playBut_clicked(videoPath)
            elif response == Gtk.ResponseType.CANCEL:
                print("Cancel clicked")
        filechooserdialog.destroy()

    def on_save(self, button):
        f = MediaFile(self.editingFile)
        f.year = self.yrEnt.get_value_as_int()
        f.artist = self.arEnt.get_text()
        f.album = self.alEnt.get_text()
        f.title = self.tiEnt.get_text()
        f.save()
        self.playlist[self.storePlaylist[self.edithis][-1]]["year"] = self.yrEnt.get_value_as_int()
        self.playlist[self.storePlaylist[self.edithis][-1]]["artist"] = self.arEnt.get_text()
        self.playlist[self.storePlaylist[self.edithis][-1]]["album"] = self.alEnt.get_text()
        self.playlist[self.storePlaylist[self.edithis][-1]]["title"] = self.tiEnt.get_text()
        self.sub2_hide("xy")
        self.gen_playlist_view(name='playlistPlayer', again=True, allPos='regen')

    def sub2_hide(self, misc, e=""):
        self.sub2.hide()
        return True

    def ed_cur(self, item):
        self.edithis = self.tree.get_selection().get_selected_rows()[1][0][0]
        self.editingFile = self.playlist[self.storePlaylist[self.edithis][-1]]["uri"].replace("file://", "")
        self.yrEnt.set_value(self.playlist[self.storePlaylist[self.edithis][-1]]["year"])
        self.arEnt.set_text(self.playlist[self.storePlaylist[self.edithis][-1]]["artist"])
        self.alEnt.set_text(self.playlist[self.storePlaylist[self.edithis][-1]]["album"])
        self.tiEnt.set_text(self.playlist[self.storePlaylist[self.edithis][-1]]["title"])
        self.sub2.set_title(f"Edit metadata for {self.editingFile.split('/')[-1]}")
        self.sub2.show_all()

    def mouse_click0(self, widget, event):
        if event.button == 1:
            self.on_playBut_clicked(0)

    def mouse_click(self, widget, event):
        if event.button == 3:
            menu = Gtk.Menu()
            menu.set_can_focus(False)
            pthinfo = self.tree.get_path_at_pos(event.x, event.y)
            path,col,cellx,celly = pthinfo
            self.tree.grab_focus()
            self.tree.set_cursor(path,col,0)
            menu_item = Gtk.MenuItem.new_with_label('Delete from current playqueue')
            menu_item.set_can_focus(False)
            menu_item.connect("activate", self.del_cur)
            menu.add(menu_item)
            menu_item = Gtk.MenuItem.new_with_label('Edit metadata')
            menu_item.set_can_focus(False)
            menu_item.connect("activate", self.ed_cur)
            menu.add(menu_item)
            menu.show_all()
            menu.popup_at_pointer()

    def del_cur(self, item):
        this = self.tree.get_selection().get_selected_rows()[1][0][0]
        self.playlist.remove(self.playlist[self.storePlaylist[this][-1]])
        self.gen_playlist_view(name='playlistPlayer', again=self.playlistPlayer, allPos='regen')

    def on_next(self, button):
        if self.nowIn == self.useMode or button == "clickMode":
            print("Next")
            if self.nowIn == "audio" or button == "clickMode":
                if button == "clickMode":
                    self.tnum = self.storePlaylist[self.relPos][-1]
                elif button == "clickModel":
                    self.tnum = 0
                else:
                    self.tree.set_cursor(self.relPos)
                    self.relPos = self.tree.get_selection().get_selected_rows()[1][0][0]
                    self.relPos = self.relPos + 1
                    if self.relPos >= len(self.playlist):
                        self.relPos = 0
                    self.tnum = self.storePlaylist[self.relPos][-1]
                try:
                    self.globSeek = False
                    self.stop()
                except:
                    print("No playbin yet to stop.")
                self.globSeek = True
                self.play()
            elif self.nowIn == "video":
                seek_time_secs = self.player.query_position(Gst.Format.TIME)[1] + 10 * Gst.SECOND
                self.player.seek_simple(Gst.Format.TIME,  Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, seek_time_secs)

    def load_cover(self):
        nam = self.url.replace('file://', '')
        binary = MediaFile(nam).art
        if not binary:
            tmpLoc = "icons/track.png"
        else:
            tmpLoc = "/tmp/cacheCover.jpg"
            f = open(tmpLoc, "wb")
            f.write(binary)
            f.close()
        coverBuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(tmpLoc, 80, 80, True)
        tg = GLib.idle_add(self.trackCover.set_from_pixbuf, coverBuf)

    def on_prev(self, button):
        if self.nowIn == self.useMode:
            print("Prev")
            if self.nowIn == "audio":
                self.tree.set_cursor(self.relPos)
                self.relPos = self.tree.get_selection().get_selected_rows()[1][0][0]
                self.relPos = self.relPos - 1
                if self.relPos < 0:
                    self.relPos = len(self.playlist)-1
                self.tnum = self.storePlaylist[self.relPos][-1]
                try:
                    self.pause()
                    self.globSeek = False
                    self.stop()
                    self.globSeek = True
                except:
                    print("No playbin yet to stop.")
                self.play()
            elif self.nowIn == "video":
                seek_time_secs = self.player.query_position(Gst.Format.TIME)[1] - 10 * Gst.SECOND
                self.player.seek_simple(Gst.Format.TIME,  Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, seek_time_secs)

    def stop(self):
        print("Stop")
        self.player.set_state(Gst.State.PAUSED)
        if self.nowIn == "audio":
            self.audioPipe = self.player
        elif self.nowIn == "video":
            self.videoPipe = self.player
        self.res = False
        self.playing = False
        self.label.set_text("0:00")
        GLib.idle_add(self.plaicon.set_from_icon_name, "media-playback-start", Gtk.IconSize.BUTTON)
        self.slider.set_value(0)
        self.player.set_state(Gst.State.NULL)

    def row_activated(self, widget, row, col):
        self.relPos = self.tree.get_selection().get_selected_rows()[1][0][0]
        print(self.relPos)
        self.on_next("clickMode")

    def pause(self): 
        print("Pause")
        self.playing = False
        self.tree.set_cursor(self.relPos)
        GLib.idle_add(self.plaicon.set_from_icon_name, "media-playback-start", Gtk.IconSize.BUTTON)
        self.player.set_state(Gst.State.PAUSED)
    
    def resume(self):
        print("Resume")
        self.playing = True
        self.tree.set_cursor(self.relPos)
        self.player.set_state(Gst.State.PLAYING)
        GLib.idle_add(self.plaicon.set_from_icon_name, "media-playback-pause", Gtk.IconSize.BUTTON)
        GLib.idle_add(self.updateSlider)
        GLib.idle_add(self.updatePos)
        # GLib.timeout_add(250, self.updateSlider)
        # GLib.timeout_add(80, self.updatePos)

    def updatePos(self):
        if(self.playing == False):
            return False
        nanosecs = self.player.query_position(Gst.Format.TIME)[1]
        self.position = float(nanosecs) / Gst.SECOND
        return True

    def on_slider_seek(self, widget):
        if self.useMode == self.nowIn:
            if self.globSeek:
                seek_time_secs = self.slider.get_value()
                if seek_time_secs < self.position:
                    self.seekBack = True
                    print('back')
                    print(seek_time_secs, self.position)
                self.player.seek_simple(Gst.Format.TIME,  Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, seek_time_secs * Gst.SECOND)
            else:
                print("No need to seek")

    def updateSlider(self):
        if(self.playing == False):
            return False # cancel timeout
        try:
                nanosecs = self.player.query_position(Gst.Format.TIME)[1]
                duration_nanosecs = self.player.query_duration(Gst.Format.TIME)[1]
                # block seek handler so we don't seek when we set_value()
                self.slider.handler_block(self.slider_handler_id)
                duration = float(duration_nanosecs) / Gst.SECOND
                position = float(nanosecs) / Gst.SECOND
                self.slider.set_range(0, duration)
                self.slider.set_value(position)
                self.label.set_text ("%d" % (position / 60) + ":%02d" % (position % 60))
                self.slider.handler_unblock(self.slider_handler_id)
        except Exception as e:
            print (f'W: {e}')
            pass
        return True

    def on_shuffBut_clicked(self, button):
        if self.nowIn == "audio":
            self.gen_playlist_view(name='shuffle')

    def play(self, misc=""):
        if self.clickedE:
            self.url = "file://"+self.clickedE
            self.nowIn = self.useMode
            if self.useMode == "audio":
                self.player = self.audioPipe
            else:
                self.player = self.videoPipe
        elif "/" in misc:
            try:
                self.url = "file://"+misc
                self.nowIn = "video"
                self.player = self.videoPipe
            except:
                return
        elif misc == "continue":
            if self.useMode == "audio":
                self.player = self.audioPipe
                self.nowIn = "audio"
            else:
                self.player = self.videoPipe
                self.nowIn = "video"
        else:
            try:
                self.url = "file://"+self.playlist[self.tnum]["uri"]
                self.nowIn = "audio"
                self.player = self.audioPipe
            except:
                return
        print("Play")
        self.res = True
        self.playing = True
        self.position = 0
        filename = self.url.replace("file://", "").split("/")[-1]
        if self.useMode == "audio":
            GLib.idle_add(self.tree.set_cursor, self.relPos)
        else:
            tmpdbnow = os.listdir(self.url.replace("file://", "").replace(filename, ""))
            if os.path.splitext(filename)[0]+".srt" in tmpdbnow:
                print("Subtitle found!")
                with open (os.path.splitext(self.url.replace("file://", ""))[0]+".srt", 'r') as subfile:
                    presub = subfile.read()
                subtitle_gen = srt.parse(presub)
                subtitle = list(subtitle_gen)
                self.needSub = True
                subs = futures.ThreadPoolExecutor(max_workers=4)
                subs.submit(self.subShow, subtitle)
        if misc != "continue":
            self.player.set_state(Gst.State.NULL)
            self.player.set_property("uri", self.url)
        self.player.set_state(Gst.State.PLAYING)
        GLib.idle_add(self.header.set_subtitle, filename)
        GLib.idle_add(self.plaicon.set_from_icon_name, "media-playback-pause", Gtk.IconSize.BUTTON)
        GLib.timeout_add(250, self.updateSlider)
        GLib.timeout_add(80, self.updatePos)
        if self.useMode == "audio":
            ld_cov = futures.ThreadPoolExecutor(max_workers=4)
            ld_cov.submit(self.load_cover)

    def on_playBut_clicked(self, button):
        if self.nowIn == self.useMode or self.nowIn == "" or "/" in button:
            if not self.playing:
                if not self.res or "/" in str(button):
                    self.play(button)
                else:
                    self.resume()
            else:
                self.pause()
        else:
            self.play("continue")

    def on_main_delete_event(self, window, e):
        x, y = window.get_position()
        sx, sy = window.get_size()
        dialogWindow = Gtk.MessageDialog(parent=self.window, modal=True, destroy_with_parent=True, message_type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.YES_NO, text='Do you really would like to exit now?')
        dialogWindow.set_title("Prompt")
        dsx, dsy = dialogWindow.get_size()
        dialogWindow.move(x+((sx-dsx)/2), y+((sy-dsy)/2))
        dx, dy = dialogWindow.get_position()
        dialogWindow.show_all()
        res = dialogWindow.run()
        if res == Gtk.ResponseType.YES:
            print('OK pressed')
            dialogWindow.destroy()
            try:
                self.mainloop.quit()
            except:
                pass
            self.force = True
            self.stopKar = True
            self.needSub = False
            raise SystemExit
        elif res == Gtk.ResponseType.NO:
            print('No pressed')
            dialogWindow.destroy()
            return True
        else:
            dialogWindow.destroy()
            return True

    def listener(self):
        APP_ID="hbud"
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus = dbus.Bus(dbus.Bus.TYPE_SESSION)
        bus_object = bus.get_object('org.gnome.SettingsDaemon', '/org/gnome/SettingsDaemon/MediaKeys')
        dbus_interface='org.gnome.SettingsDaemon.MediaKeys'
        bus_object.GrabMediaPlayerKeys(APP_ID, 0, dbus_interface=dbus_interface)
        bus_object.connect_to_signal('MediaPlayerKeyPressed', self.on_media)
        self.mainloop = GLib.MainLoop()
        self.mainloop.run()
    
    def on_media(self, app, action):
        print(app, action)
        if app == "hbud" and self.url:
            if action == "Next":
                try:
                    self.on_next("xy")
                except:
                    print('Next error')
            elif action == "Previous":
                try:
                    self.on_prev("xy")
                except:
                    print('Previous error')
            elif not self.playing:
                try:
                    self.resume()
                except:
                    print("Resume error")
            elif self.playing:
                try:
                    self.pause()
                except:
                    print('Pause error')
    
    def on_key(self, widget, key):
        # Add on_key as key_press signal to the ui file - main window preferably
        try:
            if key.keyval == 32 and self.url:
                self.on_playBut_clicked(0)
        except:
            pass

    def on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS and self.nowIn == "audio":
            self.on_next("xy")
        elif t == Gst.MessageType.ERROR:
            self.player.set_state(Gst.State.NULL)
            err, debug = message.parse_error()
            print (f"Error: {err}", debug)

    def _on_size_allocated(self, widget, alloc):
        time.sleep(0.01)
        x, y = self.sub.get_size()
        self.size = 50*x
        self.size2 = 21.4285714*x
    
    def _on_size_allocated0(self, widget, alloc):
        time.sleep(0.01)
        if self.needSub == True:
            x, y = self.window.get_size()
            self.size3 = self.sSize*y
            self.size4 = float(f"0.0{self.sMarg}")*y

    def on_karaoke_activate(self, button):
        if self.nowIn == "audio":
            if self.playing == True or self.res == True:
                print('Karaoke')
                self.stopKar = False
                track = self.playlist[self.tnum]["title"]
                artist = self.playlist[self.tnum]["artist"]
                dbnow = []
                tmpdbnow = os.listdir(self.folderPath)
                for i in tmpdbnow:
                    if ".srt" in i:
                        x = i
                        dbnow.append(f"{self.folderPath}/{x}")
                self.sub.set_title(f'{track} - {artist}')
                tmp = os.path.splitext(self.playlist[self.tnum]["uri"])[0]
                print(dbnow)
                print(tmp)
                if f"{tmp}.srt" not in dbnow:
                    x, y = self.window.get_position()
                    sx, sy = self.window.get_size()
                    dialogWindow = Gtk.MessageDialog(parent=self.window, modal=True, destroy_with_parent=True, message_type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK, text=f'The current track does not have synced lyrics. Please place the synced .srt file alongside the audio file, with the same name as the audio file.')
                    dialogWindow.set_title("Information")
                    dsx, dsy = dialogWindow.get_size()
                    dialogWindow.move(x+((sx-dsx)/2), y+((sy-dsy)/2))
                    dialogWindow.show_all()
                    res = dialogWindow.run()
                    if res == Gtk.ResponseType.OK:
                        dialogWindow.destroy()
                    else:
                        dialogWindow.destroy()
                else:
                    print("FOUND")
                    self.start_karaoke(f"{tmp}.srt")
                    self.sub.show_all()
        elif self.useMode == "video":
            if self.fulle == False:
                GLib.idle_add(self.karaokeBut.set_from_icon_name, "view-restore", Gtk.IconSize.BUTTON)
                self.window.fullscreen()
                ld_clock = futures.ThreadPoolExecutor(max_workers=1)
                ld_clock.submit(self.clock)
            else:
                GLib.idle_add(self.karaokeBut.set_from_icon_name, "view-fullscreen", Gtk.IconSize.BUTTON)
                self.resete = False
                self.hardReset = False
                self.window.unfullscreen()

    def mouse_enter(self, widget, event):
        if self.fulle == True:
            self.hardReset = True
    
    def mouse_leave(self, widget, event):
        if self.fulle == True:
            self.hardReset = False
    
    def mouse_moving(self, widget, event):
        if self.fulle == True:
            self.resete = True
            if self.exBot.get_visible() == False:
                GLib.idle_add(self.exBot.show)
                cursor = Gdk.Cursor.new_from_name(widget.get_display(), 'default')
                self.window.get_window().set_cursor(cursor)
                ld_clock = futures.ThreadPoolExecutor(max_workers=1)
                ld_clock.submit(self.clock)

    def clock(self):
        start = time.time()
        while time.time() - start < 3:
            time.sleep(0.00001)
            if self.hardReset == True:
                start = time.time()
            elif self.resete == True:
                start = time.time()
                self.resete = False
        if self.fulle == True:
            GLib.idle_add(self.exBot.hide)
            display = self.window.get_display()
            cursor = Gdk.Cursor.new_for_display(display, Gdk.CursorType.BLANK_CURSOR)
            self.window.get_window().set_cursor(cursor)

    def on_state_change(self, window, event):
        if event.changed_mask & Gdk.WindowState.FULLSCREEN:
            self.fulle = bool(event.new_window_state & Gdk.WindowState.FULLSCREEN)
            print(self.fulle)

    def subShow(self, subtitle):
        while self.needSub == True:
            time.sleep(0.001)
            for line in subtitle:
                if self.position >= line.start.total_seconds() and self.position <= line.end.total_seconds():
                    GLib.idle_add(self.theTitle.set_markup, f"<span size='{int(self.size3)}'>{line.content}</span>")
                    self.theTitle.set_margin_bottom(self.size4)
                    GLib.idle_add(self.theTitle.show)
                    while self.needSub == True and self.position <= line.end.total_seconds() and self.position >= line.start.total_seconds():
                        time.sleep(0.001)
                        pass
                    GLib.idle_add(self.theTitle.hide)
                    GLib.idle_add(self.theTitle.set_label, "")

    def start_karaoke(self, sfile):
        print('HEY')
        with open (sfile, "r") as subfile:
            presub = subfile.read()
        subtitle_gen = srt.parse(presub)
        subtitle = list(subtitle_gen)
        lyrs = futures.ThreadPoolExecutor(max_workers=4)
        lyrs.submit(self.slideShow, subtitle)

    def slideShow(self, subtitle):
        self.lenlist = len(subtitle)-1
        while not self.stopKar:
            # time.sleep(0.01)
            self.line1 = []
            self.line2 = []
            self.line3 = []
            self.buffer = []
            self.hav1 = False
            self.hav2 = False
            self.hav3 = False
            self.where = -1
            for word in subtitle:
                if '#' in word.content:
                    self.buffer.append(word)
                    if not self.hav1:
                        self.to1()
                    elif not self.hav2:
                        self.to2()
                    else:
                        self.to3()
                else:
                    self.buffer.append(word)
                if self.stopKar or self.seekBack:
                    break
                self.where += 1
            if not self.seekBack:
                self.to2()
                self.to1()
                self.line2 = []
                self.sync()
                self.stopKar = True
            else:
                self.seekBack = False
    
    def to1(self):
        if self.hav2:
            self.line1 = self.line2
        else:
            self.line1 = self.buffer
            self.buffer = []
        self.hav1 = True

    def to2(self):
        if self.where+1 <= self.lenlist:
            if self.hav3:
                self.line2 = self.line3
            else:
                self.line2 = self.buffer
                self.buffer = []
            self.hav2 = True
        else:
            if self.hav1 and not self.hav3:
                self.to1()
            self.line2 = self.line3
            self.line3 = []
            self.sync()

    def to3(self):
        if self.where+2 <= self.lenlist:
            if self.hav1 and self.hav3:
                self.to1()
            if self.hav2 and self.hav3:
                self.to2()
            self.line3 = self.buffer
            self.buffer = []
            self.hav3 = True
        else:
            if self.hav1:
                self.to1()
            if self.hav2:
                self.to2()
            self.line3 = self.buffer
            self.buffer = []
            self.hav3 = False
        self.sync()

    def sync(self):
        simpl2 = ""
        simpl3 = ""
        if self.line2 != []:
            for z in self.line2:
                if self.stopKar or self.seekBack:
                    break
                simpl2 += f"{z.content.replace('#', '')} "
        else:
            simpl2 = ""
        if self.line3 != []:
            for z in self.line3:
                if self.stopKar or self.seekBack:
                    break
                simpl3 += f"{z.content.replace('#', '')} "
        else:
            simpl3 = ""
        tg = GLib.idle_add(self.label2.set_markup, f"<span size='{int(self.size2)}'>{simpl2}</span>")
        tg = GLib.idle_add(self.label3.set_markup, f"<span size='{int(self.size2)}'>{simpl3}</span>")
        done = ""
        tmpline = self.line1[:]
        first = True
        tl1 = self.line1
        tl1.insert(0, "")
        it = 1
        maxit = len(tl1)-1
        for xy in tl1:
            if self.stopKar or self.seekBack:
                break
            if first:
                first = False
            else:
                tmpline = tmpline[1:]
            leftover = ""
            for y in tmpline:
                if self.stopKar or self.seekBack:
                    break
                leftover += f"{y.content.replace('#', '')} "
            try:
                tg = GLib.idle_add(self.label1.set_markup, f"<span size='{self.size}' color='green'>{done}</span> <span size='{self.size}' color='green'>{xy.content.replace('#', '')}</span> <span size='{self.size}' color='white'>{leftover}</span>")
            except:
                tg = GLib.idle_add(self.label1.set_markup, f"<span size='{self.size}' color='green'>{done}</span> <span size='{self.size}' color='green'>{xy}</span> <span size='{self.size}' color='white'>{leftover}</span>")
            while not self.stopKar:
                time.sleep(0.01)
                if it > maxit:
                    if self.position >= xy.end.total_seconds()-0.05 and self.position >= 0.5:
                        break
                else:
                    xz = tl1[it]
                    if self.position >= xz.start.total_seconds()-0.1 and self.position >= 0.5:
                        break
                if self.seekBack:
                    break
            it += 1
            try:
                done += f"{xy.content.replace('#', '')} "
            except:
                pass

    def config_write(self, button):
        parser.set('subtitles', 'margin', str(int(float(self.subMarSpin.get_value()))))
        parser.set('subtitles', 'size', str(int(float(self.subSpin.get_value()))))
        file = open(confP, "w+")
        parser.write(file)
        file.close()
        self.sSize = int(float(self.subSpin.get_value()))
        self.sMarg = int(float(self.subMarSpin.get_value()))

    def on_hide(self, window, e):
        self.stopKar = True
        self.sub.hide()
        return True

if __name__ == "__main__":
    # Dev/Use mode
    user = os.popen("who|awk '{print $1}'r").read()
    user = user.rstrip()
    user = user.split('\n')[0]
    parser = ConfigParser()
    confP = f"/home/{user}/.config/hbud.ini"
    if os.path.isfile(confP):
        parser.read(confP)
    else:
        os.system(f"touch {confP}")
        parser.add_section('subtitles')
        parser.set('subtitles', 'margin', str(66))
        parser.set('subtitles', 'size', str(30))
        file = open(confP, "w+")
        parser.write(file)
        file.close()
    sSize = parser.get('subtitles', 'size')
    sMarg = parser.get('subtitles', 'margin')
    Gst.init(None)
    app = GUI()
    Gtk.main()