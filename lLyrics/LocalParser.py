# -*- coding: utf-8 -*-
# Parses lyrics from a .lyric or .lrc file or from the tags of the song
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import urllib, urllib3
import os.path as path
from mutagen.oggvorbis import OggVorbis
from mutagen.oggopus import OggOpus
from mutagen.flac import FLAC
from mutagen.id3 import ID3

class Parser(object):
    def __init__(self, artist, title, song_path):
        self.artist = artist
        self.title = title
        self.lyrics = ""
        self.song_path = song_path

    def parse(self):
        # convert the song url to a usable path
        path = self.song_path
        path = urllib.parse.unquote(path)
        path = path.replace("file://", "")
        dir = path[0:((path.rfind("/")) + 1)]
        file_name = path[((path.rfind("/")) + 1):path.rfind(".")]
        out = ""
        if path.endswith("mp3"):
            out = self.get_id3_lyrics(path)
        elif path.endswith("ogg"):
            out = self.get_ogg_lyrics(path)
        elif path.endswith("opus"):
            out = self.get_opus_lyrics(path)
        elif path.endswith("flac"):
            out = self.get_flac_lyrics(path)
        if out == "":
            file = self.check_for_file(dir, file_name)
            if file == "":
            	return ""
            out = ""
            for line in file.readlines():
                out += line
            file.close()
            self.lyrics = out
            return out
        else:
            return out
    def check_for_file(self, dir, file_name):
        # This only checks for .lrc or .lyric files with the same name as the song or with the same "cleaned" name as
        # the song. If you have files in any other format, please add it to this function.
        if path.isfile(dir + file_name + ".lrc"):
            return open(dir + file_name + ".lrc")
        elif path.isfile(dir + file_name + ".lyric"):
            return open(dir + file_name + ".lyric")
        elif path.isfile(dir + self.title + ".lrc"):
            return open(dir + self.title + ".lrc")
        elif path.isfile(dir + self.title + ".lyric"):
            return open(dir + self.title + ".lyric")
        else:
            return ""
    def get_id3_lyrics(self, path):
        try:
            file = ID3(path)
        except:
            return ""
        if len(file.getall("USLT")) > 0:
            out = file.getall("USLT")[0]
            return out.text
        else:
            print("No lyrics!")
            return ""
    def get_opus_lyrics(self, path):
        file = OggOpus(path)
        out = ""
        try:
            out = file["LYRICS"]
        except:
            pass
        try:
            out = file["UNSYNCEDLYRICS"]
        except:
            pass
        if out != "":
            return out[0]
        return ""
    def get_ogg_lyrics(self, path):
        file = OggVorbis(path)
        out = ""
        try:
            out = file["LYRICS"]
        except:
            pass
        try:
            out = file["UNSYNCEDLYRICS"]
        except:
            pass
        if out != "":
            return out[0]
        return ""
    def get_flac_lyrics(self, path):
        file = FLAC(path)
        out = ""
        try:
            out = file["LYRICS"]
        except:
            pass
        try:
            out = file["UNSYNCEDLYRICS"]
        except:
            pass
        if out != "":
            return out[0]
        return ""
