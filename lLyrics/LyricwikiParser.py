# Parser for Lyricwiki.org

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

import urllib.request, urllib.error, urllib.parse
import string
import html

import re

import Util


class Parser(object):
    def __init__(self, artist, title):
        self.artist = artist
        self.title = title
        self.lyrics = ""

    def parse(self):
        # format artist and title
        self.artist = self.artist.replace(" ", "_")
        self.title = self.title.replace(" ", "_")
        clean_artist = urllib.parse.quote(self.artist)
        clean_title = urllib.parse.quote(self.title)

        # create lyrics Url
        url = "http://lyrics.wikia.com/wiki/" + clean_artist + ":" + clean_title
        print("lyricwiki Url " + url)
        try:
            resp = urllib.request.urlopen(url, None, 3).read()
        except:
            print("could not connect to lyricwiki.org")
            return ""

        resp = Util.bytes_to_string(resp)
        self.lyrics = self.get_lyrics(resp)

        return self.lyrics

    def get_lyrics(self, resp):
        # cut HTML source to relevant part
        start = resp.find("class='lyricbox'>")
        if start == -1:
            print("lyrics start not found")
            return ""
        resp = resp[(start + 17):]
        end = resp.find("<div class='lyricsbreak'>")
        if end == -1:
            print("lyrics end not found")
            return ""
        resp = resp[:end]

        # replace unwanted parts
        resp = html.unescape(resp)
        resp = resp.replace("<br>", "\n")
        resp = resp.replace("<br />", "\n")
        resp = resp.replace("<i>", "")
        resp = resp.replace("</i>", "")
        resp = re.sub("<a[^>]*>", "", resp)
        resp = resp.replace("</a>", "")
        resp = resp.strip()

        return resp
