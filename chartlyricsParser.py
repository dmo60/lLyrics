import urllib2, time
from HTMLParser import HTMLParser

class chartlyricsParser(HTMLParser):
    
    def __init__(self, artist, title):
        HTMLParser.__init__(self)
        self.artist = artist
        self.title = title
        self.tag = None
        self.lyricId = None
        self.checksum = None
        self.set = False
        self.lyric = "no lyrics found"
        
        print "search lyrics for " + artist + " - " + title
        
    def handle_starttag(self, tag, attrs):
        self.tag = tag
        
    def handle_endtag(self, tag):
        if self.set and tag == "searchlyricresult":
            self.set = False
        self.tag = None
                    
    def handle_data(self, data):
#        print "data " + data
        if self.checksum is None and self.tag == "lyricchecksum":
            self.checksum = data
            self.set = True
            return      
        
        if self.lyricId is None and self.tag == "lyricid":
            self.lyricId = data
            return
            
        if self.set and self.tag == "artist":
            if data != self.artist:
                self.lyricId = None
                self.checksum = None
                self.set = False
            return
                
        if self.set and self.tag == "song":
            if data != self.title:
                self.lyricId = None
                self.checksum = None
                self.set = False
            return
                
        if self.tag == "lyric":
            self.lyric = data
            print "found lyrics"
        
    def parse(self):
        url = "http://api.chartlyrics.com/apiv1.asmx/SearchLyric?artist=" + self.artist.replace(" ", "%20") + "&song=" + self.title.replace(" ", "%20")
        print "call chartlyrics API: " + url
        req = urllib2.Request(url)
        while True:
            try:
                resp = urllib2.urlopen(req).read()
                break
            except:
                time.sleep(2)
        self.feed(resp)
        
        if self.lyricId is not None and self.checksum is not None:
            url = "http://api.chartlyrics.com/apiv1.asmx/GetLyric?lyricId=" + self.lyricId + "&lyricCheckSum=" + self.checksum
            print "call chartlyrics API: " + url
            req = urllib2.Request(url)
            while True:
                try:
                    resp = urllib2.urlopen(req).read()
                    break
                except: 
                    time.sleep(2) 
            self.feed(resp)
        else:
            print "no lyrics found"
        
        return self.lyric
        