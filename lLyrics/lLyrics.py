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
import re, os, pango

import gettext
gettext.install('rhythmbox', RB.locale_dir())

import ChartlyricsParser, LyricwikiParser, MetrolyricsParser, TerraParser, LyrdbParser, Config

llyrics_ui = """
<ui>
    <menubar name="MenuBar">
        <menu name="ViewMenu" action="View">
            <menuitem name="lLyrics" action="ToggleLyricSideBar" />
        </menu>
    </menubar>
    <toolbar name="ToolBar">
            <toolitem name="lLyrics" action="ToggleLyricSideBar"/>
    </toolbar>
</ui>
"""


LYRIC_TITLE_STRIP=["\(live[^\)]*\)", "\(acoustic[^\)]*\)", "\([^\)]*mix\)", "\([^\)]*version\)", "\([^\)]*edit\)", "\(feat[^\)]*\)", "\([^\)]*bonus[^\)]*track[^\)]*\)"]
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
        self.shell = self.object
        self.player = self.shell.props.shell_player
                
        self.dict = dict({"Lyricwiki.org": LyricwikiParser, "Letras.terra.com.br": TerraParser,\
                         "Metrolyrics.com": MetrolyricsParser, "Chartlyrics.com": ChartlyricsParser,\
                         "Lyrdb.com": LyrdbParser})
        self.config = Config.Config()
        self.sources = self.config.get_lyrics_sources()
        self.cache = self.config.get_cache_lyrics()
        
        self.init_sidebar()
        
        # search lyrics if already playing (this will be the case if user reactivates plugin during playback)
        if self.player.props.playing:
                self.search_lyrics(self.player, self.player.get_playing_entry())
        # search lyrics if song changes 
        self.psc_id = self.player.connect ('playing-song-changed', self.search_lyrics)
        
        # Add button to toggle visibility of pane
        self.action = ('ToggleLyricSideBar','gtk-info', _("Lyrics"),
                        None, _("Display lyrics for the playing song"),
                        self.toggle_visibility, True)
        self.action_group = Gtk.ActionGroup(name='lLyricsPluginActions')
        self.action_group.add_toggle_actions([self.action])
        uim = self.shell.props.ui_manager
        uim.insert_action_group (self.action_group, 0)
        self.ui_id = uim.add_ui_from_string(llyrics_ui)
        uim.ensure_update()
        
        # hide the button in Small Display mode
        small_display_toggle = uim.get_widget ("/MenuBar/ViewMenu/ViewSmallDisplayMenu")
        tb_widget = uim.get_widget ("/ToolBar/lLyrics")
        self.tb_conn_id = small_display_toggle.connect ('toggled', self.hide_if_active, tb_widget)
                
        print "activated plugin lLyrics"

    def do_deactivate(self):    
        if self.visible:
            self.shell.remove_widget (self.vbox, RB.ShellUILocation.RIGHT_SIDEBAR)
        self.vbox = None
        self.textview = None
        self.textbuffer = None
        self.player.disconnect(self.psc_id)
        del self.psc_id
        self.player_cb_ids = None
        self.visible = None
        self.player = None
        uim = self.shell.props.ui_manager
        uim.remove_ui (self.ui_id)
        uim.remove_action_group (self.action_group)
        self.action = None
        self.action_group = None
        self.cache = None
        self.config = None
        self.dict = None
        self.sources = None
        self.ui_id = None
        self.tag = None
        
        self.shell = None

        print "deactivated plugin lLyrics"
       
    def init_sidebar(self):
        self.vbox = Gtk.VBox()
                
        frame = Gtk.Frame()
        label = Gtk.Label(_("Lyrics"))
        frame.set_shadow_type(Gtk.ShadowType.IN)
        frame.set_label_align(0.0,0.0)
        frame.set_label_widget(label)
        label.set_use_markup(True)
        label.set_padding(0,4)
        
        expander = Gtk.Expander()
        expander.set_label(_("Lyrics"))
        expander.set_margin_bottom(5)
        expander.set_spacing(5)
        
        self.combobox = Gtk.ComboBoxText.new()
        self.combobox.set_margin_right(5)
        for s in self.sources:
            self.combobox.append(s, s)
        self.combobox.append("cache", "From cache file")
        self.combobox.connect('changed', self.source_changed)
        self.combobox.set_tooltip_text("Select source to scan for lyrics")
        
        self.button = Gtk.Button()
        self.button.set_label(">")
        self.button.connect('clicked', self.next_source)
        self.button.set_tooltip_text("Scan next source in list")
        
        hbox = Gtk.HBox()
        hbox.pack_start(self.combobox, True, True, 0)
        hbox.pack_end(self.button, False, False, 5)
        
        expander.add(hbox)
        
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
        
        # initialize a TextBuffer to store lyrics in
        self.textbuffer = Gtk.TextBuffer()
        self.textview.set_buffer(self.textbuffer)
        
        # tag to style headers bold and underlined
        self.tag = self.textbuffer.create_tag(None, underline=pango.UNDERLINE_SINGLE, weight=600, pixels_above_lines=10, pixels_below_lines=20)

        # pack everything into side pane
#        self.vbox.pack_start  (frame, False, True, 0)
#        self.vbox.pack_start(hbox, False, False, 0)
        self.vbox.pack_start(expander, False, False, 0)
        self.vbox.pack_start (sw, True, True, 0)

        self.vbox.show_all()
        self.vbox.set_size_request(200, -1)
        self.shell.add_widget (self.vbox, RB.ShellUILocation.RIGHT_SIDEBAR, True, True)
        self.visible = True 
    
    def toggle_visibility (self, action):
        if not self.visible:
            self.shell.add_widget (self.vbox, RB.ShellUILocation.RIGHT_SIDEBAR, True, True)
            self.visible = True
        else:
            self.shell.remove_widget (self.vbox, RB.ShellUILocation.RIGHT_SIDEBAR)
            self.visible = False
        
    def search_lyrics(self, player, entry):
        if entry is None:
            return
        self.artist = entry.get_string(RB.RhythmDBPropType.ARTIST)
        self.title = entry.get_string(RB.RhythmDBPropType.TITLE)
        print "search lyrics for " + self.artist + " - " + self.title
   
        (self.clean_artist, self.clean_title) = self.clean_song_data(self.artist, self.title)
        self.path = self.build_cache_path(self.clean_artist, self.clean_title)
        
        self.scan_all_sources(self.clean_artist, self.clean_title)

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
    
    def hide_if_active (self, toggle_widget, ui_element):
        "Hides ui_element if toggle_widget is active."
        
        if (toggle_widget.get_active()):
            ui_element.hide()
            
        else:
            ui_element.show()
            
    def source_changed(self, combobox):
        if combobox.get_sensitive():
            source = combobox.get_active_text()
            self.scan_source(source, self.clean_artist, self.clean_title)
        
    def next_source(self, button):
        index = self.combobox.get_active() + 1
        index = index % (len(self.sources)+1)
        if index >= len(self.sources):
            source = "From cache file"
        else:
            source = self.sources[index]
        
        self.scan_source(source, self.clean_artist, self.clean_title)
    
    def scan_source(self, source, artist, title):
        Gdk.threads_enter()
        self.textbuffer.set_text("searching lyrics...")
        Gdk.threads_leave()
          
        newthread = Thread(target=self._scan_source_thread, args=(source, artist, title))
        newthread.start()
    
    def _scan_source_thread(self, source, artist, title):
        Gdk.threads_enter()
        self.button.set_sensitive(False)
        self.combobox.set_sensitive(False)        
        Gdk.threads_leave()
        
        if source == "From cache file":
            lyrics = self.get_lyrics_from_cache(self.path)
        else:   
            lyrics = self.get_lyrics_from_source(source, artist, title)
            # check if playing song changed
            if artist != self.clean_artist or title != self.clean_title:
                print "song changed"
                return

        Gdk.threads_enter()                
        self.show_lyrics(self.artist, self.title, lyrics)        
        self.button.set_sensitive(True)
        self.combobox.set_sensitive(True)        
        Gdk.threads_leave()
        
    def scan_all_sources(self, artist, title):
        
        Gdk.threads_enter()
        self.textbuffer.set_text("searching lyrics...")
        Gdk.threads_leave()
          
        newthread = Thread(target=self._scan_all_sources_thread, args=(artist, title))
        newthread.start()
    
    def _scan_all_sources_thread(self, artist, title):
        Gdk.threads_enter()        
        self.button.set_sensitive(False)
        self.combobox.set_sensitive(False)        
        Gdk.threads_leave()
        
        lyrics = self.get_lyrics_from_cache(self.path)
        
        if lyrics == "":
            i = 0
            while lyrics == "" and i < len(self.sources):
                lyrics = self.get_lyrics_from_source(self.sources[i], artist, title)
                # check if playing song changed
                if artist != self.clean_artist or title != self.clean_title:
                    print "song changed"
                    return
                i += 1
            if lyrics == "":
                self.combobox.set_active(-1)
        
        Gdk.threads_enter()        
        self.show_lyrics(self.artist, self.title, lyrics)
        self.button.set_sensitive(True)
        self.combobox.set_sensitive(True)        
        Gdk.threads_leave()
        
    def get_lyrics_from_cache(self, path):
        # try to load lyrics from cache
        if os.path.exists (path):
            try:
                cachefile = open(path, "r")
                lyrics = cachefile.read()
                cachefile.close()
                print "got lyrics from cache"
                Gdk.threads_enter()
                self.combobox.set_active_id("cache")
                Gdk.threads_leave()
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
        print "source: " + source
        
        Gdk.threads_enter()
        self.combobox.set_active_id(source)
        Gdk.threads_leave()
        
        parser = self.dict[source].Parser(artist, title)
        lyrics = parser.parse()
        
        if lyrics != "":
            print "got lyrics from source"
            lyrics = lyrics + "\n\n(lyrics from " + source + ")"
            lyrics = lyrics.decode("utf-8", "replace")
            if lyrics != "" and self.cache:
                self.write_lyrics_to_cache(self.path, lyrics)
            
        return lyrics    
    
    def show_lyrics(self, artist, title, lyrics):
        if lyrics == "":
            print "no lyrics found"
            lyrics = "No lyrics found"
            
        self.textbuffer.set_text(artist + " - " + title + "\n" + lyrics)
        # make 'artist - title' header bold and underlined 
        start = self.textbuffer.get_start_iter()
        end = start.copy()
        end.forward_to_line_end()
        self.textbuffer.apply_tag(self.tag, start, end)
        
        
