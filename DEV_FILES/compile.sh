#!/bin/bash

nuitka3 --standalone --nofollow-import-to=pytest --python-flag=nosite,-O --plugin-enable=anti-bloat,implicit-imports,pylint-warnings --clang --warn-implicit-exceptions --warn-unusual-code --prefer-source-code HBud.py
upx -9 HBud.dist/HBud
