# -*- coding: utf-8 -*-

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

import urllib.request
import urllib.parse
from httplib2 import iri2uri # Japanese url
import json
import time
import os
import re

from xml.dom.minidom import parse
from bs4 import BeautifulSoup

import Util


class Site:

    def __init__(self, name=None, start=None, end=None, Id=None, tagNumber=-1):
        self.name = name
        self.start = start
        self.end = end
        self.Id = Id
        self.tagNumber = tagNumber
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, obj):
        return isinstance(obj, Site) and obj.name == self.name
    
    def __hash__(self):
        return self.name.__hash__()


class LyricsSearcher(object):

    '''
        This class search lyrics using
        Google search to get sources
        where to get the lyrics.
        It use informations stored in
        xml file to parse the lyrics
        from the websites.
    '''

    def __init__(self):
        self.title = None
        self.artist = None
        self.file_path = None
        self.sites = None
        self.urls = []
        self.index = -1
        self.only_api = True
        self.read_filters()

    #Get sources where to parse the lyrics
    def get_sources_to_search(self):
        print('searching Google...')
        num_queries = 1 * 4
        self.urls = []
        query = urllib.parse.urlencode({'q':
                                        '-youtube.com ' +
                                        self.title + ' '
                                        + self.artist + ' lyrics'})
        url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&%s'\
               % query
        for start in range(0, num_queries, 4):
            request_url = '{0}&start={1}'.format(url, start)
            print(request_url)
            request = urllib.request.Request(request_url)
            #Don't use python agent
            request.add_header('User-Agent',
                               'Mozilla/4.0 (compatible; MSIE 6.0; \
                               Windows NT 5.1)')
            try:
                search_results = urllib.request.urlopen(request)
                encoding = search_results.headers.get_content_charset()
                response = search_results.read().decode(encoding)
                response = json.loads(response)
                if response['responseData'] is not None:
                    results = response['responseData']['results']
                else:
                    print('no more results!')
                    break
                for site in self.sites:
                    for items in results:
                        if site.name.lower() in (items['url']):
                            self.urls.append((site, items['url']))
            except:
                pass
            time.sleep(1)  # Otherwise Google will return an error
        if len(self.urls) == 0:
            self.search_Google()
        print(self.urls)

    def get_lyrics_from_source(self, site, url):
        '''
        Parse lyrics from the source using informations
        in site.
    '''
        print(site.name + " Url " + url)
        try:
            resp = urllib.request.urlopen(url, None, 3).read()
        except:
            #change the position of the site
            temp = [s for s in self.sites if s.name != site.name]
            self.sites = temp
            self.sites.append(site)
            print("could not connect " + site.name)
            return ""

        resp = Util.bytes_to_string(resp)
        lyrics = self.get_lyrics(resp, site)
        #lyrics = string.
        return lyrics

    def read_filters(self):
        print('reading filters...')
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        xmlfile = os.path.join(BASE_DIR, 'sites.xml')
        doc = parse(xmlfile)
        self.sites = []
        for item in doc.documentElement.getElementsByTagName("site"):
            try:
                site = Site()
                site.name = item.getElementsByTagName("name")[0]\
                                                .childNodes[0].nodeValue
                site.start = item.getElementsByTagName("start")[0]\
                                                .childNodes[0].nodeValue
                site.end = item.getElementsByTagName("end")[0]\
                                                .childNodes[0].nodeValue
                site.Id = item.getElementsByTagName("id")[0]\
                                                .childNodes[0].nodeValue
                site.tagNumber = int(item.getElementsByTagName("tagNumber")[0]\
                                                .childNodes[0].nodeValue)
                self.sites.append(site)
            except:
                print('Error occured when reading xml file')
        print(self.sites)

    def get_lyrics(self, resp, site):
        # cut HTML source to relevant part
        print(site.name)
        if(site.Id != None):
            soup = BeautifulSoup(resp)
            elements = soup.select(site.Id)
            size = len(elements)
            if size != 0 and site.tagNumber < size:
                lyrics = str(elements[site.tagNumber])
                lyrics = self.clean_html(lyrics)
                lyrics = lyrics + "\n\n (source : " + site.name + ")"
                return lyrics
            else:
                print('Error : mybe the site changed its presentation')
                return ""

        start_string = site.start
        start = resp.find(start_string)
        if start == -1:
            print("lyrics start not found")
            return ""
        resp = resp[(start + len(start_string)):]
        end = resp.find(site.end)
        if end == -1:
            print("lyrics end not found ")
            return ""
        resp = resp[:end]

        # replace unwanted parts
        resp = resp.replace("<br />", "")
        resp = resp.replace("&#13;", "&#10;")
        resp = resp.replace("&#", "")
        resp = resp.strip()

        lyrics = Util.decode_chars(resp)
        lyrics = lyrics + "\n\n (source : " + site.name + ")"
        lyrics = self.clean_html(lyrics)
        return resp

    def Search_lyrics(self, artist, title, file_path=None):
        self.read_filters()
        self.title = title
        self.artist = artist
        self.file_path = file_path
        self.index = -1
        self.only_api = True
        if self.file_path is not None:
            lyrics = Util.get_lyrics_from_audio_tag(file_path)
            if lyrics != "":
                return lyrics
        self.index = 0
        print('searching lyrics...')
        self.get_sources_to_search()  # we use Google api first
        lyrics = self.get_lyrics_from_sources()
        return lyrics
    
    def next_lyrics(self):
        if self.index == -1:
            print("first time")
            self.get_sources_to_search()
            self.index = 0
        if self.only_api and self.index > len(self.urls):
            print("search_Google")
            self.search_Google()
        lyrics = self.get_lyrics_from_sources()
        if lyrics == "" and self.only_api:
            print('search Google html')
            self.search_Google()
            lyrics = self.get_lyrics_from_sources()
        return lyrics

    def get_lyrics_from_sources(self):
        print(self.urls)
        print(self.index)
        while self.index != -1 and self.index < len(self.urls):
            print("self.index = " + str(self.index))
            site, url = self.urls[self.index]
            print('searching lyrics from ' + url)
            lyrics = self.get_lyrics_from_source(site, url)
            self.index += 1
            if(lyrics != ""):
                return lyrics
        print('No more results!')
        return ""
    
    def get_url(self):
        url = "https://www.google.com/search?num=20&q=-youtube.com+"
        url = url + self.title.replace(" ", "+")
        url = url + "+"
        url = url + self.artist.replace(" ", "+")
        url = url + "+lyrics"
        url = str(iri2uri(url))
        return url

    def search_Google(self):
        url = self.get_url()
        print(url)
        self.only_api = False
        request = urllib.request.Request(url)
        request.add_header('User-Agent',
                           'Mozilla/4.0 (compatible; MSIE 6.0; \
                           Windows NT 5.1)')
        try:
            search_results = urllib.request.urlopen(request)
            encoding = search_results.headers.get_content_charset()
            try:
                resp = search_results.read().decode(encoding)
            except:
                print("could not connect to Google")
            soup = BeautifulSoup(resp)
            elements = soup.select("h3.r")
            for site in self.sites:
                for i in range(len(elements)):
                    element = elements[i]
                    element = element.select("a")[0]
                    url = element['href']
                    url = self.parse_url(url)
                    if site.name.lower() in (url):
                        self.urls.append((site, url))
        except Exception as e:
            print(e)
            print("Error : opening url " + url)
        print(self.urls)

    def parse_url(self, url):
        start = url.find("http")
        url = url[start:]
        end = url.find("&sa=U&ei=")
        url = url[:end]
        return urllib.parse.unquote(url)

    def clean_html(self, html):
        clean = re.sub('<[ /]*?br[ /]*?>', '\n', html)
        clean = re.sub('</p>', '\n\n', clean)
        clean = re.sub('<.*?>', '', clean)
        clean = re.sub('\n\n\n', '\n\n', clean)
        return clean

    def get_sites(self):
        return self.sites
