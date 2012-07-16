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

import urllib2
import string

class Parser(object):
    
    def __init__(self, artist, title):
        self.artist = artist
        self.title = title
        self.lyrics = ""
        
    def parse(self):
        # create lyrics Url
        url = "http://webservices.lyrdb.com/lookup.php?q=" + urllib2.quote(self.artist) + "|" + urllib2.quote(self.title) + "&for=match&agent=llyrics"
        print "call lyrdb API " + url
        try:
            resp = urllib2.urlopen(url, None, 3).read()
        except:
            print "could not connect to lyrdb.com"
            return ""
        
        end = resp.find("\\");
        if end == -1:
            print "no id found"
            return ""
        lyricsid = resp[:end]
        print lyricsid
        
        url = "http://www.lyrdb.com/getlyr.php?q=" + lyricsid
        print "url " + url
        try:
            self.lyrics = urllib2.urlopen(url, None, 3).read()
        except:
            print "could not connect to lyrdb.com"
            return ""
        
        self.lyrics = string.capwords(self.lyrics, "\n").strip()
        
        return self.lyrics