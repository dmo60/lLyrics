# Parser for Sogou.com

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
import urllib2
import chardet

class Parser(object):

    def __init__(self, artist, title):
        self.artist = artist
        self.title = title

    def changeUrlToGb(self, info):
        address = unicode(info, 'utf-8').encode('gb18030')
        return address

    def parse(self):
        url1 = 'http://mp3.sogou.com/gecisearch.so?query='
        url2_pre = '%s %s' % (self.changeUrlToGb(self.title), self.changeUrlToGb(self.artist))
        url2 = urllib2.quote(url2_pre)
        url = url1 + url2
        print "url: " + url

        try:
            resp = urllib2.urlopen(url, None, 3).read()
        except IOError:
            print "could not open sogou url"
            return ""
        
        tmp = unicode(resp, 'gb18030').encode('utf-8')
        tmpList = re.search('href=\"downlrc\.jsp\?tGroupid=.*?\"', tmp)
        if tmpList is None:
            return ""
        
        lrcUrl = 'http://mp3.sogou.com/' + re.sub('href="|"', '', tmpList.group())
        print "lrcfile: " + lrcUrl
        try:
            lyrics = urllib2.urlopen(lrcUrl, None, 3).read()
        except:
            print "could not download sogou lrc file"
            return ""
        
        try:
            encoding = chardet.detect(lyrics)['encoding']
        except:
            encoding = 'gb18030'
            lyrics = lyrics.decode(encoding, 'replace')
        
        return lyrics
