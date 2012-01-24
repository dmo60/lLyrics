from gi.repository import GObject, Peas, Gdk
from gi.repository import RB
from gi.repository import Gtk
from threading import Thread
import re
import pango
import ChartlyricsParser, LyricwikiParser, MetrolyricsParser

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


LYRIC_TITLE_STRIP=["\(live[^\)]*\)", "\(acoustic[^\)]*\)", "\([^\)]*mix\)", "\([^\)]*version\)", "\([^\)]*edit\)", "\(feat[^\)]*\)", "\(bonus track\)"]
LYRIC_TITLE_REPLACE=[("/", "-"), (" & ", " and ")]
LYRIC_ARTIST_REPLACE=[("/", "-"), (" & ", " and ")]

LYRIC_SOURCES=["Metrolyrics.com", "Lyricwiki.org", "Chartlyrics.com"]

class lLyrics(GObject.GObject, Peas.Activatable):
    __gtype_name = 'lLyrics'
    object = GObject.property(type=GObject.GObject)
    
    def __init__(self):
        GObject.GObject.__init__(self)
        GObject.threads_init()
        Gdk.threads_init()

    def do_activate(self):
        """
        activate plugin
        """        
        self.shell = self.object
        self.init_sidebar()

        self.player = self.shell.props.shell_player
        # search lyrics if already playing (this will be the case if user reactivates plugin during playback)
        if self.player.props.playing:
                self.search_lyrics(self.player, self.player.get_playing_entry())
        # search lyrics if song changes 
        self.psc_id = self.player.connect ('playing-song-changed', self.search_lyrics)
        
        # Add button to toggle visibility of pane
        self.action = ('ToggleLyricSideBar','gtk-info', _("Lyrics"),
                        None, _("Change the visibility of the lyrics sidebar"),
                        self.toggle_visibility, True)
        self.action_group = Gtk.ActionGroup(name='lLyricsPluginActions')
        self.action_group.add_toggle_actions([self.action])
        uim = self.shell.props.ui_manager
        uim.insert_action_group (self.action_group, 0)
        self.ui_id = uim.add_ui_from_string(llyrics_ui)
        uim.ensure_update()
        
        print "activated plugin lLyrics"

    def do_deactivate(self):
        """
        deactivate plugin
        """        
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
        self.vbox.pack_start  (frame, False, True, 0)
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
        self.textbuffer.set_text("searching lyrics...")        
        newthread = Thread(target=self._search_lyrics_thread, args=(player, entry))
        newthread.start()
    
    def _search_lyrics_thread(self, player, entry):
        if entry is None:
            return
        artist = entry.get_string(RB.RhythmDBPropType.ARTIST)
        title = entry.get_string(RB.RhythmDBPropType.TITLE)
        print "search lyrics for " + artist + " - " + title
   
        (clean_artist, clean_title) = self.clean_song_data(artist, title)
        
        lyrics = ""
        i = 0
        while lyrics == "" and i < len(LYRIC_SOURCES):
            print "source: " + LYRIC_SOURCES[i]
            parser = self.get_parser(clean_artist, clean_title, i)
            lyrics = parser.parse()
            i += 1
        if lyrics == "":
            print "no lyrics found"
            lyrics = "No lyrics found"
            source = ""
        else:
            source = "\n\n(lyrics from " + LYRIC_SOURCES[i-1] + ")"
            print "found lyrics"
            
        Gdk.threads_enter()
        self.textbuffer.set_text(artist + " - " + title + "\n" + lyrics + source)
        # make 'artist - title' header bold and underlined 
        start = self.textbuffer.get_start_iter()
        end = start.copy()
        end.forward_to_line_end()
        self.textbuffer.apply_tag(self.tag, start, end)
        Gdk.threads_leave()

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
    
    def get_parser(self, artist, title, source):
        if source == 0:
            return MetrolyricsParser.MetrolyricsParser(artist, title)
        if source == 1:
            return LyricwikiParser.LyricwikiParser(artist, title)
        if source == 2:
            return ChartlyricsParser.ChartlyricsParser(artist, title)
        
        