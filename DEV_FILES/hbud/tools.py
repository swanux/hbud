#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi, os
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, GLib
from configparser import ConfigParser

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
        }""" % (c,w,c)
        css = str.encode(css)
        provider.load_from_data(css)
        GLib.idle_add(window.get_style_context().add_provider_for_display, Gdk.Display.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

def get_lyric(title, artist, DAPI):
    DAPI.title, DAPI.artist = title, artist
    try: result = DAPI.getLyrics()
    except: result = 0
    return result

def real_init():
    parser, confP = ConfigParser(), f"{GLib.get_user_config_dir()}/hbud.ini"
    needsWrite = False
    if not os.path.isfile(confP):
        print("No config file yet")
        os.system(f"touch {confP}")
        needsWrite = True
    else: parser.read(confP)
    dataList = {}
    for (y, x, z) in zip(["subtitles", "gui", "services", "misc"], [["size", "margin", "bg"], ["theme", "color"], ["MusixMatch", "AZLyrics", "Letras.br", "CoverSize"], ["autoscroll", "positioning", "minimal_mode", "hwa_enabled"]], [[str(30), str(66), "False"], [str(0), "rgb(17, 148, 156)"], ["True", "True", "True", str(500)], ["True", "5", "False", "True"]]):
        if parser.has_section(y) == False:
            parser.add_section(y)
            needsWrite = True
        for (i, d) in zip(x, z):
            if parser.has_option(y, i): dataList[i] = parser.get(y, i)
            else:
                parser.set(y, i, d)
                dataList[i] = d
                needsWrite = True
    if needsWrite:
        print("Needed to update config")
        with open(confP, "w+") as f: parser.write(f)
        needsWrite = False
    return parser, confP, dataList["theme"], dataList["color"], dataList["MusixMatch"], dataList["AZLyrics"], dataList["Letras.br"], dataList["CoverSize"], dataList["size"], dataList["margin"], dataList["bg"], dataList["autoscroll"], dataList["positioning"], dataList["minimal_mode"], dataList["hwa_enabled"]