#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: engine_baidu.py

import engine
# import re
import urllib
#import chardet
from bs4 import BeautifulSoup


UA = "Mozilla/5.0 (iPad; CPU OS 5_1_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B206 Safari/7534.48.3"


class Parser(engine.engine):

    def __init__(self, artist, title):
        engine.engine.__init__(self, proxy=None, locale="utf-8")
        self.artist = artist
        self.title = title
        self.found = True
        self.lyric_url = None
        self.lyrics = ""
        self.proxy = None

    def request(self):
        url1 = 'http://music.baidu.com/search/lrc?key='
        url2_pre = '%s %s' % (self.title, self.artist)
        url2 = urllib.parse.quote(url2_pre)
        url = url1 + url2

        try:
            #request = urllib2.Request(url)
            #opener = urllib2.build_opener()
            #request.add_header('User-Agent', UA)
            #content = opener.open(request).read()
            content = urllib.request.urlopen(url).read()
        except IOError:
            return (None, True)
        else:
            lrc_list = []
            soup = BeautifulSoup(content)
            # num = soup.find(attrs={'class': re.compile("number")}).get_text()
            try:
                li = soup.find(name='div', attrs={'class': r"lrc-list"}).find_all('li')
            except:
                return (None, True)
            for i in li:
                try:
                    ti = i.find(attrs={'class': 'song-title'}).get_text().split()[1]
                except:
                    ti = ''
                try:
                    ar = i.find(attrs={'class': 'artist-title'}).get_text().split()[1]
                except:
                    ar = ''
                try:
                    al = i.find(attrs={'class': 'album-title'}).get_text().split()[1]
                except:
                    al = ''
                try:
                    lrc_url = i.find(attrs={'class': 'down-lrc-btn'}).get('class')[2].split("'")[3]
                    lrc_url = "http://music.baidu.com" + lrc_url
                except:
                    lrc_url = ''
                lrc_list.append([ti, ar, al, lrc_url])
        return (lrc_list, False)

    def parse(self):
        (lrcList, flag) = self.request()
        if flag == True or lrcList is None:
            return ""
        else:
            lrcUrl = lrcList[0][3]
            print(lrcUrl)
            lyrics, check = self.downIt(lrcUrl)
#            detect_dict = chardet.detect(lyrics)
#            try:
#                confidence, encoding = detect_dict['confidence'], detect_dict['encoding']
#            except:
#                encoding = 'gb18030'
#            print(encoding)
#            lyrics = lyrics.decode(encoding, 'ignore')
#            lyrics = lyrics.encode("utf-8", "replace")
#            return lyrics
            return self.decompress(lyrics.split('\n'))

