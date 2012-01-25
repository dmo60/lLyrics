# Parser for LYRDB.com

import urllib2, string

class Parser():
    
    def __init__(self, artist, title):
        self.artist = artist
        self.title = title
        self.lyrics = ""
        
    def parse(self):
        # create lyrics Url
        url = "http://webservices.lyrdb.com/lookup.php?q=" + urllib2.quote(self.artist) + "|" + urllib2.quote(self.title) + "&for=match&agent=llyrics"
        print "call lyrdb API " + url
        try:
            resp = urllib2.urlopen(url).read()
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
            self.lyrics = urllib2.urlopen(url).read()
        except:
            print "could not connect to lyrdb.com"
            return ""
        
        self.lyrics = string.capwords(self.lyrics, "\n").strip()
        
        return self.lyrics