# Utility functions
#
# Chartlyrics API seems to have problems with multiple consecutive requests
# (it apparently requires a 20-30sec interval between two API-calls), 
# so just use SearchLyricDirect since it only needs one API request.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
import string
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import xml.dom.minidom

from urllib.parse import urlparse
from urllib.parse import unquote

try:
    import chardet
except:
    print("module chardet not found or not installed!")


LASTFM_API_KEY = "6c7ca93cb0e98979a94c79a7a7373b77"


def decode_chars(resp):
    chars = resp.split(";")
    resp = ""
    for c in chars:
        try:
            resp = resp + chr(int(c))
        except:
            print("unknown character " + c)
    return resp



def remove_punctuation(data):
    for c in string.punctuation:
        data = data.replace(c, "")
    
    return data



def parse_lrc(data):
    tag_regex = "(\[\d+\:\d+\.\d*])"
    match = re.search(tag_regex, data)
    
    # no tags
    if match is None:
        return (data, None)
    
    data = data[match.start():]
    splitted = re.split(tag_regex, data)[1:]
    
    tags = []
    lyrics = ''
    for i in range(len(splitted)):
        if i % 2 == 0:
            # tag
            tags.append((time_to_seconds(splitted[i]), splitted[i+1]))
        else:
            # lyrics
            lyrics += splitted[i]
    
    return (lyrics, tags)
    
    
    
def time_to_seconds(time):
    time = time[1:-1].replace(":", ".")
    t = time.split(".")
    return 60 * int(t[0]) + int(t[1])



def bytes_to_string(data):
    try:
        encoding = chardet.detect(data)['encoding']
    except:
        print("could not detect bytes encoding, assume utf-8")
        encoding = 'utf-8'
    try:
        string = data.decode(encoding, 'replace')
    except:
        print("failed to decode bytes to string")
        return ""
    
    return string



def get_lastfm_correction(artist, title):
    params = urllib.parse.urlencode({'method':'track.getcorrection',
                               'api_key':LASTFM_API_KEY,
                               'artist':artist, 
                               'track':title})
    try:
        result = urllib.request.urlopen("http://ws.audioscrobbler.com/2.0/?" + params, None, 3).read()
    except:
        print("could not connect to LastFM API")
        return (artist, title, False)
    
    response = xml.dom.minidom.parseString(result)
    corrections = response.getElementsByTagName("correction")
    if not corrections:
        print("no LastFM corrections found")
        return (artist, title, False)
    
    # only consider one correction for now
    correction = corrections[0]
    
    if correction.getAttribute("artistcorrected") == "1":
        artist = correction.getElementsByTagName("name")[0].firstChild.data
        print("LastFM artist correction: " + artist)
    
    
    if correction.getAttribute("trackcorrected") == "1":
        title = correction.getElementsByTagName("name")[1].firstChild.data
        print("LastFM title correction: " + title)
    
    return (artist, title, True)
    