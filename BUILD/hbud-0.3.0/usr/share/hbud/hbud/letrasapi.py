#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import urllib.request, re

def get_lyric(artist, track):
    artist = artist.lower()
    track = track.lower()
    track = re.sub("[\(\[].*?[\)\]]", "", track)
    artist = re.sub('[^A-Za-z0-9]+', "-", artist)
    track = re.sub('[^A-Za-z0-9]+', "", track)
    url = "https://www.letras.mus.br/"+artist+"/"
    try:
        content = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(content, 'html.parser')
        lyriclist = str(soup)
        x = re.findall("<li class=\"cnt-list-row -song is-visible.*class=\"song-options\"></div> </li>", lyriclist)
        x = x[0].split("<li ")
        del x [0]
        # lyrdir = []
        # i = 0
        for item in x:
            title = re.findall("data-name=\"(.*?)\"", item)[0]
            title = re.sub("[\(\[].*?[\)\]]", "", title)
            title = re.sub('[^A-Za-z0-9]+', "", title)
            link = re.findall("data-shareurl=\"(.*?)\"", item)[0]
            # lyrdir.append({"title" : title, "url" : link, "id" : i})
            if title.lower() == track:
                break
            # i += 1
        content = urllib.request.urlopen(link).read()
        soup = BeautifulSoup(content, 'html.parser')
        lyric = str(soup)
        x = re.findall("<div class=\"cnt-letra(.*?)</div>", lyric)
        x = x[0].split("<p>")
        del x [0]
        finallyr = ""
        for line in x:
            finallyr += line.replace("<br>", "\n").replace("<br/>", "\n").replace("</br></p>", "\n\n").replace("</p>", "\n\n")
        finallyr = finallyr.rstrip()
        return finallyr
    except:
        return None