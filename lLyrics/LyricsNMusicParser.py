# Parser for Lyricsnmusic.com

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

import urllib.request
import json
import string

import Util

API_KEY = "5ad5728ee39ebc05de6b8a7a154202"

class Parser():
    
    def __init__(self, artist, title):
        self.artist = artist
        self.title = title
        self.lyrics = ""
        
    def parse(self):
        # remove punctuation from artist/title
        clean_artist = Util.remove_punctuation(self.artist)
        clean_title = Util.remove_punctuation(self.title)
        
        # API request
        url = "http://api.lyricsnmusic.com/songs?api_key=" + API_KEY + "&artist=" + clean_artist.replace(" ", "+") + "&track=" + clean_title.replace(" ", "+")
        print("call lyricsnmusic API: " + url)
        try:
            resp = urllib.request.urlopen(url, None, 3).read()
        except:
            print("could not connect to lyricsnmusic.com API")
            return ""
        
        resp = Util.bytes_to_string(resp)
        if resp == "":
            return ""
        
        resp = json.loads(resp)
        
        if len(resp) == 0:
            return ""
        
        resp = self.verify(resp)
        if resp is None:
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
        start = resp.find("<pre itemprop='description'>")
        if start == -1:
            print("lyrics start not found")
            return ""
        resp = resp[(start+28):]
        end = resp.find("</pre>")
        if end == -1:
            print("lyrics end not found")
            return ""
        resp = resp[:(end)]
        
        return resp
    
    def verify(self, resp):
        for entry in resp:
            title = entry["title"].lower()
            artist = entry["artist"]["name"].lower()
            if self.artist == artist and self.title == title:
                return entry
            print("wrong artist/title! " + artist + " - " + title)
            
        return None
        