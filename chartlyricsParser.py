import urllib2, time
from HTMLParser import HTMLParser

class chartlyricsParser(HTMLParser):
    
    def __init__(self, artist, title):
        HTMLParser.__init__(self)
        self.artist = artist.replace(" ", "%20")
        self.title = title.replace(" ", "%20")
        self.tag = None
        self.lyricId = None
        self.checksum = None
        self.lyric = "not found"
        self.found = False
    
    def handle_starttag(self, tag, attrs):
        self.tag = tag
        print "starttag " + tag
        
    def handle_endtag(self, tag):
        self.tag = None
#        print "endtag " + tag
                    
    def handle_data(self, data):
#        print "data " + data
        if self.found:
            return
        if self.lyricId is None and self.tag == "lyricid":
            self.lyricId = data
            print "set lyricId to " + self.lyricId
        if self.checksum is None and self.tag == "lyricchecksum":
            self.checksum = data
            print "set checksum to " + self.checksum
        if self.tag == "lyric":
            self.lyric = data
            print "found lyrics"
        
    def parse(self):
        url = "http://api.chartlyrics.com/apiv1.asmx/SearchLyric?artist=" + self.artist + "&song=" + self.title
        print url
        req = urllib2.Request(url)
        try:
            resp = urllib2.urlopen(req).read()
        except:
            None
        self.feed(resp)
        
        url = "http://api.chartlyrics.com/apiv1.asmx/GetLyric?lyricId=" + self.lyricId + "&lyricCheckSum=" + self.checksum
        print url
        req = urllib2.Request(url)
        while True:
            try:
                resp = urllib2.urlopen(req).read()
                break
                print resp
            except: 
                time.sleep(2)
            
        self.feed(resp)
        
        return self.lyric
        