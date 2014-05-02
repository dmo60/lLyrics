# Parser for leoslyrics.com

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
import json
import time
import os
import re

from xml.dom.minidom import parse
from bs4 import BeautifulSoup

import Util


class Site:
    name = None
    start = None
    end = None
    Id = None
    tagNumber = -1

    def __init__(self):
        pass


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
        self.ignore_sites = []
        self.read_filters()

    #Get sources where to parse the lyrics
    def get_sources_to_search(self):
        print('searching Google...')
        num_queries = 1 * 4

        query = urllib.parse.urlencode({'q':
                                        self.title + ' '
                                        + self.artist + ' lyrics'})
        url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&%s'\
               % query
        urls = []
        site_list = [site for site in self.sites
                             if site not in self.ignore_sites]
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
                for site in site_list:
                    for items in results:
                        if site.name.lower() in (items['url']):
                            urls.append((site, items['url']))
            except:
                pass
            time.sleep(1)  # Otherwise Google will return an error
        return urls

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

    def Search_lyrics(self, artist, title, ignore_sites, file_path=None):
        self.title = title
        self.artist = artist
        self.file_path = file_path
        self.ignore_sites = ignore_sites
        print("ignored sites are : ")
        if self.file_path is not None:
            lyrics = Util.get_lyrics_from_audio_tag(file_path)
            if lyrics != "":
                return None, lyrics
        print('searching lyrics...')
        urls = self.get_sources_to_search()  # we use Google api first
        site, lyrics = self.get_lyrics_from_sources(urls)
        if site == "":
            print('searching google (html)')
            urls = self.search_Google()
            return self.get_lyrics_from_sources(urls)
        return site, lyrics

    def get_lyrics_from_sources(self, urls):
        print(len(urls))
        for i in range(len(urls)):
            site, url = urls[i]
            print('searching lyrics from ' + url)
            lyrics = self.get_lyrics_from_source(site, url)
            if(lyrics != ""):
                return site, lyrics
        return "", ""

    def search_Google(self):
        url = "https://www.google.com/search?q="
        url = url + self.title.replace(" ", "+")
        url = url + "+"
        url = url + self.artist.replace(" ", "+")
        url = url + "+lyrics"
        urls = []
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
                return urls
            soup = BeautifulSoup(resp)
            elements = soup.select("h3.r")
            site_list = [site for site in self.sites
                             if site not in self.ignore_sites]
            for site in site_list:
                for i in range(len(elements)):
                    element = elements[i]
                    element = element.select("a")[0]
                    url = element['href']
                    url = self.parse_url(url)
                    if site.name.lower() in (url):
                        urls.append((site, url))
        except Exception as e:
            print(e)
            print("Error : opening url " + url)
        return urls

    def parse_url(self, url):
        print(url)
        start = url.find("http")
        url = url[start:]
        end = url.find("&sa=U&ei=")
        url = url[:end]
        return url

    def clean_html(self, html):
        clean = re.sub('<[ /]*?br[ /]*?>', '\n', html)
        clean = re.sub('</p>', '\n\n', clean)
        clean = re.sub('<.*?>', '', clean)
        clean = re.sub('\n\n\n', '\n\n', clean)
        return clean

    def get_sites(self):
        return self.sites
