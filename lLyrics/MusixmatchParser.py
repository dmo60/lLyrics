import requests
import json
import urllib.request

class Parser(object):
        
    def __init__(self, artist, title):
        self.artist = artist
        self.title = title
        self.lyrics = ""
        self.API_KEY = '1a2244035bb2332c83f241548413509f'
        self.API = 'http://api.musixmatch.com/ws/1.1/'

    def parse(self):
        METHOD = 'matcher.track.get'
        query = '%s%s?apikey=%s' % (self.API, METHOD, self.API_KEY)

        if self.artist:
            query += '&q_artist=%s' % (self.artist)
        if self.title:
            query += '&q_track=%s' % (self.title)

        try:
            resp = requests.get(query)
        except:
            print("Cannot connect to Musixmatch")
            return ""

        if resp.status_code != 200:
            print("Error %s" % (resp.status_code))
            return ""

        resp = json.loads(resp.content.decode('utf-8'))

        status_code = resp['message']['header']['status_code']
        if status_code != 200:
            print("Error %s" % (status_code))
            return ""
        
        share_url = resp['message']['body']['track']['track_share_url']
        self.lyrics = self.get_lyrics(share_url)

        return self.lyrics

    def get_lyrics(self, url):
        try:
            html = urllib.request.urlopen(url).read()
        except:
            print("Cannot connect to Musixmatch")
            return ""

        html = html.decode("utf-8")

        start = html.find("$lyrics-body")
        end = html[start:].find("</span>")

        return html[start+14:start+end]

