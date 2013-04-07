# -*- coding: utf-8 -*- 
# Parser for lrc123.com

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

import urllib2
import string
import re 
class Parser(object):
    
    def __init__(self, artist, title):
        self.artist = artist
        self.title = title
        self.lyrics = ""
        self.url_home = "http://www.lrc123.com"
    def parse(self):
        # create lyrics Url
      #  url = "http://webservices.lyrdb.com/lookup.php?q=" + urllib2.quote(self.artist) + "|" + urllib2.quote(self.title) + "&for=match&agent=llyrics"
        url = "http://www.lrc123.com/?keyword=" + urllib2.quote(self.title) +  "&field=song"
   #     print "call lyrdb API " + url
        try:
            resp = urllib2.urlopen(url, None, 3).read()
        except:
            print "could not get result list"
            return ""
       
        partern1 = r'歌手:<a.*' + self.artist + r'.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*\n.*'
        result = re.search ( partern1, resp )
        if result == None:
            return self.lyrics                   # no find the result , return none 
        
        partern2 = r'/download.*aspx'
        result_url = re.search ( partern2, result.group(0) )
        if result_url == None:
            return ""
        url = self.url_home + result_url.group(0)
        try:
            self.lyrics = urllib2.urlopen( url, None, 3).read()
        except:
            print "could not download lrc"
            return ""
      
        return self.lyrics.decode('gbk').encode('utf-8')

    

if __name__  == '__main__':
 #  test = Parser(r'苏打绿', r'无与伦比的美丽')
    test = Parser(r'蔡琴', r'你的眼神')
    
    print test.parse()
