#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from requests import get
from bs4 import BeautifulSoup
from urllib.parse import quote

user_agent = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}

def get_lyric(artist, track):
    try:
        query = quote(f"{track} - {artist}", safe="")
        query += "/tracks"
        search_url = f"https://www.musixmatch.com/search/{query}"
        search_resp = get(search_url, headers=user_agent)
        if not search_resp.ok: return None

        search_soup = BeautifulSoup(search_resp.text, "html.parser")
        song_url_tag = search_soup.select_one("a[href^='/lyrics/']")

        song_url = "https://www.musixmatch.com" + str(song_url_tag.get("href", ""))
        if song_url.split("/")[-1] == "add": return None
        lyrics_resp = get(song_url, headers=user_agent)
        if not lyrics_resp.ok: return None

        lyrics_soup = BeautifulSoup(lyrics_resp.text, "html.parser")
        lyrics_paragraphs = lyrics_soup.select("p.mxm-lyrics__content")
        lyrics = "\n".join(i.get_text() for i in lyrics_paragraphs)
        return lyrics
    except:
        return None