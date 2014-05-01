from gi.repository import Gtk
import gettext
import os
gettext.install('lLyrics', os.path.dirname(__file__) + "/locale/")


class DownAllWindow(object):

    def __init__(self):
        self.window = None
        self.progressbar = None
        self.label = None
        self.grid = None
        self.cancel = False

    def get_Down_All_Window(self):
        if self.window != None:
            self.cancel = False
            self.label.set_text("")
            return self.window
        self.window = Gtk.Window()
        self.window.connect('delete-event', self.close)

        self.window.set_border_width(10)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.window.add(vbox)

        self.progressbar = Gtk.ProgressBar()
        self.progressbar.set_show_text(True)
        vbox.pack_start(self.progressbar, True, True, 0)

        self.label = Gtk.Label()
        vbox.pack_start(self.label, True, True, 0)

        self.grid = Gtk.Grid()
        vbox.pack_start(self.grid, True, True, 0)

        self.button = Gtk.Button(_("Cancel"))
        self.button.connect("clicked", self.cancel_callback)
        self.grid.add(self.button)

        return self.window

    def set_progress(self, progress, text):
        self.progressbar.set_fraction(progress)
        self.progressbar.set_text(text)

    def set_text(self, text):
        self.label.set_text(text)

    def cancel_callback(self, button):
        if not self.cancel:
            self.cancel = True
            self.set_text(_("Canceling thread..."))
            button.set_sensitive = False
        else:
            self.window.destroy()

    def is_canceled(self):
        return self.cancel

    def is_visible(self):
        return self.window == None

    def close(self):
        self.window.destroy()
        return True

    def change_button_text(self):
        self.button.set_sensitive = True
        self.button.set_label(_("Exit"))
        