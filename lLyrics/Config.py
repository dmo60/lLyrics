# Class to manage gconf settings

import gconf

import lLyrics

GCONF_DIR = '/apps/rhythmbox/plugins/llyrics'

class Config():
    
    def __init__(self):        
        self.gconf_client = gconf.client_get_default()
        self.gconf_client.add_dir(GCONF_DIR, gconf.CLIENT_PRELOAD_RECURSIVE)
        self.init_sources_key()
        self.init_cache_key()
        
    
    def init_sources_key(self):        
        # create and set key if it doesn't exist
        if self.gconf_client.get_without_default(GCONF_DIR + "/lyrics_sources") is None:
            self.gconf_client.set_list(GCONF_DIR + "/lyrics_sources", gconf.VALUE_STRING, lLyrics.LYRIC_SOURCES)
            print "set gconf lyrics_sources default"
            return
        
        # check correct type
        if self.gconf_client.get_without_default(GCONF_DIR + "/lyrics_sources").type != gconf.VALUE_LIST:
            self.gconf_client.set_list(GCONF_DIR + "/lyrics_sources", gconf.VALUE_STRING, lLyrics.LYRIC_SOURCES)
            print "set gconf lyrics_sources default"
            return  
              
        # remove invalid entries
        changed = False
        sources_list = self.gconf_client.get_list(GCONF_DIR + "/lyrics_sources", gconf.VALUE_STRING)
        for entry in sources_list:
            if not entry in lLyrics.LYRIC_SOURCES:
                sources_list.remove(entry)
                changed = True
                print "invalid gconf sources entry: " + entry
                
        # if list is empty, set default
        if len(sources_list) == 0:
            self.gconf_client.set_list(GCONF_DIR + "/lyrics_sources", gconf.VALUE_STRING, lLyrics.LYRIC_SOURCES)
            print "set gconf lyrics_sources default"
            return
        
        # update key, if changed
        if changed:
            self.gconf_client.set_list(GCONF_DIR + "/lyrics_sources", gconf.VALUE_STRING, sources_list)   
    
    
    def init_cache_key(self):
        # create and set key if it doesn't exist
        if self.gconf_client.get_without_default(GCONF_DIR + "/cache_lyrics") is None:
            self.gconf_client.set_bool(GCONF_DIR + "/cache_lyrics", True)
            print "set gconf cache_lyrics default"
            return
        
        # check correct type
        if self.gconf_client.get_without_default(GCONF_DIR + "/cache_lyrics").type != gconf.VALUE_BOOL:
            self.gconf_client.set_bool(GCONF_DIR + "/cache_lyrics", True)
            print "set gconf cache_lyrics default"
            return
        
    
    def get_lyrics_sources(self):
        return self.gconf_client.get_list(GCONF_DIR + "/lyrics_sources", gconf.VALUE_STRING)
    
    
    def get_cache_lyrics(self):
        return self.gconf_client.get_bool(GCONF_DIR + "/cache_lyrics")
        