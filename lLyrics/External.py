# Module to retrieve lyrics from the builtin lyrics plugin

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

import threading
import string

class Parser(object):
    
    def __init__(self, artist, title):
        self.artist = artist
        self.title = title
        self.lyrics = ""
        
        self.ext_event = threading.Event()
        self.ext_event.set()

    def parse(self):
        self.ext_event.clear()
        
        try:
            import LyricsParse
        except:
            print("Error importing LyricsParse module")
            return ""
        
        # call the built-in lyrics plugin parser
        parser = LyricsParse.Parser(self.artist, self.title)
        parser.get_lyrics(self.receive_lyrics_from_ext_source)
        
        # wait for received results
        self.ext_event.wait()
        
        lyrics = self.lyrics
        
        if lyrics == "":
            return lyrics
        
        lyrics = self.clean_lyrics(lyrics)
        lyrics = string.capwords(lyrics, "\n").strip()
        
        return lyrics
        
    def receive_lyrics_from_ext_source(self, lyrics):
        if lyrics is None:
            lyrics = ""
        
        self.lyrics = lyrics
        self.ext_event.set()
    
    def clean_lyrics(self, lyrics):
        # remove the artist/title header
        lower = lyrics.lower()
        title_end = lower.find(self.title)
        strip_count = len(self.title)
        
        if title_end == 0:
            title_end = lower.find(self.artist)
            strip_count = len(self.artist)
        if title_end == -1:
            print("could not remove artist/title, not found")
        else:
            lyrics = lyrics[(title_end + strip_count):]
        
        lyrics = lyrics.strip()
        return lyrics

