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

import urllib2, string
from HTMLParser import HTMLParser

class Parser(HTMLParser):
    
    def __init__(self, artist, title):
        HTMLParser.__init__(self)
        self.artist = artist
        self.title = title
        self.tag = None
        self.found = True
        self.lyric_url = None
        self.lyrics = ""
    
    # define handler for parsing             
    def handle_starttag(self, tag, attrs):
        self.tag = tag
    
    # definde handler for parsing    
    def handle_endtag(self, tag):
        self.tag = None
    
    # definde handler for parsing               
    def handle_data(self, data):
        if self.tag == "lyrics":
            if data == "Not found":
                self.found = False
        if self.found and self.tag == "url":
            self.lyric_url = data
        
    def parse(self):
        # API getSong request
        url = "http://lyrics.wikia.com/api.php?func=getSong&artist=" + urllib2.quote(self.artist) + "&song=" + urllib2.quote(self.title) + "&fmt=xml"
        print "call lyrikwiki API: " + url
        try:
            resp = urllib2.urlopen(url, None, 3).read()
            self.feed(resp)
        except:
            print "could not connect to lyricwiki.org API"
            return ""
        
        if self.lyric_url is None:
            return ""
        
        print "url: " + self.lyric_url
        
        # open lyrics-URL
        try:
            resp = urllib2.urlopen(self.lyric_url, None, 3).read()
        except:
            print "could not open lyricwiki url"
            return ""
        
        self.lyrics = self.get_lyrics(resp)
        self.lyrics = string.capwords(self.lyrics, "\n").strip()
        
        return self.lyrics
    
    def get_lyrics(self, resp):
        # cut HTML source to relevant part
        start = resp.find("</a></div>&")
        if start == -1:
            start = resp.find("</a></div><i>&")
            if start == -1:
                print "lyrics start not found"
                return ""
        resp = resp[(start+10):]
        end = resp.find("<!--")
        if end == -1:
            print "lyrics end not found"
            return ""
        resp = resp[:(end-1)]
        
        # replace unwanted characters
        resp = resp.replace("<br\n/>", "&#10;").replace("<br />", "&#10;").replace("<i>", "").replace("</i>", "").replace("&#", "");
        
        # decode characters
        resp = decode_chars(resp)
        
        # if lyrics incomplete, skip!
        if resp.find("[...]") != -1:
            print "uncomplete lyrics"
            resp = ""
        
        return resp
    
    
def decode_chars(resp):
    chars = resp.split(";")
    resp = ""
    for c in chars:
        try:
            resp = resp + unichr(int(c))
        except:
            print "unknown character " + c
    return resp
        
        
        