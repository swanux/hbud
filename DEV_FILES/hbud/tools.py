#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi, os
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, GLib
from configparser import ConfigParser

# def themer(provider, window, v, c, w=""):
#         css = """#cover_img {
#             padding-bottom: %spx;
#         }
#         menu, .popup {
#             border-radius: %spx;
#         }
#         decoration, headerbar{
#             border-radius: %spx;
#         }
#         button, menuitem, entry {
#             border-radius: %spx;
#             margin: 5px;
#         }
#         .titlebar {
#             border-top-left-radius: %spx;
#             border-top-right-radius: %spx;
#             border-bottom-left-radius: 0px;
#             border-bottom-right-radius: 0px;
#         }
#         window, notebook, stack, box, scrolledwindow, viewport {
#             border-top-left-radius: %spx;
#             border-top-right-radius: %spx;
#             border-bottom-left-radius: %spx;
#             border-bottom-right-radius: %spx;
#             border-width: 0px;
#             border-image: none;
#             box-shadow: none;
#         }
#         switch:checked, highlight, selection, menuitem:hover {
#             background-color: %s;
#         }
#         tab:checked {
#             box-shadow: 0 -4px %s inset;
#         }
#         #search_play:focus, spinbutton:focus {
#             box-shadow: 0 0 0 1px %s;
#         }
#         #trackbox_%s{
#             background: %s;
#             color: #000;
#             border-radius: %spx;
#         }
#         .maximized, .fullscreen, .maximized .titlebar {
#             border-radius: 0px;
#         }""" % (float(v)/2.6,float(v)/1.5,v,v,v,v,v,v,v,v,c,c,c,w,c,v)
#         css = str.encode(css)
#         provider.load_from_data(css)
#         GLib.idle_add(window.get_style_context().add_provider_for_display, Gdk.Display.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

def themer(provider, window, c, w=""):
        css = """picture {
            border-radius: 10px;
        }
        switch:checked, highlight, selection, menuitem:hover {
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
    
# def diabuilder (text, title, mtype, buts, window):
    # x, y = window.get_position()
    # sx, sy = window.get_size()
    # dialogWindow = Gtk.MessageDialog(parent=window, modal=True, destroy_with_parent=True, message_type=mtype, buttons=buts, text=text, title=title)
    # dialogWindow.set_transient_for(window)
    # dsx, dsy = dialogWindow.get_size()
    # dialogWindow.move(x+((sx-dsx)/2), y+((sy-dsy)/2))
    # dialogWindow.present()
    # dialogWindow.run()
    # dialogWindow.destroy()

def get_lyric(title, artist, DAPI):
    DAPI.title, DAPI.artist = title, artist
    try: result = DAPI.getLyrics()
    except: result = 0
    return result

def real_init():
    # user = GLib.get_user_name()
    parser, confP = ConfigParser(), f"{GLib.get_user_config_dir()}/hbud.ini"
    needsWrite = False
    if not os.path.isfile(confP):
        print("No config file yet")
        os.system(f"touch {confP}")
        needsWrite = True
    else: parser.read(confP)
    dataList = {}
    for (y, x, z) in zip(["subtitles", "gui", "services", "misc"], [["size", "margin", "bg"], ["theme", "color"], ["MusixMatch", "AZLyrics", "Letras.br", "CoverSize"], ["autoscroll", "positioning", "minimal_mode"]], [[str(30), str(66), "False"], [str(0), "rgb(17, 148, 156)"], ["True", "True", "True", str(500)], ["True", "5", "False"]]):
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
    return parser, confP, dataList["theme"], dataList["color"], dataList["MusixMatch"], dataList["AZLyrics"], dataList["Letras.br"], dataList["CoverSize"], dataList["size"], dataList["margin"], dataList["bg"], dataList["autoscroll"], dataList["positioning"], dataList["minimal_mode"]