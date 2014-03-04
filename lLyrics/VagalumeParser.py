# Parser for Vagalume.com.br

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
import json
import string

import Util

class Parser():
    
    def __init__(self, artist, title):
        self.artist = artist
        self.title = title
        self.lyrics = ""
        
    def parse(self):
        # API request
        url = "http://app2.vagalume.com.br/api/search.php?nolyrics=1&art=" + urllib.parse.quote(self.artist) + "&mus=" + urllib.parse.quote(self.title)
        print("call Vagalume API: " + url)
        try:
            resp = urllib.request.urlopen(url, None, 3).read()
        except:
            print("could not connect to vagalume.com.br API")
            return ""
        
        resp = Util.bytes_to_string(resp)
        if resp == "":
            return ""
        
        resp = json.loads(resp)
        
        if "notfound" in resp["type"]:
            return ""
        
        if resp["type"] == "aprox":
            if not self.verify(resp):
                return ""
            
        lyrics_url = resp["mus"][0]["url"]
        print("url: " + lyrics_url)
        
        # open lyrics-URL
        try:
            resp = urllib.request.urlopen(lyrics_url, None, 3).read()
        except:
            print("could not open lyricwiki url")
            return ""
        
        resp = Util.bytes_to_string(resp)
        
        self.lyrics = self.get_lyrics(resp)
        self.lyrics = string.capwords(self.lyrics, "\n").strip()
        
        return self.lyrics
    
    def get_lyrics(self, resp):
        # cut HTML source to relevant part
        start = resp.find("<div itemprop=description>")
        if start == -1:
            print("lyrics start not found")
            return ""
        resp = resp[(start+26):]
        end = resp.find("</div>")
        if end == -1:
            print("lyrics end not found ")
            return ""
        resp = resp[:(end)]
        
        # replace unwanted parts
        resp = resp.replace("<br/>", "\n")
        
        return resp
        
    def verify(self, resp):
        artist = resp["art"]["name"].lower()
        title = resp["mus"][0]["name"].lower()
        
        if self.artist != artist or self.title != title:
            print("wrong artist/title! " + artist + " - " + title)
            return False
        
        return True
        