# Parser for Metrolyrics.com

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

class Parser(object):
    
    def __init__(self, artist, title):
        self.artist = artist
        self.title = title
        self.lyrics = ""
        
    def parse(self):
        # remove punctuation from artist/title
        clean_artist = Util.remove_punctuation(self.artist)
        clean_title = Util.remove_punctuation(self.title)
            
        # create lyrics Url
        url = "http://www.metrolyrics.com/" + clean_title.replace(" ", "-") + "-lyrics-" + clean_artist.replace(" ", "-") + ".html"
        print("metrolyrics Url " + url)
        try:
            resp = urllib.request.urlopen(url, None, 3).read()
        except:
            print("could not connect to metrolyrics.com")
            return ""
        
        resp = Util.bytes_to_string(resp)
        
        # verify title
        title = resp
        start = title.find("<title>")
        if start == -1:
            print("no title found")
            return ""
        title = title[(start+7):]
        end = title.find(" Lyrics | MetroLyrics</title>")
        if end == -1:
            print("no title end found")
            return ""
        title = title[:end]
        title = HTMLParser().unescape(title)
        songdata = title.split(" - ")
        try:
            if self.artist != songdata[0].lower() or self.title != songdata[1].lower():
                print("wrong artist/title! " + songdata[0].lower() + " - " + songdata[1].lower())
                return ""
        except:
            print("incomplete artist/title")
            return ""
        
        self.lyrics = self.get_lyrics(resp)
        self.lyrics = string.capwords(self.lyrics, "\n").strip()
        
        return self.lyrics
    
    def get_lyrics(self, resp):
        # cut HTML source to relevant part
        start = resp.find("<p class='verse'>")
        if start == -1:
            print("lyrics start not found")
            return ""
        resp = resp[start:]
        end = resp.find("</div>")
        if end == -1:
            print("lyrics end not found ")
            return ""
        resp = resp[:(end)]
        
        # replace unwanted parts
        resp = resp.replace("<p class='verse'>", "")
        resp = resp.replace("</p>", "\n\n")
        resp = resp.replace("<br/>", "")
        resp = resp.strip()
        
        return resp
    
