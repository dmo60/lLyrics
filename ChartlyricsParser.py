# Parser for Chartlyrics.com API
#
# Chartlyrics API seems to have problems with multiple consecutive requests
# (it apparently requires a 20-30sec interval between two API-calls), 
# so just use SearchLyricDirect since it only needs one API request. 

import urllib2
from HTMLParser import HTMLParser

class ChartlyricsParser(HTMLParser):
    
    def __init__(self, artist, title):
        HTMLParser.__init__(self)
        self.artist = artist
        self.title = title
        self.tag = None
        self.correct = True
        self.lyrics = ""
    
    # define handler for parsing             
    def handle_starttag(self, tag, attrs):
        self.tag = tag
    
    # definde handler for parsing    
    def handle_endtag(self, tag):
        self.tag = None
    
    # definde handler for parsing               
    def handle_data(self, data):
        if self.tag == "lyricsong":
            if data.lower() != self.title:
                self.correct = False
            return
        if self.correct and self.tag == "lyricsartist":
            if data.lower() != self.artist:
                self.correct = False
            return
        if self.correct and self.tag == "lyric":
            self.lyrics = data
        
    def parse(self):
        # API searchLyric request
        url = "http://api.chartlyrics.com/apiv1.asmx/SearchLyricDirect?artist=" + urllib2.quote(self.artist) + "&song=" + urllib2.quote(self.title)
        print "call chartlyrics API: " + url
        req = urllib2.Request(url)
        try:
            resp = urllib2.urlopen(req).read()
            self.feed(resp)
        except:
            print "could not connect to chartlyric.com API"
        
        return self.lyrics
        