# Parser for letras.terra.com.br

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

import urllib.request, urllib.parse
import string

from html.parser import HTMLParser

import Util

class Parser(object):
    
    def __init__(self, artist, title):
        self.artist = artist
        self.title = title
        self.lyrics = ""
        
    def parse(self):        
        artist = urllib.parse.quote(self.artist)
        title = urllib.parse.quote(self.title)
        join = urllib.parse.quote(' - ')
            
        # create artist Url
        url = "http://letras.mus.br/winamp.php?t=%s%s%s" % (artist, join, title)
        
        print("letras.terra.com.br Url " + url)
        try:
            resp = urllib.request.urlopen(url, None, 3).read()
        except:
            print("could not connect to letras.terra.com.br")
            return ""
        
        resp = Util.bytes_to_string(resp)
        
        if not self.verify(resp):
            return ""
        
        self.lyrics = self.get_lyrics(resp)
        self.lyrics = string.capwords(self.lyrics, "\n").strip()
        
        return self.lyrics
        
    def get_lyrics(self, resp):
        # cut HTML source to relevant part
        start = resp.find("<p>")
        if start == -1:
            print("lyrics start not found")
            return ""
        resp = resp[(start+3):]
        end = resp.find("<div id=")
        if end == -1:
            print("lyrics end not found ")
            return ""
        resp = resp[:(end)]
        
        # replace unwanted parts
        resp = resp.replace("<br/>", "")
        resp = resp.replace("</p>", "")
        resp = resp.replace("<p>", "\n")
        
        resp = HTMLParser().unescape(resp)
                
        return resp
    
    def verify(self, resp):
        # verify song artitst/title
        title = resp
        start = title.find("<h1>")
        if start == -1:
            print("no title found")
            return False
        title = title[(start+4):]
        
        start = title.find(">")
        if start == -1:
            print("no title start found")
            return False
        title = title[(start+1):]
        
        end = title.find("</a>")
        if end == -1:
            print("no title end found")
            return False
        title = HTMLParser().unescape(title[:end]).lower()
        
        artist = resp
        start = artist.find("<h2>")
        if start == -1:
            print("no artist found")
            return False
        artist = artist[(start+4):]
        
        start = artist.find(">")
        if start == -1:
            print("no artist start found")
            return False
        artist = artist[(start+1):]
        
        end = artist.find("</a>")
        if end == -1:
            print("no artist end found")
            return False
        artist = HTMLParser().unescape(artist[:end]).lower()
        
        if self.artist != artist or self.title != title:
            print("wrong artist/title! " + artist + " - " + title)
            return False
        
        return True
