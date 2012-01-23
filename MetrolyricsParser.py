# Parser for Metrolyrics.com

import urllib2, string, re
from LyricwikiParser import LyricwikiParser

class MetrolyricsParser():
    
    def __init__(self, artist, title):
        self.artist = artist
        self.title = title
        self.lyrics = ""
        
    def parse(self):
        # create lyrics Url
        url = "http://www.metrolyrics.com/" + self.artist.replace(" ", "-") + "-lyrics-" + self.title.replace(" ", "-") + ".html"
        print "metrolyrics Url " + url
        req = urllib2.Request(url)
        try:
            resp = urllib2.urlopen(req).read()
        except:
            print "could not connect to metrolyrics.com"
            return ""
        
        # verify title
        title = resp
        start = title.find("<title>")
        if start == -1:
            print "no title found! broken page?"
            return ""
        title = title[(start+7):]
        end = title.find(" LYRICS</title>")
        if end == -1:
            print "no title end found! broken page?"
            return ""
        title = title[:end]
        songdata = title.split(" - ")
        if self.artist != songdata[0].lower() or self.title != songdata[1].lower():
            print "wrong artist/title!"
            return ""
        
        self.lyrics = self.get_lyrics(resp)
        
        return self.lyrics
    
    def get_lyrics(self, resp):
        # cut HTML source to relevant part
        start = resp.find("<span class='line line-s' id='line_1'>")
        if start == -1:
            if start == -1:
                print "lyrics start not found"
                return ""
        resp = resp[start:]
        end = resp.find("</div")
        if end == -1:
            print "lyrics end not found "
            return ""
        resp = resp[:(end)]
        
        # replace unwanted characters
        resp = resp.replace("<span class='line line-s' id='line_1'>", "")
        resp = re.sub("\<span class\=\'line line-s\' id\=\'line_[0-9][0-9]?\'\>\<span style\=\'color:#888888;font-size:0\.75em\'\>\[.+\]\</span\>", "", resp)
        resp = re.sub("\<span class\=\'line line-s\' id\=\'line_[0-9][0-9]?\'\>", "&#10;", resp)
        resp = re.sub("\<em class\=\"smline sm\" data-meaningid\=\"[0-9]+\" \>", "", resp)
        resp = re.sub("(\</em\>)?\</span\>", "", resp)
        resp = resp.replace("<br />", "&#10;")
        resp = resp.replace("</p>", "")
        resp = resp.replace("&#", "")
        resp = resp.strip()
        resp = resp[:1]
        
        # decode characters
        resp = LyricwikiParser.decode_chars(resp)
        
        return resp