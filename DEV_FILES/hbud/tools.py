#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi, os
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from configparser import ConfigParser

def themer(provider, window, v, c, w=""):
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
        tab:checked {
            box-shadow: 0 -4px %s inset;
        }
        #search_play:focus, spinbutton:focus {
            box-shadow: 0 0 0 1px %s;
        }
        #trackbox_%s{
            background: %s;
            color: #000;
            border-radius: %spx;
        }
        .maximized, .fullscreen, .maximized .titlebar {
            border-radius: 0px;
        }""" % (float(v)/2.6,float(v)/1.5,v,v,v,v,v,v,c,c,c,w,c,v)
        css = str.encode(css)
        provider.load_from_data(css)
        window.get_style_context().add_provider_for_screen(Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    
def diabuilder (text, title, mtype, buts, window):
    x, y = window.get_position()
    sx, sy = window.get_size()
    dialogWindow = Gtk.MessageDialog(parent=window, modal=True, destroy_with_parent=True, message_type=mtype, buttons=buts, text=text, title=title)
    dsx, dsy = dialogWindow.get_size()
    dialogWindow.move(x+((sx-dsx)/2), y+((sy-dsy)/2))
    dialogWindow.show_all()
    dialogWindow.run()
    dialogWindow.destroy()

def get_lyric(title, artist, DAPI):
    DAPI.title, DAPI.artist = title, artist
    try: result = DAPI.getLyrics()
    except: result = 0
    return result

def real_init():
    user = os.popen("who|awk '{print $1}'r").read().rstrip().split('\n')[0]
    parser, confP = ConfigParser(), f"/home/{user}/.config/hbud.ini"
    try: parser.read(confP)
    except: print("No config file yet")
    if not os.path.isfile(confP):
        os.system(f"touch {confP}")
        # parser.add_section('subtitles')
        # parser.set('subtitles', 'margin', str(66))
        # parser.set('subtitles', 'size', str(30))
        # parser.set('subtitles', 'bg', "False")
        parser.add_section('gui')
        parser.set('gui', 'rounded', "10")
        parser.set('gui', 'dark', "False")
        parser.set('gui', 'color', "rgb(17, 148, 156)")
        parser.add_section('services')
        parser.set('services', 'MusixMatch', "True")
        parser.set('services', 'AZLyrics', "True")
        parser.set('services', 'Letras.br', "True")
        parser.set('services', 'CoverSize', "500")
        file = open(confP, "w+")
        parser.write(file)
        file.close()
    # sSize, sMarg, bg = parser.get('subtitles', 'size'), parser.get('subtitles', 'margin'), parser.get('subtitles', 'bg')
    rounded, dark, color = parser.get('gui', 'rounded'), parser.get('gui', 'dark'), parser.get('gui', 'color')
    musix, azlyr, letras, coverSize = parser.get('services', 'MusixMatch'), parser.get('services', 'AZLyrics'), parser.get('services', 'Letras.br'), int(parser.get('services', 'CoverSize'))
    return user, parser, confP, rounded, dark, color, musix, azlyr, letras, coverSize
    # sSize, sMarg, bg,