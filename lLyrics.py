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
        print "activate plugin lLyrics"
        self.shell = self.object
        player = self.shell.props.shell_player
        self.player_cb_ids = (
                              player.connect ('playing-song-changed', self.init_sidebar)
        )
#        self.init_sidebar()

    def do_deactivate(self):
        """
        deactivate plugin
        """
        print "deactivate plugin lLyrics"
        self.shell.remove_widget (self.vbox, RB.ShellUILocation.RIGHT_SIDEBAR)
        
        
    def init_sidebar(self, player, entry):
        self.vbox = Gtk.VBox()
        frame = Gtk.Frame()
        self.label = Gtk.Label(_("Lyrics"))
        frame.set_shadow_type(Gtk.ShadowType.IN)
        frame.set_label_align(0.0,0.0)
        frame.set_label_widget(self.label)
        self.label.set_use_markup(True)
        self.label.set_padding(0,4)
        
        if entry is not None:
            artist = entry.get_string(RB.RhythmDBPropType.ARTIST)
            title = entry.get_string(RB.RhythmDBPropType.TITLE)
        else:
            artist = "none"
            title = "none"        
        
        textview = Gtk.TextView()
        textbuffer = Gtk.TextBuffer()
        textbuffer.set_text(artist + " - " + title)
        textview.set_buffer(textbuffer)
        textview.set_editable(False)
        textview.set_cursor_visible(False)
        textview.set_left_margin(10)
        textview.set_right_margin(10)
        textview.set_pixels_above_lines(10)
        textview.set_pixels_below_lines(10)
        textview.set_wrap_mode(Gtk.WrapMode.WORD)
        

        #---- pack everything into side pane ----#
        self.vbox.pack_start  (frame, False, True, 0)
        self.vbox.pack_start (textview, True, True, 10)

        self.vbox.show_all()
        self.vbox.set_size_request(200, -1)
        self.shell.add_widget (self.vbox, RB.ShellUILocation.RIGHT_SIDEBAR, True, True)
    