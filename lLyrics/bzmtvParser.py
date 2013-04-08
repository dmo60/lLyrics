# -*- coding: utf-8 -*- 
# Parser for lrc.bzmtv.com

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
import chardet 
class Parser(object):
    
    def __init__(self, artist, title):

        self.artist = artist
        self.title = title
        self.lyrics = ""
        self.url_home = "http://lrc.bzmtv.com/"
    def parse(self):
        # create lyrics Url
    
        #url = "http://lrc.bzmtv.com/so.asp?key=" + urllib2.quote(self.title) +  "&go=go&y=1"  #go=(go|so) go为精确搜索 so模糊搜索  y=(1|2|3)(歌名|歌手|专辑)
        url = "http://lrc.bzmtv.com/so.asp?key=" + self.title.decode('utf-8').encode('gb2312') +  "&go=go&y=1"  
#go=(go|so) go为精确搜索 so模糊搜索  y=(1|2|3)(歌名|歌手|专辑)   网站的比较是使用gb2312编码, 所以title需要编码
  
    
        try:
            resp = urllib2.urlopen(url, None, 3).read()
        except:
            print "could not get result list"
            return ""
        resp = resp.decode( 'gb2312', 'ignore').encode('utf-8')
    
        partern1 = r'.*class="slmc".*' + self.title  + r'.*\n.*class="acll".*' + self.artist
        result = re.search ( partern1, resp )
        if result == None:
            return ""
        
        partern2 = r'lrc/.*htm'
        result_url = re.search ( partern2, result.group(0) )
        if result_url == None:
            return ""
        url = self.url_home + result_url.group(0)
        try:
            self.lyrics = urllib2.urlopen( url, None, 3).read()
        except:
            print "could not download lrc"
            return ""
        self.lyrics = self.lyrics.decode('gb2312', 'ignore').encode('utf-8')
        partern =  r'\[ti:' + self.title
        startm = re.search ( partern , self.lyrics )
        partern =  r'\[.*</pre>'
        endm = re.search ( partern , self.lyrics )
        return self.lyrics[startm.start(): endm.end()-len("</pre>")]
      

    

if __name__  == '__main__':
 #  test = Parser(r'苏打绿', r'无与伦比的美丽')
    print "Input the artist and title :"
 #   artist = raw_input () 
 #   title = raw_input () 
 #   art =  unicode( artist, 'utf-8')
 #   tit = unicode ( title, 'utf-8') 
    test = Parser( u'蔡琴'.encode('utf-8') , u'你的眼神'.encode('utf-8')  )
    
    print test.parse()
