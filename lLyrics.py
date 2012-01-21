from gi.repository import GObject, Peas
from gi.repository import RB
from gi.repository import Gtk

class lLyrics(GObject.GObject, Peas.Activatable):
    __gtype_name = 'lLyrics'
    object = GObject.property(type=GObject.GObject)
    
    def __init__(self):
        GObject.GObject.__init__(self)

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
        self.shell = None
        self.player_cb_ids = None
        self.visible = None
        self.player = None
        
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
        self.textview.set_pixels_above_lines(10)
        self.textview.set_pixels_below_lines(10)
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD)
        
        # initialize a TextBuffer to store lyrics in
        self.textbuffer = Gtk.TextBuffer()

        # pack everything into side pane
        self.vbox.pack_start  (frame, False, True, 0)
        self.vbox.pack_start (self.textview, True, True, 10)

        self.vbox.show_all()
        self.vbox.set_size_request(200, -1)
        # do not add widget yet, this will be done when user starts playback
        self.visible = False
        
    def search_lyrics(self, player, entry):
        # show sidebar at first playback or when reactivating plugin during playback
        if not self.visible:
            self.shell.add_widget (self.vbox, RB.ShellUILocation.RIGHT_SIDEBAR, True, True)
            self.visible = True

        if entry is not None:
            artist = entry.get_string(RB.RhythmDBPropType.ARTIST)
            title = entry.get_string(RB.RhythmDBPropType.TITLE)
        else:
            artist = "none"
            title = "none"     
            
        self.textbuffer.set_text(artist + " - " + title)
        self.textview.set_buffer(self.textbuffer)
    