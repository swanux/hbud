#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#________________________________________________________________________________ BEGINNING OF INIT ____________________________________________________________#

# Version of the program
version = 'HSuite v0.8.1 | Quake'
v = ''

### Import modules ###

# Set program root location
import os, subprocess, gettext, apt, shlex, locale, gi, re, webbrowser, time, notify2, platform, sys, dbus
if os.path.exists('/home/daniel/GitRepos/hsuite'):
    fdir = "/home/daniel/GitRepos/hsuite/DEV_FILES/"
    print(fdir)
    os.chdir(fdir)
    print('Running in development mode.')
else:
    fdir = "/usr/share/hsuite/"
    print(fdir)
    os.chdir(fdir)
    print('Running in production mode.')
# Translation
APP = "hsuite"
WHERE_AM_I = os.path.abspath(os.path.dirname(__file__))
LOCALE_DIR = os.path.join(WHERE_AM_I, 'translations/mo')
locale.setlocale(locale.LC_ALL, locale.getlocale())
locale.bindtextdomain(APP, LOCALE_DIR)
# locale.textdomain(APP)
gettext.bindtextdomain(APP, LOCALE_DIR)
gettext.textdomain(APP)
_ = gettext.gettext
print(_('Temporarly here'))
# Import GUI modules
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, GLib, Gdk, GObject, Gio
from cron_descriptor import get_description
from crontab import CronTab
# Config
from configparser import ConfigParser
# Running background processes
from threading import Thread
from concurrent import futures
# Using time
from datetime import date
# URL handling
from urllib.request import urlopen
from decimal import Decimal
# Own module for descriptions
import details as d
import htransfer, husb
from aptdaemon import client, enums
from aptdaemon.gtk3widgets import AptProgressBar

### Declare global variables ###

# Date
today = date.today()
month = today.strftime("%m")
day = today.strftime("%d")
year = today.strftime("%Y")

# Getting the name of the non-root user
user = os.popen("who|awk '{print $1}'r").read()
try:
    dplenv = int(os.popen("echo $DISPLAY").read().rstrip().replace(':', ''))
except:
    print('no dplenv for now')
# Edit to only contain the name itself
user = user.rstrip()
user = user.split('\n')[0]

# Used with Distro Boutique
# It's declared because of some functions which ones are called from concurrent future
fn = 'sth'
# The name of the currently in progress download
shDict = {'downl_mint': 'True', 'downl_ubuntu': 'True', 'downl_solus': 'True', 'downl_deepin': 'True', 'downl_steamos': 'True', 'downl_deb': 'True',
          'downl_fedora': 'True', 'downl_suse': 'True', 'downl_gentoo': 'True', 'downl_arch': 'True', 'downl_lfs': 'True', 'downl_drauger' : 'True', 'downl_slax' : 'True', 'downl_puppy' : 'True', 'downl_tiny' : 'True', 'downl_sparky' : 'True', 'downl_bodhi' : 'True'}  # Dictionary for current state of download buttons (clickable or not)
dlist = ['downl_mint', 'downl_ubuntu', 'downl_solus', 'downl_deepin', 'downl_steamos',
         'downl_fedora', 'downl_suse', 'downl_deb', 'downl_arch', 'downl_gentoo', 'downl_lfs', 'downl_drauger', 'downl_slax', 'downl_puppy', 'downl_tiny', 'downl_sparky', 'downl_bodhi']
namDict = {'downl_mint' : 'Linux Mint', 'downl_ubuntu' : 'Ubuntu', 'downl_solus' : 'Solus Linux', 'downl_deepin' : 'Deepin Linux', 'downl_steamos' : 'SteamOS',
         'downl_fedora' : 'Fedora', 'downl_suse' : 'openSUSE', 'downl_deb' : 'Debian', 'downl_arch' : 'Arch', 'downl_gentoo' : 'Gentoo', 'downl_lfs' : 'Linux from Scratch (LFS)', 'downl_drauger' : 'Drauger OS', 'downl_slax' : 'Slax', 'downl_puppy' : 'Puppy Linux', 'downl_tiny' : 'Tiny Core', 'downl_sparky' : 'SparkyLinux', 'downl_bodhi' : 'Bodhi Linux'}
# List of distros
dlistLen = len(dlist)                   # The number of distros
toChoseDir = {
    'mint_choser' : {_('Cinnamon (Default)') : 'cinnamon', 'MATE' : 'mate', 'XFCE' : 'xfce', _('Debian Edition') : 'lmde'},

    'ubuntu_choser' : {_('Gnome (Default)') : 'ubuntu', 'Kubuntu (KDE)' : 'kubuntu', 'Lubuntu (LXQt)' : 'lubuntu', 'Budgie' : 'ubuntu-budgie', 'Kylin' : 'ubuntukylin', 'MATE' : 'ubuntu-mate', _('Studio') : 'ubuntustudio', 'Xubuntu (XFCE)' : 'xubuntu'},

    'solus_chose' : {_('Budgie (Default)') : 'Budgie', 'Gnome' : 'GNOME', 'MATE' : 'MATE', 'KDE' : 'Plasma'},

    'deb_chose' : {'Cinnamon' : 'cinnamon', 'Gnome' : 'gnome', 'KDE' : 'kde', 'LXDE' : 'lxde', 'LXQt' : 'lxqt', 'MATE' : 'mate', 'XFCE' : 'xfce'},

    'fedora_chose' : {_('Gnome (Default)') : 'default', 'KDE' : 'KDE', 'XFCE' : 'Xfce', 'LXQt' : 'LXQt', 'LXDE' : 'LXDE', 'MATE' : 'MATE_Compiz', 'Cinnamon' : 'Cinnamon', 'SOAS' : 'SoaS'},

    'suse_chose' : {_('Tumbeweed (Rolling)') : 'roll', _('Leap (Standard)') : 'stay'}
    }

# Used with App Spotlight
# Check if PKG cache is already in memory or not
appList = ['opera-stable', 'barrier', 'google-chrome-stable', 'epiphany-browser', 'firefox', 'vivaldi-stable', 'wps-office', 'libreoffice', 'onlyoffice-desktopeditors', 'softmaker-freeoffice-2018', 'gedit', 'emacs', 'code', 'atom', 'sublime-text', 'geany', 'skypeforlinux', 'discord', 'telegram-desktop', 'signal-desktop', 'hexchat', 'franz', '0ad', 'supertux', 'lutris', 'playonlinux', 'steam', 'minecraft-launcher', 'popsicle', 'woeusb', 'winehq-staging', 'virtualbox-6.1', 'gparted', 'fusuma', 'audacity', 'deja-dup', 'timeshift', 'teamviewer', 'gnome-boxes', 'supertuxkart', 'henv', 'publii', 'vlc', 'meld', 'transmission-gtk', 'htidal']                                                                        # The list with the debian app names

butDict = {'opera-stable': 'opera', 'barrier': 'barr', 'google-chrome-stable': 'chrome', 'epiphany-browser': 'web', 'firefox': 'firefox', 'vivaldi-stable': 'vivaldi', 'wps-office': 'woffice', 'libreoffice': 'loffice', 'onlyoffice-desktopeditors': 'ooffice', 'softmaker-freeoffice-2018': 'foffice', 'gedit': 'gedit', 'emacs': 'gnu', 'code': 'vscode', 'atom': 'atom', 'sublime-text': 'stedit', 'geany': 'geany', 'skypeforlinux': 'skype', 'discord': 'discord', 'telegram-desktop': 'telegram', 'signal-desktop': 'signal', 'hexchat': 'hex', 'franz': 'franz', '0ad': 'ad', 'supertux': 'tux', 'lutris': 'lutris', 'playonlinux': 'pol', 'steam': 'steam', 'minecraft-launcher': 'mc', 'popsicle': 'pops', 'woeusb': 'woe', 'winehq-staging': 'wine', 'virtualbox-6.1': 'vbox', 'gparted': 'gparted', 'fusuma': 'gest', 'audacity': 'auda', 'deja-dup': 'deja', 'timeshift': 'tims', 'teamviewer': 'tw', 'gnome-boxes': 'box', 'supertuxkart': 'skart', 'henv' : 'henv', 'publii' : 'publii', 'vlc' : 'vlc', 'meld' : 'meld', 'transmission-gtk' : 'transm', 'htidal' : 'htidal'}                                # Dictionary with the context of debname:buttonName

appListLen = len(appList)          
                 # Number of apps
statDict = {'Opera': '', 'Chrome': '', 'Web': '', 'Firefox': '', 'Vivaldi': '', 'Edge': '', 'WPS Office': '', 'Libreoffice': '', 'Only Office': '', 'Free Office': '', 'Gedit': '', 'GNU Emacs': '', 'VS Code': '', 'Atom Editor': '', 'Sublime Text Editor': '', 'Geany': '', 'Skype': '', 'Discord': '', 'Telegram': '', 'Signal': '', 'HexChat': '', 'Franz': '', '0 A.D.': '', 'SuperTuxKart': '', 'SuperTux': '', 'Lutris': '', 'Barrier': '', 'Play On Linux': '', 'Steam': '', 'Minecraft': '', 'Popsicle': '', 'WoeUSB': '', 'Wine': '', 'Virtualbox-6.1': '', 'GParted': '', 'fusuma': '', 'Audacity': '', 'Déja-Dup': '', 'Timeshift': '', 'TeamViewer': '', 'Gnome Boxes': '', 'HEnv' : '', 'Publii' : '', 'HTidal' : '', 'VLC' : '', 'Meld' : '', 'Transmission' : ''}  # store the status (installed or not)

layDict = {'opera-stable': 'Opera', 'google-chrome-stable': 'Chrome', 'epiphany-browser': 'Web', 'firefox': 'Firefox', 'vivaldi-stable': 'Vivaldi', 'dikk': 'Edge', 'wps-office': 'WPS Office', 'libreoffice': 'Libreoffice', 'onlyoffice-desktopeditors': 'Only Office', 'softmaker-freeoffice-2018': 'Free Office', 'gedit': 'Gedit', 'emacs': 'GNU Emacs', 'code': 'VS Code', 'atom': 'Atom Editor', 'sublime-text': 'Sublime Text Editor', 'geany': 'Geany', 'skypeforlinux': 'Skype', 'discord': 'Discord', 'telegram-desktop': 'Telegram', 'signal-desktop': 'Signal', 'hexchat': 'HexChat', 'franz': 'Franz', '0ad': '0 A.D.', 'supertux': 'SuperTux', 'supertuxkart': 'SuperTuxKart', 'lutris': 'Lutris', 'barrier': 'Barrier', 'playonlinux': 'Play On Linux', 'steam': 'Steam', 'minecraft-launcher': 'Minecraft', 'popsicle': 'Popsicle', 'woeusb': 'WoeUSB', 'winehq-staging': 'Wine', 'virtualbox-6.1': 'Virtualbox', 'gparted': 'GParted', 'fusuma': 'fusuma', 'audacity': 'Audacity', 'deja-dup': 'Déja-Dup', 'timeshift': 'Timeshift', 'teamviewer': 'TeamViewer', 'gnome-boxes': 'Gnome Boxes', 'henv' : 'HEnv', 'publii' : 'Publii', 'htidal' : 'HTidal', 'vlc' : 'VLC', 'meld' : 'Meld', 'transmission-gtk' : 'Transmission'}                                          # debname:displayName

srcDict = {
    'barrweb' : 'https://github.com/debauchee/barrier',
    'boxweb' : 'https://gitlab.gnome.org/GNOME/gnome-boxes/',
    'timweb' : 'https://github.com/teejee2008/timeshift',
    'dejaweb' : 'https://gitlab.gnome.org/World/deja-dup',
    'audaweb' : 'https://github.com/audacity/audacity',
    'gestweb' : 'https://github.com/iberianpig/fusuma',
    'partweb' : 'https://gitlab.gnome.org/GNOME/gparted',
    'vboxweb' : 'https://www.virtualbox.org/browser/vbox/trunk',
    'wineweb' : 'https://github.com/wine-mirror/wine',
    'woeweb' : 'https://github.com/WoeUSB',
    'popweb' : 'https://github.com/pop-os/popsicle',
    'kartweb' : 'https://github.com/supertuxkart/stk-code',
    'polweb' : 'https://github.com/PlayOnLinux/POL-POM-4',
    'lutweb' : 'https://github.com/lutris/lutris',
    'tuxweb' : 'https://github.com/SuperTux/supertux',
    'adweb' : 'https://gitlab.com/0ad/0ad',
    'franzweb' : 'https://github.com/meetfranz/franz',
    'hexweb' : 'https://github.com/hexchat/hexchat',
    'sigweb' : 'https://github.com/signalapp',
    'telweb' : 'https://github.com/TelegramOrg',
    'geanweb' : 'https://github.com/geany/geany',
    'atomweb' : 'https://github.com/atom/atom',
    'vsweb' : 'https://github.com/microsoft/vscode',
    'gedweb' : 'https://gitlab.gnome.org/GNOME/gedit',
    'libreweb' : 'https://github.com/LibreOffice/core',
    'vivweb' : 'https://github.com/ric2b/Vivaldi-browser',
    'webweb' : 'https://gitlab.gnome.org/GNOME/epiphany',
    'suiteweb' : 'https://github.com/swanux/hsuite',
    'envweb' : 'https://github.com/swanux/henv',
    'htidalweb' : 'https://github.com/swanux/htidal',
    'transmweb' : 'https://github.com/transmission/transmission',
    'meldweb' : 'https://gitlab.gnome.org/GNOME/meld',
    'vlcweb' : 'https://www.videolan.org/vlc/download-sources.html',
    'publiiweb' : 'https://github.com/GetPublii/Publii'
}

liLi = {
    'opera_but' : ['Opera', 'opera-stable', 'opera-codecs', 0],
    'chrome_but' : ['Chrome', 'google-chrome-stable', '', 1],
    'web_but' : ['Web', 'epiphany-browser', '', 2],
    'firefox_but' : ['Firefox', 'firefox', '', 3],
    'vivaldi_but' : ['Vivaldi', 'vivaldi-stable', '', 4],
    'edge_but' : ['', '', '', 5],
    'woffice_but' : ['WPS Office', 'wps-office', 'ttf-wps-fonts', 6],
    'loffice_but' : ['Libreoffice', 'libreoffice', '', 7],
    'ooffice_but' : ['Only Office', 'onlyoffice-desktopeditors', '', 8],
    'foffice_but' : ['Free Office', 'softmaker-freeoffice-2018', '', 11],
    'gedit_but' : ['Gedit', 'gedit', 'gedit-plugins', 12],
    'gnu_but' : ['GNU Emacs', 'emacs', '', 13],
    'vscode_but' : ['VS Code', 'code', '', 14],
    'atom_but' : ['Atom Editor', 'atom', '', 15],
    'stedit_but' : ['Sublime Text Editor', 'sublime-text', '', 16],
    'geany_but' : ['Geany', 'geany', '', 17],
    'skype_but' : ['Skype', 'skypeforlinux', '', 18],
    'discord_but' : ['Discord', 'discord', '', 19],
    'telegram_but' : ['Telegram', 'telegram-desktop', '', 20],
    'signal_but' : ['Signal', 'signal-desktop', '', 21],
    'hex_but' : ['HexChat', 'hexchat', '', '', '', 22],
    'franz_but' : ['Franz', 'franz', '', 23],
    '0ad_but' : ['0 A.D.', '0ad', '', 24],
    'skart_but' : ['SuperTuxKart', 'supertuxkart', '', 30],
    'tux_but' : ['SuperTux', 'supertux', '', 25],
    'lutris_but' : ['Lutris', 'lutris', '', 26],
    'barr_but' : ['Barrier', 'barrier', '', 42],
    'pol_but' : ['Play On Linux', 'playonlinux', '', 27],
    'steam_but' : ['Steam', 'steam-installer', '', 28],
    'mc_but' : ['Minecraft', 'minecraft-launcher', '', 29],
    'pops_but' : ['Popsicle', 'popsicle', 'popsicle-gtk', 31],
    'hsuite_but' : ['', '', '', 62],
    'henv_but' : ['HEnv', 'henv', '', 63],
    'woe_but' : ['WoeUSB', 'woeusb', '', 32],
    'wine_but' : ['Wine', 'winehq-staging', '', 33],
    'vbox_but' : ['Virtualbox', 'virtualbox-6.1', '', 34],
    'gparted_but' : ['GParted', 'gparted', 'gpart', 35],
    'gest_but' : ['fusuma', 'fusuma', 'wmctrl libinput-tools xdotool', 36],
    'auda_but' : ['Audacity', 'audacity', '', 37],
    'deja_but' : ['Déja-Dup', 'deja-dup', '', 38],
    'tims_but' : ['Timeshift', 'timeshift', '', 39],
    'tw_but' : ['TeamViewer', 'teamviewer', '', 40],
    'box_but' : ['Gnome Boxes', 'gnome-boxes', '', 41],
    'publii_but' : ['Publii', 'publii', '', 64],
    'htidal_but' : ['HTidal', 'htidal', '', 65],
    'transm_but' : ['Transmission', 'transmission-gtk', '', 66],
    'vlc_but' : ['VLC Media Player', 'vlc', '', 67],
    'meld_but' : ['Meld', 'meld', '', 68]
    }
loLa = {'mint' : 43, 'ubuntu' : 44, 'solus' : 45, 'deepin' : 46, 'elementary' : 47, 'steamos' : 48, 'deb' : 49, 'fedora' : 50, 'opsu' : 51, 'arch' : 52, 'gentoo' : 53, 'lfs' : 54, 'drauger' : 55, 'slax' : 56, 'pepper' : 57, 'bodhi' : 58, 'sparky' : 59, 'puppy' : 60, 'tiny' : 61}

extDat = { # FIXME
    0 : ['places-menu@gnome-shell-extensions.gcampax.github.com', 'drive-menu@gnome-shell-extensions.gcampax.github.com','dash-to-dock@micxgx.gmail.com', 'appindicatorsupport@rgcjonas.gmail.com', 'Move_Clock@rmy.pobox.com', 'user-theme@gnome-shell-extensions.gcampax.github.com'],
    1 : ['appindicatorsupport@rgcjonas.gmail.com', 'user-theme@gnome-shell-extensions.gcampax.github.com', 'dash-to-panel@jderose9.github.com', 'arc-menu@linxgem33.com', 'remove-dropdown-arrows@mpdeimos.com', 'TopIcons@phocean.net'],
    2 : ['dash-to-dock@micxgx.gmail.com', 'user-theme@gnome-shell-extensions.gcampax.github.com', 'Move_Clock@rmy.pobox.com', 'appindicatorsupport@rgcjonas.gmail.com', 'unite@hardpixel.eu']
}

themDat = { # FIXME
    _('Desktop theme') : 
    {
        'Gnome' : [
            'cd ~/ && wget https://github.com/swanux/hsuite/raw/master/DEV_FILES/themes_src/Mojave-dark-20200519113011.tar.xz && tar -xf Mojave-dark-20200519113011.tar.xz && rm -rf ~/.themes/Mojave-dark && mv Mojave-dark ~/.themes/ && gsettings set org.gnome.shell.extensions.user-theme name "Mojave-dark" && gsettings set org.gnome.desktop.interface gtk-theme "Mojave-dark" && rm -rf ~/.themes/Unity-8-2.0 ~/.themes/Windows-10-Dark-3.2-dark',
            'cd ~/ && wget https://github.com/swanux/hsuite/raw/master/DEV_FILES/themes_src/Windows-10-Dark-3.2-dark.tar.gz && tar -xf Windows-10-Dark-3.2-dark.tar.gz && rm -rf ~/.themes/Windows-10-Dark-3.2-dark && mv Windows-10-Dark-3.2-dark ~/.themes/ && gsettings set org.gnome.shell.extensions.user-theme name "Windows-10-Dark-3.2-dark" && gsettings set org.gnome.desktop.interface gtk-theme "Windows-10-Dark-3.2-dark" && rm -rf ~/.themes/Unity-8-2.0 ~/.themes/Mojave-dark',
            'cd ~/ && wget https://github.com/swanux/hsuite/raw/master/DEV_FILES/themes_src/Unity-8-2.0.tar.gz && tar -xf Unity-8-2.0.tar.gz && rm -rf ~/.themes/Unity-8-2.0 && mv Unity-8-2.0 ~/.themes/ && gsettings set org.gnome.shell.extensions.user-theme name "Unity-8-2.0" && gsettings set org.gnome.desktop.interface gtk-theme "Unity-8-2.0" && rm -rf ~/.themes/Mojave-dark ~/.themes/Windows-10-Dark-3.2-dark'
        ],
        'MATE' : [
            """cd ~/ && wget https://github.com/swanux/hsuite/raw/master/DEV_FILES/themes_src/Mojave-dark-20200519113011.tar.xz && tar -xf Mojave-dark-20200519113011.tar.xz && rm -rf ~/.themes/Mojave-dark && mv Mojave-dark ~/.themes/ && dconf write /org/mate/desktop/interface/gtk-theme "'Mojave-dark'" && dconf write /org/mate/marco/general/theme "'Mojave-dark'" && rm -rf ~/.themes/Unity-8-2.0 ~/.themes/Windows-10-Dark-3.2-dark""",
            """cd ~/ && wget https://github.com/swanux/hsuite/raw/master/DEV_FILES/themes_src/Windows-10-Dark-3.2-dark.tar.gz && tar -xf Windows-10-Dark-3.2-dark.tar.gz && rm -rf ~/.themes/Windows-10-Dark-3.2-dark && mv Windows-10-Dark-3.2-dark ~/.themes/ && dconf write /org/mate/desktop/interface/gtk-theme "'Windows-10-Dark-3.2-dark'" && dconf write /org/mate/marco/general/theme "'Windows-10-Dark-3.2-dark'" && rm -rf ~/.themes/Unity-8-2.0 ~/.themes/Mojave-dark""",
            """cd ~/ && wget https://github.com/swanux/hsuite/raw/master/DEV_FILES/themes_src/Unity-8-2.0.tar.gz && tar -xf Unity-8-2.0.tar.gz && rm -rf ~/.themes/Unity-8-2.0 && mv Unity-8-2.0 ~/.themes/ && dconf write /org/mate/desktop/interface/gtk-theme "'Unity-8-2.0'" && "'Unity-8-2.0'" && rm -rf ~/.themes/Mojave-dark ~/.themes/Windows-10-Dark-3.2-dark"""
        ],
        'Budgie' : [
            'cd ~/ && wget https://github.com/swanux/hsuite/raw/master/DEV_FILES/themes_src/Mojave-dark-20200519113011.tar.xz && tar -xf Mojave-dark-20200519113011.tar.xz && rm -rf ~/.themes/Mojave-dark && mv Mojave-dark ~/.themes/ && gsettings set org.gnome.desktop.interface gtk-theme "Mojave-dark" && rm -rf ~/.themes/Unity-8-2.0 ~/.themes/Windows-10-Dark-3.2-dark',
            'cd ~/ && wget https://github.com/swanux/hsuite/raw/master/DEV_FILES/themes_src/Windows-10-Dark-3.2-dark.tar.gz && tar -xf Windows-10-Dark-3.2-dark.tar.gz && rm -rf ~/.themes/Windows-10-Dark-3.2-dark && mv Windows-10-Dark-3.2-dark ~/.themes/ && gsettings set org.gnome.desktop.interface gtk-theme "Windows-10-Dark-3.2-dark" && rm -rf ~/.themes/Unity-8-2.0 ~/.themes/Mojave-dark',
            'cd ~/ && wget https://github.com/swanux/hsuite/raw/master/DEV_FILES/themes_src/Unity-8-2.0.tar.gz && tar -xf Unity-8-2.0.tar.gz && rm -rf ~/.themes/Unity-8-2.0 && mv Unity-8-2.0 ~/.themes/ && gsettings set org.gnome.desktop.interface gtk-theme "Unity-8-2.0" && rm -rf ~/.themes/Mojave-dark ~/.themes/Windows-10-Dark-3.2-dark'
        ],
        'Cinnamon' : [
            'cd ~/ && wget https://github.com/swanux/hsuite/raw/master/DEV_FILES/themes_src/Mojave-dark-20200519113011.tar.xz && tar -xf Mojave-dark-20200519113011.tar.xz && rm -rf ~/.themes/Mojave-dark && mv Mojave-dark ~/.themes/ && gsettings set org.cinnamon.theme name "Mojave-dark" && gsettings set org.cinnamon.desktop.interface gtk-theme "Mojave-dark" && gsettings set org.cinnamon.desktop.wm.preferences theme "Mojave-dark" && rm -rf ~/.themes/Unity-8-2.0 ~/.themes/Windows-10-Dark-3.2-dark',
            'cd ~/ && wget https://github.com/swanux/hsuite/raw/master/DEV_FILES/themes_src/Windows-10-Dark-3.2-dark.tar.gz && tar -xf Windows-10-Dark-3.2-dark.tar.gz && rm -rf ~/.themes/Windows-10-Dark-3.2-dark && mv Windows-10-Dark-3.2-dark ~/.themes/ && gsettings set org.cinnamon.theme name "Windows-10-Dark-3.2-dark" && gsettings set org.cinnamon.desktop.interface gtk-theme "Windows-10-Dark-3.2-dark" && gsettings set org.cinnamon.desktop.wm.preferences theme "Windows-10-Dark-3.2-dark" && rm -rf ~/.themes/Unity-8-2.0 ~/.themes/Mojave-dark',
            'cd ~/ && wget https://github.com/swanux/hsuite/raw/master/DEV_FILES/themes_src/Unity-8-2.0.tar.gz && tar -xf Unity-8-2.0.tar.gz && rm -rf ~/.themes/Unity-8-2.0 && mv Unity-8-2.0 ~/.themes/ && gsettings set org.cinnamon.theme name "Unity-8-2.0" && gsettings set org.cinnamon.desktop.interface gtk-theme "Unity-8-2.0" && gsettings set org.cinnamon.desktop.wm.preferences theme "Unity-8-2.0" && rm -rf ~/.themes/Mojave-dark ~/.themes/Windows-10-Dark-3.2-dark'
        ],
        'XFCE' : [
            'cd ~/ && wget https://github.com/swanux/hsuite/raw/master/DEV_FILES/themes_src/Mojave-dark-20200519113011.tar.xz && tar -xf Mojave-dark-20200519113011.tar.xz && rm -rf ~/.themes/Mojave-dark && mv Mojave-dark ~/.themes/ && xfconf-query -c xsettings -p /Net/ThemeName -s "Mojave-dark" && xfconf-query -c xfwm4 -p /general/theme -s "Mojave-dark" && xfconf-query -c xfce4-notifyd -p /theme -s Mojave-dark && rm -rf ~/.themes/Unity-8-2.0 ~/.themes/Windows-10-Dark-3.2-dark',
            'cd ~/ && wget https://github.com/swanux/hsuite/raw/master/DEV_FILES/themes_src/Windows-10-Dark-3.2-dark.tar.gz && tar -xf Windows-10-Dark-3.2-dark.tar.gz && rm -rf ~/.themes/Windows-10-Dark-3.2-dark && mv Windows-10-Dark-3.2-dark ~/.themes/ && xfconf-query -c xfwm4 -p /general/theme -s "Windows-10-Dark-3.2-dark" && xfconf-query -c xfce4-notifyd -p /theme -s "Windows-10-Dark-3.2-dark" && xfconf-query -c xsettings -p /Net/ThemeName -s "Windows-10-Dark-3.2-dark" && rm -rf ~/.themes/Unity-8-2.0 ~/.themes/Mojave-dark',
            'cd ~/ && wget https://github.com/swanux/hsuite/raw/master/DEV_FILES/themes_src/Unity-8-2.0.tar.gz && tar -xf Unity-8-2.0.tar.gz && rm -rf ~/.themes/Unity-8-2.0 && mv Unity-8-2.0 ~/.themes/ && xfconf-query -c xsettings -p /Net/ThemeName -s "Unity-8-2.0" && xfconf-query -c xfwm4 -p /general/theme -s "Unity-8-2.0" && xfconf-query -c xfce4-notifyd -p /theme -s "Unity-8-2.0" && rm -rf ~/.themes/Mojave-dark ~/.themes/Windows-10-Dark-3.2-dark'
        ],
    },
    _('Layout') : 
    {
        'Gnome' : [
            f'gsettings set org.gnome.shell enabled-extensions "{extDat[0]}" && gsettings set org.gnome.shell.extensions.dash-to-dock dock-position "BOTTOM" && gsettings set org.gnome.shell.extensions.dash-to-dock intellihide "true" && gsettings set org.gnome.shell.extensions.dash-to-dock autohide true && gsettings set org.gnome.shell.extensions.dash-to-dock extend-height "false" && gsettings set org.gnome.shell.extensions.dash-to-dock background-opacity "0.4" && gsettings set org.gnome.shell.extensions.dash-to-dock dock-fixed "false" && gsettings set org.gnome.shell.extensions.dash-to-dock click-action "minimize" && gsettings set org.gnome.shell.extensions.dash-to-dock show-apps-at-top "true" && gsettings set org.gnome.shell.extensions.dash-to-dock show-running "true" && gsettings set org.gnome.shell.extensions.dash-to-dock apply-custom-theme "false" && gsettings set org.gnome.desktop.wm.preferences button-layout "close,minimize,maximize:"',
            f'gsettings set org.gnome.shell enabled-extensions "{extDat[1]}" && gsettings set org.gnome.shell.extensions.topicons tray-pos "Center" && gsettings set org.gnome.shell.extensions.topicons tray-order "2" && gsettings set org.gnome.shell.extensions.dash-to-panel panel-position "BOTTOM" && gsettings set org.gnome.shell.extensions.dash-to-panel location-clock "STATUSRIGHT" && gsettings set org.gnome.desktop.wm.preferences button-layout ":minimize,maximize,close" && gsettings set org.gnome.shell.extensions.arc-menu menu-button-icon "Custom_Icon" && gsettings set org.gnome.shell.extensions.arc-menu menu-button-active-color "rgb(45,138,217)" && gsettings set org.gnome.shell.extensions.arc-menu menu-hotkey "Super_L" && gsettings set org.gnome.shell.extensions.arc-menu menu-layout "Windows" && gsettings set org.gnome.shell.extensions.arc-menu multi-monitor "true" && gsettings set org.gnome.shell.extensions.dash-to-panel show-show-apps-button "false"',
            f'gsettings set org.gnome.shell enabled-extensions "{extDat[2]}" && gsettings set org.gnome.shell.extensions.dash-to-dock dock-position "LEFT" && gsettings set org.gnome.shell.extensions.dash-to-dock intellihide "false" && gsettings set org.gnome.shell.extensions.dash-to-dock autohide false && gsettings set org.gnome.shell.extensions.dash-to-dock background-opacity "0.7" && gsettings set org.gnome.shell.extensions.dash-to-dock background-color "#2C001E" && gsettings set org.gnome.shell.extensions.dash-to-dock dock-fixed "true" && gsettings set org.gnome.shell.extensions.dash-to-dock extend-height "true" && gsettings set org.gnome.shell.extensions.dash-to-dock show-running true && gsettings set org.gnome.shell.extensions.dash-to-dock show-apps-at-top true && gsettings set org.gnome.desktop.wm.preferences button-layout "close,minimize,maximize:"'
        ],
        'MATE' : [
            'mate-tweak --layout eleven'
            'mate-tweak --layout redmond'
            'mate-tweak --layout mutiny'
        ],
        'Cinnamon' : [
            'gsettings set org.cinnamon.desktop.interface gtk-decoration-layout "close,minimize,maximize:"',
            'gsettings set org.cinnamon.desktop.interface gtk-decoration-layout ":minimize,maximize,close"',
            'gsettings set org.cinnamon.desktop.interface gtk-decoration-layout "close,minimize,maximize:"'
        ],
        'XFCE' : [
            'xfconf-query -c xsettings -p /Gtk/DecorationLayout -s "close,minimize,maximize:"',
            'xfconf-query -c xsettings -p /Gtk/DecorationLayout -s ":minimize,maximize,close"',
            'xfconf-query -c xsettings -p /Gtk/DecorationLayout -s "close,minimize,maximize:"'
        ],
    },
    _('Icons') : 
    {
        'Gnome' : [
            'cd ~/ && wget https://github.com/swanux/hsuite/raw/master/DEV_FILES/themes_src/McMojave-circle.tar.xz && tar -xf McMojave-circle.tar.xz && rm -rf ~/.icons/McMojave-circle && rm -rf ~/.icons/McMojave-circle-dark && mv McMojave-circle ~/.icons/ && mv McMojave-circle-dark ~/.icons/ && gsettings set org.gnome.desktop.interface icon-theme "McMojave-circle-dark" && rm -rf ~/.icons/Suru ~/.icons/Windows-10-1.0',
            'cd ~/ && wget https://github.com/swanux/hsuite/raw/master/DEV_FILES/themes_src/Windows-10-1.0.tar.gz && tar -xf Windows-10-1.0.tar.gz && rm -rf ~/.icons/Windows-10-1.0 && mv Windows-10-1.0 ~/.icons/ && gsettings set org.gnome.desktop.interface icon-theme "Windows-10-1.0" && rm -rf ~/.icons/Suru ~/.icons/McMojave-circle ~/.icons/McMojave-circle-dark',
            'cd ~/ && wget https://github.com/swanux/hsuite/raw/master/DEV_FILES/themes_src/Suru.tar.xz && tar -xf Suru.tar.xz && rm -rf ~/.icons/Suru && mv Suru ~/.icons/ && gsettings set org.gnome.desktop.interface icon-theme "Suru" && rm -rf ~/.icons/McMojave-circle ~/.icons/McMojave-circle-dark ~/.icons/Windows-10-1.0',
        ],
        'Budgie' : [
            'cd ~/ && wget https://github.com/swanux/hsuite/raw/master/DEV_FILES/themes_src/McMojave-circle.tar.xz && tar -xf McMojave-circle.tar.xz && rm -rf ~/.icons/McMojave-circle && rm -rf ~/.icons/McMojave-circle-dark && mv McMojave-circle ~/.icons/ && mv McMojave-circle-dark ~/.icons/ && gsettings set org.gnome.desktop.interface icon-theme "McMojave-circle-dark" && rm -rf ~/.icons/Suru ~/.icons/Windows-10-1.0',
            'cd ~/ && wget https://github.com/swanux/hsuite/raw/master/DEV_FILES/themes_src/Windows-10-1.0.tar.gz && tar -xf Windows-10-1.0.tar.gz && rm -rf ~/.icons/Windows-10-1.0 && mv Windows-10-1.0 ~/.icons/ && gsettings set org.gnome.desktop.interface icon-theme "Windows-10-1.0" && rm -rf ~/.icons/Suru ~/.icons/McMojave-circle ~/.icons/McMojave-circle-dark',
            'cd ~/ && wget https://github.com/swanux/hsuite/raw/master/DEV_FILES/themes_src/Suru.tar.xz && tar -xf Suru.tar.xz && rm -rf ~/.icons/Suru && mv Suru ~/.icons/ && gsettings set org.gnome.desktop.interface icon-theme "Suru" && rm -rf ~/.icons/McMojave-circle ~/.icons/McMojave-circle-dark ~/.icons/Windows-10-1.0',
        ],
        'MATE' : [
            """cd ~/ && wget https://github.com/swanux/hsuite/raw/master/DEV_FILES/themes_src/McMojave-circle.tar.xz && tar -xf McMojave-circle.tar.xz && rm -rf ~/.icons/McMojave-circle && rm -rf ~/.icons/McMojave-circle-dark && mv McMojave-circle ~/.icons/ && mv McMojave-circle-dark ~/.icons/ && dconf write /org/mate/desktop/interface/icon-theme "'McMojave-circle-dark'" && rm -rf ~/.icons/Suru ~/.icons/Windows-10-1.0""",
            """cd ~/ && wget https://github.com/swanux/hsuite/raw/master/DEV_FILES/themes_src/Windows-10-1.0.tar.gz && tar -xf Windows-10-1.0.tar.gz && rm -rf ~/.icons/Windows-10-1.0 && mv Windows-10-1.0 ~/.icons/ && dconf write /org/mate/desktop/interface/icon-theme "'Windows-10-1.0'" && rm -rf ~/.icons/Suru ~/.icons/McMojave-circle ~/.icons/McMojave-circle-dark""",
            """cd ~/ && wget https://github.com/swanux/hsuite/raw/master/DEV_FILES/themes_src/Suru.tar.xz && tar -xf Suru.tar.xz && rm -rf ~/.icons/Suru && mv Suru ~/.icons/ && dconf write /org/mate/desktop/interface/icon-theme "'Suru'" && rm -rf ~/.icons/McMojave-circle ~/.icons/McMojave-circle-dark ~/.icons/Windows-10-1.0""",
        ],
        'Cinnamon' : [
            'cd ~/ && wget https://github.com/swanux/hsuite/raw/master/DEV_FILES/themes_src/McMojave-circle.tar.xz && tar -xf McMojave-circle.tar.xz && rm -rf ~/.icons/McMojave-circle && rm -rf ~/.icons/McMojave-circle-dark && mv McMojave-circle ~/.icons/ && mv McMojave-circle-dark ~/.icons/ && gsettings set org.cinnamon.desktop.interface icon-theme "McMojave-circle-dark" && rm -rf ~/.icons/Suru ~/.icons/Windows-10-1.0',
            'cd ~/ && wget https://github.com/swanux/hsuite/raw/master/DEV_FILES/themes_src/Windows-10-1.0.tar.gz && tar -xf Windows-10-1.0.tar.gz && rm -rf ~/.icons/Windows-10-1.0 && mv Windows-10-1.0 ~/.icons/ && gsettings set org.cinnamon.desktop.interface icon-theme "Windows-10-1.0" && rm -rf ~/.icons/Suru ~/.icons/McMojave-circle ~/.icons/McMojave-circle-dark',
            'cd ~/ && wget https://github.com/swanux/hsuite/raw/master/DEV_FILES/themes_src/Suru.tar.xz && tar -xf Suru.tar.xz && rm -rf ~/.icons/Suru && mv Suru ~/.icons/ && gsettings set org.cinnamon.desktop.interface icon-theme "Suru" && rm -rf ~/.icons/McMojave-circle ~/.icons/McMojave-circle-dark ~/.icons/Windows-10-1.0',
        ],
        'XFCE' : [
            'cd ~/ && wget https://github.com/swanux/hsuite/raw/master/DEV_FILES/themes_src/McMojave-circle.tar.xz && tar -xf McMojave-circle.tar.xz && rm -rf ~/.icons/McMojave-circle && rm -rf ~/.icons/McMojave-circle-dark && mv McMojave-circle ~/.icons/ && mv McMojave-circle-dark ~/.icons/ && xfconf-query -c xsettings -p /Net/IconThemeName -s "McMojave-circle-dark" && rm -rf ~/.icons/Suru ~/.icons/Windows-10-1.0',
            'cd ~/ && wget https://github.com/swanux/hsuite/raw/master/DEV_FILES/themes_src/Windows-10-1.0.tar.gz && tar -xf Windows-10-1.0.tar.gz && rm -rf ~/.icons/Windows-10-1.0 && mv Windows-10-1.0 ~/.icons/ && xfconf-query -c xsettings -p /Net/IconThemeName -s "Windows-10-1.0" && rm -rf ~/.icons/Suru ~/.icons/McMojave-circle ~/.icons/McMojave-circle-dark',
            'cd ~/ && wget https://github.com/swanux/hsuite/raw/master/DEV_FILES/themes_src/Suru.tar.xz && tar -xf Suru.tar.xz && rm -rf ~/.icons/Suru && mv Suru ~/.icons/ && xfconf-query -c xsettings -p /Net/IconThemeName -s "Suru" && rm -rf ~/.icons/McMojave-circle ~/.icons/McMojave-circle-dark ~/.icons/Windows-10-1.0',
        ],
    },
    _('Cursor') : 
    {
        'Gnome' : [
            'cd ~/ && wget https://github.com/swanux/hsuite/raw/master/DEV_FILES/themes_src/capitaine-cursors-r3.tar.xz && tar -xf capitaine-cursors-r3.tar.xz && rm -rf ~/.icons/capitaine-cursors && mv capitaine-cursors ~/.icons/ && gsettings set org.gnome.desktop.interface cursor-theme capitaine-cursors && rm -rf ~/.icons/Win-8.1-S',
            'cd ~/ && wget https://github.com/swanux/hsuite/raw/master/DEV_FILES/themes_src/Win-8.1-S.tar.xz && tar -xf Win-8.1-S.tar.xz && rm -rf ~/.icons/Win-8.1-S && mv Win-8.1-S ~/.icons/ && gsettings set org.gnome.desktop.interface cursor-theme Win-8.1-S && rm -rf ~/.icons/capitaine-cursors',
            'gsettings set org.gnome.desktop.interface cursor-theme DMZ-White',
        ],
        'Budgie' : [
            'cd ~/ && wget https://github.com/swanux/hsuite/raw/master/DEV_FILES/themes_src/capitaine-cursors-r3.tar.xz && tar -xf capitaine-cursors-r3.tar.xz && rm -rf ~/.icons/capitaine-cursors && mv capitaine-cursors ~/.icons/ && gsettings set org.gnome.desktop.interface cursor-theme capitaine-cursors && rm -rf ~/.icons/Win-8.1-S',
            'cd ~/ && wget https://github.com/swanux/hsuite/raw/master/DEV_FILES/themes_src/Win-8.1-S.tar.xz && tar -xf Win-8.1-S.tar.xz && rm -rf ~/.icons/Win-8.1-S && mv Win-8.1-S ~/.icons/ && gsettings set org.gnome.desktop.interface cursor-theme Win-8.1-S && rm -rf ~/.icons/capitaine-cursors',
            'gsettings set org.gnome.desktop.interface cursor-theme DMZ-White',
        ],
        'MATE' : [
            """cd ~/ && wget https://github.com/swanux/hsuite/raw/master/DEV_FILES/themes_src/capitaine-cursors-r3.tar.xz && tar -xf capitaine-cursors-r3.tar.xz && rm -rf ~/.icons/capitaine-cursors && mv capitaine-cursors ~/.icons/ && dconf write /org/mate/desktop/interface/cursor-theme "'capitaine-cursors'" && rm -rf ~/.icons/Win-8.1-S""",
            """cd ~/ && wget https://github.com/swanux/hsuite/raw/master/DEV_FILES/themes_src/Win-8.1-S.tar.xz && tar -xf Win-8.1-S.tar.xz && rm -rf ~/.icons/Win-8.1-S && mv Win-8.1-S ~/.icons/ && dconf write /org/mate/desktop/interface/cursor-theme "'Win-8.1-S'" && rm -rf ~/.icons/capitaine-cursors""",
            """dconf write /org/mate/desktop/interface/cursor-theme "'DMZ-White'" && cd""",
        ],
        'Cinnamon' : [
            'cd ~/ && wget https://github.com/swanux/hsuite/raw/master/DEV_FILES/themes_src/capitaine-cursors-r3.tar.xz && tar -xf capitaine-cursors-r3.tar.xz && rm -rf ~/.icons/capitaine-cursors && mv capitaine-cursors ~/.icons/ && gsettings set org.cinnamon.desktop.interface cursor-theme capitaine-cursors && rm -rf ~/.icons/Win-8.1-S',
            'cd ~/ && wget https://github.com/swanux/hsuite/raw/master/DEV_FILES/themes_src/Win-8.1-S.tar.xz && tar -xf Win-8.1-S.tar.xz && rm -rf ~/.icons/Win-8.1-S && mv Win-8.1-S ~/.icons/ && gsettings set org.cinnamon.desktop.interface cursor-theme Win-8.1-S && rm -rf ~/.icons/capitaine-cursors',
            'gsettings set org.cinnamon.desktop.interface cursor-theme DMZ-White',
        ],
        'XFCE' : [
            'cd ~/ && wget https://github.com/swanux/hsuite/raw/master/DEV_FILES/themes_src/capitaine-cursors-r3.tar.xz && tar -xf capitaine-cursors-r3.tar.xz && rm -rf ~/.icons/capitaine-cursors && mv capitaine-cursors ~/.icons/ && xfconf-query -c xsettings -p /Gtk/CursorThemeName -s capitaine-cursors && rm -rf ~/.icons/Win-8.1-S',
            'cd ~/ && wget https://github.com/swanux/hsuite/raw/master/DEV_FILES/themes_src/Win-8.1-S.tar.xz && tar -xf Win-8.1-S.tar.xz && rm -rf ~/.icons/Win-8.1-S && mv Win-8.1-S ~/.icons/ && xfconf-query -c xsettings -p /Gtk/CursorThemeName -s Win-8.1-S && rm -rf ~/.icons/capitaine-cursors',
            'xfconf-query -c xsettings -p /Gtk/CursorThemeName -s DMZ-White',
        ],
    }
}
woutput = 0

# Used generally
# The glade file
UI_FILE = "hsuite.glade"
# Get current session type
xorw = os.popen('echo $XDG_SESSION_TYPE').read()
# It's Xorg, so it wokrs with gestures'
if "x" in xorw:
    lehete = _("""You need to reboot after the install has been completed
to apply all changes. You can configure the tool
through the ~/.config/fusuma/config.yml file.""")
# It is Wayland, so it won't work
else:
    lehete = _("""You need to reboot after the install has been completed
to apply all changes. However note that support for Wayland
is experimental. You can configure the tool
through the ~/.config/fusuma/config.yml file.""")
# Discover the current working dir
wer = os.popen('ls').read()

#________________________________________________________________________ END OF INIT ____________________________________________________________#

#___________________________________________________________________ BEGIN OF GUI ___________________________________________________________________#

# This class handles everything releated to the GUI and some background tasks connected to the program
class myThread (Thread):
    def __init__(self, threadID, name, ds=0, extra=0, post=0):
        Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.extra = extra
        self.ds = ds
        self.post = post
        self._stop_event = False

    def run(self):
        print("Starting " + self.name)
        # Calls the function
        if self.name == "Data":
            c = htransfer.Transser()
            lists = ""
            t = 0
            for i in self.extra:
                if t == 0:
                    lists = lists + f'/home/{user}/{i}'
                else:
                    lists = lists + f', /home/{user}/{i}'
                t = t+1
            print('Lets do this')
            c.modPre(lists, f'/home/{user}/hswitcher/BUILD/restore-1.0/backups/')
        elif self.name == "Write":
            global woutput
            woutput = 0
            dln = _("Downloads")
            command = "pkexec popsicle -yu /home/{0}/{1}/{2} /dev/{3}".format(user, dln, self.extra, self.ds)
            print(command)
            process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
            while True:
                tmp = process.stdout.readline().decode('utf-8')
                if 'Finished' in tmp:
                    break
                if self.ds in tmp and 'Device' not in tmp:
                    prew = re.findall(r'\d+', tmp)
                    woutput = int(prew[0])
                if process.poll() is not None:
                    break
            woutput = 1
            process.poll()
        else:
            os.system(f"mkdir -p /home/{user}/hswitcher/BUILD/restore-1.0/")
            os.system(f"cd /home/{user}/hswitcher/BUILD/restore-1.0/ && dh_make -s -n -y && cd debian/ && rm -fr *.ex *.EX docs source RE* *.docs copyright")
            changelog = f'restore (1.0-1) unstable; urgency=medium\n\n  * Initial Release\n\n -- {user} <{user}@{platform.uname().node}>  {time.strftime("%a, %d %b %Y %H:%M:%S +0200")}'
            change_file = open(f"/home/{user}/hswitcher/BUILD/restore-1.0/debian/changelog", "w")
            change_file.write(changelog)
            change_file.close()
            compat_file = open(f"/home/{user}/hswitcher/BUILD/restore-1.0/debian/compat", "w")
            compat_file.write("11")
            compat_file.close()
            bds = "debhelper (>= 11)"
            print('DS_HERE')
            control = f"Source: restore\nSection: metapackages\nPriority: optional\nMaintainer: {user} <{user}@{platform.uname().node}>\nBuild-Depends: {bds}\nStandards-Version: 1.0-1\n\nPackage: restore\nArchitecture: amd64\nDepends: tar, zenity, {self.ds}\nDescription: Backup by HSwitcher\n Backup by HSwitcher. Just install it to use, then remove."
            print('Mem control')
            control_file = open(f"/home/{user}/hswitcher/BUILD/restore-1.0/debian/control", "w")
            control_file.write(control)
            control_file.close()
            install = "backups /usr/share/\n"
            install_file = open(f"/home/{user}/hswitcher/BUILD/restore-1.0/debian/install", "w")
            install_file.write(install)
            install_file.close()
            print('MAN')
            print("SUP")
            postins_file = open(f"/home/{user}/hswitcher/BUILD/restore-1.0/debian/postinst", "w")
            postins_file.write("#!/bin/bash +e\n\n"+self.post+"\n\n#DEBHELPER#")
            postins_file.close()
            os.system(f"chmod +x /home/{user}/hswitcher/BUILD/restore-1.0/debian/postinst")
            os.system(f"cd /home/{user}/hswitcher/BUILD/restore-1.0/ && debuild -i -us -uc -b && cd .. && cd .. && cd ..&& cp hswitcher/BUILD/*.deb restore.deb && rm -rf hswitcher/")
        print("Exiting " + self.name)

    def stop(self):
        self._stop_event = True
        print("stop func")

class GUI:
    count = 0
    def __init__(self):
        # Prepare to use builder
        self.builder = Gtk.Builder()
        # Import the glade file
        self.builder.add_from_file(UI_FILE)
        self.builder.set_translation_domain(APP)
        self.scanner = True
        self.them_conf = []
        self.hardCron = ""
        self.cPkg = ''
        self.runE = False
        self.tC2 = futures.ThreadPoolExecutor(max_workers=2)
        self.cache = {}
        self.stop = False
        self.Tdownl = ""
        self.quit = True
        self.b_cron = False
        self.b_progs = False
        self.b_settings = False
        self.b_theme = False
        self.b_data = False
        self.b_desk = False
        self.b_dl = False
        self.b_doc = False
        self.b_ms = False
        self.b_pic = False
        self.b_vid = False
        self.hsdir = f'/home/{user}/hswitcher/BUILD/restore-1.0/backups'
        # Connect all signals
        self.builder.connect_signals(self)
        self.switch_stack = self.builder.get_object('switch_stack')
        self.builder.get_object('them_chk').set_label(_(f'{desktop} desktop'))
        if desktop == 'Gnome':
            os.system(f"mkdir -p /home/{user}/.local/share/gnome-shell/extensions")
            self.SITE = "https://extensions.gnome.org"
            self.VERSION = os.popen("DISPLAY=':0' gnome-shell --version | tr -cd '0-9.' | cut -d'.' -f1,2").read().rstrip()
            self.EXTENSION_PATH = f"/home/{user}/.local/share/gnome-shell/extensions"
            self.DIRS = os.popen("find /usr/share/gnome-shell/extensions $HOME/.local/share/gnome-shell/extensions -maxdepth 1 -type d -printf '%P\n'").read().replace('\n\n', '\n').split('\n')
        elif desktop == 'Budgie':
            self.lady = {0 : 'cupertino', 1 : 'redmond', 2 : 'theone'}
        if desktop != 'Gnome' and desktop != 'Cinnamon':
            self.builder.get_object('ready_txt').set_label(_("Done!\n\nTo make sure that every modification works, you may log out/in or reboot."))
        # Get the main stack object
        self.stack = self.builder.get_object('stack')
        self.window = self.builder.get_object(
            'window')                  # Get the main window
        # window.connect('check-resize', self.on_resize)
        if os.geteuid() == 0:
            # Indicate if runnung as root or not
            self.window.set_title(version+' (as superuser)')
        else:
            self.window.set_title(version)
        # Display the program
        self.progBox = self.builder.get_object('progBox')
        if distro == 'Ubuntu' or distro == 'Debian':
            self.dia = AptProgressBar()
        else:
            self.dia = Gtk.ProgressBar()
        self.progBox.pack_start(self.dia, True, True, 0)
        self.window.show_all()
        GLib.idle_add(self.dia.hide)
    
    # def on_resize(self, e):
    #     time.sleep(0.01)
    #     sx, sy = self.window.get_size()
    #     num = sy/4
    #     ssig = "%"
    #     num2 = "%s%s" % (num, ssig)
    #     css = """
    #     window {
    #         font-size: %s
    #     }
    #     button {
    #         border-radius: 15px;
    #         color:whitesmoke;
    #         background-color: dimgray;
    #         background-image:none;
    #         border-right-width: 3px; 
    #         border-left-width: 3px;
    #     }
    #     notebook > header.top > tabs > tab {
    #         color: whitesmoke;
    #     }
    #     notebook > header.bottom > tabs > tab {
    #         color: whitesmoke;
    #     }
    #     notebook > header > tabs > tab:hover {
    #         background: rgb(0, 153, 255);
    #         color: whitesmoke;
    #         border-image: none;
    #     }
    #     notebook > header > tabs > tab:checked {
    #         background: rgb(0, 91, 175);
    #         color: whitesmoke;
    #         border-image: none;
    #     }
    #     button:hover {
    #         background-color: rgb(0, 153, 255);
    #         color:whitesmoke;
    #     }
    #     button:disabled {
    #         background-color: rgb(54, 54, 54);
    #         color:whitesmoke;
    #     }
    #     button:hover:active {
    #         background-color: lightblue;
    #         color: darkgreen;
    #     }
    #     .red-background{
    #         background-image: none;
    #         background-color: red;
    #         color: white;
    #     }
    #     .green-background{
    #         background-image: none;
    #         background-color: green;
    #         color: white;
    #     }
    #     """
    #     css = css % num2
    #     css = str.encode(css)
    #     provider.load_from_data(css)
        # GLib.idle_add(provider.load_from_data, css)

    # This happens when close button is clicked
    def on_window_delete_event(self, window, e):
        self.construct_dialog(Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, _('Do you really would like to exit now?'), _("Prompt"), 'exit')
        return True

###################################################################################

    # Set the button colors
    def colorer(self, gbut, name, insList):
        # Call function to check if apps are installed or not
        status = self.OnCheck(name, insList)
        # set the button label depending on this
        GLib.idle_add(gbut.set_label, status)
        gbut.get_style_context().remove_class("red-background")
        gbut.get_style_context().remove_class("green-background")
        if _("Remove") in status:
            gbut.get_style_context().add_class('red-background')
        else:
            gbut.get_style_context().add_class('green-background')
        return status

    def scannerf(self):                                         # Scans the OS for programs
        insList = apt.Cache()
        # Check for every program in the list
        for i in range(appListLen):
            if distro == 'Ubuntu' or distro == 'Debian':
                # the name to check for
                name = appList[i]
            else:
                print('ERROR IN NAME')
            # importing the button
            gbut = self.builder.get_object(f"{butDict[appList[i]]}_but")
            # Call function for setting label and color
            status = self.colorer(gbut, name, insList)
            # value refers to the state: Install/Remove
            tempNam = layDict[appList[i]]
            statDict[tempNam] = status

        # It indicates that the state of every program is now loaded into the memory
        self.scanner = False

    # check if program is installed or not
    def OnCheck(self, name, insList):
        if 'fusuma' in name:
            vane = os.popen('gem list --local').read()
            vfil = os.popen('ls /usr/lib/ruby/gems/2.6.0/cache/').read()
            if name in vane or name in vfil:
                status = _('Remove')
            else:
                status = _('Install')
        elif 'TeamViewer' in name:
            vane = os.path.exists("/opt/teamviewer")
            print(f'tw check = {vane}')
            if vane:
                status = _('Remove')
            else:
                status = _('Install')
        else:
            if distro == 'Debian' or distro == 'Ubuntu':
                try:
                    if insList[name].is_installed:
                        print(f'Found {name}')
                        status = _('Remove')
                    else:
                        print(f'Not found {name}')
                        status = _('Install')
                except:
                    print('Auto error handling --> Falling back to default (Not found)')
                    status = _('Install')
        return status

    def construct_dialog(self, typed, typeb, txt, title, name, mode=''):
        # Getting the window position
        x, y = self.window.get_position()
        # Get the size of the window
        sx, sy = self.window.get_size()
        dialogWindow = Gtk.MessageDialog(parent=self.window, modal=True, destroy_with_parent=True, message_type=typed, buttons=typeb, text=txt)
        # set the title
        dialogWindow.set_title(title)
        dsx, dsy = dialogWindow.get_size()                          # get the dialogs size
        # Move it to the center of the main window
        dialogWindow.move(x+((sx-dsx)/2), y+((sy-dsy)/2))
        dx, dy = dialogWindow.get_position()                        # set the position
        print(dx, dy)
        if name == 'custom':
            dialogWindow.add_button("What's new", 55)
            dialogWindow.show_all()
            res = dialogWindow.run()
            print(res)
            if res == 55:
                print('Want visit')
                webbrowser.open_new("https://github.com/swanux/hsuite")
            else:
                print('just ok')
            dialogWindow.destroy()
        else:
            print('first dial_else')
            dialogWindow.show_all()
            res = dialogWindow.run()
            if 'general' not in name:
                if res == Gtk.ResponseType.YES:                             # if yes ...
                    print('OK pressed')
                    dialogWindow.destroy()
                    if name == 'exit':
                        self.noMean = True
                        code = 'force'
                        if osLayer.alive:
                            code = self.construct_dialog(Gtk.MessageType.WARNING, Gtk.ButtonsType.YES_NO, _(f"Do you really would like to abort now? It could end up with a broken program. If you decide to abort, then you may need to remove {self.cPkg} manually."), _("Attention!"), 'abort', 'install')
                        if self.quit == False:
                            code = self.construct_dialog(Gtk.MessageType.WARNING, Gtk.ButtonsType.YES_NO, _(f"Do you really would like to abort now? Download is currently in progress for {namDict[self.Tdownl]}."), _("Attention!"), 'abort', 'download')
                        if code == 'force':
                            self.stop = True
                            try:
                                self.tS.shutdown()
                            except:
                                pass
                            raise SystemExit
                        else:
                            dialogWindow.destroy()
                            return True
                    elif name == 'switcher':
                        if res == Gtk.ResponseType.YES:
                            print('OK pressed')
                            dialogWindow.destroy()
                            return 'True'
                        elif res == Gtk.ResponseType.NO:
                            print('No pressed')
                            dialogWindow.destroy()
                            return 'False'
                        else:
                            return False
                    elif name == 'write':
                        if res == Gtk.ResponseType.YES:
                            print('OK pressed')
                            dialogWindow.destroy()
                            us_stack = self.builder.get_object('us_stack')
                            write_box = self.builder.get_object('write_box')
                            written_txt = self.builder.get_object('written_txt')
                            GLib.idle_add(us_stack.set_visible_child, write_box)
                            barw = self.builder.get_object('write')
                            barw.set_fraction(0.00)
                            self.wrT = myThread(3, "Write", extra=self.wFile_name, ds=self.targ)
                            self.wrT.start()
                            concF = os.path.getsize(f'/home/{user}/Downloads/{self.wFile_name}')
                            def counter(timer):
                                if self.wrT.isAlive():
                                    GLib.idle_add(barw.set_fraction, woutput/concF)
                                    return True
                                else:
                                    GLib.idle_add(us_stack.set_visible_child, written_txt)
                                    return False
                            self.source_id = GLib.timeout_add(200, counter, None)
                        elif res == Gtk.ResponseType.NO:
                            print('No pressed')
                            dialogWindow.destroy()
                            self.del_themer(self.builder.get_object('themer_win'), '')
                        else:
                            return True
                    elif name == 'abort':
                        if res == Gtk.ResponseType.YES:
                            if mode == 'download':
                                self.quit = True
                                self.rmE = True
                                print(self.quit)
                            elif mode == 'install':
                                print('Installation already running')
                                if distro == 'Ubuntu' or distro == 'Debian':
                                    try:
                                        print(self.trans.cancellable)
                                        self.trans.cancel()
                                    except:
                                        print('Cant cancel')
                                        self.construct_dialog(Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, _("You can't cancel installation, as it's in a critical state."), _("Safety first!"), 'general')
                                else:
                                    print('ERROR IN DIST AB')
                            print('OK pressed')
                            dialogWindow.destroy()
                            return 'force'
                        elif res == Gtk.ResponseType.NO:
                            print('No pressed')
                            dialogWindow.destroy()
                            return True
                elif res == Gtk.ResponseType.NO:                            # if no ...
                    print('No pressed')
                    dialogWindow.destroy()                                  # destroy dialog
                    return True                                             # end function
                else:
                    dialogWindow.destroy()                                  # destroy dialog
                    return True                                             # end function
            elif name == 'generalBack':
                dialogWindow.destroy()
                return False
            else:
                dialogWindow.destroy()
                return True

    def on_fin(self, transaction, exit_state):
        GLib.idle_add(self.dia.hide)
        osLayer.alive = False
        print(f'Trans : {transaction}')
        print(f'Code : {exit_state}')
        print("FIN")
    
    def on_done(self, sth):
        osLayer.alive = False

    # This is executed when an app is being installed/removed
    def OnNeed(self, cInB, name, status, comm1, comm2, extra, tempInd=''):
        # removes scan cache from memory because it needs to rescan because one app changed
        sTxt = cInB
        # Current pkg name
        self.cPkg = name
        if distro == 'Ubuntu' or distro == 'Debian':
            progr, self.trans = osLayer.my_thread(status, distro, comm1, comm2, extra)
            if progr == True:
                self.dia.set_transaction(self.trans)
                GLib.idle_add(self.dia.show)
                self.trans.connect("finished", self.on_fin)
                self.trans.run()
            else:
                print('E: osLayer error')
        wt = False
        print(self, wt)
        for i in range(appListLen):
            print(f"Toggle {i}")
            if appList[i] != tempInd:
                print(appList[i], butDict[appList[i]], tempInd)
                cBut = self.builder.get_object(f'{butDict[appList[i]]}_but')
                GLib.idle_add(cBut.set_sensitive, wt)
        # function for counting time
        def counter(timer, m):
            # seconds incraseing
            s = timer.count+1
            # counter is equal to s
            timer.count = s
            sTxt.set_label(str(m) + ':' + str(s))
            if s == 59:                                                             # add one to min and reset sec
                timer.count = -1
                m = m+1
            if osLayer.alive:                                                        # if thread is still running repeat
                return True
            else:                                                                   # on exit
                # reset counter
                timer.count = 0
                # declare button variable (don't know why)
                button = 0
                # imitate reopening of app spotlight
                wt = True
                print(self, wt)
                for i in range(appListLen):
                    cBut = self.builder.get_object(f'{butDict[appList[i]]}_but')
                    GLib.idle_add(cBut.set_sensitive, wt)
                self.scanner = True
                self.button_clicked(button)
                if not self.window.is_active():
                    notify2.init('HSuite')
                    n = notify2.Notification('HSuite', _(f'Finished processing {self.cPkg}!'))
                    n.show()
                self.cPkg = ''
                return False                                                      # end
        self.source_id = GLib.timeout_add(1000, counter, self, 0)

    def lilFunc(self, name, comm1, extra):
        if osLayer.alive:
            print(f'Operation already running, which is {self.cPkg}')
        if name == self.cPkg:
            self.construct_dialog(Gtk.MessageType.WARNING, Gtk.ButtonsType.YES_NO, _("Do you really would like to abort now?"), _("Attention!"), 'abort', 'install')
        else:
            comm2 = ''
            cInB = self.builder.get_object(f"{butDict[comm1]}_but")
            tempInd = comm1
            if _('Install') in statDict[name]:
                if name == 'fusuma':
                    self.construct_dialog(Gtk.MessageType.WARNING, Gtk.ButtonsType.OK, lehete, _("Note!"), 'general')
                print(name)
                self.OnNeed(cInB, name, 'install', comm1, comm2, extra, tempInd)
            elif _('Remove') in statDict[name]:
                print(name)
                self.OnNeed(cInB, name, 'remove', comm1, comm2, extra)

# Download methods

    # Disable or enable buttons based on a pattern
    def toggle(self, fn):
        print(self, fn, self.state)
        for i in range(dlistLen):
            if dlist[i] != self.Tdownl:
                cBut = self.builder.get_object(dlist[i])
                t = cBut.get_label()
                if self.state == True:
                    if t == _("Server error") or t == _("No edition chosen") or t == _("Ready in ~/Downloads/"):
                        pass
                    else:
                        GLib.idle_add(cBut.set_sensitive, self.state)
                        shDict[dlist[i]] = str(self.state)
                else:
                    GLib.idle_add(cBut.set_sensitive, self.state)
                    shDict[dlist[i]] = str(self.state)
        if self.state:
            self.scanningUrl = False

    # Starting download in a background thread BUT inside the GUI class, not the thread. This is because of the nature of GTK (and other GUI toolkits) that can't handle GUI changes from outside of the main thread (gui class)
    def ex_target(self, block_sz, downl, file_size, file_name, file_size_dl, u, f):
        print("DLthread...")
        # This variable shows if the thread needs to exit
        self.quit = False
        while not self.quit:
            # Reads the downloaded bytes in blocks
            buffer = u.read(block_sz)
            if not buffer:
                # break if error occures
                break
            # Set the downloaded file size to buffer
            file_size_dl += len(buffer)
            # write this block to the downloaded file
            f.write(buffer)
            status = _("Cancel")+r"  [%3.2f%%]" % (
                file_size_dl * 100 / file_size)  # Calculate precentage
            # Place on waiting list to change the label to the actual status
            GLib.idle_add(downl.set_label, status)
        print("DLend!!")
        # Shows that no downloads are running
        self.runE = False
        # Set back the button label to the original
        GLib.idle_add(downl.set_label, self.orig)
        print(f'quit: {self.quit}')
        print(self.orig)
        print("Label restore")
        # If the download is aborted by the user, remove the already downloaded file
        if self.rmE:
            print('Cleaning up...')
            os.system(_('rm /home/{0}/Downloads/{1}').format(user, file_name))
        else:
            # Set label to ready
            if "lfs" not in file_name.lower():
                GLib.idle_add(downl.set_label, _("Write out to USB"))
            else:
                GLib.idle_add(downl.set_label, _("Ready in ~/Downloads/"))
                GLib.idle_add(downl.set_sensitive, False)
            print("done with it")
            if not self.window.is_active():
                notify2.init('HSuite')
                n = notify2.Notification('HSuite', _(f'Finished downloading {namDict[self.Tdownl]}!'))
                n.show()
        self.quit = True

    def on_downl_begin(self, url, downl):
        # Open the url
        u = urlopen(url)
        if self.runE == True:                                                  # If download is already running
            # set remove flag to true
            self.rmE = True
            # tell the thread to stop
            self.quit = True
            print("TruTogle")
            # set button state to enabled
            self.state = True
            # enable every button
            self.toggle(fn)
            return
        elif self.runE == False:                                               # If no downloads are running
            # toggle that now one is running
            self.runE = True
            # we don't need to remove the downloaded file, because it's ready
            self.rmE = False
            # save the original label of the button
            self.orig = downl.get_label()
        file_name = url.split('/')[-1]
        f = open(_('/home/{0}/Downloads/{1}').format(user, file_name), 'wb')  # set download location
        print(f'Downloading {file_name}')
        print("FalsTogle")
        # disable buttons
        self.state = False
        # run function to do this
        self.toggle(fn)
        t1 = futures.ThreadPoolExecutor(
            max_workers=4)                    # init thread
        # start it
        fa = t1.submit(self.ex_target, 8192, downl, int(
            u.getheader('Content-Length')), file_name, 0, u, f)
        # set buttons to active
        self.state = True
        # after done run this function
        fa.add_done_callback(self.toggle)

    def generalSizer(self, di, url):
        print(self.uriDict[di])
        print('Updated linklist!!')
        print("Getting size...")
        cBut = self.builder.get_object(di)
        try:
            u = urlopen(url)
            time.sleep(0.1)
            file_name = url.split('/')[-1]
            print(file_name)
            if os.path.exists(_("/home/{0}/Downloads/{1}").format(user, file_name)):
                if "lfs" not in file_name.lower():
                    GLib.idle_add(cBut.set_label, _("Write out to USB"))
                    self.cache[di] = "R"
                else:
                    GLib.idle_add(cBut.set_label, _("Ready in ~/Downloads/"))
                    GLib.idle_add(cBut.set_sensitive, False)
            else:
                file_size = int(u.getheader('Content-Length'))
                # convert to MB
                file_size = Decimal(int(file_size) / 1024 / 1024)
                GLib.idle_add(cBut.set_label, f"Download ({round(file_size, 1)} MB)")  # set download label
                # store value in cache
                self.cache[di] = round(file_size, 1)
                GLib.idle_add(cBut.set_sensitive, True)
        except:
            if url == 'res':
                GLib.idle_add(cBut.set_label, _("No edition chosen"))
            else:
                print('URL ERROR!')
                GLib.idle_add(cBut.set_label, _("Server error"))
            GLib.idle_add(cBut.set_sensitive, False)
            self.cache[di] = "E"

    def getSizeOnce(self, forDl, distrol, flav):
        print('Getting Link...')
        if 'mint' in distrol:
            print('mint now')
            if 'lmde' in forDl:
                vers, misc = self.findNew("http://mirrors.evowise.com/linuxmint/debian/", r'-+[\d]+-', r'[\d]') # pylint: disable=unused-variable
                url = f'http://mirrors.evowise.com/linuxmint/debian/lmde-{vers[0]}-cinnamon-64bit.iso'
            else:
                vers, misc = self.findNew("http://mirrors.evowise.com/linuxmint/stable/", r'"+[\d]+.[\d]+/', r'[\d]+[\d]+[\d]')
                url = f'http://mirrors.evowise.com/linuxmint/stable/{vers[0]}{vers[1]}.{vers[2]}/linuxmint-{vers[0]}{vers[1]}.{vers[2]}-{forDl}-64bit.iso'
            self.uriDict['downl_mint'] = url
            self.generalSizer('downl_mint', url)
        elif 'ubuntu' in distrol:
            print('ubuntu now')
            vers, misc = self.findNew(f"http://cdimage.ubuntu.com/{forDl}/releases/", r'"+[\d]+.[\d]+/', r'[\d]+[\d]+[\d]+[\d]')
            versX, misc = self.findNew(f"http://cdimage.ubuntu.com/{forDl}/releases/", r'[\d]+.[\d]+.[\d]+/', r'[\d]+[\d]+[\d]+[\d]')
            if vers[1] == versX[1] and vers[2] == versX[2]:
                print('using VERSX method')
                if 'studio' in forDl:
                    print('Studio time!')
                    url = f'http://cdimage.ubuntu.com/{forDl}/releases/{versX[0]}{versX[1]}.{versX[2]}{versX[3]}.{versX[4]}/release/{forDl}-{versX[0]}{versX[1]}.{versX[2]}{versX[3]}.{versX[4]}-dvd-amd64.iso'
                elif forDl == 'ubuntu':
                    print('Basic one')
                    url = f'http://releases.ubuntu.com/{versX[0]}{versX[1]}.{versX[2]}{versX[3]}.{versX[4]}/ubuntu-{versX[0]}{versX[1]}.{versX[2]}{versX[3]}.{versX[4]}-desktop-amd64.iso'
                else:
                    url = f'http://cdimage.ubuntu.com/{forDl}/releases/{versX[0]}{versX[1]}.{versX[2]}{versX[3]}.{versX[4]}/release/{forDl}-{versX[0]}{versX[1]}.{versX[2]}{versX[3]}.{versX[4]}-desktop-amd64.iso'
            else:
                if 'studio' in forDl:
                    print('Studio time!')
                    url = f'http://cdimage.ubuntu.com/{forDl}/releases/{vers[0]}{vers[1]}.{vers[2]}{vers[3]}/release/{forDl}-{vers[0]}{vers[1]}.{vers[2]}{vers[3]}-dvd-amd64.iso'
                elif forDl == 'ubuntu':
                    print('Basic one')
                    url = f'http://releases.ubuntu.com/{vers[0]}{vers[1]}.{vers[2]}{vers[3]}/ubuntu-{vers[0]}{vers[1]}.{vers[2]}{vers[3]}-desktop-amd64.iso'
                else:
                    url = f'http://cdimage.ubuntu.com/{forDl}/releases/{vers[0]}{vers[1]}.{vers[2]}{vers[3]}/release/{forDl}-{vers[0]}{vers[1]}.{vers[2]}{vers[3]}-desktop-amd64.iso'
            self.uriDict['downl_ubuntu'] = url
            self.generalSizer('downl_ubuntu', url)
        elif 'solus' in distrol:
            print('solus now')
            vers, misc = self.findNew("https://solus.veatnet.de/iso/images", r'"+[\d]+.[\d]+/', r'[\d]+[\d]')
            url = f'https://solus.veatnet.de/iso/images/{vers[0]}.{vers[1]}/Solus-{vers[0]}.{vers[1]}-{forDl}.iso'
            self.uriDict['downl_solus'] = url
            self.generalSizer('downl_solus', url)
        elif 'deb' in distrol:
            print('debian now')
            vers, misc = self.findNew("https://cdimage.debian.org/images/unofficial/non-free/images-including-firmware/current-live/amd64/iso-hybrid/", r'debian-live-+[\d]+[\d]+.[\d]+.[\d]', r'[\d]+[\d]+[\d]')
            url = f'https://cdimage.debian.org/images/unofficial/non-free/images-including-firmware/current-live/amd64/iso-hybrid/debian-live-{vers[0]}{vers[1]}.{vers[2]}.{vers[3]}-amd64-{forDl}+nonfree.iso'
            self.uriDict['downl_deb'] = url
            self.generalSizer('downl_deb', url)
        elif 'fedora' in distrol:
            print('fedora now')
            if 'default' in forDl:
                vers, misc = self.findNew("http://fedora.inode.at/releases/", r'"+[\d]+/', r'[\d]+[\d]')
                versf, misc = self.findNew(f'http://fedora.inode.at/releases/{vers[0]}{vers[1]}/Workstation/x86_64/iso', r'-+[\d]+.+[\d]+.', r'-+[\d]+[\d]+-x')
                url = f'http://fedora.inode.at/releases/{vers[0]}{vers[1]}/Workstation/x86_64/iso/Fedora-Workstation-Live-x86_64-{vers[0]}{vers[1]}-{versf[0]}.{versf[2]}.iso'
            else:
                vers, misc = self.findNew("http://fedora.inode.at/releases/", r'"+[\d]+/', r'[\d]+[\d]')
                versf, misc = self.findNew(f'http://fedora.inode.at/releases/{vers[0]}{vers[1]}/Spins/x86_64/iso', r'-+[\d]+.+[\d]+.', r'-+[\d]+[\d]+-x')
                url = f'http://fedora.inode.at/releases/{vers[0]}{vers[1]}/Spins/x86_64/iso/Fedora-{forDl}-Live-x86_64-{vers[0]}{vers[1]}-{versf[0]}.{versf[2]}.iso'
            self.uriDict['downl_fedora'] = url
            self.generalSizer('downl_fedora', url)
        elif 'suse' in distrol:
            print('opensuse now')
            if 'roll' in forDl:
                url = 'https://download.opensuse.org/tumbleweed/iso/openSUSE-Tumbleweed-DVD-x86_64-Current.iso'
            else:
                reponse = urlopen("https://download.opensuse.org/distribution/openSUSE-stable/iso")
                dat = reponse.read()
                text = dat.decode('utf-8')
                pattern = re.findall(r'openSUSE-Leap-+[\d]+[\d]+.+[\d]+-DVD-x86_64.iso"><', text)
                vers = pattern[0].replace('"', '').replace('><', '')
                url = f"https://download.opensuse.org/distribution/openSUSE-stable/iso/{vers}"
            self.uriDict['downl_suse'] = url
            self.generalSizer('downl_suse', url)
            

    def on_choose(self, widget):
        distrol = Gtk.Buildable.get_name(widget)
        flav = widget.get_active_text()
        if flav == _("Choose version"):
            if 'mint' in distrol:
                self.generalSizer('downl_mint', 'res')
            elif 'ubuntu' in distrol:
                self.generalSizer('downl_ubuntu', 'res')
            elif 'solus' in distrol:
                self.generalSizer('downl_solus', 'res')
            elif 'deb' in distrol:
                self.generalSizer('downl_deb', 'res')
            elif 'fedora' in distrol:
                self.generalSizer('downl_fedora', 'res')
            elif 'suse' in distrol:
                self.generalSizer('downl_suse', 'res')
        else:
            linkForIso = toChoseDir[distrol][flav]
            self.tS = futures.ThreadPoolExecutor(max_workers=2)
            self.tS.submit(self.getSizeOnce, forDl=linkForIso, distrol=distrol, flav=flav)

    def on_us_tog(self, widget, name):
        if widget.get_active():
            self.targ = name
            print(self.targ)
    
    def write_but_clicked(self, button):
        self.construct_dialog(Gtk.MessageType.WARNING, Gtk.ButtonsType.YES_NO, _('Warning! All of your DATA will be EREASED on the selected USB drive. Are you sure you would like to continue?'), _("Prompt"), 'write')

    def listUSB(self):
        devices = husb.list_media_devices()
        self.driveDict = {}
        self.boxUS = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        btn = Gtk.RadioButton.new_with_label_from_widget(None, 'All')
        for device in devices:
            chker1 = Gtk.RadioButton.new_with_label_from_widget(btn, "{0} {1} (/dev/{2}) : {3}G".format(husb.get_vendor(device), husb.get_model(device),husb.get_device_name(device) , husb.get_size(device) / 1024 ** 3))
            chker1.connect("toggled", self.on_us_tog, husb.get_device_name(device))
            self.boxUS.pack_start(chker1, True, True, 0)
            self.driveDict[husb.get_device_name(device)] = [husb.is_removable(device), husb.get_size(device) / 1024 ** 3, husb.get_model(device), husb.get_vendor(device)]
        print(self.driveDict)

    def general_download(self, button):
        label = button.get_label()
        self.Tdownl = Gtk.Buildable.get_name(button)
        if label == _("Write out to USB"):
            print('write')
            url = self.uriDict[self.Tdownl]
            print(url)
            self.wFile_name = url.split('/')[-1]
            win = self.builder.get_object('themer_win')
            self.builder.get_object('main_stack').set_visible_child(self.builder.get_object('scroll_us'))
            self.listUSB()
            self.builder.get_object('us_box').pack_start(self.boxUS, True, True, 0)
            win.show_all()
        else:
            self.on_downl_begin(self.uriDict[self.Tdownl], self.builder.get_object(self.Tdownl))

# End of download section

    # Button is the name of the app spotlight button
    def button_clicked(self, button):
        # If already in memory don't waste resources
        if self.scanner == False:
            print('VALUE_FOUND')
            # notebook box is the name of the app spotlight page
            notebook_box = self.builder.get_object('notebook_box')
            # set it visible
            self.stack.set_visible_child(notebook_box)
        # if not in memory, then scan it now
        elif self.scanner:
            notebook_box = self.builder.get_object('notebook_box')
            self.stack.set_visible_child(notebook_box)
            print('NO_VALUE')
            # start scanning
            aS = futures.ThreadPoolExecutor(max_workers=2)
            s = aS.submit(self.scannerf)
            print('SCANN START')
            print(s)
        else:
            print('ERROR')

    # feedback button
    def on_fb_but_clicked(self, button):
        web_box = self.builder.get_object('web_box')
        texV = self.builder.get_object('txt_long')
        titE = self.builder.get_object('tit_entry')
        text = texV.get_buffer()
        text = text.set_text('')
        titE.set_text('')
        self.stack.set_visible_child(web_box)
        tC = futures.ThreadPoolExecutor(max_workers=2)
        f = tC.submit(self.check)
        self.where = 'fb'
        f.add_done_callback(self.chk_again)

    def check(self):
        try:
            urlopen('http://216.58.192.142', timeout=5)
            print('yes, net')
            self.net = True
        except:
            print('no internet')
            self.net = False
    def chk_again(self, arg):
        print('again chk')
        if not self.net:
            button = 0
            GLib.idle_add(self.construct_dialog, Gtk.MessageType.WARNING, Gtk.ButtonsType.OK, _("You have no internet connection!"), _("Attention!"), 'generalBack')
            if self.where == 'fb':
                self.home_clicked(button)
            else:
                self.tC2 = futures.ThreadPoolExecutor(max_workers=2)
                for i in range(dlistLen):
                    # dlist is distro list (contains all distro names), cbut is current button
                    cBut = self.builder.get_object(dlist[i])
                    cBut.set_label(_('No internet'))
        else:
            if self.where == 'gs':
                self.tS = futures.ThreadPoolExecutor(max_workers=2)
                f = self.tS.submit(self.getSize)
                # toggle everything back when ready
                self.state = True
                f.add_done_callback(self.toggle)

    def on_send(self, button):
        titE = self.builder.get_object('tit_entry')
        emE = self.builder.get_object('email_entry')
        texV = self.builder.get_object('txt_long')
        cat = self.builder.get_object('typ_comb')
        which = self.builder.get_object('which_comb')
        title = titE.get_text()
        email = emE.get_text()
        text = texV.get_buffer()
        start = text.get_start_iter()
        end = text.get_end_iter()
        text = text.get_text(start, end, True)
        category = cat.get_active_text()
        program = which.get_active_text()
        if '@' not in email or '.' not in email:
            if email == '' or email == None:
                print('Optional, of course')
                email = 'Not provided'
            else:
                print('invalid email!!')
                self.construct_dialog(Gtk.MessageType.WARNING, Gtk.ButtonsType.OK, _('Invalid email address!'), _("Attention!"), 'general')
                return
        elif text == '' or title == '':
            self.construct_dialog(Gtk.MessageType.WARNING, Gtk.ButtonsType.OK, _('You need to fill out all the fields!'), _("Attention!"), 'general')
            return
        text = text+f"qnqn---------------------------------qnqnEmail: {email}qnUsername: {user}qnComputer name: {platform.uname().node}qnOS: {platform.platform()}qnCPU: {platform.processor()}qnProviding feedback for: {program}"
        if category == _('Enhancement'):
            lab = 'enhancement'
        elif category == _('Question'):
            lab = 'question'
        elif category == _('Bug'):
            lab = 'bug'
        else:
            print('Feedback Error')
            lab = ['invalid']
        print(title, text, category, email)
        os.system(f'./sfdaemon "{lab}" "{title}" "{text}"')
        print('Uploaded')
        self.construct_dialog(Gtk.MessageType.INFO, Gtk.ButtonsType.OK, _('Feedback submitted succesfully!'), _("Information"), 'general')
        self.home_clicked(button)

    # information button in about section
    def on_git_link_clicked(self, button):
        # open project page in browser
        webbrowser.open_new("https://swanux.github.io/hsuite.html")
    
    def on_chos_but_clicked(self, button):
        webbrowser.open_new("https://distrochooser.de/en/")

#######################################################################################

    def patchControl(self, ext=''):
        if desktop == 'Gnome':
            if ext == '':
                os.system('mkdir -p ~/.local/share/glib-2.0/schemas/ && export XDG_DATA_DIRS=~/.local/share:/usr/share && find ~/.local/share/gnome-shell/extensions/ -name *gschema.xml -exec ln {} -sfn ~/.local/share/glib-2.0/schemas/ \; && glib-compile-schemas ~/.local/share/glib-2.0/schemas/') # pylint: disable=anomalous-backslash-in-string
            elif ext == 'cleanup':
                os.system(f'rm -rf /home/{user}/Mojave-dark-20200519113011.tar.xz /home/{user}/Windows-10-Dark-3.2-dark.tar.gz /home/{user}/Unity-8-2.0.tar.gz')
            else:
                if 'remove-dropdown-arrows' in ext and float(self.VERSION) >= 3.36:
                    JSON = f"{self.SITE}/extension-info/?uuid={ext}&shell_version=3.34"
                else:
                    JSON = f"{self.SITE}/extension-info/?uuid={ext}&shell_version={self.VERSION}"
                tmp = os.popen(f"curl -s '{JSON}'").read().split(' ')
                EXTENSION_URL = self.SITE + tmp[-1].replace('"', '').replace('}', '')
                os.system(f"wget --header='Accept-Encoding:none' -O '/home/{user}/tmp.zip' '{EXTENSION_URL}'")
                os.system(f"mkdir -p {self.EXTENSION_PATH}/{ext} && unzip -oq ~/tmp.zip -d {self.EXTENSION_PATH}/{ext} && chmod +r {self.EXTENSION_PATH}/{ext}/* && rm -f ~/tmp.zip")

    def sw(self):
        print('in sw')
        os.system('mkdir -p ~/.themes && mkdir -p ~/.icons')
        for i in self.them_conf:
            if i == 'Layout' and desktop == 'Budgie':
                bus = dbus.SessionBus()
                proxy = bus.get_object('org.UbuntuBudgie.ExtrasDaemon', '/org/ubuntubudgie/extrasdaemon')
                iface = dbus.Interface(proxy, 'org.UbuntuBudgie.ExtrasDaemon')
                iface.ResetLayout(self.lady[self.themNum])
            else:
                command = themDat[i][desktop][self.themNum]
                if i == 'Layout' and desktop == 'Gnome':
                    # os.system('gsettings set org.gnome.shell enabled-extensions []')
                    for ext in extDat[self.themNum]:
                        if ext in self.DIRS:
                            print(f'{ext} is already installed.')
                        else:
                            print(f'Installing {ext}...')
                            self.patchControl(ext)
                self.patchControl()
                print(command)
                try:
                    os.system(command)
                except:
                    print("E: Can't execute command for some reason")
        self.patchControl('cleanup')

    def sw2(self, sth):
        print('in sw2')
        st = self.builder.get_object('them_stack')
        bx = self.builder.get_object('ready_txt')
        GLib.idle_add(st.set_visible_child, bx)

    def appl_but_clicked(self, button):
        sw = futures.ThreadPoolExecutor(max_workers=2)
        f = sw.submit(self.sw)
        f.add_done_callback(self.sw2)
        st = self.builder.get_object('them_stack')
        bx = self.builder.get_object('wait_box')
        st.set_visible_child(bx)

    def del_themer(self, twindow, e):
        if woutput == 1 or woutput == 0:
            self.builder.get_object('them_stack').set_visible_child(self.builder.get_object('the_box'))
            self.builder.get_object('us_stack').set_visible_child(self.builder.get_object('us_box'))
            try:
                self.builder.get_object('us_box').remove(self.boxUS)
            except:
                print('no usb for now')
            twindow.hide()
            return True

    def all_toggle(self, widget):
        if widget.get_active():
            print('Active')
            self.builder.get_object('desk_them_chk').set_active(True)
            self.builder.get_object('lay_chk').set_active(True)
            self.builder.get_object('ico_chk').set_active(True)
            self.builder.get_object('cur_chk').set_active(True)
        else:
            print('Inactive')
            self.builder.get_object('desk_them_chk').set_active(False)
            self.builder.get_object('lay_chk').set_active(False)
            self.builder.get_object('ico_chk').set_active(False)
            self.builder.get_object('cur_chk').set_active(False)
        print(self.them_conf)

    def them_conf_ch(self, widget):
        name = widget.get_label()
        if widget.get_active():
            print('Active')
            self.them_conf.append(name)
        else:
            print('Inactive')
            self.them_conf.remove(name)
        print(self.them_conf)

    def general_theme_click(self, button):
        name = button.get_label()
        if 'MacOS' in name:
            self.themNum = 0
        elif 'Windows' in name:
            self.themNum = 1
        else:
            self.themNum = 2
        win = self.builder.get_object('themer_win')
        self.builder.get_object('main_stack').set_visible_child(self.builder.get_object('scroll_the'))
        win.show_all()

#######################################################################################

    def on_general_chk(self, widget):
        which = Gtk.Buildable.get_name(widget)
        status = widget.get_active()
        if 'prog' in which:
            self.b_progs = status
        elif 'usr' in which:
            self.b_data = status
        elif 'cron' in which:
            self.b_cron = status
        elif 'them' in which:
            self.b_theme = status
            self.b_settings = status
    
    def on_prog_tog(self, widget, name):
        if widget.get_active():
            print('Active')
            self.appsToSave.append(name)
        else:
            print('Inactive')
            self.appsToSave.remove(name)
        print(self.appsToSave)

    def on_dat_toggle(self, widget):
        name = widget.get_label()
        if widget.get_active():
            print('Active')
            self.datToSave.append(name)
        else:
            print('Inactive')
            self.datToSave.remove(name)
        print(self.datToSave)

    def on_dat_proc_but_clicked(self, button):
        barcur = self.builder.get_object('current')
        bartot = self.builder.get_object('total')
        barcur.set_fraction(0.00)
        bartot.set_fraction(0.00)
        self.builder.get_object('back_button1').set_sensitive(False)
        GLib.idle_add(self.switch_stack.set_visible_child, self.builder.get_object('data_box'))
        self.datT = myThread(3, "Data", extra=self.datToSave)
        self.datT.start()
        def counter(timer):
            if self.datT.isAlive():
                GLib.idle_add(barcur.set_fraction, htransfer.filePer/100)
                GLib.idle_add(barcur.set_text, htransfer.yetFil)
                GLib.idle_add(bartot.set_fraction, htransfer.currPer/100)
                return True
            else:
                self.crTask()
                return False
        self.source_id = GLib.timeout_add(200, counter, None)

    def extTh(self, postinst):
        postinst = postinst + 'tar -pxzf /usr/share/backups/shellTheme.tar.gz -C /usr/share/themes/\n'
        postinst = postinst + 'tar -pxzf /usr/share/backups/deskTheme.tar.gz -C /usr/share/themes/\n'
        postinst = postinst + 'tar -pxzf /usr/share/backups/cursorTheme.tar.gz -C /usr/share/themes/\n'
        postinst = postinst + 'tar -pxzf /usr/share/backups/iconTheme.tar.gz -C /usr/share/icons/\n'
        return postinst
    
    def exEx(self, cDE, postinst):
        postinst = postinst + f"extensions=$(echo '{self.DIRS}')\n"
        postinst = postinst + f"version=$(DISPLAY=':0' {cDE} --version | tr -cd '0-9.' | cut -d'.' -f1,2)\n"
        postinst = postinst + "declare -a allExt=(`echo $extensions |sed 's/, / /g'`)\n"
        if cDE == 'gnome-shell':
            postinst = postinst + """for var in "${allExt[@]}"
do
    if [[ ${var} == "[" || ${var} == "]" || ${var} == "" ]]; then
        echo pass
    else
        json="https://extensions.gnome.org/extension-info/?uuid=${var}&shell_version=${version}"
        EXTENSION_URL=https://extensions.gnome.org$(curl -s "${json}" | sed -e 's/^.*download_url[\": ]*\([^\"]*\).*$/\\1/')
        wget --header='Accept-Encoding:none' -O "/home/${user}/tmp.zip" "${EXTENSION_URL}"
        mkdir -p /home/${user}/.local/share/gnome-shell/extensions/${var}
        unzip -oq "/home/${user}/tmp.zip" -d "/home/${user}/.local/share/gnome-shell/extensions/${var}"
        chmod +r /home/${user}/.local/share/gnome-shell/extensions/${var}/* && rm -f /home/${user}/tmp.zip
    fi
done\n"""
        return postinst

    def crTask(self):
        self.builder.get_object('back_button1').set_sensitive(False)
        spinner = self.builder.get_object('create_spin')
        spinner.start()
        self.switch_stack.set_visible_child(self.builder.get_object('create_box'))
        postinst = ""
        postinst = postinst + "user=$(who|awk '{print $1}'r)\n"
        postinst += 'zenity --info --text="Welcome ${user}!\nNow we will begin to restore everything for you.\nPlease be patient, it may take a while...\n\nIf you understand press OK to begin." --no-wrap\n'
        if self.b_data:
            for i in self.datToSave:
                postinst = postinst + "cp -R /usr/share/backups/{%s}/* /home/${user}/%s/\n" % (i, i)
        ds = ""
        if self.b_progs:
            postinst = postinst + 'apt-key add /usr/share/backups/sources/Repo.keys\n'
            l = 0
            for i in self.appsToSave:
                if l == 0:
                    ds = ds+str(i)
                else:
                    ds = ds+f", {i}"
                l = l+1
            for i in self.appsToSave:
                postinst = postinst + f"apt-mark manual {i}\n"
        if self.b_theme:
            postinst = postinst + 'cp /usr/share/backups/background/* /usr/share/backgrounds/\n'
            if desktop == 'Gnome':
                postinst = self.extTh(postinst)
                postinst = self.exEx('gnome-shell', postinst)
                postinst = postinst + "runuser -l ${user} -c 'dconf load / < /usr/share/backups/dcBkup'\n"
            elif desktop == 'Elementary':
                postinst = postinst + "runuser -l ${user} -c 'dconf load / < /usr/share/backups/dcBkup'\n"
            elif desktop == 'Cinnamon' or desktop == 'Budgie' or desktop == 'MATE': # TODO
                postinst = self.extTh(postinst)
                postinst = postinst + "runuser -l ${user} -c 'dconf load / < /usr/share/backups/dcBkup'\n"
            elif desktop == 'XFCE':
                postinst = self.extTh(postinst)
                postinst = postinst + 'cp -R /usr/share/backups/xfce4 /home/${user}/.config/\n'
        if self.b_cron:
            postinst = postinst + 'crontab -u ${user} /usr/share/backups/crontab\n'
        postinst += 'chown -R ${user} /home/${user}/\n'
        t1 = myThread(5, "Builder", ds=ds, post=postinst)
        t1.start()
        def counter(timer):
            if t1.isAlive():
                return True
            else:
                spinner.stop()
                self.builder.get_object('back_button1').set_sensitive(True)
                self.switch_stack.set_visible_child(self.builder.get_object('done_txt'))
                return False
        self.source_id = GLib.timeout_add(1000, counter, None)

    def on_prog_proc_but_clicked(self, button):
        if self.b_data:
            self.switch_stack.set_visible_child(self.builder.get_object('scroll_dat'))
        else:
            self.crTask()

    def getBg(self, locparse, cDE):
        if desktop == 'XFCE':
            background = os.popen('xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitorVirtual1/workspace0/last-image').read().strip()
            fname = background.split('/')[-1].replace("'", '')
            os.system(f'cp {background} {self.hsdir}/background/{fname}')
            print(fname)
            os.system(f'xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitorVirtual1/workspace0/last-image -s "/usr/share/backgrounds/{fname}"')
            os.system(f'cp -R /home/{user}/.config/xfce4 {self.hsdir}/')
            os.system(f'xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitorVirtual1/workspace0/last-image -s {background}')
        else:
            if cDE == 'mate':
                background = locparse.get(f'org/{cDE}/desktop/background', 'picture-filename')
            else:
                background = locparse.get(f'org/{cDE}/desktop/background', 'picture-uri').replace('file://', '')
            fname = background.split('/')[-1].replace("'", '')
            os.system(f'cp {background} {self.hsdir}/background/{fname}')
            print(fname)
            locparse.set(f'org/{cDE}/desktop/background', 'picture-uri', f"'file:///usr/share/backgrounds/{fname}'")
            return locparse

    def getTh(self, shellTheme, deskTheme, iconTheme, cursorTheme, wmTheme=""):
        try:
            print('####################')
            print(shellTheme, deskTheme, iconTheme, cursorTheme, wmTheme)
            print('####################')
            if shellTheme != '':
                if os.path.exists('/home/{0}/.themes/{1}'.format(user, shellTheme.replace("'", ""))):
                    os.system(f'cd /home/{user}/.themes/ && tar -pczf {self.hsdir}/shellTheme.tar.gz {shellTheme}')
                else:
                    os.system(f'cd /usr/share/themes/ && tar -pczf {self.hsdir}/shellTheme.tar.gz {shellTheme}')
            if os.path.exists('/home/{0}/.themes/{1}'.format(user, deskTheme.replace("'", ""))):
                os.system(f'cd /home/{user}/.themes/ && tar -pczf {self.hsdir}/deskTheme.tar.gz {deskTheme}')
            else:
                os.system(f'cd /usr/share/themes/ && tar -pczf {self.hsdir}/deskTheme.tar.gz {deskTheme}')
            if os.path.exists('/home/{0}/.themes/{1}'.format(user, cursorTheme.replace("'", ""))):
                os.system(f'cd /home/{user}/.icons/ && tar -pczf {self.hsdir}/cursorTheme.tar.gz {cursorTheme}')
            else:
                os.system(f'cd /usr/share/icons/ && tar -pczf {self.hsdir}/cursorTheme.tar.gz {cursorTheme}')
            if os.path.exists('/home/{0}/.themes/{1}'.format(user, iconTheme.replace("'", ""))):
                os.system(f'cd /home/{user}/.icons/ && tar -pczf {self.hsdir}/iconTheme.tar.gz {iconTheme}')
            else:
                os.system(f'cd /usr/share/icons/ && tar -pczf {self.hsdir}/iconTheme.tar.gz {iconTheme}')
            if wmTheme != "":
                if os.path.exists('/home/{0}/.themes/{1}'.format(user, wmTheme.replace("'", ""))):
                    os.system(f'cd /home/{user}/.themes/ && tar -pczf {self.hsdir}/wmTheme.tar.gz {wmTheme}')
                else:
                    os.system(f'cd /usr/share/themes/ && tar -pczf {self.hsdir}/wmTheme.tar.gz {wmTheme}')
        except:
            print("E: Can't execute command for some reason No.2")

    def on_proc_but_clicked(self, button):
        if desktop == 'Unknown' and self.b_theme == True:
            self.construct_dialog(Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, _('Your desktop is not supported currently, so we have disabled the desktop backup function for you. Please uncheck it, and use only the other options. Thank you for your understanding.'), _("Error"), 'general')
        else:
            os.system(f"mkdir -p {self.hsdir}/")
            self.appsToSave = []
            self.datToSave = []
            if self.b_settings and self.b_theme:
                os.system(f"mkdir -p {self.hsdir}/background")
                locparse = ConfigParser()
                if desktop == 'Gnome' or desktop == 'Budgie':
                    os.system(f'dconf dump / > {self.hsdir}/dcBkup')
                    locparse.read(f'{self.hsdir}/dcBkup')
                    locparse = self.getBg(locparse, 'gnome')
                    try:
                        shellTheme = locparse.get('org/gnome/shell/extensions/user-theme', 'name')
                    except:
                        shellTheme = ''
                    deskTheme = locparse.get('org/gnome/desktop/interface', 'gtk-theme')
                    iconTheme = locparse.get('org/gnome/desktop/interface', 'icon-theme')
                    cursorTheme = locparse.get('org/gnome/desktop/interface', 'cursor-theme')
                    self.getTh(shellTheme, deskTheme, iconTheme, cursorTheme)
                elif desktop == 'Elementary':
                    os.system(f'dconf dump / > {self.hsdir}/dcBkup')
                    locparse.read(f'{self.hsdir}/dcBkup')
                    locparse = self.getBg(locparse, 'gnome')
                elif desktop == 'Cinnamon': # TODO
                    os.system(f'dconf dump / > {self.hsdir}/dcBkup')
                    locparse.read(f'{self.hsdir}/dcBkup')
                    locparse = self.getBg(locparse, 'cinnamon')
                    shellTheme = locparse.get('org/cinnamon/theme', 'name')
                    deskTheme = locparse.get('org/cinnamon/desktop/interface', 'gtk-theme')
                    iconTheme = locparse.get('org/cinnamon/desktop/interface', 'icon-theme')
                    cursorTheme = locparse.get('org/cinnamon/desktop/interface', 'cursor-theme')
                    wmTheme = locparse.get('org/cinnamon/desktop/wm/preferences', 'theme')
                    self.getTh(shellTheme, deskTheme, iconTheme, cursorTheme, wmTheme)
                elif desktop == 'XFCE':
                    self.getBg('', '')
                    shellTheme = os.popen('xfconf-query -c xfwm4 -p /general/theme').read().strip()
                    deskTheme = os.popen('xfconf-query -c xsettings -p /Net/ThemeName').read().strip()
                    iconTheme = os.popen('xfconf-query -c xsettings -p /Net/IconThemeName').read().strip()
                    cursorTheme = os.popen('xfconf-query -c xsettings -p /Gtk/CursorThemeName').read().strip()
                    self.getTh(shellTheme, deskTheme, iconTheme, cursorTheme)
                elif desktop == 'MATE':
                    os.system(f'dconf dump / > {self.hsdir}/dcBkup')
                    locparse.read(f'{self.hsdir}/dcBkup')
                    locparse = self.getBg(locparse, 'mate')
                    shellTheme = ''
                    deskTheme = locparse.get('org/mate/desktop/interface', 'gtk-theme')
                    iconTheme = locparse.get('org/mate/desktop/interface', 'icon-theme')
                    cursorTheme = locparse.get('org/mate/desktop/interface', 'cursor-theme')
                    self.getTh(shellTheme, deskTheme, iconTheme, cursorTheme)
                tconf = open(f'{self.hsdir}/dcBkup', 'w+')
                locparse.write(tconf)
                tconf.close()

            if self.b_progs:
                b_simple = self.construct_dialog(Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, _('Would you like to view a simplified list of applications? (some less common programs may miss from the list)'), _("Ask"), 'switcher')
                print('Programs true')
                extendedApps = subprocess.check_output('apt-mark showmanual', shell=True, executable='/bin/bash') # pylint: disable=unexpected-keyword-arg
                extendedApps = extendedApps.decode()
                extendedApps = extendedApps.split('\n')
                if b_simple == 'True':
                    print('Minimal')
                    search_word = ['acpi', 'alsa', 'anacron', 'apache', 'avahi', 'bluez', 'tty', 'certificates', 'cups', 'eog', 'evince', 'festival', 'festvox', 'ffmpeg', 'locale', 'fonts', '-db-', '-mod', 'multilib', 'fwupd', 'gdm', 'gnome', 'gir1.2', '-agent', 'grub', 'gstreamer', 'gtk2', 'gtk3', 'theme-', 'gvfs', 'hplip', 'hostname', 'ibus', '-config', 'jq', 'kernel', 'language-pack', 'lib', '-sensors', 'maim', 'mokutil', 'mpc', 'mpd', 'mysql', 'nautilus-', 'ncurses', 'network-', 'driver', 'openj', '-ppds', 'orca', 'php', 'pcmc', 'packagekit', 'plymouth', 'policykit', 'ppp', '-module-', '-is-', 'rfkill', '-signed', 'snapd', 'printer', 'ubuntu-', 'udev', 'update-', 'upower', 'vorbis', 'wpasupplicant', 'xcursor', 'xdg', 'xkb', 'xorg', 'xul-ext', 'yelp', '-dev', 'flatpak', 'genisoimage', 'germinate', 'ghostscript', 'grep', 'zip', 'init', 'inotify', 'inputattach', 'mousetweaks', 'net-', 'spice-', '-dispatcher', 'whoopsie', 'xmind', 'app-install', 'apport', 'at-spi2', 'dash', 'diffutils', 'dirmngr', 'dmz', '-data', 'apt-', 'base-', 'console-', 'cpio', 'dbus', '-utils', 'dh-', 'doc-', 'dpkg', 'e2fsprogs', 'elementary', 'system76-', 'gcc-', 'geoclue-', 'gpgv', 'gsignond', 'hunspell-', 'iproute', 'iputils', 'isc-', 'kbd', 'kexec-', 'kmod', 'linux-', 'logrotate', 'lsb-', 'mawk', 'mime-', 'nplan', 'pantheon', 'passwd', '-base', 'procps', 'pulseaudio', '-yaml', '-minimal', '-common', 'rsyslog', 'sudo', 'switchboard', 'systemd', 'wingpanel', 'wamerican', 'wbrazilian', 'wbritish', 'wbulgarian', 'wcatalan', 'wdanish', 'wdutch', 'wfrench', '-tools', '-utils', 'witalian', 'wngerman', 'wnorwegian', 'wogerman', 'wpolish', 'wportuguese', 'wspanish', 'wswedish', 'wswiss', 'wukrainian', 'xxd', 'debian', 'i18n', 'light-locker', 'netcat-', 'ucf', 'vim-', '-linux', 'ubiquity', 'login', 'dmsetup', 'devscripts', 'debhelper', 'debconf', 'coreutils', 'build-essential', 'bsdutils', 'adduser']
                    minimalApps = []
                    for i in extendedApps:
                        bad = False
                        for xy in search_word:
                            if xy in i:
                                bad = True
                                break
                        if bad == False:
                            minimalApps.append(i)
                self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
                self.builder.get_object('progs_box').pack_start(self.box, True, True, 0)
                if b_simple == 'True':
                    for program in minimalApps:
                        if program == "" or program == None:
                            break
                        chker = Gtk.CheckButton.new_with_label(program)
                        chker.connect("toggled", self.on_prog_tog, program)
                        self.box.pack_start(chker, True, True, 0)
                else:
                    for program in extendedApps:
                        if program == "" or program == None:
                            break
                        chker = Gtk.CheckButton.new_with_label(program)
                        chker.connect("toggled", self.on_prog_tog, program)
                        self.box.pack_start(chker, True, True, 0)
                os.system(f'mkdir -p {self.hsdir}/sources/ && apt-key exportall > {self.hsdir}/sources/Repo.keys')
                self.box.show_all()
            if self.b_cron:
                print('Cron true')
                os.system('crontab -l > {self.hsdir}/crontab')
            if self.b_progs:
                if self.b_data == False:
                    self.builder.get_object('prog_proc_but').set_label('Start backup')
                else:
                    self.builder.get_object('prog_proc_but').set_label('Continue')
                self.switch_stack.set_visible_child(self.builder.get_object('scroll_progs'))
            elif self.b_data:
                self.switch_stack.set_visible_child(self.builder.get_object('scroll_dat'))
            else:
                self.crTask()

    # hswitcher clicked
    def on_ac_but_clicked(self, button):
        self.switch_stack.set_visible_child(self.builder.get_object('r_box'))
        self.stack.set_visible_child(self.builder.get_object('scroll_switcher'))

######################################################################################################################

    # hcontrol
    def row_activated(self, widget, row, col):
        relPos = self.tree.get_selection().get_selected_rows()[1][0][0]
        print(relPos)

    def mouse_click(self, widget, event):
        if event.button == 3:
            try:
                pthinfo = self.tree.get_path_at_pos(event.x, event.y)
                path,col,cellx,celly = pthinfo # pylint: disable=unused-variable
                self.tree.grab_focus()
                self.tree.set_cursor(path,col,0)
                menu = Gtk.Menu()
                menu_item = Gtk.MenuItem.new_with_label('Delete job')
                menu_item.connect("activate", self.del_cur)
                menu.add(menu_item)
                menu.show_all()
                menu.popup_at_pointer()
            except:
                print('Not the best place to right-click bro!')
    
    def del_cur(self, action):
        cron  = CronTab(user=True)
        this = self.tree.get_selection().get_selected_rows()[1][0][0]
        print(this)
        print(cron[this])
        cron.remove(cron[this])
        cron.write()
        self.on_htools_but_clicked('button')

    def new_but_clicked(self, button):
        self.page = 0
        self.noMean = False
        self.builder.get_object('au_stack').set_visible_child(self.builder.get_object('cron_box'))
        self.on_cron_book_change_current_page('widget', 'box', self.page)
    
    def cancel_but_clicked(self, button):
        self.noMean = True
        self.builder.get_object('au_stack').set_visible_child(self.builder.get_object('au_box'))
    
    def cron_entr_changed(self, widget):
        print('man')
        atx = self.builder.get_object('cron_entr').get_text().split(' ')
        self.minu = atx[0]
        self.hour = atx[1]
        self.daym = atx[2]
        self.cmonth = atx[3]
        self.dayw = atx[4]

    def min_entr_changed(self, widget):
        self.minu = self.builder.get_object('min_entr').get_text()
    
    def hour_entr_changed(self, widget):
        self.hour = self.builder.get_object('hour_entr').get_text()
    
    def day_entr_changed(self, widget):
        self.daym = self.builder.get_object('day_entr').get_text()
    
    def month_choose_changed(self, widget):
        self.cmonth = self.builder.get_object('month_choose').get_active_text()

    def exec_choose_changed(self, widget):
        self.hardCron = self.builder.get_object('exec_choose').get_active_text()

    def on_cron_book_change_current_page(self, widget, box, page):
        print('Changed mode {page}')
        self.page = page
        self.noMean = True
        self.hardCron, self.minu, self.hour, self.daym, self.cmonth, self.dayw = "", "", "", "", "", ""
        if page == 0:
            print('simple')
            self.hardCron = self.builder.get_object('exec_choose').get_active_text()
        elif page == 1:
            print('adv')
            self.dayw = '*'
            self.minu = self.builder.get_object('min_entr').get_text()
            self.hour = self.builder.get_object('hour_entr').get_text()
            self.daym = self.builder.get_object('day_entr').get_text()
            self.cmonth = self.builder.get_object('month_choose').get_active_text()
        elif page == 2:
            print('man')
            atx = self.builder.get_object('cron_entr').get_text()
            if '@' not in atx:
                atx = atx.split(' ')
                self.minu = atx[0]
                self.hour = atx[1]
                self.daym = atx[2]
                self.cmonth = atx[3]
                self.dayw = atx[4]
            else:
                self.hardCron = atx
        self.noMean = False
        tC = futures.ThreadPoolExecutor(max_workers=2)
        tC.submit(self.getMeaning)
    
    def getMeaning(self):
        print('Getting meaning')
        while self.noMean == False:
            try:
                if self.cronCommand != "" and self.cronJob != "": # pylint: disable=access-member-before-definition
                    self.builder.get_object('done_but').set_sensitive(True)
                else:
                    self.builder.get_object('done_but').set_sensitive(False)
            except:
                self.builder.get_object('done_but').set_sensitive(False)
            time.sleep(0.1)
            if self.minu != "" and self.hour != "" and self.daym != "" and self.cmonth != "" and self.dayw != "":
                print('first if')
                cronMean = get_description(f"{self.minu} {self.hour} {self.daym} {self.cmonth} {self.dayw}")
                self.cronJob = f"{self.minu} {self.hour} {self.daym} {self.cmonth} {self.dayw}"
            elif self.hardCron != "":
                print('sec if')
                print(self.hardCron)
                if self.hardCron == _("reboot") or self.hardCron == _("yearly") or self.hardCron == _("monthly") or self.hardCron == _("weekly") or self.hardCron == _("daily") or self.hardCron == _("hourly"):
                    print('sir if')
                    if self.hardCron == _('reboot'):
                        cronMean = _('After reboot.')
                    elif self.hardCron == _('minutely'):
                        cronMean = _('Every minute.')
                    else:
                        cronMean = _("Repeat ")+self.hardCron+"."
                    self.cronJob = f"@{self.hardCron}"
                else:
                    print('xs else')
                    cronMean = _("Invalid syntax!")
                    self.cronJob = ""
            else:
                print('xl else')
                cronMean = _("Invalid syntax!")
                self.cronJob = ""
            self.cronCommand = self.builder.get_object('comm_entr').get_text()
            GLib.idle_add(self.builder.get_object('tx_lab').set_label, cronMean)
        print(cronMean)
        print(self.cronJob)
        print(self.cronCommand)
        print('stopmean')

    def on_done_but_clicked(self, button):
        print('Saving...')
        cron  = CronTab(user=True)
        job = cron.new(command=f"DISPLAY={dplenv} && {self.cronCommand}")
        job.setall(self.cronJob)
        cron.write()
        self.builder.get_object('au_stack').set_visible_child(self.builder.get_object('au_box'))
        self.on_htools_but_clicked('button')

    def on_htools_but_clicked(self, button):
        self.noMean = True
        cron  = CronTab(user=True)
        box = self.builder.get_object('au_box')
        try:
            box.remove(self.scrollable_treelist) # pylint: disable=access-member-before-definition
        except:
            pass
        storeCron = Gtk.ListStore(str, int)
        self.tree = Gtk.TreeView.new_with_model(storeCron)
        self.tree.connect("row-activated", self.row_activated)
        self.tree.connect("button_press_event", self.mouse_click)
        self.tree.set_reorderable(False)
        self.scrollable_treelist = Gtk.ScrolledWindow()
        self.scrollable_treelist.set_vexpand(True)
        self.scrollable_treelist.add(self.tree)
        box.pack_start(self.scrollable_treelist, True, True, 0)
        l = 0
        for job in cron:
            storeCron.append([str(job), l])
            l += 1
        print("First time")
        for i, column_title in enumerate([_("Job"), "ID"]):
            renderer = Gtk.CellRendererText(xalign=0)
            renderer.set_property("ellipsize", True)
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            if column_title == _("Job"):
                column.set_fixed_width(700)
                column.set_resizable(True)
            else:
                column.set_max_width(50)
                column.set_resizable(False)
            column.set_sort_column_id(i)
            self.tree.append_column(column)
        self.builder.get_object('control_box').show_all()
        self.stack.set_visible_child(self.builder.get_object('control_box'))

##################################################################################

    def findNew(self, urii, perPat, perVer):
        if self.stop:
            print('Aborted by user.')
            raise SystemExit
        reponse = urlopen(urii)
        dat = reponse.read()
        text = dat.decode('utf-8')
        pattern = re.findall(perPat, text)
        # print(pattern)
        gentoo = pattern[0]
        pattern = ''.join(pattern)
        pattern = pattern.replace(".", "")
        pattern = re.findall(perVer, pattern)
        if 'fedora' in urii and 'iso' in urii:
            pattern = ''.join(pattern)
            pattern = pattern.replace('-', '').replace('x', '')
        pattern = list(map(int, pattern))
        try:
            pattern.remove(710)
            pattern.remove(710)
        except:
            pass
        pattern.sort()
        vers = pattern[-1]
        # print(vers)
        vers = [int(i) for i in str(vers)]
        if 'fedora' in urii and 'iso' in urii:
            vers = [str(i) for i in pattern]
            vers = int("".join(vers))
            vers = [int(d) for d in str(vers)]
        return vers, gentoo

    # fetch download sizes
    def getSize(self):
        print('Getting Links...')
        reponse = urlopen("http://mirrors.evowise.com/archlinux/iso/latest")
        dat = reponse.read()
        text = dat.decode('utf-8')
        pattern = re.findall(r'archlinux-+[\d]+[\d]+[\d]+[\d]+.+[\d]+[\d]+.+[\d]+[\d]+-x86_64.iso">', text)
        print(pattern)
        vers = pattern[0].replace('"', '').replace('>', '')
        archLink = f'http://mirrors.evowise.com/archlinux/iso/latest/{vers}'
        
        vers, misc = self.findNew("http://ftp.sh.cvut.cz/slax/", r'Slax-+[\d]+.x', r'[\d]')
        print('slax')
        tmp = f"http://ftp.sh.cvut.cz/slax/Slax-{vers[0]}.x/"
        vers, misc = self.findNew(tmp, r'slax-64bit-+[\d]+.[\d]+.[\d]', r'[\d]+[\d]+[\d]')
        slaxLink = f"{tmp}slax-64bit-{vers[0]}.{vers[1]}{vers[2]}.{vers[3]}.iso"

        vers, misc = self.findNew("https://sourceforge.net/projects/bodhilinux/files/", r'/[\d].[\d].[\d]/', r'[\d]+[\d]')
        print('bodhi')
        bodhiLink = f'https://jztkft.dl.sourceforge.net/project/bodhilinux/{vers[0]}.{vers[1]}.{vers[2]}/bodhi-{vers[0]}.{vers[1]}.{vers[2]}-64.iso'

        vers, misc = self.findNew("https://dotsrc.dl.osdn.net/osdn/sparkylinux/68112/", r'sparkylinux-+[\d]+.[\d]+-x86_64', r'[\d]+[\d]')
        print('sparky')
        sparkyLink = f'https://dotsrc.dl.osdn.net/osdn/sparkylinux/68112/sparkylinux-{vers[0]}{vers[1]}{vers[2]}{vers[3]}.{vers[4]}{vers[5]}-x86_64-lxqt.iso'

        print('puppy')
        puppyLink = "http://ftp.nluug.nl/ftp/pub/os/Linux/distr/puppylinux/puppy-bionic/bionicpup64/bionicpup64-8.0-uefi.iso"

        print('tiny')
        tinyLink = "http://tinycorelinux.net/11.x/x86/release/CorePlus-current.iso"

        vers1, misc = self.findNew("http://mirror.inode.at/data/deepin-cd/", r'>+[\d]+<', r'[\d]+[\d]')
        vers2, misc = self.findNew("http://mirror.inode.at/data/deepin-cd/", r'>+[\d]+.[\d]+<', r'[\d]+[\d]+[\d]')
        vers3, misc = self.findNew("http://mirror.inode.at/data/deepin-cd/", r'>+[\d]+.[\d]+.[\d]+<', r'[\d]+[\d]+[\d]')
        vers = []
        # print(vers1, vers2, vers3)
        tvers1, tvers2, tvers3 = vers1.copy(), vers2.copy(), vers3.copy()
        for i in [tvers1, tvers2, tvers3]:
            for x in range(5):
                try:
                    print(i[x])
                except:
                    i.append(0)
            string_ints = [str(int) for int in i]
            vers.append(int(''.join(string_ints)))
        vers.sort()
        vers = [int(i) for i in str(vers[-1])]
        # global deepinLink
        print('deepin')
        if vers == tvers1:
            deepinLink = f'http://mirror.inode.at/data/deepin-cd/{vers1[0]}{vers1[1]}/deepin-desktop-community-1002-amd64.iso'
        elif vers == tvers2:
            deepinLink = f'http://mirror.inode.at/data/deepin-cd/{vers2[0]}{vers2[1]}.{vers2[2]}{vers2[3]}/deepin-{vers2[0]}{vers2[1]}.{vers2[2]}{vers2[3]}-amd64.iso'
        elif vers == tvers3:
            deepinLink = f'http://mirror.inode.at/data/deepin-cd/{vers3[0]}{vers3[1]}.{vers3[2]}{vers3[3]}.{vers3[4]}/deepin-{vers3[0]}{vers3[1]}.{vers3[2]}{vers3[3]}.{vers3[4]}-amd64.iso'
        else:
            print(vers, tvers1, tvers2, tvers3)

        # global steamosLink
        print('steam')
        steamosLink = 'http://repo.steampowered.com/download/SteamOSDVD.iso'

        vers, misc = self.findNew("https://sourceforge.net/projects/drauger-os/files/", r'Drauger_OS-+[\d]+.[\d]+.[\d]', r'[\d]+[\d]+[\d]')
        print('drauger')
        draugerLink = f'https://netix.dl.sourceforge.net/project/drauger-os/Drauger_OS-{vers[0]}.{vers[1]}.{vers[2]}-amd64.iso'

        vers, misc = self.findNew("http://distfiles.gentoo.org/releases/amd64/autobuilds/current-install-amd64-minimal/", r'[\d]+[\d]+[\w]+[\d][\w]', r'[\d]+[\d]')
        # global gentooLink
        print('gentoo')
        gentooLink = f'http://distfiles.gentoo.org/releases/amd64/autobuilds/current-install-amd64-minimal/install-amd64-minimal-{misc}.iso'

        vers, misc = self.findNew("http://www.linuxfromscratch.org/lfs/downloads/", r'[\d]+.[\d]+-systemd/', r'[\d]+[\d]')
        # global lfsLink
        print('lfs')
        lfsLink = f'http://www.linuxfromscratch.org/lfs/downloads/{vers[0]}{vers[1]}.{vers[2]}-systemd/LFS-BOOK-{vers[0]}{vers[1]}.{vers[2]}-systemd.pdf'

        self.uriDict = {'downl_mint': '', 'downl_ubuntu': '', 'downl_solus': '', 'downl_deepin': deepinLink, 'downl_steamos': steamosLink, 'downl_deb': '', 'downl_fedora': '', 'downl_suse': '', 'downl_gentoo': gentooLink, 'downl_arch': archLink, 'downl_lfs': lfsLink, 'downl_drauger' : draugerLink, 'downl_slax' : slaxLink, 'downl_bodhi' : bodhiLink, 'downl_sparky' : sparkyLink, 'downl_puppy' : puppyLink, 'downl_tiny' : tinyLink}
        print('Updated linklist!!')
        print("Getting size...")
        # dlistlen is the length of dlist
        for i in range(dlistLen):
            if self.stop:
                print('Aborted by user.')
                raise SystemExit
            # dlist is distro list (contains all distro names), cbut is current button
            cBut = self.builder.get_object(dlist[i])
            # get url from dictionary
            url = self.uriDict[dlist[i]]
            try:
                u = urlopen(url)
                time.sleep(0.1)
                file_name = url.split('/')[-1]
                print(file_name)
                if os.path.exists(_("/home/{0}/Downloads/{1}").format(user, file_name)):
                    if "lfs" not in file_name.lower():
                        GLib.idle_add(cBut.set_label, _("Write out to USB"))
                        self.cache[dlist[i]] = "R"
                    else:
                        GLib.idle_add(cBut.set_label, _("Ready in ~/Downloads/"))
                        GLib.idle_add(cBut.set_sensitive, False)
                else:
                    file_size = int(u.getheader('Content-Length'))
                    # convert to MB
                    file_size = Decimal(int(file_size) / 1024 / 1024)
                    GLib.idle_add(cBut.set_label, f"Download ({round(file_size, 1)} MB)")  # set download label
                    # store value in cache
                    self.cache[dlist[i]] = round(file_size, 1)
            except:
                if url == '':
                    GLib.idle_add(cBut.set_label, _("No edition chosen"))
                else:
                    print('URL ERROR!')
                    GLib.idle_add(cBut.set_label, _("Server error"))
                self.cache[dlist[i]] = "E"

    def on_db_but_clicked(self, button):
        distro_box = self.builder.get_object('distro_box')
        thss = len(self.tC2._threads)
        print(thss)
        if not self.cache and thss == 0:                                                             # if not fetched already
            # disable
            self.scanningUrl = True
            self.state = False
            self.toggle(fn)  # all buttons
            # init non-normal thread (getting sizes)
            f = self.tC2.submit(self.check)
            self.where = 'gs'
            f.add_done_callback(self.chk_again)
        self.stack.set_visible_child(distro_box)

    # on about ...
    def on_about_but_clicked(self, button):
        scroll_about = self.builder.get_object('scroll_about')
        self.stack.set_visible_child(scroll_about)

    def home_clicked(self, button):  # back button
        self.noMean = True
        scroll_home = self.builder.get_object('scroll_home')
        self.stack.set_visible_child(scroll_home)

    def on_page(self, button):                                      # general descrition page
        text = self.builder.get_object('page_txt')
        page = self.builder.get_object('scroll_desc')
        back_button = self.builder.get_object(
            'back_button')        # back but not to home
        # hide rew link and web link when not in distro boutique
        rew_link = self.builder.get_object('rew_link')
        rew_link.hide()
        web_link = self.builder.get_object('web_link')
        web_link.hide()
        # if yes, show. bp indicates the current page, regarding its meaning I have no idea
        if self.bp == _("Distro Boutique"):
            rew_link.show()
            web_link.show()
        text.set_text(self.label)
        back_button.set_label(self.bp)
        self.stack.set_visible_child(page)

    # when going back but not to home
    def on_back_button_clicked(self, button):
        if self.bp == _("App Spotlight"):                                 # go back to app spotlight or distro boutique
            self.button_clicked(button)
        elif self.bp == _("Distro Boutique"):
            distro_box = self.builder.get_object('distro_box')
            self.stack.set_visible_child(distro_box)
        else:
            print('ERROR')

    def on_rew_link_clicked(self, button):
        webbrowser.open_new(self.rew)

    def on_web_link_clicked(self, button):
        webbrowser.open_new(self.web)
    
    def general_src(self, button):
        btn = Gtk.Buildable.get_name(button)
        webbrowser.open_new(srcDict[btn])

# What to do on button clicks
    def general_clicks(self, button):
        btn = Gtk.Buildable.get_name(button)
        self.lilFunc(name=liLi[btn][0], comm1=liLi[btn][1], extra=liLi[btn][2])

    def on_msoffice_but_clicked(self, button):
        webbrowser.open_new("https://office.com")

    def on_goffice_but_clicked(self, button):
        webbrowser.open_new("https://docs.google.com")

# End of button clicks

# Descriptions

    def displayDesc(self, x, button, trye=""):
        self.label = d.descList[x]
        self.bp = d.descDict[self.label]
        if self.bp == _('Distro Boutique'):
            if "steam" in trye or "lfs" in trye or "drauger" in trye:
                self.builder.get_object('rew_link').set_label(_('Demo/Review (YouTube)'))
            else:
                self.builder.get_object('rew_link').set_label(_('Try it now (online)'))
            self.web = d.webDict[self.label]
            self.rew = d.vidDict[self.label]
        self.on_page(button)
    
    def applay(self, button):
        fLili = Gtk.Buildable.get_name(button)
        self.displayDesc(liLi[f'{fLili}_but'][3], button)

    def on_msoffice_clicked(self, button):
        self.displayDesc(9, button)

    def on_goffice_clicked(self, button):
        self.displayDesc(10, button)
    
    def dissplay(self, button):
        fLola = Gtk.Buildable.get_name(button)
        self.displayDesc(loLa[fLola], button, trye=fLola)

# End of descriptions
# _____________________________________________________________________ END OF GUI ____________________________________________________________________#

if __name__ == "__main__":
    if sys.platform in ["win32", "cygwin"]:
        DE = "windows"
    elif sys.platform == "darwin":
        DE = "mac"
    else: #Most likely either a POSIX system or something not much common
        desktop_session = os.environ.get("DESKTOP_SESSION")
        if desktop_session is not None: #easier to match if we doesn't have  to deal with caracter cases
            desktop_session = desktop_session.lower()
            if desktop_session in ["gnome","unity", "cinnamon", "mate", "xfce4", "lxde", "fluxbox", 
                                    "blackbox", "openbox", "icewm", "jwm", "afterstep","trinity", "kde", "ubuntu"]:
                DE = desktop_session
            ## Special cases ##
            elif "xubuntu" in desktop_session:
                DE = "xfce4"
            elif desktop_session.startswith("ubuntu"):
                DE = "unity"       
            elif desktop_session.startswith("lubuntu"):
                DE = "lxde" 
            elif desktop_session.startswith("pop"):
                DE = "gnome"
            elif desktop_session.startswith("pantheon"):
                DE = "elementary"
            elif desktop_session.startswith("kubuntu"): 
                DE = "kde"
            elif desktop_session.startswith("budgie"): 
                DE = "budgie"
            elif desktop_session.startswith("razor"): # e.g. razorkwin
                DE = "razor-qt"
            elif desktop_session.startswith("wmaker"): # e.g. wmaker-common
                DE = "windowmaker"
        else:
            if os.environ.get('KDE_FULL_SESSION') == 'true':
                DE = "kde"
            elif os.environ.get('GNOME_DESKTOP_SESSION_ID'):
                if not "deprecated" in os.environ.get('GNOME_DESKTOP_SESSION_ID'):
                    DE = "gnome2"
            else:
                DE = "unknown"
    print(DE)
    if 'gnome' in DE or 'ubuntu' in DE:
        desktop = 'Gnome'
    elif 'elementary' in DE:
        desktop = 'Elementary'
    elif 'xfce' in DE:
        desktop = 'XFCE'
    elif 'cinnamon' in DE: # TODO
        desktop = 'Cinnamon'
    elif 'budgie' in DE:
        desktop = 'Budgie'
    elif 'mate' in DE:
        desktop = 'MATE'
    else:
        desktop = 'Unknown'
    ## Config section ##
    parser = ConfigParser()
    confP = f'/home/{user}/.config/hsuite.conf'
    if os.path.exists(confP):
        print('Configured already')
        parser.read(confP)
        distro = parser.get('system', 'distro')
        v = parser.get('hsuite', 'v')
        dist = parser.get('system', 'dist')
        app = GUI()  # variable to call GUI class
    else:
        print('Config not found')
        # Detect distro
        dist = os.popen('uname -a').read()          # Get distro name
        if 'Ubuntu' in dist:
            distro = 'Ubuntu'
        # elif 'solus' in dist:
        #     distro = 'Solus'
        elif 'Debian' in dist:
            distro = 'Debian'
        elif 'deepin' in dist:
            distro = 'Debian'
            print('W: Not fully compatible with Deepin!')
            app = GUI()
            app.construct_dialog(Gtk.MessageType.WARNING, Gtk.ButtonsType.OK, _("Your distro is detected as Deepin. This distro is not fully tested, you may encounter some problems with the program. Currently tested on distros: Ubuntu (bionic, focal), Debian (buster)."), _("Attention!"), 'general')
        else:
            distro = ''
            app = GUI()
            print('E: Complete incompatibility!')
            app.construct_dialog(Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, _("Can not detect your distro. Currently compatible with distros: Ubuntu (bionic, focal), Debian (buster) and everything based on them. Aborting now."), _("Attention!"), 'general')
            raise SystemExit
        app = GUI()
        parser.add_section('system')
        parser.add_section('hsuite')
        parser.set('system', 'distro',  distro)
        parser.set('hsuite', 'v', version)
        parser.set('system', 'dist', dist)
        file = open(confP, "w+")
        parser.write(file)
        file.close()
        # os.system("./sfbknd hsuite")
    if desktop == 'Unknown':
        app.construct_dialog(Gtk.MessageType.WARNING, Gtk.ButtonsType.OK, _(f"Your desktop is detected as {DE.upper()}. This desktop is not supported yet, you may encounter some problems with DE specific parts of the program. Currently supported: Gnome/Ubuntu"), _("Attention!"), 'general')
    elif desktop == 'Budgie' and os.popen('apt list --installed | grep budgie-extras-daemon').read() == '':
        app.construct_dialog(Gtk.MessageType.WARNING, Gtk.ButtonsType.OK, _("To be able to use Budgie theming options, please run the following command:\n\n\tsudo apt install budgie-extras-daemon -y"), _("Attention!"), 'general')
    elif desktop == 'MATE' and os.popen('apt list --installed | grep mate-tweaks').read() == '':
        app.construct_dialog(Gtk.MessageType.WARNING, Gtk.ButtonsType.OK, _("To be able to use MATE theming options, please run the following command:\n\n\tsudo apt install mate-tweaks -y"), _("Attention!"), 'general')
    # Own module for root prompt and background installation
    import osLayer
    osLayer.init(distro)
    osLayer.user = user
    ## Colors (button)
    provider = Gtk.CssProvider()
    colors = Gio.File.new_for_path('colors.css')
    provider.load_from_file(colors)
    Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    if v != version and v != '':
        app.construct_dialog(Gtk.MessageType.INFO, Gtk.ButtonsType.OK, _(f"HSuite has been updated to {version}. For changelog click the button below."), _("Information"), 'custom')
        parser.set('hsuite', 'v', version)
        file = open(confP, "w+")
        parser.write(file)
        file.close()
        v = parser.get('hsuite', 'v')
    # Print info to debug
    print(f"Current date: {today}")
    print(f"Current day: {day}")
    print(f"Current month: {month}")
    print(f"Current year: {year}")
    print(f"Name of non-root user: {user}")
    print('---BEGIN---')
    print(f"Content of working directory: {str(wer)}")
    print("---END---")
    print(f"Output of $uname -a$ : {dist}")
    print(f"Detected distro: {distro}")
    print(f'Updated? : {v}')
    Gtk.main()  # execute main GTK window