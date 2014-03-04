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
        # API getSong request
        url = "http://lyrics.wikia.com/api.php?func=getSong&artist=" + urllib.parse.quote(self.artist) + "&song=" + urllib.parse.quote(self.title) + "&fmt=realjson"
        print("call lyrikwiki API: " + url)
        try:
            resp = urllib.request.urlopen(url, None, 3).read()
        except:
            print("could not connect to lyricwiki.org API")
            return ""
        
        resp = Util.bytes_to_string(resp)
        if resp == "":
            return ""
        
        resp = json.loads(resp)
        
        if resp["lyrics"] == "Not found":
            return ""
        
        lyrics_url = resp["url"]
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
        start = resp.find("</span></div>&")
        if start == -1:
            start = resp.find("</span></div><i>&")
            if start == -1:
                print("lyrics start not found")
                return ""
        resp = resp[(start+13):]
        end = resp.find("<!--")
        if end == -1:
            print("lyrics end not found")
            return ""
        resp = resp[:(end-1)]
        
        # replace unwanted characters
        resp = resp.replace("<br\n/>", "&#10;").replace("<br />", "&#10;").replace("<i>", "").replace("</i>", "").replace("&#", "");
        
        # decode characters
        resp = Util.decode_chars(resp)
        
        # if lyrics incomplete, skip!
        if resp.find("[...]") != -1:
            print("uncomplete lyrics")
            resp = ""
        
        return resp
    

        
        
        