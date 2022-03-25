import functools
import json
import traceback
import urllib.request
import urllib.parse
from lxml import html


class Parser(object):

    def __init__(self, artist, title):
        self.artist = artist
        self.title = title
        self.lyrics = ""
        self.API_KEY = '1a2244035bb2332c83f241548413509f'
        self.API_URL = 'https://api.musixmatch.com/ws/1.1/'

    def parse(self):
        # URL encode artist and title strings
        encoded_artist = urllib.parse.quote(self.artist)
        encoded_title = urllib.parse.quote(self.title)

        # Match & Fetch Track Details
        METHOD = 'matcher.track.get'
        query = '%s%s?apikey=%s' % (self.API_URL, METHOD, self.API_KEY)

        # Add artist or title to query URL
        if encoded_artist:
            query += '&q_artist=%s' % (encoded_artist)
        if encoded_title:
            query += '&q_track=%s' % (encoded_title)

        # Call the API
        try:
            resp = urllib.request.urlopen(query, None, 5)
        except:
            print("Cannot connect to Musixmatch\ncall Musixmatch API:%s" % (query))
            traceback.print_exc()
            return ""

        # Stop if HTTP Response code is not 200
        if resp.status != 200:
            print("Error! call Musixmatch API:%s\nHTML Reponse Code:%s" % (query, resp.status))
            return ""

        # Parse JSON response
        resp = resp.read().decode('utf-8')
        resp = json.loads(resp)

        # Check API Response Status Code
        status_code = resp['message']['header']['status_code']
        if status_code != 200:
            print("call Musixmatch API: %s\nError from Musixmatch API>> %s: %s" % (query, status_code, self.get_error_details_from_status_code(status_code)))
            return ""

        # Fetch and log track details and confidence score from the API
        track_details = resp['message']['body']['track']
        confidence_score = resp['message']['header']['confidence']
        print("Musixmatch Identified Track(Confidence %s%%) Details:>> %s" % (confidence_score, track_details))

        # Find if lyrics are available or terminate if not available
        has_lyrics = resp['message']['body']['track']['has_lyrics']
        if has_lyrics == 0:
            print("Musixmatch does not have lyrics for this song")
            return ""

        # Fetch track URL for getting lyrics
        track_url = track_details['track_share_url']
        # Fetch and return lyrics
        self.lyrics = self.get_lyrics(track_url)

        return self.lyrics

    def get_lyrics(self, url):

        try:
            lyrics_request = urllib.request.Request(url, headers={
                'Host': 'www.musixmatch.com',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
            })
            lyrics_html = urllib.request.urlopen(lyrics_request).read()
        except:
            print("Cannot connect to Musixmatch")
            traceback.print_exc()
            return ""

        # Parse response to a html page
        lyrics_html = html.fromstring(lyrics_html)
        # Extract lyrics from html
        lyrics = lyrics_html.xpath('//span[@class="lyrics__content__ok"]/text()')
        # Join parts of lyrics
        lyrics = functools.reduce(lambda a, b: a+b, lyrics)

        return lyrics

    def get_error_details_from_status_code(self, statusCode):
        details = {
            200: "The request was successful.",
            400: "The request had bad syntax or was inherently impossible to be satisfied.",
            401: "Authentication failed, probably because of invalid/missing API key.",
            402: "The usage limit has been reached, either you exceeded per day requests limits or your balance is insufficient.",
            403: "You are not authorized to perform this operation.",
            404: "The requested resource was not found.",
            405: "The requested method was not found.",
            500: "Ops. Something were wrong.",
            503: "Our system is a bit busy at the moment and your request can't be satisfied."
        }
        # Return error details based on API's status code
        return details.get(statusCode, 'Some error occurred')
