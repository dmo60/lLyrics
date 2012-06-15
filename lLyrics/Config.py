# Class to manage gconf settings

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

from gi.repository import Gio

import lLyrics

DCONF_DIR = 'org.gnome.rhythmbox.plugins.llyrics'

class Config():
    
    def __init__(self):
        self.settings = Gio.Settings(DCONF_DIR)
        self.init_sources_key()
             
    
    def init_sources_key(self):        
        # remove invalid entries
        changed = False
        sources_list = self.settings["lyrics-sources"]
        for entry in sources_list:
            if not entry in lLyrics.LYRIC_SOURCES:
                sources_list.remove(entry)
                changed = True
                print "remove invalid dconf sources entry: " + entry
                
        # if list is empty, set default
        if len(sources_list) == 0:
            self.settings.reset("lyrics-sources")
            print "set dconf lyrics_sources default"
            return
        
        # update key, if changed
        if changed:
            self.settings.set_strv(sources_list)  
        
    
    def get_lyrics_sources(self):
        return self.settings["lyrics-sources"]
    
    def get_cache_lyrics(self):
        return self.settings["cache-lyrics"]
        