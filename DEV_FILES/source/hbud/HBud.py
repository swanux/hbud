#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi, srt, azapi, json, os, sys, acoustid, musicbrainzngs, subprocess, hashlib, shutil
from concurrent import futures
from time import time
from operator import itemgetter
from collections import deque
from datetime import timedelta
from random import sample
from icu import Locale
from mediafile import MediaFile, MediaField, MP3DescStorageStyle, StorageStyle
gi.require_version('Gtk', '4.0')
gi.require_version('Gst', '1.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, GLib, GdkPixbuf, Gdk, Adw, Gio, Gst
from hbud import letrasapi, musixapi, frontend, mpris, tools

class Main(frontend.UI):
    def __init__(self):
        super().__init__()
        self.toolClass = tools.Tools()
        self.toolClass.position = 0
        self.toolClass.o = self.settings.get_int("opacity")/10
        self.mpris_adapter = None
        GLib.Thread.new(None, mpris.init, self)
        self.toolClass.label1 = self.sub._label1
        self.toolClass.label2 = self.sub._label2
        self.toolClass.label3 = self.sub._label3
        self.def_cur = Gdk.Cursor.new_from_name('default')
        self.blank_cur = Gdk.Cursor.new_from_name('none')
        tmlist = json.loads(self.settings.get_string("saved-order"))
        self.toolClass.plnum = -1
        GLib.idle_add(self.flap_init, tmlist)
        self.toast_templ = Adw.Toast()
        self.toast_templ.set_timeout(3)
        self.clickedE = False

    def do_open(self, files, n_files, _):
        print(files, n_files)
        self.activate()
        self.manual_file_parser(files)

    def flap_init(self, tmlist):
        if len(tmlist) != 0:
            self.window._main_stack._flap_stack.set_visible_child(self.window._main_stack._play_list_box)
        else:
            self.window._main_stack._flap_stack.set_visible_child(self.window._main_stack._nope_lab)
        child = self.window._main_stack._play_list_box.get_first_child()
        while child is not None:
            self.window._main_stack._play_list_box.remove(child)
            child = self.window._main_stack._play_list_box.get_first_child()
        for i, item in enumerate(tmlist):
            print(i, item["name"])
            widget = frontend.PlayListBox(item["name"], self._("{} Tracks".format(len(item["content"]))), i)
            widget._del_but.connect("clicked", self.on_clear_order)
            widget._start_but.connect("clicked", self.load_saved_list)
            widget._ed_but.connect("clicked", self.edit_saved_list)
            self.window._main_stack._play_list_box.append(widget)

    def load_saved_list(self, button):
        tmlist = json.loads(self.settings.get_string("saved-order"))
        self.toolClass.plnum = int(button.get_name().replace("start_but_", ""))
        print(self.toolClass.plnum)
        self.reset_player()
        self.playlist = tmlist[self.toolClass.plnum]["content"]
        self.folderPath = GLib.path_get_dirname(self.playlist[0]["uri"])
        print(self.folderPath)
        for item in self.playlist[:]:
            if os.path.isfile(f"{item['uri']}") is False: self.playlist.remove(item)
        GLib.idle_add(self.window._main_stack._sup_stack.set_visible_child, self.window._main_stack._sup_spinbox)
        GLib.idle_add(self.window._main_stack._side_flap.set_reveal_flap, False)
        GLib.Thread.new(None, self.loader, self.folderPath, False, True)

    def do_activate(self):
        self.confDir = GLib.get_user_config_dir()
        self.API_KEY = "Erv1I6jCqZ"
        musicbrainzngs.set_useragent("hbud", "0.4.2", "https://github.com/swanux/hbud")
        self.DAPI = azapi.AZlyrics('duckduckgo', accuracy=0.65)
        self.createPipeline("local")
        self.connect_signals()

        self.size3, self.size4 = self.settings.get_int("relative-size")*450, float("0.0{}".format(self.settings.get_int("relative-margin")))*450
        self.toolClass.size, self.toolClass.size2 = 35000, 15000
        self.themeDict = {"0" : 0, "1" : 4, "2" : 1}
        self.theme = self.themeDict[self.settings.get_string("theme")]
        self.styles.set_color_scheme(self.theme)
        self.color = self.settings.get_string("color")
        coco = Gdk.RGBA()
        coco.parse(self.color)
        self.prefwin._colorer.set_rgba(coco)
        self.toolClass.themer(self.provider, self.window, self.color)
        self.adj = self.window._main_stack._sup_scroll.get_vadjustment()

        # Display the program
        self.window.set_application(self)
        self.window.present()
        self.hwa_change()
        if self.settings.get_boolean("minimal-mode") is True:
            GLib.idle_add(self.window._head_box.hide)
            GLib.idle_add(self.window._toggle_pane_button.hide)
            GLib.idle_add(self.window._main_stack.set_visible_child, self.window._main_stack._rd_box)
            GLib.idle_add(self.window.set_default_size, 1, 1)
            GLib.idle_add(self.window._label_end.hide)
            GLib.idle_add(self.window._drop_but.hide)
            self.window.set_resizable(False)
        self.window._loc_but.set_active(True)

    def connect_signals(self):
        self.window.connect("close-request", self.on_main_delete_event)
        self.prefwin.connect("close-request", self.on_pref_close)
        self.sub.connect("close-request", self.on_hide)
        self.sub2.connect("close-request", self.sub2_hide)
        self.about.connect("close-request", self.about_hide)
        self.shortcuts.connect("close-request", self.on_shortcuts_hide)

        self.window._ev_key_main.connect("key-pressed", self.on_key_local)
        self.window._ev_key_main.connect("key-released", self.on_key_local_release)
        self.sub._ev_key_sub.connect("key-pressed", self.on_key_local)
        self.sub._ev_key_sub.connect("key-released", self.on_key_local_release)

        action = Gio.SimpleAction.new("pref", None)
        action.connect("activate", self.on_infBut_clicked)
        self.add_action(action)
        action = Gio.SimpleAction.new("shortcuts", None)
        action.connect("activate", self.on_shortcuts_show)
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
        action = Gio.SimpleAction.new("nextthis", None)
        action.connect("activate", self.next_cur)
        self.add_action(action)
        self.window._ofo_but.connect("clicked", self.on_openFolderBut_clicked)
        self.window._loc_but.connect("toggled", self.allToggle)
        self.window._str_but.connect("toggled", self.allToggle)
        self.window._play_but.connect("clicked", self.on_playBut_clicked)
        self.window._main_stack._overlay_play.connect("clicked", self.on_playBut_clicked)
        self.window._prev_but.connect("clicked", self.on_prev)
        self.window._next_but.connect("clicked", self.on_next)
        self.window._shuff_but.connect("clicked", self.on_shuffBut_clicked)
        self.window._karaoke_but.connect("clicked", self.on_karaoke_activate)
        self.window._main_stack._overlay_full.connect("clicked", self.on_karaoke_activate)
        self.window._drop_but.connect("clicked", self.on_dropped)
        self.sub2._magi_but.connect("clicked", self.on_magiBut_clicked)
        self.sub2._ichoser.connect("clicked", self.on_iChoser_clicked)
        self.sub2._sav_but.connect("clicked", self.on_save)
        self.window._main_stack._combo_sort.connect("changed", self.on_sort_change)
        self.window._main_stack._search_play.connect("activate", self.on_search)
        self.window._main_stack._order_but.connect("clicked", self.on_order_save)
        self.window._main_stack._order_but2.connect("clicked", self.on_rescan_order)
        self.window._main_stack._video_click.connect("pressed", self.on_playBut_clicked)

        self.window._main_stack._drop_music.connect("drop", self.on_drop)

        self.sub._ye_but.connect("clicked", self.on_correct_lyr)
        self.sub._no_but.connect("clicked", self.on_wrong_lyr)

        self.sub._off_but.connect("clicked", self.on_off_but_clicked)
        self.window.connect('notify', self._on_notify)
        self.sub.connect('notify', self._on_notify)
        self.settings.connect("changed", self.special_settings)
        self.prefwin._colorer.connect("color-set", self.special_settings)
        self.prefwin._clear_cache.connect("clicked", self.cache_clear)

        self.window._slider_click.connect("released", self.on_slider_seek)
        self.window._slider.connect("value-changed", self.on_slider_grabbed)
        self.window._slider_click.connect("pressed", self.on_slider_grab)
        self.window._main_stack._overlay_click.connect("released", self.on_slider_seek)
        self.window._main_stack._overlay_scale.connect("value-changed", self.on_slider_grabbed)
        self.window._main_stack._overlay_click.connect("pressed", self.on_slider_grab)
        self.window._main_stack._overlay_motion.connect("enter", self.mouse_enter)
        self.window._main_stack._overlay_motion.connect("leave", self.mouse_leave)
        self.window._main_stack._hub_motion.connect("enter", self.mouse_enter)
        self.window._main_stack._hub_motion.connect("leave", self.mouse_leave)
        self.window._main_stack._hub_motion2.connect("enter", self.mouse_enter)
        self.window._main_stack._hub_motion2.connect("leave", self.mouse_leave)
        self.window._main_motion.connect("motion", self.mouse_moving)
        self.window._prev_but.connect("clicked", self.prev_next_rel)
        self.window._next_but.connect("clicked", self.prev_next_rel)

    def prev_next_rel(self, *_):
        if self.useMode == self.nowIn and self.useMode == "video":
            if not self.clocking:
                self.clocking = True
                ld_clock = futures.ThreadPoolExecutor(max_workers=1)
                ld_clock.submit(self.clock, "seek")
    
    def cache_clear(self, *_):
        shutil.rmtree(f"{self.cacheDir}/hbud")
        os.mkdir(f"{self.cacheDir}/hbud")
        GLib.idle_add(self.prefwin._clear_cache.set_label, self._("Clear 0 bytes"))

    def on_about_clicked(self, *_): self.about.show()

    def about_hide(self, *_): self.about.hide()

    def on_shortcuts_show(self, *_): self.shortcuts.present()

    def on_shortcuts_hide(self, *_): self.shortcuts.hide()

    def get_directory_size(self, dir_path):
        dir = Gio.File.new_for_path(dir_path)
        enumerator = dir.enumerate_children(Gio.FILE_ATTRIBUTE_STANDARD_SIZE,
                                            Gio.FileQueryInfoFlags.NONE,
                                            None)
        total_size = 0
        for child_info in enumerator:
            total_size += child_info.get_size()
        del dir, enumerator
        self.prefwin._clear_cache.set_label(self._("Clear {}").format(GLib.format_size(total_size)))
        return False

    def on_infBut_clicked(self, *_):
        GLib.idle_add(self.get_directory_size, f"{self.cacheDir}/hbud")
        self.prefwin.present()
    
    def on_pref_close (self, *_): self.prefwin.hide()

    def highlight(self, widget, *_):
        print(widget.get_button())
        if widget.get_button() == 3:
            self.ednum = int(widget.get_widget().get_name().replace("trackbox_", ""))
            self.popover = Gtk.PopoverMenu.new_from_model(self.menu)
            self.popover.set_autohide(True)
            self.popover.set_parent(widget.get_widget())
            self.popover.popup()
        elif widget.get_button() == 1:
            nownum = int(widget.get_widget().get_name().replace("trackbox_", ""))
            if self.tnum == nownum: return
            self.tnum = nownum
            self.toolClass.themer(self.provider, self.window, self.color, self.tnum)
            self.on_next("clickMode")

    def manual_file_parser(self, arguments):
        mode, files = "", []
        for arg in arguments:
            i = arg.query_info(Gio.FILE_ATTRIBUTE_STANDARD_CONTENT_TYPE,
                            Gio.FileQueryInfoFlags.NONE,
                            None)
            tags = i.get_content_type()
            del i
            if mode == "":
                if "audio" in tags: mode = "audio"
                elif "video" in tags and self.settings.get_boolean("minimal-mode") is False and mode == "":
                    mode = "video"
                    self.reset_player()
                    self.useMode = "video"
                    break
                elif "subrip" in tags and mode == "" and self.nowIn == "video" and self.useMode == "video":
                    mode = "subtitle"
                    break
                else:
                    return False
            elif mode not in tags:
                return False
            files.append(arg)
        if mode == "audio":
            self.reset_player()
            self.clickedE = files
            self.window._loc_but.set_active(True)
            self.window._main_stack._sup_stack.set_visible_child(self.window._main_stack._sup_spinbox)
            self.loader("xy")
        elif mode == "video" and self.settings.get_boolean("minimal-mode") is False:
            self.clickedE = arguments
            self.window._str_but.set_active(True)
            self.on_playBut_clicked(arguments[0].get_path())
        elif mode == "subtitle":
            self.subdone(arguments[0].get_path(), True)
        else: self.clickedE = False

    def on_drop(self, drop_target, value, *_):
        del drop_target
        files = value.get_files()
        self.manual_file_parser(files)

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
        widList = self.neo_playlist_gen("shuff_2nd_stage")
        for i in widList:
            GLib.idle_add(self.window._main_stack._sup_box.append, i)

    def on_sort_change(self, widget):
        print("Sorting")
        aid = int(widget.get_active_id())
        if self.sorted is False: self.archive = self.playlist.copy()
        self.sorted = True
        if aid == 0 and self.sorted is True:
            self.playlist = self.archive.copy()
            self.archive = []
            self.sorted = False
        else: self.playlist = sorted(self.archive, key=itemgetter(self.searchDict[str(aid)][0]),reverse=self.searchDict[str(aid)][1])
        widList = self.neo_playlist_gen("shuff_2nd_stage")
        for i in widList:
            GLib.idle_add(self.window._main_stack._sup_box.append, i)
        num = 0
        for item in self.playlist:
            if item["title"] == self.title: break
            else: num += 1
        self.tnum = num
        self.toolClass.themer(self.provider, self.window, self.color, self.tnum)

    def on_clear_order(self, button):
        tmlist = json.loads(self.settings.get_string("saved-order"))
        curnum = int(button.get_name().replace("del_but_", ""))
        print(curnum)
        dialog = frontend.DeleteDialog(tmlist[curnum]["name"])
        dialog.connect("response", self.dia_response, curnum, tmlist)
        dialog.set_transient_for(self.window)
        dialog.present()

    def edit_saved_list(self, button):
        curnum = int(button.get_name().replace("ed_but_", ""))
        print(curnum)
        tmlist = json.loads(self.settings.get_string("saved-order"))
        dialog = frontend.RenameDialog(tmlist[curnum]["name"])
        dialog.connect("response", self.dia_response, curnum, tmlist)
        dialog.set_transient_for(self.window)
        dialog.present()
    
    def dia_response(self, dialog, response, curnum, tmlist):
        if response == "save":
            tmlist[curnum]["name"] = dialog._rename_entry.get_text()
            self.settings.set_string("saved-order", json.dumps(tmlist))
            GLib.idle_add(self.flap_init, tmlist)
        elif response == "delete":
            del tmlist[curnum]
            self.settings.set_string("saved-order", json.dumps(tmlist))
            if self.toolClass.plnum == curnum: self.toolClass.plnum = -1
            self.toast_templ.set_title(self._('Deleted Playlist Successfully'))
            self.window._main_toast.add_toast(self.toast_templ)
            GLib.idle_add(self.flap_init, tmlist)
            if curnum == self.toolClass.plnum:
                self.toolClass.plnum = -1
            elif curnum < self.toolClass.plnum:
                self.toolClass.plnum -= 1
            self.toolClass.themer(self.provider, self.window, self.color, self.tnum)

    def on_rescan_order(self, _): GLib.Thread.new(None, self.loader, self.folderPath, True)

    def on_order_save(self, _):
        data = []
        for i in range(len(self.playlist)): data.append(self.playlist[i].copy())
        for i in range(len(data)): data[i]["widget"] = None
        tmlist = json.loads(self.settings.get_string("saved-order"))
        if self.toolClass.plnum == -1:
            self.toolClass.plnum = len(tmlist)
            print("appending")
            tmlist.append({"name":self._("Unnamed Playlist"), "content":data})
        else:
            tmlist[self.toolClass.plnum]["content"] = data
        self.settings.set_string("saved-order", json.dumps(tmlist))
        self.toast_templ.set_title(self._('Saved Playlist Successfully'))
        self.window._main_toast.add_toast(self.toast_templ)
        GLib.idle_add(self.flap_init, tmlist)
        self.toolClass.themer(self.provider, self.window, self.color, self.tnum)

    def createPipeline(self, mode):
        if mode == "local":
            self.videoPipe, self.audioPipe = Gst.ElementFactory.make("playbin3"), Gst.ElementFactory.make("playbin3")
            sink = Gst.ElementFactory.make("gtk4paintablesink", "sink")
            paintable = sink.get_property("paintable")
            video_sink = Gst.ElementFactory.make("glsinkbin", "video-sink")
            video_sink.set_property("sink", sink)
            self.videoPipe.set_property("video-sink", video_sink)
            Gst.util_set_object_arg(self.videoPipe, "flags", "video+audio+deinterlace+soft-colorbalance")
            Gst.util_set_object_arg(self.audioPipe, "flags", "audio+soft-volume")
            self.window._main_stack._video_picture.set_paintable(paintable)
            bus = self.videoPipe.get_bus()
            bus.add_signal_watch()
            bus.connect("message", self.on_message)
            bus = self.audioPipe.get_bus()
            bus.add_signal_watch()
            bus.connect("message", self.on_message)

    def on_dropped(self, button):
        if self.window._drop_but.get_sensitive() is True:
            if self.window._main_stack._top_reveal.get_reveal_child() is False:
                GLib.idle_add(self.window._drop_but.set_icon_name, "go-up")
                self.window._main_stack._top_reveal.set_reveal_child(True)
                self.window._main_stack._search_play.grab_focus()
            else:
                GLib.idle_add(self.window._drop_but.set_icon_name, "go-down")
                self.window._main_stack._top_reveal.set_reveal_child(False)

    def allToggle(self, button):
        btn = button.get_name()
        if self.window._main_stack.get_visible_child() != self.switchDict[btn][0] and button.get_active() is True:
            self.window._main_stack.set_visible_child(self.switchDict[btn][0])
            GLib.idle_add(self.window._karaoke_but.set_icon_name, self.switchDict[btn][1])
            if self.playing is True:
                if self.switchDict[btn][2] == "video" and self.nowIn == "audio": self.on_playBut_clicked("xy")
                elif self.nowIn == "video" and self.switchDict[btn][2] != "video": self.on_playBut_clicked("xy")
            self.useMode = self.switchDict[btn][2]
            self.needSub = False
            GLib.idle_add(self.switchDict[btn][3].set_active, False)
        elif self.window._main_stack.get_visible_child() == self.switchDict[btn][0]: GLib.idle_add(button.set_active, True) 

    def purger(self):
        child = self.window._main_stack._sup_box.get_first_child()
        while child is not None:
            self.window._main_stack._sup_box.remove(child)
            child = self.window._main_stack._sup_box.get_first_child()

    def neo_playlist_gen(self, name="", srBox=None, dsBox=None, src=0, dst=0):
        print("neo start", time())
        widList = []
        if self.settings.get_boolean("minimal-mode") is True:
            self.on_next("clickMode")
            return
        else:
            if name == "reorder":
                self.window._main_stack._sup_box.reorder_child_after(srBox, dsBox)
                for i, item in enumerate(self.playlist):
                    item["widget"].set_name(f"trackbox_{i}")
                if self.tnum == src or self.tnum == dst:
                    if self.tnum == src: self.tnum = dst
                    elif src > dst: self.tnum += 1
                    elif src < dst: self.tnum -= 1
                else:
                    if src > self.tnum and dst < self.tnum: self.tnum += 1
                    elif src < self.tnum and dst > self.tnum: self.tnum -= 1
                self.toolClass.themer(self.provider, self.window, self.color, self.tnum)
            else:
                if name != "modular" and name != "append":
                    GLib.idle_add(self.purger)
                for i, item in enumerate(self.playlist):
                    trBox = None
                    if name == "shuff_2nd_stage":
                        if item["hidden"] is False:
                            trBox = item["widget"]
                            trBox.set_name(f"trackbox_{i}")
                    elif name != "modular" or i == self.ednum:
                        if name != "append" or self.playlist[i]["widget"] is None:
                            trBox = frontend.TrackBox(item["title"].replace("&", "&amp;"), item["artist"], i, item["year"], item["length"], item["album"])
                            self.playlist[i]["widget"] = trBox
                            trBox._right_click.connect("pressed", self.highlight)
                            trBox._left_click.connect("pressed", self.highlight)
                            self.load_cover(item["uri"], trBox.image)
                        if name == "modular" and i == self.ednum: self.window._main_stack._sup_box.insert_child_after(trBox, self.playlist[i-1]["widget"])
                    if name != "modular" and trBox is not None: widList.append(trBox)
                if name != "modular" and name != "append":
                    if self.title is not None:
                        num = 0
                        for item in self.playlist:
                            if item["title"] == self.title: break
                            else: num += 1
                        self.tnum = num
                        self.toolClass.themer(self.provider, self.window, self.color, self.tnum)
                    GLib.idle_add(self.window._drop_but.set_sensitive, True)
        print("neo end", time())
        return widList

    def metas(self, location, extrapath, misc=False):
        tf = Gio.File.new_for_path(location)
        i = tf.query_info(Gio.FILE_ATTRIBUTE_STANDARD_CONTENT_TYPE,
                        Gio.FileQueryInfoFlags.NONE,
                        None)
        tags = i.get_content_type()
        if "audio" not in tags: return
        f = MediaFile(location)
        title, artist, album, year, length = f.title, f.artist, f.album, f.year, ":".join(str(timedelta(seconds=round(f.length))).split(":")[1:])
        if not title: title = os.path.splitext(extrapath)[0]
        if not artist: artist = self._("Unknown")
        if not album: album = self._("Unknown")
        if not year: year = 0
        itmp = {"uri" : location, "title" : title, "artist" : artist, "year" : year, "album" : album, "length" : length, "widget" : None, "hidden" : False}
        if misc is True:
            if itmp not in self.playlist: self.pltmp.append(itmp)
        else: self.pltmp.append(itmp)

    def loader(self, path, misc=False, skippl=False):
        print("loader start", time())
        if skippl is False:
            self.pltmp = []
            if self.clickedE:
                self.folderPath = GLib.path_get_dirname(self.clickedE[0].get_path())
                for item in self.clickedE:
                    self.metas(item.get_path(), GLib.path_get_basename(item.get_path()))
            else:
                pltmpin = os.scandir(path)
                for i in pltmpin:
                    self.metas(f"{path}/{i.name}", i.name, misc)
        if misc is False:
            if skippl is False: self.playlist = self.pltmp
            widList = self.neo_playlist_gen()
            if self.settings.get_boolean("minimal-mode") is False:
                for i in widList:
                    GLib.idle_add(self.window._main_stack._sup_box.append, i)
            GLib.idle_add(self.window._main_stack._sup_stack.set_visible_child, self.window._main_stack._sup_scroll)
        else:
            uristmp = []
            for item in self.playlist: uristmp.append(item["uri"])
            i = 0
            for item in self.pltmp:
                if item["uri"] not in uristmp:
                    self.playlist.append(item)
                    i += 1
            widList = self.neo_playlist_gen(name="append")
            for widget in widList:
                GLib.idle_add(self.window._main_stack._sup_box.append, widget)
            self.toast_templ.set_title(self._('Rescan Complete\n{} Tracks Added').format(i))
            self.window._main_toast.add_toast(self.toast_templ)
        print("loader end", time())

    def on_openFolderBut_clicked(self, *_):
        self.clickedE = False
        if self.playing is True: self.pause()
        if self.useMode == "audio": self.fcconstructer(self._("Choose a Folder"), Gtk.FileChooserAction.SELECT_FOLDER, "Music", self.window)
        else: self.fcconstructer(self._("Choose a Video File"), Gtk.FileChooserAction.OPEN, "Videos", self.window)

    def reset_player(self):
        print("We reset")
        if self.nowIn == "audio" and self.useMode == "audio":
            try: self.stop(arg=False)
            except: print("Not stopping")
        if self.nowIn == "video" and self.useMode == "video":
            try: self.stop(arg=False)
            except: print("Not stopping")
        else:
            try: self.player.set_state(Gst.State.PAUSED)
            except: print("Not pausing")
        self.tnum = -1
        self.toolClass.themer(self.provider, self.window, self.color, self.tnum)

    def on_response(self, dialog, response, _, ftype):
        if response == Gtk.ResponseType.ACCEPT:
            if ftype == "Music":
                self.toolClass.plnum = -1
                self.reset_player()
                self.folderPath = dialog.get_files()[0].get_path()
                print("Folder selected: " + self.folderPath)
                self.window._main_stack._sup_stack.set_visible_child(self.window._main_stack._sup_spinbox)
                GLib.Thread.new(None, self.loader, self.folderPath)
            elif ftype == "Pictures":
                path = dialog.get_file().get_path()
                tf = open(path, "rb")
                tmBin = tf.read()
                tf.close()
                GLib.idle_add(self.load_cover, "brainz", tmBin)
            else:
                videoPath = dialog.get_file().get_path()
                print("File selected: " + videoPath)
                self.res = False
                self.on_playBut_clicked(videoPath)
        elif response == Gtk.ResponseType.CANCEL: print("Cancel clicked")

    def fcconstructer(self, title, action, ftype, parent):
        filechooserdialog = Gtk.FileChooserNative.new(title, parent, action, self._("Open"), self._("Cancel"))
        if ftype == "Videos":
            filterr = Gtk.FileFilter()
            filterr.set_name(self._("Video Files"))
            filterr.add_mime_type("video/*")
            filechooserdialog.add_filter(filterr)
        elif ftype == "Pictures":
            filterr = Gtk.FileFilter()
            filterr.set_name(self._("Image Files"))
            filterr.add_mime_type("image/*")
            filechooserdialog.add_filter(filterr)
        filechooserdialog.connect("response", self.on_response, filechooserdialog, ftype)
        filechooserdialog.set_transient_for(parent)
        filechooserdialog.set_modal(True)
        filechooserdialog.show()

    def on_iChoser_clicked(self, *_):
        self.fcconstructer(self._("Choose an Image File"), Gtk.FileChooserAction.OPEN, "Pictures", self.sub2)

    def on_save(self, *_):
        self.sub2._yr_ent.update()
        f = MediaFile(self.editingFile)
        buffer = self.sub2._lyr_ent.get_buffer()
        f.year, f.artist, f.album, f.title, f.art, f.lyrics = self.sub2._yr_ent.get_value_as_int(), self.sub2._ar_ent.get_text(), self.sub2._al_ent.get_text(), self.sub2._ti_ent.get_text(), self.binary, buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), True)
        f.save()
        self.playlist[self.ednum]["year"] = self.sub2._yr_ent.get_value_as_int()
        self.playlist[self.ednum]["artist"] = self.sub2._ar_ent.get_text()
        self.playlist[self.ednum]["album"] = self.sub2._al_ent.get_text()
        self.playlist[self.ednum]["title"] = self.sub2._ti_ent.get_text()
        if self.toolClass.plnum != -1:
            self.on_order_save(None)
        uuid = hashlib.md5(GLib.path_get_basename(self.editingFile).encode()).hexdigest()
        os.remove(f"{self.cacheDir}/hbud/cached_{uuid}.jpg")
        self.sub2_hide("xy")
        GLib.idle_add(self.window._main_stack._sup_box.remove, self.playlist[self.ednum]["widget"])
        self.neo_playlist_gen("modular")

    def sub2_hide(self, *_):
        self.sub2.hide()
        if self.sub2._mag_spin.get_spinning() is True: self.aborte = True
        GLib.idle_add(self.sub2._mag_spin.stop)

    def ed_cur(self, *_):
        self.popover.unparent()
        self.editingFile = self.playlist[self.ednum]["uri"].replace("file://", "")
        self.sub2._yr_ent.set_value(self.playlist[self.ednum]["year"])
        self.sub2._ar_ent.set_text(self.playlist[self.ednum]["artist"])
        self.sub2._al_ent.set_text(self.playlist[self.ednum]["album"])
        self.sub2._ti_ent.set_text(self.playlist[self.ednum]["title"])
        try: self.sub2._lyr_ent.get_buffer().set_text(MediaFile(self.playlist[self.ednum]["uri"]).lyrics)
        except: self.sub2._lyr_ent.get_buffer().set_text("")
        self.load_cover(mode="meta")
        self.sub2.present()

    def on_magiBut_clicked(self, _):
        GLib.idle_add(self.sub2._mag_spin.start)
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
        else: GLib.idle_add(self.sub2._mag_spin.stop)
        GLib.idle_add(self.choser_window.hide)
        GLib.idle_add(self.chosBox.remove, self.chosBox.get_last_child())

    def fetch_cur(self):
        path = self.playlist[self.ednum]["uri"].replace("file://", "")
        print(path)
        try:
            results = acoustid.match(self.API_KEY, path, force_fpcalc=True)
        except acoustid.NoBackendError as e:
            print("chromaprint library/tool not found", file=sys.stderr)
            print(e)
        except acoustid.FingerprintGenerationError as e:
            print("fingerprint could not be calculated", e)
        except acoustid.WebServiceError as exc:
            print("web service request failed:", exc.message, file=sys.stderr)
        self.chosefrom, i = [], 0
        try:
            for score, rid, title, artist in results:
                if self.aborte is True:
                    print("Aborted")
                    break
                if artist is not None and title is not None and i <= 10:
                    tmpData = musicbrainzngs.get_recording_by_id(rid, includes=["releases"])["recording"]["release-list"]
                    GLib.usleep(1100000)
                    i += 1
                    if len(tmpData) > 2:
                        tmpDir = {"score": score, "rid": rid, "title": title, "artist": artist, 'year' : int(tmpData[0]["date"].split("-")[0]), "album" : tmpData[0]["title"], "album_ids" : [d['id'] for d in tmpData if 'id' in d]}
                        for item in self.chosefrom:
                            if item["title"] == tmpDir["title"] and item["artist"] == tmpDir["artist"] and item["year"] == tmpDir["year"]: break
                        else: self.chosefrom.append(tmpDir)
        except: print("Something bad happened...")
        if self.aborte is True:
            print("Aborted")
            self.aborte = False
            return
        if len(self.chosefrom) == 0:
            self.toast_templ.set_title(self._('Did Not Find Any Match Online'))
            self.sub2._sub2_toast.add_toast(self.toast_templ)
            GLib.idle_add(self.sub2._mag_spin.stop)
        elif len(self.chosefrom) == 1:
            data = [self.chosefrom[0]["artist"], self.chosefrom[0]["title"], self.chosefrom[0]["rid"], self.chosefrom[0]["year"], self.chosefrom[0]["album"], self.chosefrom[0]["album_ids"]]
            thread = futures.ThreadPoolExecutor(max_workers=2)
            thread.submit(self.next_fetch, data)
        else: self.chose_one()
            
    def next_fetch(self, data):
        for i in range(10):
            if self.aborte is True:
                print("Aborted")
                self.aborte = False
                break
            print("Trying to get cover: "+str(i))
            try:
                release = musicbrainzngs.get_image_front(data[5][i], int(self.settings.get_string("cover-size")))
                GLib.usleep(1200000)
                print("Cover found")
                break
            except: release = None
        GLib.idle_add(self.sub2._yr_ent.set_value, data[3])
        GLib.idle_add(self.sub2._ar_ent.set_text, data[0])
        GLib.idle_add(self.sub2._al_ent.set_text, data[4])
        GLib.idle_add(self.sub2._ti_ent.set_text, data[1])
        if release is not None: GLib.idle_add(self.load_cover, "brainz", release)
        GLib.idle_add(self.sub2._mag_spin.stop)
        self.toast_templ.set_title(self._('Metadata Fetched Successfully'))
        self.sub2._sub2_toast.add_toast(self.toast_templ)

    def del_cur(self, *_):
        print(self.playlist[self.ednum])
        try: self.popover.unparent()
        except: print("no unparent")
        torem = self.playlist[self.ednum]["widget"]
        GLib.idle_add(self.window._main_stack._sup_box.remove, torem)
        self.playlist.remove(self.playlist[self.ednum])
        for i, item in enumerate(self.playlist):
            item["widget"].set_name(f"trackbox_{i}")
        self.visnum = 0
        for i, item in enumerate(self.playlist):
            if item["hidden"] is False and i<self.tnum: self.visnum += 1
        if self.tnum == self.ednum: self.play()

    def next_cur(self, *_):
        print(self.playlist[self.ednum])
        try: self.popover.unparent()
        except: print("no unparent")
        self.reorderer(self.ednum, self.tnum+1, True)

    def on_next(self, arg):
        self.toolClass.stopKar = True
        if self.nowIn == self.useMode or "clickMode" in arg:
            if self.nowIn == "audio" or "clickMode" in arg:
                if "clickMode" not in arg:
                    self.tnum += 1
                    if self.tnum >= len(self.playlist): self.tnum = 0
                    while self.playlist[self.tnum]["hidden"] is True:
                        self.tnum += 1
                        if self.tnum >= len(self.playlist): self.tnum = 0
                elif arg == "clickMode0": self.tnum = 0
                self.play()
                if self.sub.get_visible(): self.on_karaoke_activate("xy")
                if self.useMode == "audio" and arg != "clickMode" and self.settings.get_boolean("autoscroll") is True and self.settings.get_boolean("minimal-mode") is False:
                    try: self.adj.set_value(self.visnum*79-self.settings.get_int("positioning"))
                    except: print("nah")
            elif self.nowIn == "video":
                self.seeking = True
                self.resete2 = time()
                GLib.idle_add(self.window._slider.set_value, self.window._slider.get_value() + 10)

    def load_cover(self, mode="", bitMage=""):
        uuid = None
        if mode == "mpris":
            self.binary = MediaFile(self.playlist[self.tnum]["uri"]).art
            if not self.binary: return ""
            else:
                uuid = hashlib.md5(GLib.path_get_basename(self.url).encode()).hexdigest()
                tmpLoc = f"{self.cacheDir}/hbud/mpris_thumbnail_{uuid}.jpg"
                if not os.path.isfile(tmpLoc):
                    f = open(tmpLoc, "wb")
                    f.write(self.binary)
                    f.close()
                return f"file://{tmpLoc}"
        else:
            if mode == "meta": self.binary = MediaFile(self.editingFile).art
            elif mode == "brainz": self.binary = bitMage
            else:
                uuid = hashlib.md5(GLib.path_get_basename(mode.replace("file://", "")).encode()).hexdigest()
                self.binary = MediaFile(mode.replace('file://', '')).art
            if not self.binary:
                if mode == "meta" or mode == "brainz":
                    GLib.idle_add(self.sub2._meta_cover.set_from_icon_name, "emblem-music-symbolic")
                else:
                    GLib.idle_add(bitMage.set_from_icon_name, "emblem-music-symbolic")
            else:
                if uuid is not None: tmpLoc = f"{self.cacheDir}/hbud/cached_{uuid}.jpg"
                else: tmpLoc = f"{self.cacheDir}/hbud/cacheCover.jpg"
                if not os.path.isfile(tmpLoc) or "cacheCover" in tmpLoc:
                    f = open(tmpLoc, "wb")
                    f.write(self.binary)
                    f.close()
                if mode == "meta" or mode == "brainz":
                    coverBuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(tmpLoc, 100, 100, True)
                    GLib.idle_add(self.sub2._meta_cover.set_from_pixbuf, coverBuf)
                else:
                    coverBuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(tmpLoc, 65, 65, True)
                    GLib.idle_add(bitMage.set_from_pixbuf, coverBuf)

    def on_prev(self, _):
        self.toolClass.stopKar = True
        if self.nowIn == self.useMode:
            if self.nowIn == "audio":
                self.tnum -= 1
                if self.tnum < 0: self.tnum = len(self.playlist)-1
                while self.playlist[self.tnum]["hidden"] is True:
                    self.tnum -= 1
                    if self.tnum < 0: self.tnum = len(self.playlist)-1
                try:
                    self.pause()
                    self.stop()
                except: print("No playbin yet to stop.")
                self.play()
                if self.sub.get_visible(): self.on_karaoke_activate("xy")
                if self.useMode == "audio" and self.settings.get_boolean("autoscroll") is True and self.settings.get_boolean("minimal-mode") is False:
                    try: self.adj.set_value(self.visnum*79-self.settings.get_int("positioning"))
                    except: print("nah")
            elif self.nowIn == "video":
                self.seeking = True
                self.resete2 = time()
                GLib.idle_add(self.window._slider.set_value, self.window._slider.get_value() - 10)

    def stop(self, arg=False):
        print("Stop")
        self.player.set_state(Gst.State.PAUSED)
        if self.nowIn == "audio": self.audioPipe = self.player
        elif self.nowIn == "video": self.videoPipe = self.player
        self.playing = False
        if self.settings.get_boolean("minimal-mode") is True: self.window._label.set_text("00:00")
        else: self.window._label.set_text("0:00:00")
        GLib.idle_add(self.window._play_but.set_icon_name, "media-playback-start")
        self.window._slider.set_value(0)
        if arg is False:
            self.res = False
            self.player.set_state(Gst.State.NULL)

    def pause(self, *_): 
        print("Pause")
        self.playing = False
        try:
            GLib.idle_add(self.window._play_but.set_icon_name, "media-playback-start")
            self.player.set_state(Gst.State.PAUSED)
        except: print("Pause exception")
    
    def resume(self):
        print("Resume")
        print(self.res)
        self.playing = True
        self.player.set_state(Gst.State.PLAYING)
        GLib.idle_add(self.window._play_but.set_icon_name, "media-playback-pause")
        GLib.timeout_add(500, self.updateSlider)
        GLib.timeout_add(40, self.updatePos)

    def on_slider_grab(self, *_): self.seeking = True
    
    def on_slider_grabbed(self, *_):
        current_time = str(timedelta(seconds=round(self.window._slider.get_value())))
        GLib.idle_add(self.window._slider.set_tooltip_text, f"{current_time}")


    def on_slider_seek(self, *_):
        if self.useMode == self.nowIn:
            seek_time_secs = self.window._slider.get_value()
            if seek_time_secs < self.toolClass.position: self.toolClass.seekBack = True
            self.player.seek_simple(Gst.Format.TIME,  Gst.SeekFlags.FLUSH | Gst.SeekFlags.FLUSH, seek_time_secs * Gst.SECOND)
            self.toolClass.position = seek_time_secs
            GLib.idle_add(self.updateSlider, True)
        self.seeking = False

    def updatePos(self):
        if self.playing is False: return False
        try:
            position_nanosecs = self.player.query_position(Gst.Format.TIME)[1]
            self.toolClass.position = float(position_nanosecs) / Gst.SECOND
        except Exception as e:
            print (f'WP: {e}')
            pass
        return True

    def updateSlider(self, static=False):
        if self.playing is False and static is False: return False
        try:
            if self.duration_nanosecs == -1: return True
            self.remaining = float(self.duration_nanosecs) / Gst.SECOND - self.toolClass.position
            if self.seeking is False and static is False:
                self.window._slider.set_value(self.toolClass.position)
            fvalue, svalue = str(timedelta(seconds=round(self.toolClass.position))), str(timedelta(seconds=int(self.remaining)))
            if self.settings.get_boolean("minimal-mode") is True: fvalue, svalue = ":".join(fvalue.split(":")[1:]), ":".join(svalue.split(":")[1:])
            if self.fulle is False:
                self.window._label.set_text(fvalue)
                self.window._label_end.set_text(svalue)
            else:
                self.window._main_stack._overlay_time.set_text(f"{fvalue} / {svalue}")
        except Exception as e:
            print (f'WS: {e}')
            pass
        return not static

    def on_shuffBut_clicked(self, *_):
        try:
            playlistLoc = sample(self.playlist, len(self.playlist))
            self.playlist, self.tnum = playlistLoc, 0
            widList = self.neo_playlist_gen("shuff_2nd_stage")
            for i in widList:
                GLib.idle_add(self.window._main_stack._sup_box.append, i)
            self.on_next('clickMode0')
        except: print("shuffle pass")

    def extract_sub(self, videofile, subtitles):
        out = subprocess.run(['ffprobe','-of','json','-show_entries', 'format:stream', videofile], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        results = json.loads(out.stdout)
        for stream in results['streams']:
            if stream['codec_type'] == 'subtitle':
                data = {}
                data["index"]="0:{}".format(stream['index'])
                try: data["lang"]=stream['tags']['language']
                except: data["lang"]="unknown"
                subtitles.append(data)
        print(subtitles)
        for i in subtitles.copy():
            out = subprocess.run(['ffmpeg','-i',videofile, '-map', i['index'], '-f','srt','-'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            i["content"] = out.stdout
        self.subtitle_dict = subtitles
        return

    def subdone(self, args, misc=False):
        if misc is False:
            data = self.local_sub(Gst.uri_get_location(self.uri))
            if data is not None: self.subtitle_dict.append({"index" : "none", "lang" : "local", "content" : data})
        else:
            print(args)
            with open (args, 'r') as subfile: data = subfile.read()
            self.subtitle_dict.append({"index" : "none", "lang" : "local", "content" : data})
        popbox = Gtk.Box.new(1, 2)
        if len(self.subtitle_dict) >= 1:
            check0 = Gtk.CheckButton.new_with_label(self._("Empty"))
            check0.set_name("subno_empty")
            check0.connect("toggled", self.sub_toggle)
            for e, element in enumerate(self.subtitle_dict):
                if element["lang"] == "unknown": check = Gtk.CheckButton.new_with_label(self._("Unknown"))
                elif element["lang"] == "local": check = Gtk.CheckButton.new_with_label(self._("Local"))
                else: check = Gtk.CheckButton.new_with_label(Locale(element["lang"]).getDisplayLanguage(Locale(element["lang"])))
                check.set_group(check0)
                check.set_name("subno_{}".format(e))
                check.connect("toggled", self.sub_toggle)
                popbox.append(check)
            popbox.append(check0)
            check0.set_active(True)
        else:
            popbox.append(Gtk.Label.new(self._("No Subtitles Found")))
            popbox.append(Gtk.Label.new(self._("Visit OpenSubtitles or Subscene")))
        GLib.idle_add(self.window._sub_track.get_popover().set_child, popbox)
        GLib.idle_add(self.window._sub_track.set_sensitive, True)

    def sub_toggle(self, button):
        btn = button.get_name().replace("subno_", "")
        if btn == "empty": self.needSub = False
        else:
            presub = self.subtitle_dict[int(btn)]["content"]
            subtitle_gen = srt.parse(presub)
            subtitle = list(subtitle_gen)
            self.needSub = True
            subs = futures.ThreadPoolExecutor(max_workers=2)
            subs.submit(self.subShow, subtitle)

    def subtitle_search_on_play(self):
        GLib.idle_add(self.window._sub_track.set_sensitive, False)
        self.subtitle_dict = []
        subber = futures.ThreadPoolExecutor(max_workers=4)
        submitted = subber.submit(self.extract_sub, Gst.uri_get_location(self.uri), [])
        submitted.add_done_callback(self.subdone)

    def local_sub(self, videofile):
        filename = GLib.path_get_basename(videofile)
        try: neo_tmpdbnow = os.listdir(videofile.replace(filename, "")+"misc/")
        except: neo_tmpdbnow = []
        tmpdbnow = os.listdir(videofile.replace(filename, ""))
        if os.path.splitext(filename)[0]+".srt" in tmpdbnow or os.path.splitext(filename)[0]+".srt" in neo_tmpdbnow:
            print("Subtitle found!")
            srfile = os.path.splitext(videofile)[0]+".srt"
            neo_srfile = videofile.replace(filename, "")+"misc/"+os.path.splitext(filename)[0]+".srt"
            print(srfile, neo_srfile)
            try:
                with open (srfile, 'r') as subfile: presub = subfile.read()
            except:
                with open (neo_srfile, 'r') as subfile: presub = subfile.read()
            return presub
        else: return None

    def play(self, misc=""):
        if "/" in misc:
            self.url, self.nowIn, self.player = "file://"+misc, "video", self.videoPipe
        elif self.clickedE is not False and self.useMode == "video":
            self.url, self.nowIn, self.player = self.clickedE[0].get_path(), "video", self.videoPipe
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
        self.res, self.playing, self.toolClass.position = True, True, 0
        if self.useMode == "audio":
            self.title = self.playlist[self.tnum]["title"]
            if self.settings.get_boolean("minimal-mode") is True:
                self.window._main_stack._rd_title.set_text(self.playlist[self.tnum]["title"])
                self.window._main_stack._rd_artist.set_text(self.playlist[self.tnum]["artist"])
                self.window._main_stack._rd_year.set_text(str(self.playlist[self.tnum]["year"]))
            else: self.toolClass.themer(self.provider, self.window, self.color, self.tnum)
        if misc != "continue":
            self.player.set_state(Gst.State.NULL)
            self.player.set_property("uri", Gst.filename_to_uri(self.url.replace("file://", "")))
        self.player.set_state(Gst.State.PLAYING)
        self.uri = self.player.get_property("uri")
        GLib.idle_add(self.window._play_but.set_icon_name, "media-playback-pause")
        GLib.timeout_add(500, self.updateSlider)
        GLib.timeout_add(40, self.updatePos)
        if self.nowIn == "video" and misc != "continue": self.subtitle_search_on_play()
        self.mpris_adapter.emit_all()
        self.mpris_adapter.on_playback()
        GLib.idle_add(self.ranger)

    def ranger(self):
        while True:
            GLib.usleep(20000)
            try:
                self.duration_nanosecs = self.player.query_duration(Gst.Format.TIME)[1]
                if self.duration_nanosecs == -1: raise Exception
                GLib.idle_add(self.window._slider.set_range, 0, float(self.duration_nanosecs) / Gst.SECOND)
                break
            except: pass

    def on_playBut_clicked(self, button, *_):
        if self.window._play_but.is_visible() is False and self.window._main_stack._video_picture.is_visible() is False: return
        if self.useMode == "audio" and self.nowIn != "video" and self.settings.get_boolean("autoscroll") is True and self.settings.get_boolean("minimal-mode") is False and self.player.get_state(1)[1] is not Gst.State.NULL:
            self.visnum = 0
            for i, item in enumerate(self.playlist):
                if item["hidden"] is False and i<self.tnum: self.visnum += 1
            try: self.adj.set_value(self.visnum*79-self.settings.get_int("positioning"))
            except: pass
        if self.nowIn == self.useMode or self.nowIn == "" or "/" in str(button):
            if self.playing is False:
                if self.res is False or "/" in str(button):
                    try: self.play(button)
                    except Exception as e: print (f'WSP: {e}')
                else: self.resume()
            else: self.pause()
        else: self.play("continue")
        self.mpris_adapter.on_playpause()

    def on_main_delete_event(self, _):
        print("Quitting...")
        self.toolClass.stopKar, self.hardReset, self.needSub, self.hardreset2 = True, True, False, True
        raise SystemExit

    def reorderer(self, src, dst, misc=False):
        if self.sorted is True or self.searched is True: return
        else:
            srcBox = self.playlist[src]["widget"]
            playlistLoc, cutList = self.playlist, []
            if dst < src:
                [cutList.append(playlistLoc[i]) for i in range(dst, src+1)]
                rby, corrector = 1, dst
            elif dst > src:
                if misc is False: [cutList.append(playlistLoc[i]) for i in range(src, dst+1)]
                else: [cutList.append(playlistLoc[i]) for i in range(src, dst)]
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
        if self.useMode == self.nowIn and self.useMode == "video":
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
                if keyval == 102 and self.settings.get_boolean("minimal-mode") is False and self.useMode == "audio":
                    self.on_dropped("key") # F
                elif keyval == 111: self.on_openFolderBut_clicked(None) # O
                elif keyval == 65289: # Tab
                    if self.useMode == "video": self.window._loc_but.set_active(True)
                    else: self.window._str_but.set_active(True)
            elif keyval == 32 and self.url: self.on_playBut_clicked(0) # Space
            elif keyval == 65480:
                if self.useMode == "video": self.on_karaoke_activate(0) # F11
            elif keyval == 65363: self.on_next("") # Right
            elif keyval == 65361: self.on_prev("") # Left
            elif keyval == 65535 and self.useMode == "audio" and self.settings.get_boolean("minimal-mode") is False: # Delete
                self.ednum = self.tnum
                self.del_cur()
            elif keyval == 65362 and self.useMode == "audio" and self.settings.get_boolean("minimal-mode") is False: # Up
                if self.tnum-1 < 0: self.reorderer(self.tnum, len(self.playlist)-1)
                else: self.reorderer(self.tnum, self.tnum-1)
            elif keyval == 65364 and self.useMode == "audio" and self.settings.get_boolean("minimal-mode") is False: # Down
                if self.tnum+1 > len(self.playlist)-1: self.reorderer(self.tnum, 0)
                else: self.reorderer(self.tnum, self.tnum+1)
        except: print("No key local")

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
            try:
                if emitter == self.window:
                    if self.needSub is True:
                        self.size3, self.size4 = self.settings.get_int("relative-size")*y, float("0.0{}".format(self.settings.get_int("relative-margin")))*y
                else: self.toolClass.size, self.toolClass.size2 = 50*x, 21.4285714*x
            except: return
        elif param.name == "maximized":
            sizThread = futures.ThreadPoolExecutor(max_workers=1)
            sizThread.submit(self.different_resize, emitter)
        elif param.name == "fullscreened":
            self.fulle = self.window.is_fullscreen()
            if self.fulle is True:
                GLib.idle_add(self.switch_popover, self.window._sub_track, self.window._main_stack._overlay_subs)
                GLib.idle_add(self.window._main_stack._overlay_time.set_text, "{} / {}".format(self.window._label.get_text(), self.window._label_end.get_text()))
                self.window._head_reveal.set_reveal_child(False)
            else:
                GLib.idle_add(self.switch_popover, self.window._main_stack._overlay_subs, self.window._sub_track)
                GLib.idle_add(self.window._label.set_text, self.window._main_stack._overlay_time.get_text().split(" / ")[0])
                GLib.idle_add(self.window._label_end.set_text, self.window._main_stack._overlay_time.get_text().split(" / ")[1])
                self.window._head_reveal.set_reveal_child(True)
            sizThread = futures.ThreadPoolExecutor(max_workers=1)
            sizThread.submit(self.different_resize, emitter)

    def switch_popover(self, a, b):
        popover = a.get_popover()
        widget = popover.get_child()
        popover.set_child()
        b.get_popover().set_child(widget)
        del popover, widget

    def different_resize(self, emitter):
        GLib.usleep(300000)
        x, y = emitter.get_size(Gtk.Orientation.HORIZONTAL), emitter.get_size(Gtk.Orientation.VERTICAL)
        if emitter == self.window: self.size3, self.size4 = self.settings.get_int("relative-size")*y, float("0.0{}".format(self.settings.get_int("relative-margin")))*y
        else: self.toolClass.size, self.toolClass.size2 = 50*x, 21.4285714*x

    def on_off_but_clicked(self, _):
        self.sub._off_spin.update()
        self.toolClass.offset = int(self.sub._off_spin.get_value())
        f = MediaFile(self.playlist[self.tnum]["uri"])
        f.offset = self.toolClass.offset
        f.save()
        self.sub.set_focus(None)

    def on_correct_lyr(self, _):
        f = MediaFile(self.playlist[self.tnum]["uri"])
        f.lyrics = self.tmp_lyric
        f.save()
        GLib.idle_add(self.sub._sub_stackhead.hide)
    
    def on_wrong_lyr(self, _): self.on_karaoke_activate()

    def on_karaoke_activate(self, *_):
        if self.useMode == "audio" and self.nowIn == "audio":
            if self.playing is True or self.res is True:
                print('Karaoke')
                self.toolClass.stopKar = False
                track = self.playlist[self.tnum]["title"]
                try:
                    artist = self.playlist[self.tnum]["artist"].split("/")[0]
                    if artist == "AC": artist = self.playlist[self.tnum]["artist"]
                except: artist = self.playlist[self.tnum]["artist"]
                dbnow, neo_dbnow = [], []
                tmpdbnow = os.listdir(self.folderPath)
                try: neo_tmpdbnow = os.listdir(self.folderPath+"/misc/")
                except: neo_tmpdbnow = []
                for i in tmpdbnow:
                    if ".srt" in i or ".txt" in i:
                        dbnow.append(f"{self.folderPath}/{i}")
                for i in neo_tmpdbnow:
                    if ".srt" in i or ".txt" in i:
                        neo_dbnow.append(f"{self.folderPath}/misc/{i}")
                self.sub.set_title(f'{track} - {artist}')
                tmp = os.path.splitext(self.playlist[self.tnum]["uri"])[0]
                neo_tmp = os.path.splitext(GLib.path_get_basename(self.playlist[self.tnum]["uri"]))[0]
                if f"{tmp}.srt" not in dbnow and f"{self.folderPath}/misc/{neo_tmp}.srt" not in neo_dbnow:
                    GLib.idle_add(self.sub._off_but.hide)
                    GLib.idle_add(self.sub._off_lab.hide)
                    GLib.idle_add(self.sub._off_spin.hide)
                    if f"{tmp}.txt" in dbnow or f"{self.folderPath}/misc/{neo_tmp}.txt" in neo_dbnow:
                        try: f = open(f"{tmp}.txt", "r")
                        except: f = open(f"{self.folderPath}/misc/{neo_tmp}.txt", "r")
                        lyric = f.read()
                        f.close()
                        self.sub._lyr_lab.set_label(lyric)
                        self.sub._sub_stack.set_visible_child(self.sub._lyr_lab.get_parent().get_parent())
                        self.sub.present()
                        GLib.idle_add(self.sub._sub_stackhead.hide)
                    else:
                        try:
                            f = MediaFile(self.playlist[self.tnum]["uri"])
                            lyric = f.lyrics
                            print(lyric)
                            if lyric != "":
                                self.sub._lyr_lab.set_label(lyric)
                                self.sub._sub_stack.set_visible_child(self.sub._lyr_lab.get_parent().get_parent())
                                self.sub.present()
                                GLib.idle_add(self.sub._sub_stackhead.hide)
                            else: raise Exception
                        except:
                            self.sub._sub_stackhead.set_visible_child(self.sub._sub_box2)
                            GLib.idle_add(self.sub._sub_stackhead.show)
                            thread = futures.ThreadPoolExecutor(max_workers=2)
                            thread.submit(self.lyr_fetcher, artist, track)
                else:
                    GLib.idle_add(self.sub._off_but.show)
                    GLib.idle_add(self.sub._off_lab.show)
                    GLib.idle_add(self.sub._off_spin.show)
                    f = MediaFile(self.playlist[self.tnum]["uri"])
                    try:
                        field = MediaField(MP3DescStorageStyle(u'offset'), StorageStyle(u'offset'))
                        f.add_field(u'offset', field)
                    except: pass
                    if f.offset is None: f.offset = 0
                    self.toolClass.offset = int(f.offset)
                    GLib.idle_add(self.sub._off_spin.set_value, self.toolClass.offset)
                    f.save()
                    print("FOUND")
                    try:
                        with open (f"{tmp}.srt", "r") as subfile: presub = subfile.read()
                    except:
                        with open (f"{self.folderPath}/misc/{neo_tmp}.srt", "r") as subfile: presub = subfile.read()
                    subtitle_gen = srt.parse(presub)
                    subtitle, lyrs = list(subtitle_gen), futures.ThreadPoolExecutor(max_workers=2)
                    lyrs.submit(self.toolClass.slideShow, subtitle)
                    self.sub._sub_stack.set_visible_child(self.sub._label1.get_parent().get_parent().get_parent())
                    self.sub._sub_stackhead.set_visible_child(self.sub._sub_box)
                    GLib.idle_add(self.sub._sub_stackhead.show)
                    self.sub.present()
        elif self.useMode == "video":
            if self.fulle is False:
                self.window.fullscreen()
                self.window._main_stack._overlay_revealer.set_reveal_child(True)
                self.revealed = True
                GLib.timeout_add(500, self.displayclock)
                self.window._main_stack._overlay_hub.set_reveal_child(True)
                ld_clock = futures.ThreadPoolExecutor(max_workers=1)
                ld_clock.submit(self.clock, "full")
            else:
                self.resete, self.keepReset = False, False
                self.window.unfullscreen()
                self.window._main_stack._overlay_revealer.set_reveal_child(False)
                self.window._main_stack._overlay_hub.set_reveal_child(False)
                self.revealed = False
                self.countermove = 0
                GLib.timeout_add(2000, self.mouse_eraser)
                self.window.set_cursor(self.def_cur)

    def lyr_fetcher(self, artist, track):
        print("Fetcher...")
        GLib.idle_add(self.window._lyr_stack.set_visible_child, self.window._lyr_spin)
        GLib.idle_add(self.window._lyr_spin.start)
        lyric = None
        if self.settings.get_boolean("musixmatch") is True and self.lyr_states[0] is True:
            print("musix")
            lyric, self.lyr_states = musixapi.get_lyric(artist, track), [False, True, True]
        if self.settings.get_boolean("letrasbr") is True and lyric is None and self.lyr_states[1] is True:
            print("letras")
            lyric, self.lyr_states = letrasapi.get_lyric(artist, track), [False, False, True]
        if self.settings.get_boolean("azlyrics") is True and lyric is None and self.lyr_states[2] is True:
            print("AZ")
            lyric, self.lyr_states = self.toolClass.get_lyric(track, artist, self.DAPI), [False, False, False]
        print("end")
        GLib.idle_add(self.window._lyr_stack.set_visible_child, self.window._karaoke_but)
        if lyric == 0:
            self.toast_templ.set_title(self._('Could Not Fetch Lyrics for the Current Track.\nPlease Provide it Manually.'))
            self.window._main_toast.add_toast(self.toast_templ)
            self.lyr_states = [True, True, True]
        else:
            self.tmp_lyric = lyric
            GLib.idle_add(self.sub._lyr_lab.set_label, lyric)
            GLib.idle_add(self.sub._sub_stack.set_visible_child, self.sub._lyr_lab.get_parent().get_parent())
            GLib.idle_add(self.sub.present)

    def mouse_enter(self, *_):
        if self.fulle is True: self.keepReset = True
    
    def mouse_leave(self, *_):
        if self.fulle is True: self.keepReset = False
    
    def mage(self):
        self.window._main_stack._overlay_revealer.set_reveal_child(True)
        self.revealed = True
        GLib.timeout_add(500, self.displayclock)
        self.window._main_stack._overlay_hub.set_reveal_child(True)
        self.window.set_cursor(self.def_cur)

    def mouse_eraser(self):
        self.countermove = 0
        return not self.revealed

    def mouse_moving(self, _, x, y):
        if self.fulle is True:
            if self.mx != x and self.my != y and self.revealed is False:
                self.mx, self.my = x, y
                self.countermove += 1
            elif self.revealed is True and self.mx != x and self.my != y:
                self.mx, self.my = x, y
                self.resete = True
            if self.countermove >= 3:
                self.countermove = 0
                self.resete = True
                if self.revealed is False:
                    self.mage()
                    ld_clock = futures.ThreadPoolExecutor(max_workers=1)
                    ld_clock.submit(self.clock, "full")

    def displayclock(self):
        datetimenow = GLib.DateTime.new_now_local().format('%H:%M')
        self.window._main_stack._current_time.set_label(datetimenow)
        endtime = GLib.DateTime.new_now_local().add_seconds(self.remaining).format('%H:%M')
        self.window._main_stack._end_time.set_label(self._(f"Ends At: {endtime}"))
        return self.revealed

    def clock(self, ltype):
        start = time()
        if ltype == "full":
            while time() - start < 2:
                if self.hardReset is True: return
                if self.keepReset is True: start = time()
                elif self.resete is True: start, self.resete = time(), False    
                GLib.usleep(20000)
            if self.fulle is True:
                print("Reveal?")
                self.window.set_cursor(self.blank_cur)
                self.window._main_stack._overlay_revealer.set_reveal_child(False)
                self.window._main_stack._overlay_hub.set_reveal_child(False)
                self.revealed = False
                self.countermove = 0
                GLib.timeout_add(2000, self.mouse_eraser)
        elif ltype == "seek":
            while time() - start < 0.3:
                if self.hardreset2 is True: return
                start = self.resete2
                GLib.usleep(1000)
            self.on_slider_seek()
            self.clocking = False

    def subShow(self, subtitle):
        while self.needSub is True:
            GLib.usleep(1000)
            for line in subtitle:
                if self.toolClass.position >= line.start.total_seconds() and self.toolClass.position <= line.end.total_seconds():
                    if self.settings.get_boolean("dark-background") is True: GLib.idle_add(self.window._main_stack._subtitles.set_markup, f"<span size='{int(self.size3)}' color='white' background='black'>{line.content}</span>")
                    else: GLib.idle_add(self.window._main_stack._subtitles.set_markup, f"<span size='{int(self.size3)}' color='white'>{line.content}</span>")
                    self.window._main_stack._subtitles.set_margin_bottom(self.size4)
                    GLib.idle_add(self.window._main_stack._subtitles.show)
                    while self.needSub is True and self.toolClass.position <= line.end.total_seconds() and self.toolClass.position >= line.start.total_seconds():
                        GLib.usleep(1000)
                        pass
                    GLib.idle_add(self.window._main_stack._subtitles.hide)
                    GLib.idle_add(self.window._main_stack._subtitles.set_label, "")

    def special_settings(self, obj, key=None):
        if key == "hwa-enabled": self.hwa_change()
        elif key == "opacity":
            self.toolClass.o = obj.get_int(key)/10
            self.toolClass.themer(self.provider, self.window, self.color, self.tnum)
        elif key == "minimal-mode":
            if obj.get_boolean(key) is False:
                GLib.idle_add(self.window._head_box.show)
                GLib.idle_add(self.window._toggle_pane_button.show)
                GLib.idle_add(self.window._main_stack.set_visible_child, self.window._main_stack._side_flap)
                GLib.idle_add(self.window.set_default_size, 600, 450)
                GLib.idle_add(self.window._label_end.show)
                GLib.idle_add(self.window._drop_but.show)
                self.window.set_resizable(True)
                if self.playlist is not None:
                    widList = self.neo_playlist_gen()
                    for i in widList:
                        GLib.idle_add(self.window._main_stack._sup_box.append, i)
            else:
                GLib.idle_add(self.window._head_box.hide)
                GLib.idle_add(self.window._toggle_pane_button.hide)
                self.window._loc_but.set_active(True)
                GLib.idle_add(self.window._main_stack.set_visible_child, self.window._main_stack._rd_box)
                GLib.idle_add(self.window.set_default_size, 1, 1)
                GLib.idle_add(self.window._label_end.hide)
                GLib.idle_add(self.window._drop_but.hide)
                try:
                    GLib.idle_add(self.window._main_stack._rd_title.set_text, self.playlist[self.tnum]["title"])
                    GLib.idle_add(self.window._main_stack._rd_artist.set_text, self.playlist[self.tnum]["artist"])
                    GLib.idle_add(self.window._main_stack._rd_year.set_text, str(self.playlist[self.tnum]["year"]))
                except: pass
                self.window.set_resizable(False)
            GLib.idle_add(self.on_pref_close)
            GLib.idle_add(self.window.hide)
            GLib.idle_add(self.window.present)
        elif key == "theme":
            self.theme = self.themeDict[obj.get_string("theme")]
            self.styles.set_color_scheme(self.theme)
        elif key is None:
            self.color = obj.get_rgba().to_string()
            self.settings.set_string("color", self.color)
            self.toolClass.themer(self.provider, self.window, self.color, self.tnum)

    def hwa_change(self):
        if self.settings.get_boolean("hwa-enabled") is True:
            filt = Gst.ELEMENT_FACTORY_TYPE_DECODER
            filt |= Gst.ELEMENT_FACTORY_TYPE_MEDIA_VIDEO
            factories = Gst.ElementFactory.list_get_elements(filt, Gst.Rank.MARGINAL)
            factories = sorted(factories, key=lambda f: f.get_rank(), reverse=True)
            max_rank_element = factories[0]
            target_rank = max_rank_element.get_rank() + 1
        else: target_rank = 0
        for element in self.prefwin.present_codecs:
            target_element = self.prefwin.present_codecs[element][0]
            if target_element is not None:
                target_element.set_rank(target_rank)
                print("Rank of target plugin:", target_element.get_name(), "(", target_element.get_rank(), ")")
            else: print("Element {} is not present.".format(element))

    def on_hide(self, *_):
        self.toolClass.stopKar = True
        self.lyr_states = [True, True, True]
        self.sub.hide()

def run():
    app = Main()
    frontend.app = app
    app.run(sys.argv)