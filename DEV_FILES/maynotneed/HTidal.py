#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time, gettext, locale, gi, subprocess, re, sys, os, threading, urllib, srt, datetime, webbrowser, random, requests, dbus, dbus.mainloop.glib, dbus.service
# from configparser import ConfigParser
from concurrent import futures
gi.require_version('Gtk', '3.0')
gi.require_version('Gst', '1.0')
from gi.repository import Gtk, Gst, GLib, Gio, GdkPixbuf, Gdk
# from getpass import getpass
from mediafile import MediaFile
import numpy as np
from PIL import Image, ImageDraw

class GUI:
    def __init__(self):
        # Prepare to use builder
        print('Init here')
        self.builder = Gtk.Builder()
        self.builder.set_translation_domain(APP)
        # Import the glade file
        self.builder.add_from_file(UI_FILE)
        # Connect all signals
        self.builder.connect_signals(self)
        self.boxWait = self.builder.get_object('boxForWait')
        self.boxNo = self.builder.get_object('boxForNo')
        self.boxText = self.builder.get_object('boxForText')
        self.subStack = self.builder.get_object('subStack')
        self.sub = self.builder.get_object('sub')
        self.seekBack = False
        self.playlist = []
        self.allPlaylist = ''
        self.expanded = False
        self.position = 0
        self.adding = False
        self.multiTracks = True
        self.x = 0
        self.inFav = False
        self.fLab = self.builder.get_object("infoBut")
        self.relPos = 0
        self.tnum = 0
        self.query = {}
        self.playing = False
        self.res = False
        self.all = False
        self.playlistPlayer = False
        self.albume = False
        self.globSeek = True
        self.treeType = ""
        self.rem = self.builder.get_object("remember")
        self.trackCover = self.builder.get_object("cover")
        self.alb_cover = self.builder.get_object("album_img")
        self.plaicon = self.builder.get_object("play")
        self.playbut = self.builder.get_object("playBut")
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
        self.box.pack_start(self.label, False, False, 0)
        self.boxMore = self.builder.get_object("more_box")
        # Dload
        self.dlStack = self.builder.get_object("dlStack")
        self.dlWin = self.builder.get_object("dlWin")
        self.whLab = self.builder.get_object("whDlLab")
        self.whLab1 = self.builder.get_object("whDlLab1")
        self.dlBar = self.builder.get_object("dlBar")
        self.dlBox1 = self.builder.get_object("dlBox1")
        self.dlBox = self.builder.get_object("dlBox")
        # Spotlight
        self.namer = self.builder.get_object("name")
        self.dat_role = self.builder.get_object("date_role")
        self.topOrNot = self.builder.get_object("track_label")
        self.rels = self.builder.get_object("nam_lab1")
        self.relis = self.builder.get_object("reli1")
        self.exLab = self.builder.get_object("extra_label")
        # Search widgets
        self.boxList = [self.builder.get_object('tracks_box'), self.builder.get_object('artists_box'), self.builder.get_object('albums_box'), self.builder.get_object('playlist_box'), self.builder.get_object('top_box')]
        self.s_label = [self.builder.get_object('top_label'), self.builder.get_object('tracks_label'), self.builder.get_object('artists_label'), self.builder.get_object('albums_label'), self.builder.get_object('playlist_label')]
        # Stores (shopping mall?)
        self.storePlaylist = Gtk.ListStore(str, str, int)
        self.allStore = Gtk.ListStore(str, int)
        self.storeAlbum = Gtk.ListStore(str, str, int)
        # Trees (forest?)
        self.tree = Gtk.TreeView.new_with_model(self.storePlaylist)
        self.tree.set_can_focus(False)
        self.tree.connect("row-activated", self.row_activated)
        self.tree.connect("button_press_event", self.mouse_click)
        self.tree.set_reorderable(True)
        self.allTree = Gtk.TreeView.new_with_model(self.allStore)
        self.allTree.set_can_focus(False)
        self.allTree.connect("row-activated", self.all_row)
        self.allTree.connect("button_press_event", self.mouse_click)
        self.albumTree = Gtk.TreeView.new_with_model(self.storeAlbum)
        self.albumTree.set_can_focus(False)
        self.albumTree.connect("row-activated", self.album_row)
        self.albumTree.connect("button_press_event", self.mouse_click)
        # Scrolls (idk)
        self.playlistBox = self.builder.get_object("expanded")
        self.scrollable_treelist = Gtk.ScrolledWindow()
        self.scrollable_treelist.set_can_focus(False)
        self.scrollable_treelist.set_vexpand(True)
        self.scrollable_treelist.add(self.tree)
        self.playlistBox.pack_start(self.scrollable_treelist, True, True, 0)
        self.allBox = self.builder.get_object("big")
        self.allScroll = Gtk.ScrolledWindow()
        self.allScroll.set_can_focus(False)
        self.allScroll.set_vexpand(True)
        self.allScroll.add(self.allTree)
        self.allBox.pack_start(self.allScroll, True, True, 0)
        self.albumBox = self.builder.get_object("general_top")
        self.album_scroll = Gtk.ScrolledWindow()
        self.album_scroll.set_can_focus(False)
        self.album_scroll.set_vexpand(True)
        self.albumTree.set_vexpand(True)
        self.album_scroll.add(self.albumTree)
        self.albumBox.pack_end(self.album_scroll, True, True, 0)
        # END
        self.bigStack = self.builder.get_object("bigStack")
        self.emailEntry = self.builder.get_object("email")
        self.pwdEntry = self.builder.get_object("pwd")
        self.player = Gst.ElementFactory.make("playbin", "player")
        fakesink = Gst.ElementFactory.make("fakesink", "fakesink")
        self.player.set_property("video-sink", fakesink)
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)
        # Get the main stack object
        global stack
        stack = self.builder.get_object('stack')
        global window
        window = self.builder.get_object(
            'main')
        if os.geteuid() == 0:
            # Indicate if runnung as root or not
            window.set_title(version+' (as superuser)')
        else:
            window.set_title(version)
        window.connect('size-allocate', self._on_size_allocated)
        # Display the program
        window.show_all()
        for i in self.s_label:
            i.hide()
        self.force = False
        tC = futures.ThreadPoolExecutor(max_workers=4)
        tC.submit(self.check)

    def listener(self):
        APP_ID="htidal"
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
        if app == "htidal" and self.url:
            if action == "Play":
                try:
                    self.resume()
                except:
                    print("Resume error")
            elif action == "Pause" or action == "Stop":
                try:
                    self.pause()
                except:
                    print('Pause error')

    def on_req_clicked(self, button):
        webbrowser.open_new_tab("https://github.com/swanux/htidal_db/issues/new?assignees=swanux&labels=enhancement&template=custom.md&title=Lyrics+request")
    
    def on_fb_clicked(self, button):
        webbrowser.open_new_tab("https://swanux.github.io/feedbacks.html")

    def on_main_delete_event(self, window, e):
        # Getting the window position
        x, y = window.get_position()
        # Get the size of the window
        sx, sy = window.get_size()
        dialogWindow = Gtk.MessageDialog(parent=window, modal=True, destroy_with_parent=True, message_type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.YES_NO, text=gg('Do you really would like to exit now?'))
        # set the title
        dialogWindow.set_title(gg("Prompt"))
        dsx, dsy = dialogWindow.get_size()                          # get the dialogs size
        # Move it to the center of the main window
        dialogWindow.move(x+((sx-dsx)/2), y+((sy-dsy)/2))
        dx, dy = dialogWindow.get_position()                        # set the position
        print(dx, dy)
        dialogWindow.show_all()
        res = dialogWindow.run()                                    # save the response
        if res == Gtk.ResponseType.YES:                             # if yes ...
            print('OK pressed')
            dialogWindow.destroy()
            lib.cleanup()
            try:
                self.mainloop.quit()
            except:
                pass
            self.force = True
            self.stopKar = True
            raise SystemExit
        elif res == Gtk.ResponseType.NO:                            # if no ...
            print('No pressed')
            dialogWindow.destroy()                                  # destroy dialog
            return True                                             # end function
        else:
            dialogWindow.destroy()                                  # destroy dialog
            return True                                             # end function
    
    def on_playBut_clicked(self, button):
        if not self.playing:
            if not self.res:
                self.play()
            else:
                self.resume()
        else:
            self.pause()

    def on_key(self, widget, key):
        try:
            if key.keyval == 32 and self.url:
                self.on_playBut_clicked(0)
        except:
            pass

    def on_searchBut_clicked(self, button):
        self.expanded = False
        child = self.builder.get_object("search_box")
        GLib.idle_add(stack.set_visible_child, child)

    def on_searchItem_clicked(self, button):
        btn = Gtk.Buildable.get_name(button)
        print(btn)
        lis = []
        if 's_top' in btn:
            item = self.query['top_hit']
        elif 's_track' in btn:
            for i in reversed(self.query['tracks']):
                lis.append(i)
            item = lis[int(re.findall(r'\d+', btn)[0])]
        elif 's_art' in btn:
            for i in reversed(self.query['artists']):
                lis.append(i)
            item = lis[int(re.findall(r'\d+', btn)[0])]
        elif 's_album' in btn:
            for i in reversed(self.query['albums']):
                lis.append(i)
            item = lis[int(re.findall(r'\d+', btn)[0])]
        elif 's_playl' in btn:
            for i in reversed(self.query['playlists']):
                lis.append(i)
            item = lis[int(re.findall(r'\d+', btn)[0])]
        iType = item["type"]
        print(iType)
        if iType == 'ARTISTS' or iType == 'ARTIST':
            self.artist = item
            self.album = ''
            self.gen_playlist_view(name='album', playlistLoc=self.artist, again=self.albume, allPos='artistLoad')
            self.expanded = False
            stack.set_visible_child(self.builder.get_object('scrollAlbum'))
            self.builder.get_object("dlAlb").hide()
            self.prevSlide = stack.get_visible_child()
            self.cleaner(self.builder.get_object("relateds").get_children())
            tmi = self.assembleFactory("ar-al", "album", self.artist["id"])
            self.query['albums'] = tmi
            self.constructor(self.builder.get_object("relateds"), tmi, 'album', 'album')
            self.builder.get_object("general_bottom").show()
        elif iType == 'ALBUMS' or iType == 'ALBUM' or iType == 'PLAYLISTS' or iType == 'PLAYLIST':
            self.album = item
            self.artist = ''
            if iType == 'ALBUMS' or iType == 'ALBUM':
                self.gen_playlist_view(name='album', playlistLoc=self.album, again=self.albume)
            else:
                self.gen_playlist_view(name='album', playlistLoc=self.album, again=self.albume, allPos='playlistPlease')
            self.expanded = False
            stack.set_visible_child(self.builder.get_object('scrollAlbum'))
            self.builder.get_object("dlAlb").show()
            self.prevSlide = stack.get_visible_child()
            if iType == 'PLAYLISTS' or iType == 'PLAYLIST':
                print('hiding')
                self.builder.get_object("general_bottom").hide()
            else:
                print('showing')
                self.cleaner(self.builder.get_object("relateds").get_children())
                tmi = self.assembleFactory("ar-al", "album", self.album["artId"])
                self.query['albums'] = tmi
                self.constructor(self.builder.get_object("relateds"), tmi, 'album', 'album')
                self.builder.get_object("general_bottom").show()
        elif iType == 'TRACKS' or iType == 'TRACK':
            self.gen_playlist_view(name='playlistPlayer', playlistLoc=item, again=self.playlistPlayer, allPos='radio')

    def backer(self):
        if self.query["top_hit"][0]["type"] == "TRACK":
            self.constructor(self.boxList[4], self.query['top_hit'], 'top', 'track')
        elif self.query["top_hit"][0]["type"] == "ARTIST":
            self.constructor(self.boxList[4], self.query['top_hit'], 'top', 'artist')
        else:
            self.constructor(self.boxList[4], self.query['top_hit'], 'top', 'top')
        self.constructor(self.boxList[0], self.query['tracks'], 'track', 'track')
        self.constructor(self.boxList[1], self.query['artists'], 'artist', 'artist')
        self.constructor(self.boxList[2], self.query['albums'], 'album', 'album')
        self.constructor(self.boxList[3], self.query['playlists'], 'playlist', 'playlist')

    def on_searcher_search_changed(self, widget):
        txt = widget.get_text()
        if txt == '' or txt == None:
            for i in self.s_label:
                i.hide()
            for i in self.boxList:
                self.cleaner(i.get_children())
        else:
            Tquery = lib.get_search(txt.encode("utf-8"), 14)
            self.query = {}
            self.query["artists"] = []
            self.query["albums"] = []
            self.query["playlists"] = []
            self.query["tracks"] = []

            self.query["artists"] = self.assembleFactory("search", "artist", Tquery.artists)
            self.query["albums"] = self.assembleFactory("search", "album", Tquery.albums)
            self.query["playlists"] = self.assembleFactory("search", "playlist", Tquery.playlists)
            self.query["tracks"] = self.assembleFactory("search", "track", Tquery.tracks)
            print(self.query["albums"])
            tht = ffi.string(Tquery.topHitType).decode("utf-8")
            if tht == "ALBUMS":
                self.query["top_hit"] = self.assembleFactory("search", "album", Tquery.topAlbum)
            elif tht == "PLAYLISTS":
                self.query["top_hit"] = self.assembleFactory("search", "playlist", Tquery.topPlaylist)
            elif tht == "ARTISTS":
                self.query["top_hit"] = self.assembleFactory("search", "artist", Tquery.topArtist)
            elif tht == "TRACKS":
                self.query["top_hit"] = self.assembleFactory("search", "track", Tquery.topTrack)
            for i in self.boxList:
                self.cleaner(i.get_children())
            window.show_all()
            qld = futures.ThreadPoolExecutor(max_workers=4)
            qld.submit(self.backer)
            time.sleep(0.2)

    def cleaner(self, lis):
        if lis == []:
            pass
        else:
            for i in lis:
                i.destroy()

    def constructor(self, targetParent, items, btn, iType):
        self.inFav = False
        if len(items) == 0:
            print(f'Not in this category {btn}')
            for i in self.s_label:
                if btn in Gtk.Buildable.get_name(i):
                    i.hide()
        else:
            if targetParent == self.boxMore:
                moreBox = Gtk.Box.new(1, 10)
                moreBox.set_homogeneous(False)
                moreBox.set_can_focus(False)
            else:
                moreGrid = Gtk.Grid.new()
                moreGrid.set_can_focus(False)
            zed = 0
            prev = None
            for item in reversed(items):
                if len(items) == 1:
                    ITEM = items[0]
                else:
                    ITEM = item
                if targetParent == self.boxMore:
                    subBox = Gtk.Box.new(0, 10)
                else:
                    subBox = Gtk.Box.new(1, 10)
                namBut = Gtk.Button.new_with_label("test")
                namBut.set_can_focus(False)
                namBut.set_size_request(-1, 25)
                tmpLab = namBut.get_child()
                tmpLab.set_ellipsize(3)
                if targetParent == self.boxMore:
                    tmpLab.set_markup('<big><b>'+ITEM["title"].replace('&', 'and')+'</b></big>')
                else:
                    tmpLab.set_label(ITEM["title"].replace('&', 'and'))
                tmpLab.set_halign(Gtk.Align(1))
                tmpLab.set_valign(Gtk.Align(3))
                namBut.set_relief(Gtk.ReliefStyle.NONE)
                imaje = Gtk.Image.new()
                evBox = Gtk.EventBox.new()
                if btn == 'otAlBut':
                    Gtk.Buildable.set_name(namBut, f"s_album{zed}")
                    Gtk.Buildable.set_name(evBox, f"img_s_album{zed}")
                elif btn == 'track':
                    Gtk.Buildable.set_name(namBut, f"s_track{zed}")
                    Gtk.Buildable.set_name(evBox, f"img_s_track{zed}")
                elif btn == 'album':
                    Gtk.Buildable.set_name(namBut, f"s_album{zed}")
                    Gtk.Buildable.set_name(evBox, f"img_s_album{zed}")
                elif btn == 'artist':
                    Gtk.Buildable.set_name(namBut, f"s_art{zed}")
                    Gtk.Buildable.set_name(evBox, f"img_s_art{zed}")
                elif btn == 'playlist':
                    Gtk.Buildable.set_name(namBut, f"s_playl{zed}")
                    Gtk.Buildable.set_name(evBox, f"img_s_playl{zed}")
                elif btn == 'top':
                    Gtk.Buildable.set_name(namBut, f"s_top")
                    Gtk.Buildable.set_name(evBox, f"img_s_top{zed}")
                else:
                    Gtk.Buildable.set_name(namBut, f"s_art{zed}")
                    Gtk.Buildable.set_name(evBox, f"img_s_art{zed}")
                namBut.connect("clicked", self.on_searchItem_clicked)
                namBut.connect("button_press_event", self.mouse_click)
                imaje.set_margin_start(10)
                imaje.set_margin_end(10)
                evBox.connect("button_press_event", self.image_click)
                if targetParent == self.boxMore:
                    imaje.set_margin_bottom(10)
                    imaje.set_margin_top(10)
                    evBox.add(imaje)
                    subBox.pack_start(evBox, False, False, 0)
                    subBox.pack_start(namBut, True, True, 0)
                else:
                    imaje.set_margin_top(5)
                    evBox.add(imaje)
                    subBox.pack_start(evBox, False, False, 0)
                    subBox.pack_end(namBut, True, True, 0)
                if targetParent == self.boxMore:
                    moreBox.pack_start(subBox, False, False, 0)
                else:
                    moreGrid.attach_next_to(subBox, prev, 0, 1, 1)
                prev = subBox
                ld_cov = futures.ThreadPoolExecutor(max_workers=4)
                if btn == 'track' or iType == 'track':
                    ld_cov.submit(self.load_cover, where='search', widget=imaje, something=ITEM, iType=iType)
                else:
                    ld_cov.submit(self.load_cover, where='search', widget=imaje, something=ITEM, iType=iType)
                if len(items) == 1:
                    break
                else:
                    zed += 1
            yetScroll = Gtk.ScrolledWindow()
            yetScroll.set_can_focus(False)
            yetScroll.set_vexpand(True)
            yetScroll.set_hexpand(True)
            yetScroll.set_size_request(-1, 200)
            yetScroll.set_margin_end(10)
            if targetParent == self.boxMore:
                yetScroll.add(moreBox)
            else:
                yetScroll.add(moreGrid)
            targetParent.pack_start(yetScroll, True, True, 0)
            yetScroll.show_all()

    def on_git_link_clicked(self, button):
        # open project page in browser
        webbrowser.open_new_tab("https://swanux.github.io/htidal.html")

    def on_go_more(self, button):
        self.cleaner(self.boxMore.get_children())
        btn = Gtk.Buildable.get_name(button)
        if self.artist == '':
            if btn == 'otAlBut':
                items = self.album.artist.get_albums()
                self.query['albums'] = items
            else:
                items = self.album.artist.get_similar()
                self.query['artists'] = items
        else:
            if btn == 'otAlBut':
                items = self.artist.get_albums()
                self.query['albums'] = items
            else:
                items = self.artist.get_similar()
                self.query['artists'] = items
        self.constructor(self.boxMore, items, btn)
        stack.set_visible_child(self.boxMore)

    def on_go_radio(self, widget):
        if self.artist == '':
            item = self.album.tracks(limit=1, offset=0)[0]
        else:
            item = self.artist
        self.gen_playlist_view(name='playlistPlayer', playlistLoc=item, again=self.playlistPlayer, allPos='radio')

    def on_go_artist(self, widget):
        self.artist = self.playlist[self.tnum].artist
        self.album = ''
        self.gen_playlist_view(name='album', playlistLoc=self.artist, again=self.albume, allPos='artistLoad')
        self.expanded = False
        stack.set_visible_child(self.builder.get_object('scrollAlbum'))
        self.cleaner(self.builder.get_object("relateds").get_children())
        tmi = self.artist.get_albums(limit=None, offset=0)
        self.query['albums'] = tmi
        self.constructor(self.builder.get_object("relateds"), tmi, 'album')
        self.builder.get_object("general_bottom").show()
        self.builder.get_object("dlAlb").hide()
        self.prevSlide = stack.get_visible_child()

    def on_go_album(self, widget):
        btn = Gtk.Buildable.get_name(widget)
        if btn == 'goAlbum':
            self.album = self.playlist[self.tnum].album
        self.artist = ''
        self.gen_playlist_view(name='album', playlistLoc=self.album, again=self.albume)
        self.expanded = False
        stack.set_visible_child(self.builder.get_object('scrollAlbum'))
        self.cleaner(self.builder.get_object("relateds").get_children())
        tmi = self.album.artist.get_albums(limit=None, offset=0)
        self.query['albums'] = tmi
        self.constructor(self.builder.get_object("relateds"), tmi, 'album')
        self.builder.get_object("general_bottom").show()
        self.builder.get_object("dlAlb").show()
        self.prevSlide = stack.get_visible_child()

    def on_dl_alb(self, button):
        iType = self.get_type(self.album)
        dl = futures.ThreadPoolExecutor(max_workers=4)
        dl.submit(self.general_download, items=self.album.tracks(), tpe=iType, name=self.album.name)
        self.dlStack.set_visible_child(self.dlBox1)
        self.dlWin.show_all()

    def on_dload_activate(self, widget):
        dl = futures.ThreadPoolExecutor(max_workers=4)
        dl.submit(self.general_download, items=[self.playlist[self.tnum]], tpe='track')
        self.dlStack.set_visible_child(self.dlBox)
        self.whLab.set_label("Preparing...")
        self.dlWin.show_all()

    def general_download(self, items, tpe, name=''):
        dlDir = {}
        self.tot_size = 0
        i = 1
        lens = len(items)
        for item in items:
            GLib.idle_add(self.whLab1.set_label, f"{i} out of {lens}")
            time.sleep(1.5)
            url = item.get_url()
            tmp = urllib.request.urlopen(url)
            file_name = item.id
            track = item.name
            file_size = int(tmp.getheader('Content-Length'))
            if tpe == 'track':
                target = f'/home/{user}/Music/htidal/tracks/{track}.{self.ftype}'
            elif tpe == 'album':
                target = f'/home/{user}/Music/htidal/albums/{name}/{track}.{self.ftype}'
            elif tpe == 'playlist':
                target = f'/home/{user}/Music/htidal/playlists/{name}/{track}.{self.ftype}'
            elif tpe == 'playqueue':
                target = f'/home/{user}/Music/htidal/snapshots/{name}/{track}.{self.ftype}'
            dlDir[file_name] = {'size' : file_size, 'url' : url, 'track' : track, 'artist' : item.artist.name, 'album' : item.album.name, 'year' : item.album.release_date.strftime("%Y"), 'target' : target.replace(' ', "\ ").replace('(', '').replace(')', '')}
            self.tot_size += file_size
            i += 1
        print(dlDir)
        self.dlBar.set_fraction(0.00)
        self.dlded = 0
        self.dlStack.set_visible_child(self.dlBox)
        dl = futures.ThreadPoolExecutor(max_workers=4)
        dl.submit(self.dl_backend, dlDir=dlDir)
        def counter(timer):
            if self.dlded < self.tot_size:
                print(self.dlded/self.tot_size)
                GLib.idle_add(self.dlBar.set_fraction, self.dlded/self.tot_size)
                return True
            else:
                GLib.idle_add(self.dlWin.hide)
                return False
        self.source_id = GLib.timeout_add(200, counter, None)

    def dl_backend(self, dlDir):
        GLib.idle_add(self.whLab.set_label, f"{round(self.dlded/1024/1024, 1)} MB downloaded of total {round(self.tot_size/1024/1024, 1)} MB")
        for current in dlDir:
            time.sleep(1)
            url = dlDir[current]['url']
            print(url)
            u = urllib.request.urlopen(url)
            target = dlDir[current]['target']
            targetList = target.split('/')
            targetList.remove(targetList[-1])
            os.system(f"mkdir -p {'/'.join(targetList)}")
            print(self.dlded, self.tot_size)
            with open(target.replace('\\ ', ' '), "wb") as f:
                while True:
                    buffer = u.read(4096)
                    if not buffer:
                        break
                    self.dlded += len(buffer)
                    f.write(buffer)
                    GLib.idle_add(self.whLab.set_label, f"{round(self.dlded/1024/1024, 1)} MB downloaded of total {round(self.tot_size/1024/1024, 1)} MB")
            f = MediaFile(target.replace('\\ ', ' '))
            f.title = dlDir[current]['track']
            f.album = dlDir[current]['album']
            f.artist = dlDir[current]['artist']
            f.year = dlDir[current]['year']
            f.save()

    def on_karaoke_activate(self, widget):
        print('Karaoke')
        self.stopKar = False
        track = self.playlist[self.tnum].name
        tid = self.playlist[self.tnum].id
        artists = self.playlist[self.tnum].artists
        dbnow = os.listdir('/usr/share/htidal/db/')
        self.sub.set_title(f'{track} - {artists[0].name}')
        tmp = track.replace(' ', '_').replace("'", '').replace('(', '').replace(')', '')
        if f"{tmp}-{tid}.srt" not in dbnow:
            indices = [i for i, s in enumerate(dbnow) if f'{tmp}' in s]
            if indices == []:
                print("NEW NEEDED1")
                self.builder.get_object('id').set_label(f'Track ID: {tid}')
                self.subStack.set_visible_child(self.boxNo)
            else:
                print("PARTIAL")
                x, y = window.get_position()
                sx, sy = window.get_size()
                dialogWindow = Gtk.MessageDialog(parent=window, modal=True, destroy_with_parent=True, message_type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.YES_NO, text=gg(f'The current track does not have synced lyrics. However there is one which might be similar: {dbnow[indices[0]]}.\nWould you like to give it a try?'))
                dialogWindow.set_title(gg("Prompt"))
                dsx, dsy = dialogWindow.get_size()
                dialogWindow.move(x+((sx-dsx)/2), y+((sy-dsy)/2))
                dx, dy = dialogWindow.get_position()
                print(dx, dy)
                dialogWindow.show_all()
                res = dialogWindow.run()
                if res == Gtk.ResponseType.YES:
                    print('OK pressed')
                    dialogWindow.destroy()
                    self.start_karaoke(dbnow[indices[0]])
                else:
                    print('No pressed')
                    dialogWindow.destroy()
                    self.builder.get_object('id').set_label(f'Track ID: {tid}')
                    self.subStack.set_visible_child(self.boxNo)
        else:
            print("FOUND")
            self.start_karaoke(f"{tmp}-{tid}.srt")
        self.sub.show_all()

    def on_hide(self, window, e):
        print('hide')
        self.stopKar = True
        self.sub.hide()
        return True

    def on_settingBut_clicked(self, button):
        self.expanded = False
        stack.set_visible_child(self.builder.get_object('scrollSet'))

    def on_event1_button_press_event(self, event, button):
        print('eventhere')
    
    def on_event2_button_press_event(self, event, button):
        print('event2here')

    # def on_wr_but_clicked(self, button):
    #     nQuality = self.builder.get_object('qual_combo').get_active()
    #     parser.set('misc', 'quality', str(nQuality))
    #     file = open(f"/home/{user}/.config/htidal/htidal.ini", "w+")
    #     parser.write(file)
    #     file.close()

    def on_fav_gen(self, button):
        self.cleaner(self.boxMore.get_children())
        try:
            btn = Gtk.Buildable.get_name(button)
        except:
            btn = button
        if "track" in btn:
            items = self.favs
            self.query['tracks'] = items
            btn = "track"
        elif "list" in btn:
            items = self.favPlys
            self.query['playlists'] = items
            btn = "playlist"
        elif "art" in btn:
            items = self.favArts
            self.query['artists'] = items
            btn = "artist"
        else:
            items = self.favAlbs
            self.query['albums'] = items
            btn = "album"
        stack.set_visible_child(self.boxMore)
        self.constructor(self.boxMore, items, btn, btn)
        self.inFav = True

    def on_favs_clicked(self, button):
        stack.set_visible_child(self.builder.get_object("scrollFavs"))

    def on_myLists_clicked(self, button):
        self.gen_playlist_view(name="all", again=self.all)
        stack.set_visible_child(self.builder.get_object('big'))

    def start_karaoke(self, sfile):
        print('HEY')
        with open (f"/usr/share/htidal/db/{sfile}", "r") as subfile:
            presub = subfile.read()
        subtitle_gen = srt.parse(presub)
        subtitle = list(subtitle_gen)
        self.subStack.set_visible_child(self.boxText)
        lyrs = futures.ThreadPoolExecutor(max_workers=4)
        lyrs.submit(self.slideShow, subtitle)

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
        # if not self.seekingLyr:
        tg = GLib.idle_add(self.label2.set_label, simpl2)
        # GLib.source_remove(tg)
        tg = GLib.idle_add(self.label3.set_label, simpl3)
        # GLib.source_remove(tg)
        done = ""
        tmpline = self.line1[:]
        first = True
        tl1 = self.line1
        tl1.insert(0, "")
        it = 1
        maxit = len(tl1)-1
        for xy in tl1:
            # if self.position <= xy.end.total_seconds():
            #     self.seekingLyr = False
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
            # if not self.seekingLyr:
            try:
                tg = GLib.idle_add(self.label1.set_markup, f"<span color='green'>{done}</span> <span color='green'>{xy.content.replace('#', '')}</span> <span color='white'>{leftover}</span>")
            except:
                print('Null')
                tg = GLib.idle_add(self.label1.set_markup, f"<span color='green'>{done}</span> <span color='green'>{xy}</span> <span color='white'>{leftover}</span>")
            # GLib.source_remove(tg)
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
                print('First word')

    def slideShow(self, subtitle):
        self.lenlist = len(subtitle)-1
        self.label1 = self.builder.get_object('label1')
        self.label2 = self.builder.get_object('label2')
        self.label3 = self.builder.get_object('label3')
        while not self.stopKar:
            time.sleep(0.01)
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

    def row_activated(self, widget, row, col):
        self.relPos = self.tree.get_selection().get_selected_rows()[1][0][0]
        self.on_next("clickMode")
    
    def playIt(self, button):
        self.relPos = 0
        if self.artiste == False:
            self.gen_playlist_view(name="playlistPlayer", again=self.playlistPlayer, allPos='albumLoad')
        else:
            self.gen_playlist_view(name="playlistPlayer", again=self.playlistPlayer, allPos='artistLoad')
        print('submit3')
        self.on_next("clickModeA")
    
    def album_row(self, widget, row, col):
        print('posAlb')
        self.relPos = self.albumTree.get_selection().get_selected_rows()[1][0][0]
        if self.artiste == False:
            self.gen_playlist_view(name="playlistPlayer", again=self.playlistPlayer, allPos='albumLoad')
        else:
            self.gen_playlist_view(name="playlistPlayer", again=self.playlistPlayer, allPos='artistLoad')
        print('submit3')
        self.on_next("clickModeA")
    
    def on_newList_clicked(self, button):
        stack.set_visible_child(self.builder.get_object("scrollCreate"))

    def on_cancel(self, button):
        stack.set_visible_child(self.allBox)

    def on_create(self, button):
        name = self.builder.get_object("create_entry").get_text()
        # tidalapi.user.LoggedInUser(self.session, self.userID).create_playlist(name, '')
        lib.create_playlist(name.encode("utf-8"))
        # self.allPlaylist = tidalapi.user.LoggedInUser(self.session, self.userID).playlists()
        self.favver(["playlist"])
        self.allPlaylist = self.favPlys
        self.on_myLists_clicked("")

    def all_row(self, widget, row, col):
        if self.adding == False:
            print('pos')
            self.allPos = self.allTree.get_selection().get_selected_rows()[1][0][0]
            self.artist = ""
            self.album = self.allPlaylist[self.allPos]
            self.gen_playlist_view(name='album', playlistLoc="myList", again=self.albume, allPos=self.allPos)
            self.expanded = False
            stack.set_visible_child(self.builder.get_object('scrollAlbum'))
            self.builder.get_object("general_bottom").hide()
            self.builder.get_object("dlAlb").show()
            self.prevSlide = stack.get_visible_child()
            print('submit2')
        else:
            allPos = self.allTree.get_selection().get_selected_rows()[1][0][0]
            playlist = self.allPlaylist[allPos]
            # local = tidalapi.playlist.UserPlaylist(self.session, playlist.id)
            # local.add([self.whatToAdd.id])
            lib.add_playlist_item(playlist.id.encode("utf-8"), self.whatToAdd.id)
            # self.allPlaylist = tidalapi.user.LoggedInUser(self.session, self.userID).playlists()
            self.favver(["playlist"])
            self.allPlaylist = self.favPlys
            stack.set_visible_child(self.prevTmp)
            self.adding = False

    def rem_fav(self, item):
        if 's_track' in self.btn:
            item = self.query['tracks'][int(re.findall(r'\d+', self.btn)[0])]
            # self.favourite.remove_track(item.id)
            lib.delete_favorite_track(item.id)
            # self.favs = self.favourite.tracks()
            self.favs.remove(item)
            self.on_fav_gen("track")
        elif 's_art' in self.btn:
            item = self.query['artists'][int(re.findall(r'\d+', self.btn)[0])]
            # self.favourite.remove_artist(item.id)
            lib.delete_favorite_artist(item.id)
            # self.favArts = self.favourite.artists()
            self.favArts.remove(item)
            self.on_fav_gen("art")
        elif 's_album' in self.btn:
            item = self.query['albums'][int(re.findall(r'\d+', self.btn)[0])]
            # self.favourite.remove_album(item.id)
            lib.delete_favorite_album(item.id)
            # self.favAlbs = self.favourite.albums()
            self.favAlbs.remove(item)
            self.on_fav_gen("album")
        elif 's_playl' in self.btn:
            item = self.query['playlists'][int(re.findall(r'\d+', self.btn)[0])]
            # self.favourite.remove_playlist(item.id)
            lib.delete_favorite_playlist(item.id)
            # self.favPlys = self.favourite.playlists()
            self.favPlys.remove(item)
            self.on_fav_gen("list")

    def image_click(self, widget, event):
        if event.button == 1:
            self.on_searchItem_clicked(widget)

    def mouse_click(self, widget, event):
        if event.button == 3:
            menu = Gtk.Menu()
            menu.set_can_focus(False)
            loc = Gtk.Buildable.get_name(stack.get_visible_child())
            if self.treeType == "own" and loc == "scrollAlbum":
                pthinfo = self.albumTree.get_path_at_pos(event.x, event.y)
                path,col,cellx,celly = pthinfo
                self.albumTree.grab_focus()
                self.albumTree.set_cursor(path,col,0)
                menu_item = Gtk.MenuItem.new_with_label('Remove from playlist')
                menu_item.set_can_focus(False)
                menu_item.connect("activate", self.del_pl)
                menu.add(menu_item)
                menu.show_all()
                menu.popup_at_pointer()
            elif self.inFav == True and loc == "more_box":
                self.btn = Gtk.Buildable.get_name(widget)
                menu_item = Gtk.MenuItem.new_with_label('Remove from Favourites')
                menu_item.set_can_focus(False)
                menu_item.connect("activate", self.rem_fav)
                menu.add(menu_item)
                menu.show_all()
                menu.popup_at_pointer()
            elif loc == "scrollAlbum" and self.artist == '':
                pthinfo = self.albumTree.get_path_at_pos(event.x, event.y)
                path,col,cellx,celly = pthinfo
                self.albumTree.grab_focus()
                self.albumTree.set_cursor(path,col,0)
                this = self.albumTree.get_selection().get_selected_rows()[1][0][0]
                for i in self.favs:
                    if self.albumTracks[self.storeAlbum[this][2]].id == i.id:
                        state = 'Remove from Favourites'
                        break
                    else:
                        state = 'Add to Favourites'
                menu_item = Gtk.MenuItem.new_with_label(state)
                menu_item.set_can_focus(False)
                menu_item.connect("activate", self.add_cur)
                menu.add(menu_item)
                menu_item = Gtk.MenuItem.new_with_label('Add to playlist')
                menu_item.set_can_focus(False)
                menu_item.connect("activate", self.add_pl)
                menu.add(menu_item)
                menu.show_all()
                menu.popup_at_pointer()
            elif loc == "big":
                pthinfo = self.allTree.get_path_at_pos(event.x, event.y)
                path,col,cellx,celly = pthinfo
                self.allTree.grab_focus()
                self.allTree.set_cursor(path,col,0)
                menu_item = Gtk.MenuItem.new_with_label('Delete playlist')
                menu_item.set_can_focus(False)
                menu_item.connect("activate", self.del_pyl)
                menu.add(menu_item)
                menu.show_all()
                menu.popup_at_pointer()
            elif loc == "expanded":
                pthinfo = self.tree.get_path_at_pos(event.x, event.y)
                path,col,cellx,celly = pthinfo
                self.tree.grab_focus()
                self.tree.set_cursor(path,col,0)
                menu_item = Gtk.MenuItem.new_with_label('Delete from current playqueue')
                menu_item.set_can_focus(False)
                menu_item.connect("activate", self.del_cur)
                menu.add(menu_item)
                this = self.tree.get_selection().get_selected_rows()[1][0][0]
                for i in self.favs:
                    if self.playlist[self.storePlaylist[this][2]].id == i.id:
                        state = 'Remove from Favourites'
                        break
                    else:
                        state = 'Add to Favourites'
                menu_item = Gtk.MenuItem.new_with_label(state)
                menu_item.set_can_focus(False)
                menu_item.connect("activate", self.add_cur)
                menu.add(menu_item)
                menu_item = Gtk.MenuItem.new_with_label('Save current playqueue offline')
                menu_item.set_can_focus(False)
                menu_item.connect("activate", self.dl_cur)
                menu.add(menu_item)
                menu_item = Gtk.MenuItem.new_with_label('Add to playlist')
                menu_item.set_can_focus(False)
                menu_item.connect("activate", self.add_pl)
                menu.add(menu_item)
                menu.show_all()
                menu.popup_at_pointer()
    
    def del_pyl(self, itme):
        this = self.allTree.get_selection().get_selected_rows()[1][0][0]
        # local = tidalapi.playlist.UserPlaylist(self.session, self.allPlaylist[self.allStore[this][1]].id)
        # local.delete()
        lib.delete_playlist(self.allPlaylist[self.allStore[this][1]].id)
        # self.allPlaylist = tidalapi.user.LoggedInUser(self.session, self.userID).playlists()
        self.favver(["playlist"])
        self.allPlaylist = self.favPlys
        self.gen_playlist_view(name="all", again=self.all)

    def add_pl(self, item):
        self.prevTmp = stack.get_visible_child()
        self.whatToAdd = self.playlist[self.tnum]
        self.adding = True
        self.on_myLists_clicked('')

    def del_pl(self, item):
        this = self.albumTree.get_selection().get_selected_rows()[1][0][0]
        local = tidalapi.playlist.UserPlaylist(self.session, self.album.id)
        local.remove_by_index(this)
        self.favver(["playlist"])
        self.allPlaylist = self.favPlys
        self.album = self.allPlaylist[self.allPos]
        self.gen_playlist_view(name='album', playlistLoc="myList", again=self.albume, allPos=self.allPos)

    def del_cur(self, item):
        this = self.tree.get_selection().get_selected_rows()[1][0][0]
        self.playlist.remove(self.playlist[self.storePlaylist[this][2]])
        self.gen_playlist_view(name='playlistPlayer', again=self.playlistPlayer, allPos='regen')
    
    def dl_cur(self, item):
        now = datetime.datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        dl = futures.ThreadPoolExecutor(max_workers=4)
        dl.submit(self.general_download, items=self.playlist, tpe='playqueue', name=f"Playqueue_{str(dt_string).replace('.', '-').replace(' ', '_')}")
        self.dlStack.set_visible_child(self.dlBox1)
        self.dlWin.show_all()

    def add_cur(self, item):
        state = item.get_label()
        loc = Gtk.Buildable.get_name(stack.get_visible_child())
        if loc == "expanded":
            this = self.tree.get_selection().get_selected_rows()[1][0][0]
            track = self.playlist[self.storePlaylist[this][2]]
        elif loc == "scrollAlbum":
            this = self.albumTree.get_selection().get_selected_rows()[1][0][0]
            track = self.albumTracks[self.storeAlbum[this][2]]
        if "Add" in state:
            self.favourite.add_track(track.id)
            print(f"Added {track.name}")
        else:
            self.favourite.remove_track(track.id)
            print(f"Removed {track.name}")
        self.favs = self.favourite.tracks()
    
    def add_fav(self, button):
        state = button.get_label()
        if "Add" in state:
            if self.artist == '':
                try:
                    self.album.creator.name
                    self.favourite.add_playlist(self.album.id)
                    self.favPlys = self.favourite.playlists()
                    print(f"Added playlist {self.album.name}")
                except:
                    self.favourite.add_album(self.album.id)
                    self.favAlbs = self.favourite.albums()
                    print(f"Added album {self.album.name}")
            else:
                self.favourite.add_artist(self.artist.id)
                self.favArts = self.favourite.artists()
                print(f"Added artist {self.artist.name}")
            button.set_label("Remove from Favourites")
        else:
            if self.artist == '':
                try:
                    self.album.creator.name
                    self.favourite.remove_playlist(self.album.id)
                    self.favPlys = self.favourite.playlists()
                    print(f"Removed playlist {self.album.name}")
                except:
                    self.favourite.remove_album(self.album.id)
                    self.favAlbs = self.favourite.albums()
                    print(f"Removed album {self.album.name}")
            else:
                self.favourite.remove_artist(self.artist.id)
                self.favArts = self.favourite.artists()
                print(f"Removed artist {self.artist.name}")
            button.set_label("Add to Favourites")

    def on_next(self, button):
        print("Next")
        if button == "clickMode":
            self.tnum = self.storePlaylist[self.relPos][2] # pylint: disable=unsubscriptable-object
        elif button == "clickModel":
            self.tnum = 0
        elif button == "clickModeA":
            self.tnum = self.storeAlbum[self.relPos][2] # pylint: disable=unsubscriptable-object
        else:
            try:
                self.albumTree.set_cursor(self.relPos)
            except:
                print('Out of length')
            self.tree.set_cursor(self.relPos)
            self.relPos = self.tree.get_selection().get_selected_rows()[1][0][0]
            self.relPos = self.relPos + 1
            if self.relPos >= len(self.playlist):
                self.relPos = 0
            self.tnum = self.storePlaylist[self.relPos][2] # pylint: disable=unsubscriptable-object
        try:
            self.globSeek = False
            self.stop("xy")
        except:
            print("No playbin yet to stop.")
        self.globSeek = True
        self.x = 0
        ld_cov = futures.ThreadPoolExecutor(max_workers=4)
        ld_cov.submit(self.load_cover)
        self.play()

    def on_prev(self, button):
        print("Prev")
        try:
            self.albumTree.set_cursor(self.relPos)
        except:
            print('Out of length')
        self.tree.set_cursor(self.relPos)
        self.relPos = self.tree.get_selection().get_selected_rows()[1][0][0]
        self.relPos = self.relPos - 1
        if self.relPos < 0:
            self.relPos = len(self.playlist)-1
        self.tnum = self.storePlaylist[self.relPos][2] # pylint: disable=unsubscriptable-object
        try:
            self.pause()
            self.globSeek = False
            self.stop("xy")
            self.globSeek = True
        except:
            print("No playbin yet to stop.")
        self.x = 0
        ld_cov = futures.ThreadPoolExecutor(max_workers=4)
        ld_cov.submit(self.load_cover)
        self.play()

    def _on_size_allocated(self, widget, alloc):
        x, y = window.get_size()
        try:
            if int(x/2.4) - int(self.w/2.4) >= 20 or int(self.w/2.4) - int(x/2.4) >= 20:
                nam = f"/tmp/htidal/thumbnails/{self.playlist[self.tnum].album.id}"
                coverBuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(nam, int(x/2.4), int(y/1.4), True)
                self.w, self.h = x, y
                self.trackCover.clear()
                tg = GLib.idle_add(self.trackCover.set_from_pixbuf, coverBuf)
        except:
            pass

    def load_cover(self, where='', widget='', something='', iType=''):
        # print("Load cover")
        self.w, self.h = window.get_size()
        if where == '':
            # album = self.playlist[self.tnum]["cover"]
            Tid = self.playlist[self.tnum]["id"]
            nam = f"/tmp/htidal/thumbnails/{Tid}"
            if os.path.exists(nam):
                print("In cache")
                pass
            else:
                try:
                    # pic = album.image(640)
                    Tpic = self.playlist[self.tnum]["cover"].replace("-", "/")
                    pic = f"https://resources.tidal.com/images/{Tpic}/320x320.jpg"
                    response = urllib.request.urlopen(pic)
                    with open(nam, "wb") as img:
                        img.write(response.read())
                except:
                    nam = f"icons/album.png"
            coverBuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(nam, int(self.w/2.4), int(self.h/1.4), True)
            tg = GLib.idle_add(self.trackCover.set_from_pixbuf, coverBuf)
        elif where == 'search':
            Tid = something["id"]
            if iType == "artist":
                nam = f"/tmp/htidal/thumbnails/{Tid}_circle.png"
            else:
                nam = f"/tmp/htidal/thumbnails/{Tid}"
            if os.path.exists(nam):
                pass
            else:
                try:
                    # pic = something.image(320)
                    # if iType == "track":
                    #     Tpic = ffi.string(lib.get_album(lib.get_track(something).albumId[0]).cover[0]).decode("utf-8").replace("-", "/")
                    Tpic = something["cover"].replace("-", "/")
                    pic = f"https://resources.tidal.com/images/{Tpic}/320x320.jpg"
                    response = urllib.request.urlopen(pic)
                    with open(nam, "wb") as img:
                        img.write(response.read())
                    if iType == "artist":
                        self.circler(nam)
                except:
                    nam = f"icons/{iType}.png"
            if widget == self.alb_cover:
                coverBuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(nam, 190, 190, True)
            elif widget.get_margin_bottom() == 10:
                coverBuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(nam, 70, 70, True)
            else:
                coverBuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(nam, 150, 150, True)
            tg = GLib.idle_add(widget.set_from_pixbuf, coverBuf)

    def circler(self, nam):
        img = Image.open(nam).convert("RGB")
        npImage = np.array(img)
        h, w = img.size
        alpha = Image.new('L', img.size,0)
        draw = ImageDraw.Draw(alpha)
        draw.pieslice([0,0,h,w],0,360,fill=255)
        npAlpha = np.array(alpha)
        npImage = np.dstack((npImage,npAlpha))
        Image.fromarray(npImage).save(nam)

    def on_expand_clicked(self, button):
        self.tree.set_cursor(self.relPos)
        if self.expanded == False:
            print("expand")
            self.expanded = True
            self.prevSlide = stack.get_visible_child()
            stack.set_visible_child(self.builder.get_object("expanded"))
        else:
            self.expanded = False
            stack.set_visible_child(self.prevSlide)
            try:
                self.albumTree.set_cursor(self.relPos)
            except:
                print('Out of length')
    
    def on_back(self, button):
        print("Home")
        self.expanded = False
        stack.set_visible_child(self.builder.get_object("scrollHome"))
        
    def on_slider_seek(self, widget):
        print("Slider seek")
        if self.globSeek:
            seek_time_secs = self.slider.get_value()
            # self.seekingLyr = True
            if seek_time_secs < self.position:
                self.seekBack = True
                print('back')
                print(seek_time_secs, self.position)
            self.player.seek_simple(Gst.Format.TIME,  Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, seek_time_secs * Gst.SECOND)
        else:
            print("No need to seek")

    def on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            self.on_next("xy")
        elif t == Gst.MessageType.ERROR:
            self.player.set_state(Gst.State.NULL)
            err, debug = message.parse_error()
            print (f"Error: {err}", debug)

    def on_shuffBut_clicked(self, button):
        self.gen_playlist_view(name='shuffle')

    def gen_playlist_view(self, playlistLoc='', name='', again=False, allPos=''):
        if name == 'shuffle':
            if self.playlistPlayer == True:
                self.relPos = 0
                playlistLoc = random.sample(self.playlist, len(self.playlist))
                self.playlist = playlistLoc
                self.gen_playlist_view(name='playlistPlayer', again=self.playlistPlayer, allPos='regen')
                self.on_next('clickModel')
        elif name == 'playlistPlayer':
            if allPos == 'albumLoad':
                self.playlist = self.assembleFactory("al-tr", "track", self.album["id"])
            elif allPos == 'artistLoad':
                self.playlist = self.assembleFactory("top", "track", self.artist["id"])
            elif allPos == 'regen':
                print('Regenerate only')
            elif allPos == 'radio':
                self.relPos = 0
                if self.get_type(playlistLoc) == 'artist':
                    try:
                        self.playlist = playlistLoc.get_radio()
                    except:
                        print('No radio station avilable')
                else:
                    try:
                        self.playlist = playlistLoc.artist.get_radio()
                    except:
                        print('No radio station avilable')
                    self.playlist.insert(0, playlistLoc)
            else:
                print('Passing in generator')
            playlistLoc = self.playlist
            self.storePlaylist = Gtk.ListStore(str, str, int)
            self.tree.set_model(self.storePlaylist)
            def doapp():
                for x in range(len(playlistLoc)):
                    self.storePlaylist.append([t[x], a[x], il[x]])
                return False
            t = []
            a = []
            il = []
            for i in range(len(playlistLoc)):
                t.append(playlistLoc[i]["title"])
                a.append(playlistLoc[i]["artist"])
                il.append(i)
            GLib.idle_add(doapp)
            if not again:
                print("First time")
                for i, column_title in enumerate(["Title", "Artist", "ID"]):
                    renderer = Gtk.CellRendererText(xalign=0)
                    renderer.set_property("ellipsize", True)
                    column = Gtk.TreeViewColumn(column_title, renderer, text=i)
                    if column_title == "Title" or column_title == "Artist":
                        column.set_fixed_width(140)
                        column.set_resizable(True)
                    else:
                        column.set_max_width(50)
                        column.set_resizable(False)
                    column.set_sort_column_id(i)
                    column.set_sort_indicator(False)
                    self.tree.append_column(column)
            self.playlistPlayer = True
            ld_cov = futures.ThreadPoolExecutor(max_workers=4)
            ld_cov.submit(self.load_cover)
            if allPos == 'radio':
              self.on_next('clickModel')
        elif name == "all":
            self.favver(["playlist"])
            self.allPlaylist = self.favPlys
            playlistLoc = self.allPlaylist
            self.allStore = Gtk.ListStore(str, int)
            self.allTree.set_model(self.allStore)
            def doapp():
                for x in range(len(playlistLoc)):
                    self.allStore.append([t[x], il[x]])
                return False
            t = []
            il = []
            for i in range(len(playlistLoc)):
                t.append(playlistLoc[i].name)
                il.append(i)
            GLib.idle_add(doapp)
            if not again:
                print("First time")
                for i, column_title in enumerate(["Name", "ID"]):
                    renderer = Gtk.CellRendererText()
                    renderer.set_property("ellipsize", True)
                    column = Gtk.TreeViewColumn(column_title, renderer, text=i)
                    x, y = window.get_size()
                    print(x, y)
                    if column_title == "Name":
                        column.set_fixed_width(int(x/3))
                        column.set_resizable(True)
                    else:
                        column.set_fixed_width(30)
                        column.set_resizable(False)
                    self.allTree.append_column(column)
            self.all = True
        elif name == 'album':
            self.treeType = ""
            self.fLab.show()
            self.builder.get_object("otAlBut").show()
            self.builder.get_object("otArBut").show()
            if allPos == 'artistLoad':
                # albumLoc = playlistLoc.get_top_tracks()
                # print(playlistLoc)
                albumLoc = self.assembleFactory("top", "track", playlistLoc["id"])
                # print(albumLoc)
                self.albumTracks = albumLoc
                self.artiste = True
            elif playlistLoc == "myList":
                self.artiste = False
                # albumLoc = self.allPlaylist[allPos].tracks()ű
                albumLoc = self.assembleFactory("pl-tr", "track", self.allPlaylist[allPos]["id"])
                self.albumTracks = albumLoc
            elif allPos == "playlistPlease":
                self.artiste = False
                albumLoc = self.assembleFactory("pl-tr", "track", playlistLoc["id"])
                self.albumTracks = albumLoc
            else:
                self.artiste = False
                # albumLoc = playlistLoc.tracks()
                albumLoc = self.assembleFactory("al-tr", "track", playlistLoc["id"])
                self.albumTracks = albumLoc
            self.storeAlbum = Gtk.ListStore(str, str, int)
            self.albumTree.set_model(self.storeAlbum)
            def doapp():
                for x in range(len(albumLoc)):
                    self.storeAlbum.append([t[x], a[x], il[x]])
                return False
            t = []
            a = []
            il = []
            for i in range(len(albumLoc)):
                t.append(albumLoc[i]["title"])
                a.append(albumLoc[i]["artist"])
                il.append(i)
            GLib.idle_add(doapp)
            if not again:
                print("First time album")
                for i, column_title in enumerate(["Title", "Artist", "ID"]):
                    renderer = Gtk.CellRendererText(xalign=0)
                    renderer.set_property("ellipsize", True)
                    column = Gtk.TreeViewColumn(column_title, renderer, text=i)
                    if column_title == "Title" or column_title == "Artist":
                        column.set_fixed_width(150)
                        column.set_resizable(True)
                    else:
                        column.set_max_width(50)
                        column.set_resizable(False)
                    column.set_sort_column_id(i)
                    self.albumTree.append_column(column)
            self.albume = True
            ld_cov = futures.ThreadPoolExecutor(max_workers=4)
            if playlistLoc == "myList":
                self.namer.set_label(self.allPlaylist[allPos]["title"])
            else:
                self.namer.set_label(playlistLoc["title"])
            if allPos == 'artistLoad':
                try:
                    self.dat_role.set_label(re.sub(r"[\(\[].*?[\)\]]", "", playlistLoc.get_bio()))
                except:
                    self.dat_role.set_label('No bio avilable')
                self.topOrNot.set_label("Top Tracks")
                self.exLab.set_label("Albums")
                for i in self.favArts:
                    if playlistLoc["id"] == i["id"]:
                        state = 'Remove from Favourites'
                        break
                    else:
                        state = 'Add to Favourites'
            else:
                if allPos == 'playlistPlease':
                    self.dat_role.set_label(playlistLoc["dur"])
                    for i in self.favPlys:
                        if playlistLoc["id"] == i["id"]:
                            state = 'Remove from Favourites'
                            break
                        else:
                            state = 'Add to Favourites'
                elif playlistLoc == 'myList':
                    self.treeType = "own"
                    self.dat_role.set_label(self.allPlaylist[allPos].creator.name)
                    self.fLab.hide()
                    self.builder.get_object("otAlBut").hide()
                    self.builder.get_object("otArBut").hide()
                else:
                    self.dat_role.set_label(playlistLoc["date"])
                    for i in self.favAlbs:
                        if playlistLoc["id"] == i["id"]:
                            state = 'Remove from Favourites'
                            break
                        else:
                            state = 'Add to Favourites'
                self.topOrNot.set_label("Tracks")
                self.exLab.set_label("Related")
            if playlistLoc != "myList":
                self.fLab.set_label(state)
                ld_cov.submit(self.load_cover, where='search', something=playlistLoc, widget=self.alb_cover)
            else:
                ld_cov.submit(self.load_cover, where='search', something=self.allPlaylist[allPos], widget=self.alb_cover)
    def play(self):
        print("Play")
        self.res = True
        self.playing = True
        self.position = 0
        self.url = self.playlist[self.tnum].get_url()
        tmp = str(self.playlist[self.tnum].audio_quality)
        if "lossless" in tmp:
            self.ftype = "alac"
        else:
            self.ftype = "m4a"
        self.player.set_property("uri", self.url)
        try:
            self.albumTree.set_cursor(self.relPos)
        except:
            print('Out of length')
        self.tree.set_cursor(self.relPos)
        self.player.set_state(Gst.State.PLAYING)
        self.plaicon.set_from_icon_name("media-playback-pause", Gtk.IconSize.BUTTON)
        GLib.timeout_add(250, self.updateSlider)
        GLib.timeout_add(80, self.updatePos)
    
    def resume(self):
        print("Resume")
        self.playing = True
        try:
            self.albumTree.set_cursor(self.relPos)
        except:
            print('Out of length')
        self.tree.set_cursor(self.relPos)
        self.player.set_state(Gst.State.PLAYING)
        self.plaicon.set_from_icon_name("media-playback-pause", Gtk.IconSize.BUTTON)
        GLib.timeout_add(250, self.updateSlider)
        GLib.timeout_add(80, self.updatePos)


    def stop(self, widget):
        print("Stop")
        self.res = False
        self.playing = False
        self.label.set_text("0:00")
        self.plaicon.set_from_icon_name("media-playback-start", Gtk.IconSize.BUTTON)
        self.slider.set_value(0)
        self.player.set_state(Gst.State.NULL)
    
    def pause(self): 
        print("Pause")
        self.playing = False
        try:
            self.albumTree.set_cursor(self.relPos)
        except:
            print('Out of length')
        self.tree.set_cursor(self.relPos)
        self.plaicon.set_from_icon_name("media-playback-start", Gtk.IconSize.BUTTON)
        self.player.set_state(Gst.State.PAUSED)

    def updatePos(self):
        if(self.playing == False):
            return False
        nanosecs = self.player.query_position(Gst.Format.TIME)[1]
        self.position = float(nanosecs) / Gst.SECOND
        return True

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
    
    def check(self):
        try:
            urllib.request.urlopen('http://216.58.192.142', timeout=5)
            print('yes, net')
            net = True
        except:
            print('no internet')
            net = False
            offtxt = gg("You have no internet connection!")
            os.system(f'zenity --warning --text={offtxt} --ellipsize')
            raise SystemExit
    
    def authBrowse(self, button):
        webbrowser.open_new_tab("https://link.tidal.com")

    def helperFactory(self, Tproduct, typ, offset, product):
        size = Tproduct.arraySize
        print(size)
        if typ == "track":
            for i in range(size):
                product.append({"title" : ffi.string(Tproduct.title[i]).decode("utf-8"), "cover" : ffi.string(Tproduct.cover[i]).decode("utf-8"), "id" : Tproduct.id[i], "artist" : ffi.string(Tproduct.artistName[i][0]).decode("utf-8"), "type" : typ.upper()})
        elif typ == "artist":
            for i in range(size):
                product.append({"title" : ffi.string(Tproduct.name[i]).decode("utf-8"), "cover" : ffi.string(Tproduct.picture[i]).decode("utf-8"), "id" : Tproduct.id[i], "type" : typ.upper()})
        elif typ == "album":
            for i in range(size):
                product.append({"title" : ffi.string(Tproduct.title[i]).decode("utf-8"), "cover" : ffi.string(Tproduct.cover[i]).decode("utf-8"), "id" : Tproduct.id[i], "artId" : Tproduct.artistId[i][0], "type" : typ.upper(), "date" : ffi.string(Tproduct.releaseDate[0]).decode("utf-8").split("T")[0]})
        elif typ == "playlist":
            for i in range(size):
                product.append({"title" : ffi.string(Tproduct.title[i]).decode("utf-8"), "cover" : ffi.string(Tproduct.squareImage[i]).decode("utf-8"), "id" : ffi.string(Tproduct.uuid[i]).decode("utf-8"), "dur" : str(datetime.timedelta(seconds=Tproduct.duration[i])), "type" : typ.upper()})
        return product

    def assembleFactory(self, method, typ, misc=0):
        product = []
        offset = 0
        limit = 100
        while True:
            if method == "fav":
                if typ == "track":
                    Tproduct = lib.get_favorite_tracks(limit, offset, "DATE".encode("utf-8"), "ASC".encode("utf-8"))
                elif typ == "artist":
                    Tproduct = lib.get_favorite_artist(limit, offset, "DATE".encode("utf-8"), "ASC".encode("utf-8"))
                elif typ == "album":
                    Tproduct = lib.get_favorite_album(limit, offset, "DATE".encode("utf-8"), "ASC".encode("utf-8"))
                elif typ == "playlist":
                    Tproduct = lib.get_favorite_playlist(int(limit/2), offset, "DATE".encode("utf-8"), "ASC".encode("utf-8"))
            elif method == "top":
                Tproduct = lib.get_artist_toptracks(int(misc), limit, offset)
            elif method == "ar-al":
                Tproduct = lib.get_artist_albums(int(misc), limit, offset)
            elif method == "al-tr":
                Tproduct = lib.get_album_items(int(misc), limit, offset)
            elif method == "pl-tr":
                Tproduct = lib.get_playlist_items(misc.encode("utf-8"), limit, offset)
            elif method == "search":
                print(misc)
                Tproduct = misc
            product = self.helperFactory(Tproduct, typ, offset, product)
            time.sleep(0.1)
            if Tproduct.arraySize != limit:
                break
            else:
                offset += limit
        return product

    def favver(self, which):
        print('favving')
        # self.favs = self.favourite.tracks()
        if "track" in which:
            self.favs = self.assembleFactory("fav", "track")
        if "artist" in which:
            self.favArts = self.assembleFactory("fav", "artist")
        if "album" in which:
            self.favAlbs = self.assembleFactory("fav", "album")
        if "playlist" in which:
            self.favPlys = self.assembleFactory("fav", "playlist")
        # self.favArts = self.favourite.artists()
        # self.favArts = lib.get_favorite_artist()
        time.sleep(0.2)
        # self.favAlbs = self.favourite.albums()
        # self.favArts = lib.get_favorite_album()
        time.sleep(0.2)
        # self.favPlys = self.favourite.playlists()
        # self.favPlys = lib.get_favorite_playlist()
        # time.sleep(0.2)
        # self.favIds = self.favourite.videos()


if __name__ == "__main__":
    # Dev/Use mode
    version = 'HBud Alpha 0.1 Snapshot 1'
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
    # Translate
    APP = "htidal"
    WHERE_AM_I = os.path.abspath(os.path.dirname(__file__))
    LOCALE_DIR = os.path.join(WHERE_AM_I, 'translations/mo')
    locale.setlocale(locale.LC_ALL, locale.getlocale())
    locale.bindtextdomain(APP, LOCALE_DIR)
    gettext.bindtextdomain(APP, LOCALE_DIR)
    gettext.textdomain(APP)
    gg = gettext.gettext
    # parser = ConfigParser()
    user = os.popen("who|awk '{print $1}'r").read()
    user = user.rstrip()
    user = user.split('\n')[0]
    if os.path.exists(f"/home/{user}/.config/htidal/htidal.ini"):
        print('Configured already')
        confA = True
        parser.read(f"/home/{user}/.config//htidal/htidal.ini")
        emailC = parser.get('login', 'email')
        qualityC = parser.get('misc', 'quality')
    else:
        print("Not configured yet")
        confA = False
        emailC = ''
        qualityC = '0'
        parser.add_section('login')
        parser.add_section('misc')
    # GUI
    UI_FILE = "hbud.glade"
    Gst.init(None)
    app = GUI()
    os.system("mkdir -p /tmp/htidal/thumbnails")
    Gtk.main()