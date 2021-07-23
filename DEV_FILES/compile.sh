#!/bin/bash

nuitka3 HBud.py --nofollow-imports --include-module=mediafile --include-module=srt --include-module=six --include-module=mutagen --include-module=dbus
