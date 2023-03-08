from gi.repository import GLib
from hbud.mpris_server.adapters import PlayState, MprisAdapter
from hbud.mpris_server.server import Server
from hbud.mpris_server.events import EventAdapter


class Adapter(MprisAdapter):
    def __init__(self, hbud_main):
        super().__init__()
        self.hbud_main = hbud_main

    def get_uri_schemes(self) -> list:
        return []

    def get_mime_types(self) -> list:
        return []

    def can_quit(self) -> bool:
        return False

    def quit(self):
        pass

    def get_current_position(self) -> float:
        return self.hbud_main.toolClass.position

    def next(self):
        GLib.Thread.new(None, self.hbud_main.on_next, "")

    def previous(self):
        GLib.Thread.new(None, self.hbud_main.on_prev, "")

    def pause(self):
        GLib.Thread.new(None, self.hbud_main.on_playBut_clicked, "")

    def resume(self):
        GLib.Thread.new(None, self.hbud_main.on_playBut_clicked, "")

    def stop(self):
        pass

    def play(self):
        pass

    def get_playstate(self) -> PlayState:
        if self.hbud_main.res is False and self.hbud_main.playing is False:
            return PlayState.STOPPED
        elif self.hbud_main.playing is False and self.hbud_main.res is True:
            return PlayState.PAUSED
        return PlayState.PLAYING

    def seek(self, time):
        return

    def is_repeating(self) -> bool:
        pass

    def is_playlist(self) -> bool:
        return self.hbud_main.nowIn == "audio"

    def set_repeating(self, val: bool):
        pass

    def set_loop_status(self, val: str):
        pass

    def get_rate(self) -> float:
        return 1.0

    def set_rate(self, val: float):
        pass

    def get_shuffle(self) -> bool:
        pass

    def set_shuffle(self, val: bool):
        pass

    def get_art_url(self, track):
        return ''

    def get_stream_title(self):
        return ''

    def is_mute(self) -> bool:
        return False

    def can_go_next(self) -> bool:
        return self.hbud_main.nowIn == "audio"

    def can_go_previous(self) -> bool:
        return self.hbud_main.nowIn == "audio"

    def can_play(self) -> bool:
        return self.hbud_main.res

    def can_pause(self) -> bool:
        return self.hbud_main.res

    def can_seek(self) -> bool:
        return False

    def can_control(self) -> bool:
        return True

    def metadata(self) -> dict:
        try:
            if self.hbud_main.nowIn == "video":
                return {
                'mpris:trackid': '/track/1',
                'mpris:artUrl': "",
                'xesam:title': GLib.path_get_basename(self.hbud_main.url.replace("file://", "")),
                'xesam:artist': [""]
            }
            else:
                song = self.hbud_main.playlist[self.hbud_main.tnum]
                return {
                    'mpris:trackid': '/track/1',
                    'mpris:artUrl': self.hbud_main.load_cover(mode="mpris"),
                    'xesam:title': song['title'],
                    'xesam:artist': [song['artist']]
                }
        except:
            return {'mpris:trackid': '/org/mpris/MediaPlayer2/TrackList/NoTrack'}


def init(player: object):
    mpris = Server('hbud', adapter = Adapter(player))
    player.mpris_adapter = EventAdapter(root = mpris.root, player = mpris.player)
    player.mpris_server = mpris
    player.mpris_server.loop()