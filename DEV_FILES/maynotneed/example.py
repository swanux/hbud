#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, gi, time
from threading import Thread
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

Gst.init()

main_loop = GLib.MainLoop()
thread = Thread(target=main_loop.run)
thread.start()

url = os.popen(f"youtube-dl --format m4a --get-url https://www.youtube.com/watch?v=ndl1W4ltcmg").read()
#player = Gst.parse_launch(f"souphttpsrc is-live=false location={url} ! decodebin ! audioconvert ! autoaudiosink")
player = Gst.parse_launch(f"playbin uri={url}")
#url = "file:///home/daniel/Music/Bonnie Tyler - Holding Out for a Hero - From 'Footloose' Soundtrack.mp3"
#player = Gst.parse_launch("playbin")
#player.set_property("uri", url)
player.set_state(Gst.State.PLAYING)
time.sleep(5)
player.seek_simple(Gst.Format.BYTES,  Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, 120000)

player.seek_simple(Gst.Format.TIME,  Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, 20 * Gst.SECOND)

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    pass

player.set_state(Gst.State.NULL)
main_loop.quit()
