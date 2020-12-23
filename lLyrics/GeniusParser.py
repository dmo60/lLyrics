# -*- coding: utf-8 -*-
# Parser for Genius.com
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
import re
import string

from html.parser import HTMLParser

import Util
import time

l = []


class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag == "div":
            for i, j in attrs:
                if "RightSidebar" in j:
                    l.append("\n")

    def handle_startendtag(self, tag, attrs):
        if tag == "br":
            l.append("\n")

    def handle_data(self, data):
        l.append(data)


class Parser(object):
    def __init__(self, artist, title):
        self.artist = artist
        self.title = title
        self.lyrics = ""

    def parse(self):
        # remove punctuation from artist/title
        self.artist = self.artist.replace("+", "and")
        clean_artist = Util.remove_punctuation(self.artist)
        clean_title = Util.remove_punctuation(self.title)

        # create lyrics Url
        url = (
            "https://genius.com/"
            + clean_artist.replace(" ", "-")
            + "-"
            + clean_title.replace(" ", "-")
            + "-lyrics"
        )
        print("rapgenius Url " + url)
        try:
            resp = urllib.request.urlopen(Util.add_request_header(url), None, 3).read()
        except:
            print("could not connect to genius.com")
            return ""

        try:
            resp = urllib.request.urlopen(Util.add_request_header(url), None, 3).read()
        except:
            print("could not connect to genius.com")
            return ""

        resp = Util.bytes_to_string(resp)

        self.lyrics = self.get_lyrics(resp)
        self.lyrics = string.capwords(self.lyrics, "\n").strip()

        return self.lyrics

    def get_lyrics(self, resp):
        # cut HTML source to relevant part
        start = resp.find('<div class="lyrics">')
        if start != -1:
            resp = resp[(start + 20) :]
            end = resp.find("</div>")
            if end == -1:
                print("lyrics end not found ")
                return ""
            resp = resp[:end]

            # replace unwanted parts
            resp = re.sub("<a[^>]*>", "", resp)
            resp = re.sub("<!--[^>]*>", "", resp)
            resp = resp.replace("</a>", "")
            resp = resp.replace("<br><br>", "\n")
            resp = resp.replace("<br>", "")
            resp = resp.replace("<br />", "")
            resp = resp.replace("<p>", "")
            resp = resp.replace("</p>", "")
            resp = resp.strip()

            return resp

        # parse alternative HTML version received from Genius
        start = resp.find('<div id="lyrics"')
        if start == -1:
            print("lyrics start not found")
            return ""
        resp = resp[start:]
        end = resp.find('<div id="about"')
        if end == -1:
            print("lyrics end not found ")
            return ""
        resp = resp[:end]

        parser = MyHTMLParser()
        parser.feed(resp)
        resp = "".join(l)
        l.clear()

        return resp
