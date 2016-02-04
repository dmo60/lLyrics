# Parser for LYRDB.com

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
        # create lyrics Url
        url = "http://webservices.lyrdb.com/lookup.php?q=" + urllib.parse.quote(self.artist) + "|" + urllib.parse.quote(self.title) + "&for=match&agent=llyrics"
        print("call lyrdb API " + url)
        try:
            resp = urllib.request.urlopen(url, None, 3).read()
        except:
            print("could not connect to lyrdb.com")
            return ""
        
        resp = Util.bytes_to_string(resp)
        end = resp.find("\\");
        if end == -1:
            print("no id found")
            return ""
        lyricsid = resp[:end]
        print(lyricsid)
        
        url = "http://www.lyrdb.com/getlyr.php?q=" + lyricsid
        print("url " + url)
        try:
            resp = urllib.request.urlopen(url, None, 3).read()
        except:
            print("could not connect to lyrdb.com")
            return ""
        
        resp = Util.bytes_to_string(resp)
        
        # strip error messages
        start = resp.find("</b><br />")
        if start != -1:
            resp = resp[(start+11):]
            end = resp.find("<br />")
            resp = resp[:end]
        
        self.lyrics = string.capwords(resp, "\n").strip()
        
        return self.lyrics