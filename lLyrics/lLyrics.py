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


from gi.repository import GObject, Peas, Gdk, RB, Gtk
from threading import Thread
import re, os, threading, webbrowser, pango, urllib2

import gettext
gettext.install('rhythmbox', RB.locale_dir())

import ChartlyricsParser, LyricwikiParser, MetrolyricsParser, LetrasTerraParser, LyrdbParser, Config

llyrics_ui = """
<ui>
    <menubar name="MenuBar">
        <menu name="ViewMenu" action="View">
            <menuitem name="lLyrics" action="ToggleLyricSideBar" />
        </menu>
        
        <menu name="lLyrics" action="lLyricsMenuAction">
            <menu name="ScanSource" action="ScanSourceAction">
                <menuitem name="ScanLyricwiki" action="Lyricwiki.org"/>
                <menuitem name="ScanTerra" action="Letras.terra.com.br"/>
                <menuitem name="ScanMetrolyrics" action="Metrolyrics.com"/>
                <menuitem name="ScanChartlyrics" action="Chartlyrics.com"/>
                <menuitem name="ScanLyrdb" action="Lyrdb.com"/>
                <separator/>
                <menuitem name="FromCacheFile" action="From cache file"/>
                <menuitem action="SelectNothing"/>
            </menu>
            <menuitem name="ScanAll" action="ScanAllAction"/>
            <menuitem name="ScanNext" action="ScanNextAction"/>
            <separator/>
            <menuitem name="SearchOnline" action="SearchOnlineAction"/>
            <separator/>
            <menuitem name="Instrumental" action="InstrumentalAction"/>
            <separator/>
            <menuitem name="Clear" action="ClearAction"/>
            <menuitem name="SaveToCache" action="SaveToCacheAction"/>
            <separator/>
            <menuitem name="Edit" action="EditAction"/>
            <separator/>
            <menuitem name="SearchMeanings" action="SearchMeaningsAction"/>
        </menu>
        
    </menubar>
    <toolbar name="ToolBar">
            <toolitem name="lLyrics" action="ToggleLyricSideBar"/>
    </toolbar>
</ui>
"""

LYRIC_TITLE_STRIP=["\(live[^\)]*\)", "\(acoustic[^\)]*\)", "\([^\)]*mix\)", "\([^\)]*version\)", "\([^\)]*edit\)", 
                   "\(feat[^\)]*\)", "\([^\)]*bonus[^\)]*track[^\)]*\)"]
LYRIC_TITLE_REPLACE=[("/", "-"), (" & ", " and ")]
LYRIC_ARTIST_REPLACE=[("/", "-"), (" & ", " and ")]

LYRIC_SOURCES=["Lyricwiki.org", "Letras.terra.com.br", "Metrolyrics.com", "Chartlyrics.com", "Lyrdb.com"]


class lLyrics(GObject.GObject, Peas.Activatable):
    __gtype_name = 'lLyrics'
    object = GObject.property(type=GObject.GObject)
    
    
    
    def __init__(self):
        GObject.GObject.__init__(self)
        GObject.threads_init()
        Gdk.threads_init()
        
        

    def do_activate(self):
        # Get references for the Shell, the Shell-player and the UIManager
        self.shell = self.object
        self.player = self.shell.props.shell_player
        self.uim = self.shell.props.ui_manager
        
        # Create dictionary which assigns sources to their corresponding modules
        self.dict = dict({"Lyricwiki.org": LyricwikiParser, "Letras.terra.com.br": LetrasTerraParser,
                         "Metrolyrics.com": MetrolyricsParser, "Chartlyrics.com": ChartlyricsParser,
                         "Lyrdb.com": LyrdbParser})
        
        # Get the user preferences
        config = Config.Config()
        self.sources = config.get_lyrics_sources()
        self.cache = config.get_cache_lyrics()
        
        # Initialize the UI
        self.init_sidebar()
        self.init_menu()
        
        # Create flag, used to pop out sidebar on initial start of playback
        self.first = True
        
        # Search lyrics if already playing (this will be the case if user reactivates plugin during playback)
        if self.player.props.playing:
                self.search_lyrics(self.player, self.player.get_playing_entry())
        # Search lyrics everytime the song changes 
        self.psc_id = self.player.connect('playing-song-changed', self.search_lyrics)
        
        # Hide the lLyrics UI elements when in Small Display mode
        small_display_toggle = self.uim.get_widget("/MenuBar/ViewMenu/ViewSmallDisplayMenu")
        self.tb_conn_id = small_display_toggle.connect('toggled', self.hide_if_active)
        
        # Event flag indicates whether the user is currently editing lyrics
        self.edit_event = threading.Event()
        self.edit_event.set()
        
        self.current_source = None
                
        print "activated plugin lLyrics"
        
        

    def do_deactivate(self):    
        if self.visible:
            self.shell.remove_widget (self.vbox, RB.ShellUILocation.RIGHT_SIDEBAR)
        
        self.player.disconnect(self.psc_id)
        self.uim.get_widget("/MenuBar/ViewMenu/ViewSmallDisplayMenu").disconnect(self.tb_conn_id)
        
        self.uim.remove_ui (self.ui_id)
        self.uim.remove_action_group (self.action_group)
        self.uim.remove_action_group(self.toggle_action_group)
        
        self.uim = None
        self.vbox = None
        self.textbuffer = None
        self.textview = None
        self.psc_id = None
        self.visible = None
        self.player = None
        self.action_group = None
        self.toggle_action_group = None
        self.cache = None
        self.dict = None
        self.sources = None
        self.ui_id = None
        self.tag = None
        self.first = None
        self.current_source = None
        self.artist = None
        self.title = None
        self.clean_artist = None
        self.clean_title = None
        self.path = None
        self.lyrics_before_edit = None
        self.edit_event = None
        self.path_before_edit = None
        
        self.shell = None

        print "deactivated plugin lLyrics"
        
        
        
    def init_menu(self):
        # Action to toggle the visibility of the sidebar,
        # used by the toolbar button and the ViewMenu entry.
        self.toggle_action_group = Gtk.ActionGroup(name='lLyricsPluginToggleActions')
        toggle_action = ('ToggleLyricSideBar','gtk-info', _("Lyrics"),
                        None, _("Display lyrics for the playing song"),
                        self.toggle_visibility, False)
        self.toggle_action_group.add_toggle_actions([toggle_action])
        
        # Actions used by the lyrics menu
        self.action_group = Gtk.ActionGroup(name='lLyricsPluginActions')
        
        menu_action = Gtk.Action("lLyricsMenuAction", _("Lyrics"), None, None)
        self.action_group.add_action(menu_action)
        
        source_action = Gtk.Action("ScanSourceAction", _("Source"), None, None)
        self.action_group.add_action(source_action)
        
        scan_lyricwiki_action = ("Lyricwiki.org", None, "Lyricwiki.org", None, None)
        scan_terra_action = ("Letras.terra.com.br", None, "Letras.terra.com.br", None, None)
        scan_metrolyrics_action = ("Metrolyrics.com", None, "Metrolyrics.com", None, None)
        scan_chartlyrics_action = ("Chartlyrics.com", None, "Chartlyrics.com", None, None)
        scan_lyrdb_action = ("Lyrdb.com", None, "Lyrdb.com", None, None)
        scan_cache_action = ("From cache file", None, "From cache file", None, None)
        select_nothing_action = ("SelectNothing", None, "SelectNothing", None, None)
        
        self.action_group.add_radio_actions([scan_lyricwiki_action, scan_terra_action, scan_metrolyrics_action,
                                             scan_chartlyrics_action, scan_lyrdb_action, scan_cache_action, select_nothing_action],
                                             -1, self.scan_source_action_callback, None)
        
        # This is a quite ugly hack. I couldn't find out how to unselect all radio actions,
        # so I use an invisible action for that
        self.action_group.get_action("SelectNothing").set_visible(False)
        self.action_group.get_action("SelectNothing").set_active(True)
        
        scan_next_action = ("ScanNextAction", None, _("Scan next source"),
                            None, _("Scan next lyrics source"), self.scan_next_action_callback)
        scan_all_action = ("ScanAllAction", None, _("Scan all sources"),
                           None, _("Rescan all lyrics sources"), self.scan_all_action_callback)
        search_online_action = ("SearchOnlineAction", None, _("Search online"),
                                None, _("Search lyrics for the current song online (opens your web browser)"), self.search_online_action_callback)
        search_meanings_action = ("SearchMeaningsAction", None, _("Look up song meanings"),
                                  None, _("Search song meanings for the current title online on songmeanings.net (opens your web browser)"), 
                                  self.search_meanings_action_callback)
        instrumental_action = ("InstrumentalAction", None, _("Mark as instrumental"),
                               None, _("Mark this song as instrumental"), self.instrumental_action_callback)
        save_to_cache_action = ("SaveToCacheAction", None, _("Save lyrics"),
                                None, _("Save current lyrics to the cache file"), self.save_to_cache_action_callback)
        clear_action = ("ClearAction", None, _("Clear lyrics"), None,
                        _("Delete current lyrics"), self.clear_action_callback)
        edit_action = ("EditAction", None, _("Edit lyrics"), None,
                       _("Manually edit current lyrics"), self.edit_action_callback)
        
        self.action_group.add_actions([scan_next_action, scan_all_action, search_online_action, search_meanings_action,
                                       instrumental_action, save_to_cache_action, clear_action, edit_action])
        
        # Make action group insensitive as long as there are no lyrics displayed
        self.action_group.set_sensitive(False)
        
        # Insert the UI
        self.uim.insert_action_group (self.toggle_action_group, 0)
        self.uim.insert_action_group (self.action_group, 0)
        self.ui_id = self.uim.add_ui_from_string(llyrics_ui)
        self.uim.ensure_update()
        
        
       
    def init_sidebar(self):
        self.vbox = Gtk.VBox()
                
        label = Gtk.Label(_("Lyrics"))
        label.set_use_markup(True)
        label.set_padding(3, 9)
        label.set_alignment(0, 0)
        
        # create a TextView for displaying lyrics
        self.textview = Gtk.TextView()
        self.textview.set_editable(False)
        self.textview.set_cursor_visible(False)
        self.textview.set_left_margin(10)
        self.textview.set_right_margin(10)
        self.textview.set_pixels_above_lines(5)
        self.textview.set_pixels_below_lines(5)
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD)
                
        # create a ScrollView
        sw = Gtk.ScrolledWindow()
        sw.add(self.textview)
        sw.set_shadow_type(Gtk.ShadowType.IN)
        
        # initialize a TextBuffer to store lyrics in
        self.textbuffer = Gtk.TextBuffer()
        self.textview.set_buffer(self.textbuffer)
        
        # tag to style headers bold and underlined
        self.tag = self.textbuffer.create_tag(None, underline=pango.UNDERLINE_SINGLE, weight=600, 
                                              pixels_above_lines=10, pixels_below_lines=20)
        
        # create save and cancel buttons for edited lyrics
        save_button = Gtk.Button.new_with_label(_("Save"))
        save_button.connect("clicked", self.save_button_callback)
        cancel_button = Gtk.Button.new_with_label(_("Cancel"))
        cancel_button.connect("clicked", self.cancel_button_callback)
        self.hbox = Gtk.HBox()
        self.hbox.pack_start(save_button, True, True, 3)
        self.hbox.pack_start(cancel_button, True, True, 3)
        
        # pack everything into side pane
        self.vbox.pack_start(label, False, False, 0)
        self.vbox.pack_start(sw, True, True, 0)
        self.vbox.pack_end(self.hbox, False, False, 3)

        self.vbox.show_all()
        self.hbox.hide()
        self.vbox.set_size_request(200, -1)
        self.visible = False
        
        
    
    def toggle_visibility (self, action):
        if not self.visible:
            self.shell.add_widget (self.vbox, RB.ShellUILocation.RIGHT_SIDEBAR, True, True)
            self.visible = True
            self.toggle_action_group.get_action("ToggleLyricSideBar").set_active(True)
            self.uim.get_widget("/MenuBar/lLyrics").show()
        else:
            self.shell.remove_widget (self.vbox, RB.ShellUILocation.RIGHT_SIDEBAR)
            self.visible = False
            self.toggle_action_group.get_action("ToggleLyricSideBar").set_active(False)
            self.uim.get_widget("/MenuBar/lLyrics").hide()
            
            
        
    def search_lyrics(self, player, entry):            
        if entry is None:
            return
        
        # pop out sidebar at first playback
        if self.first and not self.visible:
            self.toggle_action_group.get_action("ToggleLyricSideBar").set_active(True)
            self.first = False
            
        # get the song data
        self.artist = entry.get_string(RB.RhythmDBPropType.ARTIST)
        self.title = entry.get_string(RB.RhythmDBPropType.TITLE)
        print "search lyrics for " + self.artist + " - " + self.title
   
        (self.clean_artist, self.clean_title) = self.clean_song_data(self.artist, self.title)
        self.path = self.build_cache_path(self.clean_artist, self.clean_title)
        
        self.scan_all_sources(self.clean_artist, self.clean_title, True)
        
        

    def clean_song_data(self, artist, title):
        # convert to lowercase
        artist = artist.lower()
        title = title.lower()
    
        # replace ampersands and the like
        for exp in LYRIC_ARTIST_REPLACE:
            artist = re.sub(exp[0], exp[1], artist)
        for exp in LYRIC_TITLE_REPLACE:
            title = re.sub(exp[0], exp[1], title)
    
        # strip things like "(live at Somewhere)", "(acoustic)", etc
        for exp in LYRIC_TITLE_STRIP:
            title = re.sub (exp, '', title)
    
        # compress spaces
        title = title.strip()
        artist = artist.strip()
        
        return (artist, title)
    
    
    
    def build_cache_path(self, artist, title):
        folder = os.path.join(RB.user_cache_dir(), "lyrics")
    
        lyrics_folder = os.path.expanduser (folder)
        if not os.path.exists (lyrics_folder):
            os.mkdir (lyrics_folder)
    
        artist_folder = os.path.join(lyrics_folder, artist[:128])
        if not os.path.exists (artist_folder):
            os.mkdir (artist_folder)
    
        return os.path.join(artist_folder, title[:128] + '.lyric')
    
    
    
    def hide_if_active (self, toggle_widget):        
        menubar_item = self.uim.get_widget("/MenuBar/lLyrics")
        toolbar_item = self.uim.get_widget("/ToolBar/lLyrics")
        
        if (toggle_widget.get_active()):
            toolbar_item.hide()
            menubar_item.hide()
            
        else:
            toolbar_item.show()
            menubar_item.show()
            
            
            
    def scan_source_action_callback(self, action, activated_action):        
        source = activated_action.get_label()
        if source == "SelectNothing" or source == self.current_source:
            return
        
        self.scan_source(source, self.clean_artist, self.clean_title)
        
        
        
    def scan_next_action_callback(self, action):
        if self.current_source is None or self.current_source == "From cache file":
            index = 0
        else:
            index = self.sources.index(self.current_source) + 1
            index = index % (len(self.sources)+1)
        if index >= len(self.sources):
            source = "From cache file"
        else:
            source = self.sources[index]
        
        self.scan_source(source, self.clean_artist, self.clean_title)
        
        
    
    def scan_all_action_callback(self, action):
        self.scan_all_sources(self.clean_artist, self.clean_title, False)
        
        
    def search_online_action_callback(self, action):
        webbrowser.open("http://www.google.com/search?q=" + self.clean_artist + "+" + self.clean_title + "+lyrics")
        
        
    
    def search_meanings_action_callback(self, action):
        newthread = Thread(target=self._search_meanings_thread, args=(self.clean_artist, self.clean_title))
        newthread.start()
    
    
            
    def instrumental_action_callback(self, action):
        lyrics = "-- Instrumental --"
        self.write_lyrics_to_cache(self.path, lyrics)
        self.show_lyrics(self.artist, self.title, lyrics)
        
        self.action_group.get_action("SelectNothing").set_active(True)
        self.current_source = None
        
        
        
    def save_to_cache_action_callback(self, action):
        start, end = self.textbuffer.get_bounds()
        start.forward_lines(1)
        lyrics = self.textbuffer.get_text(start, end, False)
        
        self.write_lyrics_to_cache(self.path, lyrics)
        
        
        
    def clear_action_callback(self, action):
        self.textbuffer.set_text("")
        try:
            os.remove(self.path)
        except:
            print "No cache file found to clear"
        self.action_group.get_action("SaveToCacheAction").set_sensitive(False)
        print "cleared lyrics"
        
        
        
    def edit_action_callback(self, action):
        # Unset event flag to indicate editing and so block all other threads which 
        # want to display new lyrics until editing is finished.
        self.edit_event.clear()
        
        # Conserve lyrics in order to restore original lyrics when editing is canceled 
        start, end = self.textbuffer.get_bounds()
        self.lyrics_before_edit = self.textbuffer.get_text(start, end, False)
        # Conserve cache path in order to be able to correctly save edited lyrics although
        # the playing song might have changed during editing.
        self.path_before_edit = self.path
        
        self.action_group.set_sensitive(False)
        
        # Enable editing and set cursor
        self.textview.set_cursor_visible(True)
        self.textview.set_editable(True)
        cursor = self.textbuffer.get_iter_at_line(1)
        self.textbuffer.place_cursor(cursor)
        self.textview.grab_focus()
        
        self.hbox.show()
        
        
    
    def save_button_callback(self, button):
        self.textview.set_cursor_visible(False)
        self.textview.set_editable(False)
        self.hbox.hide()
        
        # get lyrics without artist-title header
        start, end = self.textbuffer.get_bounds()
        start.forward_lines(1)
        lyrics = self.textbuffer.get_text(start, end, False)
        
        # save edited lyrics to cache file
        self.write_lyrics_to_cache(self.path_before_edit, lyrics)
        
        # If playing song changed, set "searching lyrics..." (might be overwritten
        # immediately, if thread for the new song already found lyrics)
        if self.path != self.path_before_edit:
            self.textbuffer.set_text("searching lyrics...")
            
        self.action_group.set_sensitive(True)
        
        # Set event flag to indicate end of editing and wake all threads 
        # waiting to display new lyrics.
        self.edit_event.set()
        
        
        
    def cancel_button_callback(self, button):
        self.textview.set_cursor_visible(False)
        self.textview.set_editable(False)
        self.hbox.hide()
        
        # Restore original lyrics if playing song didn't change,
        # otherwise set "searching lyrics..." (might be overwritten
        # immediately, if thread for the new song already found lyrics)
        if self.path == self.path_before_edit:
            self.textbuffer.set_text(self.lyrics_before_edit)
            start = self.textbuffer.get_start_iter()
            end = start.copy()
            end.forward_to_line_end()
            self.textbuffer.apply_tag(self.tag, start, end)
        else:
            self.textbuffer.set_text("searching lyrics...")
        
        self.action_group.set_sensitive(True)
        
        # Set event flag to indicate end of editing and wake all threads 
        # waiting to display new lyrics.
        self.edit_event.set()
        
        
    
    def scan_source(self, source, artist, title):
        Gdk.threads_enter()
        self.textbuffer.set_text("searching lyrics...")
        Gdk.threads_leave()
          
        newthread = Thread(target=self._scan_source_thread, args=(source, artist, title))
        newthread.start()
        
        
            
    def _scan_source_thread(self, source, artist, title):
        self.action_group.set_sensitive(False)
             
        if source == "From cache file":
            lyrics = self.get_lyrics_from_cache(self.path)
        else:   
            lyrics = self.get_lyrics_from_source(source, artist, title)
            
        # check if playing song changed
        if artist != self.clean_artist or title != self.clean_title:
            print "song changed"
            return
                
        self.show_lyrics(self.artist, self.title, lyrics)          
        
        self.action_group.set_sensitive(True)
        
        
        
    def scan_all_sources(self, artist, title, cache):
        if self.edit_event.is_set():
            Gdk.threads_enter()
            self.textbuffer.set_text("searching lyrics...")
            Gdk.threads_leave()
            
        newthread = Thread(target=self._scan_all_sources_thread, args=(artist, title, cache))
        newthread.start()
        
        
    
    def _scan_all_sources_thread(self, artist, title, cache):
        self.action_group.set_sensitive(False)
        
        if cache:
            lyrics = self.get_lyrics_from_cache(self.path)
        else:
            lyrics = ""
        
        if lyrics == "":
            i = 0
            while lyrics == "" and i in range(len(self.sources)):
                lyrics = self.get_lyrics_from_source(self.sources[i], artist, title)
                # check if playing song changed
                if artist != self.clean_artist or title != self.clean_title:
                    print "song changed"
                    return
                i += 1
        
        # We can't display new lyrics while user is editing! 
        self.edit_event.wait()
        
        # check if playing song changed
        if artist != self.clean_artist or title != self.clean_title:
            print "song changed"
            return
            
        if lyrics == "":
            self.action_group.get_action("SelectNothing").set_active(True)
            self.current_source = None  
        
        self.show_lyrics(self.artist, self.title, lyrics)
        
        self.action_group.set_sensitive(True)
        
        
        
    def get_lyrics_from_cache(self, path):        
        # try to load lyrics from cache
        if os.path.exists (path):
            try:
                cachefile = open(path, "r")
                lyrics = cachefile.read()
                cachefile.close()
                print "got lyrics from cache"
                self.current_source = "From cache file"
                self.action_group.get_action("From cache file").set_active(True)
                return lyrics
            except:
                print "error reading cache file"
        return ""
    
    
    
    def write_lyrics_to_cache(self, path, lyrics):
        try:
            cachefile = open(path, "w+")
            cachefile.write(lyrics)
            cachefile.close()
            print "wrote lyrics to cache file"
        except:
            print "error writing lyrics to cache file"
            
            
        
    def get_lyrics_from_source(self, source, artist, title):
        # Playing song might change during search, so we want to 
        # conserve the correct cache path.
        path = self.path
        
        print "source: " + source        
        self.current_source = source
        self.action_group.get_action(source).set_active(True)
        
        parser = self.dict[source].Parser(artist, title)
        lyrics = parser.parse()
        
        if lyrics != "":
            print "got lyrics from source"
            lyrics = lyrics + "\n\n(lyrics from " + source + ")"
            lyrics = lyrics.decode("utf-8", "replace")
            if self.cache:
                self.write_lyrics_to_cache(path, lyrics)
            
        return lyrics    
    
    
    
    def show_lyrics(self, artist, title, lyrics):
        if lyrics == "":
            print "no lyrics found"
            lyrics = "No lyrics found"
            self.action_group.get_action("SaveToCacheAction").set_sensitive(False)
        else:        
            self.action_group.get_action("SaveToCacheAction").set_sensitive(True)
        
        Gdk.threads_enter()
        
        self.textbuffer.set_text(artist + " - " + title + "\n" + lyrics)
        # make 'artist - title' header bold and underlined 
        start = self.textbuffer.get_start_iter()
        end = start.copy()
        end.forward_to_line_end()
        self.textbuffer.apply_tag(self.tag, start, end)
        
        Gdk.threads_leave()
        
    
    
    def _search_meanings_thread(self, artist, title):
        link = self.get_songmeanings_link(artist, title)
        if link == "":
            dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.WARNING, 
                                       Gtk.ButtonsType.CLOSE, "No song meanings found")
            dialog.format_secondary_markup("You can try to search manually on <a href=\"http://www.songmeanings.net\">www.songmeanings.net</a>")
            
            Gdk.threads_enter()
            dialog.run()
            Gdk.threads_leave()
            
            Gdk.threads_enter()
            dialog.destroy()
            Gdk.threads_leave()
        else:
            print "open songmeanings link: " + link
            webbrowser.open(link)
            
    
    
    def get_songmeanings_link(self, artist, title):
        # format artist, e.g. "the strokes" -> "strokes, the"
        if re.match("the .*", artist) is not None:
            artist = artist[4:] + ", the"
        # Get the artist's song list from songmeanings.net
        url = "http://www.songmeanings.net/artist/view/songs/" + artist.replace(" ", "%20")
        print "songmeanings url: " + url
        try:
            resp = urllib2.urlopen(url, None, 3).read()
        except:
            print "could not connect to songmeanings.net"
            return ""
        
        start = resp.find("<!-- SONGS BEGINS -->")
        end = resp.find("<!-- SONGS ENDS -->")
        if start == -1 or end == -1:
            print "songmeanings: song list not found"
            return ""
        resp = resp[start:end]
        
        # find the correct title and return the link if found
        songs = resp.split("</tr>")
        for song in songs:
            if re.search(title, song, re.I) is not None:
                match = re.search("\<a href\=\"(\/songs\/view\/[0-9]*\/\#comment)\"\>[0-9]*\<\/a\>\<\/td\>", song)
                if match is None:
                    print "songmeanings: title not found"
                    return ""
                link = match.group(1)
                return "http://www.songmeanings.net" + link
        
        print "no song meanings found"
        return ""
        
