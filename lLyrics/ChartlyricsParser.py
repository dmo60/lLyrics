# Parser for Chartlyrics.com API
#
# Chartlyrics API seems to have problems with multiple consecutive requests
# (it apparently requires a 20-30sec interval between two API-calls),
# so just use SearchLyricDirect since it only needs one API request.

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

from html.parser import HTMLParser

import Util


class Parser(HTMLParser):
    def __init__(self, artist, title):
        HTMLParser.__init__(self)
        self.artist = artist
        self.title = title
        self.tag = None
        self.correct = True
        self.lyrics = ""

    # define handler for parsing
    def handle_starttag(self, tag, attrs):
        self.tag = tag

    # definde handler for parsing
    def handle_endtag(self, tag):
        self.tag = None

    # definde handler for parsing
    def handle_data(self, data):
        if self.tag == "lyricsong":
            if data.lower() != self.title:
                self.correct = False
            return
        if self.correct and self.tag == "lyricsartist":
            if data.lower() != self.artist:
                self.correct = False
            return
        if self.correct and self.tag == "lyric":
            self.lyrics = data

    def parse(self):
        # API searchLyric request
        url = (
            "http://api.chartlyrics.com/apiv1.asmx/SearchLyricDirect?artist="
            + urllib.parse.quote(self.artist)
            + "&song="
            + urllib.parse.quote(self.title)
        )
        print("chartlyrics Url " + url)
        try:
            resp = urllib.request.urlopen(url, None, 3).read()
        except:
            print("could not connect to chartlyric.com API")
            return ""

        resp = Util.bytes_to_string(resp)
        self.lyrics = self.get_lyrics(resp)
        self.lyrics = string.capwords(self.lyrics, "\n").strip()

        return self.lyrics

    def get_lyrics(self, resp):
        # cut HTML source to relevant part
        start = resp.find("<Lyric>")
        if start == -1:
            print("lyrics start not found")
            return ""
        resp = resp[(start + 7) :]
        end = resp.find("</Lyric>")
        if end == -1:
            print("lyrics end not found ")
            return ""
        resp = resp[:end]

        return resp
