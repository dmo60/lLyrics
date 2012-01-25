# Parser for letras.terra.com.br

import urllib2, re, string

class TerraParser():
    
    def __init__(self, artist, title):
        self.artist = artist
        self.title = title
        self.lyrics = ""
        
    def parse(self):
        # remove punctuation from artist
        clean_artist = self.artist
        clean_artist = clean_artist.replace("+", "and")
        for c in string.punctuation:
            clean_artist = clean_artist.replace(c, "")
        clean_artist = clean_artist.replace(" ", "-")
            
        # create artist Url
        url = "http://letras.terra.com.br/" + clean_artist
        print "letras.terra.com.br artist Url " + url
        try:
            resp = urllib2.urlopen(url).read()
        except:
            print "could not connect to letras.terra.com.br"
            return ""
        
        # find title id
        match = re.search("\<li\>\<a class\=\"elemsug\" href\=\"/" + clean_artist + "/([0-9]*)/\"\>" + re.escape(self.title) + "\</a\>\</li\>", resp, re.I)
        if match is None:
            print "could not find title"
            return ""
        lyricsid = match.group(1)
        
        # create lyrics Url
        url = url + "/" + lyricsid
        print "letras.terra.com.br Url " + url
        try:
            resp = urllib2.urlopen(url).read()
        except:
            print "could not connect to letras.terra.com.br"
            return ""
        
        self.lyrics = self.get_lyrics(resp)
        self.lyrics = string.capwords(self.lyrics, "\n").strip()
        
        return self.lyrics
        
    def get_lyrics(self, resp):
        # cut HTML source to relevant part
        start = resp.find("<p>")
        if start == -1:
            print "lyrics start not found"
            return ""
        resp = resp[(start+3):]
        end = resp.find("</p></div>")
        if end == -1:
            print "lyrics end not found "
            return ""
        resp = resp[:(end-1)]
        
        # replace unwanted parts
        resp = resp.replace("<br/>", "")
        resp = resp.replace("</p>", "")
        resp = resp.replace("<p>", "\n")
                
        return resp
        
