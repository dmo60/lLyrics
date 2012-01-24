# Parser for Lyricwiki.org

import urllib2
from HTMLParser import HTMLParser

class LyricwikiParser(HTMLParser):
    
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
        req = urllib2.Request(url)
        try:
            resp = urllib2.urlopen(req).read()
            self.feed(resp)
        except:
            print "could not connect to lyricwiki.org API"
            return ""
        
        if self.lyric_url is None:
            return ""
        
        print "url: " + self.lyric_url
        
        # open lyrics-URL
        req = urllib2.Request(self.lyric_url)
        try:
            resp = urllib2.urlopen(req).read()
        except:
            print "could not open lyricwiki url"
            return ""
        
        self.lyrics = self.get_lyrics(resp)
        
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
        resp = self.decode_chars(resp)
        
        # if lyrics incomplete, skip!
        if resp.find("[...]") != -1:
            print "uncomplete lyrics"
            resp = ""
        
        return resp
    
    @staticmethod
    def decode_chars(resp):
        chars = resp.split(";")
        resp = ""
        for c in chars:
            try:
                resp = resp + unichr(int(c))
            except:
                print "unknown character " + c
        return resp
        
        
        