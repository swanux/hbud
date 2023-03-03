#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, GLib

def themer(provider, window, c, w=""):
        css = """image {
            border-radius: 10px;
        }
        #videosink {
            border-radius: 0px;
            background: black;
        }
        switch:checked, highlight, menuitem:hover {
            background-color: %s;
        }
        #trackbox_%s{
            background: %s;
            color: #000;
            border-radius: 10px;
        }
        #overlay_scale slider {                                                                                      
            background-size: 100px 100px;                                                                   
            min-width: 100px;                                                                               
            min-height: 100px;                                                                              
        }""" % (c,w,c)
        css = str.encode(css)
        provider.load_from_data(css)
        GLib.idle_add(window.get_style_context().add_provider_for_display, Gdk.Display.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

def get_lyric(title, artist, DAPI):
    DAPI.title, DAPI.artist = title, artist
    try: result = DAPI.getLyrics()
    except: result = 0
    return result