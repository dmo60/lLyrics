#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: engine_sogou.py

import engine, re, urllib
import chardet

class Parser(engine.engine):

    def __init__(self, artist, title):
        engine.engine.__init__(self, proxy = None, locale = "utf-8")
        self.artist = artist
        self.title = title
        self.found = True
        self.lyric_url = None
        self.lyrics = ""
        self.proxy = None
        self.net_encoder = 'gb18030'

    def changeUrlToGb(self, info):
        address = unicode(info, self.locale).encode('gb18030')
        return address

#    def sogouParser(self, a):
#        wList = []
#        for i in a:
#            b = urllib.unquote_plus(i.split('=')[-1])
#            c = unicode(b, 'gb18030').encode('utf8')
#            title, artist = c.split('-', 1)
#            wList.append([artist, title, i])
#        return wList

    # def request(self, artist, title):
    #     url1 = 'http://mp3.sogou.com/gecisearch.so?query='
    #     url2_pre = '%s %s' % (self.changeUrlToGb(title), self.changeUrlToGb(artist))
    #     url2 = urllib.quote_plus(url2_pre)
    #     url = url1 + url2

    #     try:
    #         file = urllib.urlopen(url, None, self.proxy)
    #         lrc_gb = file.read()
    #         file.close()
    #     except IOError:
    #         return (None, True)
    #     else:
    #         tmp = unicode(lrc_gb, 'gb18030').encode('utf8')
    #         tmpList = re.findall('href=\"downlrc\.jsp\?tGroupid=.*?\"', tmp)
    #         if(len(tmpList) == 0):
    #             return (None, False)
    #         else:
    #             tmpList = map(lambda x: re.sub('href="|"', '', 'http://mp3.sogou.com/' + x), tmpList)
    #             lrcList = self.sogouParser(tmpList)
    #             return (lrcList, False)

    def parse(self):
        url1 = 'http://mp3.sogou.com/gecisearch.so?query='
        url2_pre = '%s %s' % (self.changeUrlToGb(self.title), self.changeUrlToGb(self.artist))
        url2 = urllib.quote_plus(url2_pre)
        url = url1 + url2
        print "url: " + url

        try:
            file = urllib.urlopen(url, None, self.proxy)
            lrc_gb = file.read()
            file.close()
        except IOError:
            print "could not open sogou url"
            return ""
        else:
            tmp = unicode(lrc_gb, 'gb18030').encode('utf8')
            tmpList = re.search('href=\"downlrc\.jsp\?tGroupid=.*?\"', tmp)
            if tmpList is not None:
                # print tmpList.group()
                lrcUrl = 'http://mp3.sogou.com/' + re.sub('href="|"', '', tmpList.group())
                # print lrcUrl
                lyrics, check = self.downIt(lrcUrl)
#                detect_dict = chardet.detect(lyrics)
#                confidence, encoding = detect_dict['confidence'], detect_dict['encoding']
#                lyrics = lyrics.decode(encoding, 'ignore')
                return lyrics
            else:
                return ""
