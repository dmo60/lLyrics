# Parser for leoslyrics.com

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

import Util

class Parser(object):
    
    def __init__(self, artist, title):
        self.artist = artist
        self.title = title
        self.lyrics = ""
        
    def parse(self):
        # remove unwanted characters from artist and title strings
        clean_artist = self.artist
        clean_artist = clean_artist.replace("and ", "")
        clean_artist = Util.remove_punctuation(clean_artist)
        clean_artist = clean_artist.replace(" ", "-")
        
        clean_title = self.title
        clean_title = Util.remove_punctuation(clean_title)
        clean_title = clean_title.replace(" ", "-")
            
        # create lyrics Url
        url = "http://www.leoslyrics.com/" + clean_artist + "/" + clean_title + "-lyrics/"
        print("leoslyrics Url " + url)
        try:
            resp = urllib.request.urlopen(url, None, 3).read()
        except:
            print("could not connect to leoslyrics.com")
            return ""
        
        resp = Util.bytes_to_string(resp)
        self.lyrics = self.get_lyrics(resp)
        self.lyrics = string.capwords(self.lyrics, "\n").strip()
        
        return self.lyrics
        
    def get_lyrics(self, resp):
        # cut HTML source to relevant part
        start_string = """<div ondragstart="return false;" onselectstart="return false;" oncontextmenu="return false;">"""
        start = resp.find(start_string)
        if start == -1:
            print("lyrics start not found")
            return ""
        resp = resp[(start+len(start_string)):]
        
        end = resp.find("</div>")
        if end == -1:
            print("lyrics end not found ")
            return ""
        resp = resp[:(end-1)]
        
        # detect no lyrics message
        if not resp.strip().startswith("&#"):
            return ""
        
        # replace unwanted parts
        resp = resp.replace("<br />", "")
        resp = resp.replace("&#13;", "&#10;")
        resp = resp.replace("&#", "")
        resp = resp.strip()
        
        resp = Util.decode_chars(resp)
                
        return resp
        
