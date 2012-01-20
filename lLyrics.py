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
        self.init_sidebar()

    def do_deactivate(self):
        """
        deactivate plugin
        """
        print "deactivate plugin lLyrics"
        self.shell.remove_widget (self.vbox, RB.ShellUILocation.RIGHT_SIDEBAR)
        
        
    def init_sidebar(self):
        self.vbox = Gtk.VBox()
        frame = Gtk.Frame()
        self.label = Gtk.Label(_("Lyrics"))
        frame.set_shadow_type(Gtk.ShadowType.IN)
        frame.set_label_align(0.0,0.0)
        frame.set_label_widget(self.label)
        self.label.set_use_markup(True)
        self.label.set_padding(0,4)

        #---- pack everything into side pane ----#
        self.vbox.pack_start  (frame, False, True, 0)

        self.vbox.show_all()
        self.vbox.set_size_request(200, -1)
        self.shell.add_widget (self.vbox, RB.ShellUILocation.RIGHT_SIDEBAR, True, True)
    