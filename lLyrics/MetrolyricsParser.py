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

import urllib2, re, string
from HTMLParser import HTMLParser

import LyricwikiParser

class Parser():
    
    def __init__(self, artist, title):
        self.artist = artist
        self.title = title
        self.lyrics = ""
        
    def parse(self):
        # remove punctuation from artist/title
        clean_artist = self.artist
        clean_title = self.title
        for c in string.punctuation:
            clean_artist = clean_artist.replace(c, "")
            clean_title = clean_title.replace(c, "")
            
        # create lyrics Url
        url = "http://www.metrolyrics.com/" + clean_title.replace(" ", "-") + "-lyrics-" + clean_artist.replace(" ", "-") + ".html"
        print "metrolyrics Url " + url
        try:
            resp = urllib2.urlopen(url, None, 3).read()
        except:
            print "could not connect to metrolyrics.com"
            return ""
        
        # verify title
        title = resp
        start = title.find("<title>")
        if start == -1:
            print "no title found"
            return ""
        title = title[(start+7):]
        end = title.find(" LYRICS</title>")
        if end == -1:
            print "no title end found"
            return ""
        title = title[:end]
        title = HTMLParser().unescape(title)
        songdata = title.split(" - ")
        try:
            if self.artist != songdata[0].lower() or self.title != songdata[1].lower():
                print "wrong artist/title! " + songdata[0].lower() + " - " + songdata[1].lower()
                return ""
        except:
            print "incomplete artist/title"
            return ""
        
        self.lyrics = self.get_lyrics(resp)
        self.lyrics = string.capwords(self.lyrics, "\n").strip()
        
        return self.lyrics
    
    def get_lyrics(self, resp):
        # cut HTML source to relevant part
        start = resp.find("<span class='line line-s' id='line_1'>")
        if start == -1:
            print "lyrics start not found"
            return ""
        resp = resp[start:]
        end = resp.find("</div")
        if end == -1:
            print "lyrics end not found "
            return ""
        resp = resp[:(end)]
        
        # replace unwanted parts
        resp = resp.replace("<span class='line line-s' id='line_1'>", "")
        resp = re.sub("\<span class\=\'line line-s\' id\=\'line_[0-9][0-9]?\'\>\<span style\=\'color:#888888;font-size:0\.75em\'\>\[.+\]\</span\>", "", resp)
        resp = re.sub("\<span class\=\'line line-s\' id\=\'line_[0-9][0-9]?\'\>", "&#10;", resp)
        resp = re.sub("\<em class\=\"smline sm\" data-meaningid\=\"[0-9]+\" \>", "", resp)
        resp = re.sub("(\</em\>)?\</span\>", "", resp)
        resp = re.sub("(\<br /\>)*\</p\>", "", resp)
        resp = resp.replace("<br />", "&#10;")
        resp = resp.replace("&#", "")
        resp = resp.strip()
        resp = resp[:-1]
        
        # decode characters
        resp = LyricwikiParser.decode_chars(resp)
        
        return resp