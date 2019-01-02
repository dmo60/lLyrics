# Parser for lyrics.alsong.co.kr
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

from xml.dom import minidom
import requests
import re
import string
import unicodedata

import Util

TEMPLATE = """\
<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope
xmlns:SOAP-ENV="http://www.w3.org/2003/05/soap-envelope"
xmlns:SOAP-ENC="http://www.w3.org/2003/05/soap-encoding"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xmlns:xsd="http://www.w3.org/2001/XMLSchema"
xmlns:ns2="ALSongWebServer/Service1Soap"
xmlns:ns1="ALSongWebServer"
xmlns:ns3="ALSongWebServer/Service1Soap12">
<SOAP-ENV:Body><ns1:GetResembleLyric2>
<ns1:stQuery>
<ns1:strTitle>{title}</ns1:strTitle>
<ns1:strArtistName>{artist}</ns1:strArtistName>
<ns1:nCurPage>{page}</ns1:nCurPage>
</ns1:stQuery>
</ns1:GetResembleLyric2>
</SOAP-ENV:Body>
</SOAP-ENV:Envelope>
"""

class Parser(object):
    def __init__(self, artist, title):
        self.artist = artist
        self.title = title
        self.lyrics = ""

    def parse(self):
        data = TEMPLATE.format(
            title = unicodedata.normalize("NFC", self.title),
            artist = unicodedata.normalize("NFC", self.artist),
            page = 0,
            ).encode()

        # create lyrics Url
        resp = requests.post(
            'http://lyrics.alsong.co.kr/alsongwebservice/service1.asmx',
            data,
            headers={'Content-Type': 'application/soap+xml'},
        )

        if resp.status_code != 200:
            print("Request is NOK")
            return ""

        return self.get_lyrics(resp)

    def get_lyrics(self, resp):
        dom = minidom.parseString(resp.content)
        lyric_list = dom.getElementsByTagName('strLyric')
        if not lyric_list:
            print("can't find strLyric")
            return ""

        try:            
            return lyric_list[0].firstChild.nodeValue.replace("<br>", "\n").strip()
        except:
            print("Parsing error")
            return ""
