# Parser for darklyrics.com

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
import re

import Util

class Parser(object):
    
    def __init__(self, artist, title):
        self.artist = artist
        self.title = title
        self.lyrics = ""
        
    def parse(self):
        # remove unwanted characters from artist and title strings
        clean_artist = self.artist
        clean_artist = Util.remove_punctuation(clean_artist)
        clean_artist = clean_artist.replace(" ", "")
            
        # create artist Url
        url = "http://www.darklyrics.com/" + clean_artist[:1] + "/" + clean_artist + ".html"
        print("darklyrics artist Url " + url)
        try:
            resp = urllib.request.urlopen(url, None, 3).read()
        except:
            print("could not connect to darklyrics.com")
            return ""
        
        resp = Util.bytes_to_string(resp)
        
        # find title with lyrics url
        match = re.search("<a href=\"\.\.(.*?)\">" + self.title + "</a><br />", resp, re.I)
        if match is None:
            print("could not find title")
            return ""
        url = "http://www.darklyrics.com" + match.group(1)
        print("darklyrics Url " + url)
        try:
            resp = urllib.request.urlopen(url, None, 3).read()
        except:
            print("could not connect to darklyrics.com")
            return ""
        
        resp = Util.bytes_to_string(resp)
        
        self.track_no = url.split("#")[1] 
        
        self.lyrics = self.get_lyrics(resp)
        self.lyrics = string.capwords(self.lyrics, "\n").strip()
        
        return self.lyrics
        
    def get_lyrics(self, resp):
        # search for the relevant lyrics
        match = re.search("<h3><a name=\"" + self.track_no + "\">" + self.track_no + "\. " + self.title + "</a></h3>", resp, re.I)
        if match is None:
            print("lyrics start not found")
            return ""
        start = match.end()
        resp = resp[start:]
        
        end = resp.find("<h3><a name")
        if end == -1:
            # case lyrics are the last ones on the page
            end = resp.find("<div ")
        if end == -1:
            print("lyrics end not found")
            return ""
        
        resp = resp[:end]
        
        # replace unwanted parts
        resp = resp.replace("<br />", "")
        resp = resp.replace("<i>", "")
        resp = resp.replace("</i>", "")
                
        return resp
        
