#!/usr/bin/python3
import os, gettext, locale
from hbud import LANGUAGES, HBud, CONSTANTS

def main():
    lang = os.getenv('LANG', 'en_US.UTF-8')
    chosen_lang = 'en'
    for l in LANGUAGES:
        if lang.split('_')[0] == l:
            chosen_lang = l
            break
    print(chosen_lang)

    if os.getenv('container', '') != 'flatpak':
        print("Running in development mode")
        locale_dir = os.path.join(os.path.dirname(os.path.abspath("__file__")), "{}locales".format(os.getenv("HDIR", "")))
        print(locale_dir)
        gettext.bindtextdomain(CONSTANTS["app_id"], locale_dir)
        gettext.textdomain(CONSTANTS["app_id"])
        locale.setlocale(locale.LC_ALL, locale.getlocale())
        locale.bindtextdomain(CONSTANTS["app_id"], locale_dir)
    else:
        print("Running in sandboxed mode")
        gettext.bindtextdomain(CONSTANTS["app_id"], "/app/share/hbud/locales")
        gettext.textdomain(CONSTANTS["app_id"])
        locale.setlocale(locale.LC_ALL, locale.getlocale())
        locale.bindtextdomain(CONSTANTS["app_id"], "/app/share/hbud/locales")

    HBud.run()

if __name__ == '__main__':
    main()