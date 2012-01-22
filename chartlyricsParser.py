# Parser for Chartlyrics.com API

import urllib2, time, string
from HTMLParser import HTMLParser

class chartlyricsParser(HTMLParser):
    
    def __init__(self, artist, title):
        HTMLParser.__init__(self)
        self.artist = artist
        self.title = title
        self.tag = None
        self.lyricId = None
        self.checksum = None
        self.found = False
        self.lyric = "no lyrics found"
    
    # define handler for parsing             
    def handle_starttag(self, tag, attrs):
        self.tag = tag
    
    # definde handler for parsing    
    def handle_endtag(self, tag):
        if self.found and tag == "searchlyricresult":
            self.found = False
        self.tag = None
    
    # definde handler for parsing               
    def handle_data(self, data):
        if self.checksum is None and self.tag == "lyricchecksum":
            self.checksum = data
            self.found = True
            return      
        
        if self.lyricId is None and self.tag == "lyricid":
            self.lyricId = data
            return
            
        if self.found and self.tag == "artist":
            if data.lower() != self.artist:
                self.lyricId = None
                self.checksum = None
                self.found = False
            return
                
        if self.found and self.tag == "song":
            if data.lower() != self.title:
                self.lyricId = None
                self.checksum = None
                self.found = False
            return
                
        if self.tag == "lyric":
            self.lyric = data
            print "found lyrics"
        
    def parse(self):
        # API searchLyric request
        url = "http://api.chartlyrics.com/apiv1.asmx/SearchLyric?artist=" + urllib2.quote(self.artist) + "&song=" + urllib2.quote(self.title)
        print "call chartlyrics API: " + url
        req = urllib2.Request(url)
        while True:
            try:
                resp = urllib2.urlopen(req).read()
                break
            except:
                time.sleep(2)
        self.feed(resp)
        
        # API getLyric request
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
            # searchLyric was not successful
            print "no lyrics found"
        
        return self.lyric
        