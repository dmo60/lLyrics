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

import os

from gi.repository import Gio
from gi.repository import GObject
from gi.repository import PeasGtk
from gi.repository import Gtk
from gi.repository import RB

import lLyrics

import gettext


DCONF_DIR = 'org.gnome.rhythmbox.plugins.llyrics'


class Config(object):

    def __init__(self):
        self.settings = Gio.Settings(DCONF_DIR)

    def check_active_sources(self):
        # remove invalid entries
        changed = False
        entries = self.settings["active-sources"]

        # update key, if changed
        if changed:
            self.settings["active-sources"] = entries

    def check_lyrics_folder(self):
        folder = self.settings["lyrics-folder"]
        changed = False

        # expand user directory
        if "~" in folder:
            folder = os.path.expanduser(folder)
            changed = True

        # path not set or invalid
        if not folder or not os.path.exists(folder):
            folder = os.path.join(RB.user_cache_dir(), "lyrics")
            folder = os.path.expanduser(folder)
            if not os.path.exists(folder):
                os.mkdir(folder)
            changed = True
            print("invalid path in lyrics-folder, set to default")

        if changed:
            self.settings["lyrics-folder"] = folder

    def get_settings(self):
        return self.settings

    def get_show_first(self):
        return self.settings["show-first"]

    def get_cache_lyrics(self):
        return self.settings["cache-lyrics"]

    def get_lyrics_folder(self):
        self.check_lyrics_folder()
        return self.settings["lyrics-folder"]

    def get_ignore_brackets(self):
        return self.settings["ignore-brackets"]

    def get_left_sidebar(self):
        return self.settings["left-sidebar"]

    def get_hide_label(self):
        return self.settings["hide-label"]


class ConfigDialog(GObject.Object, PeasGtk.Configurable):
    __gtype_name__ = 'lLyricsConfigDialog'
    object = GObject.property(type=GObject.Object)

    def __init__(self):
        GObject.Object.__init__(self)
        self.settings = Gio.Settings(DCONF_DIR)

    def do_create_configure_widget(self):
        # init locales
        gettext.install('lLyrics', os.path.dirname(__file__) + "/locale/")

        # page 1 for general settings
        page1 = Gtk.VBox()

        # switch for show-first
        hbox = Gtk.HBox()
        switch = Gtk.Switch()
        switch.set_active(self.settings["show-first"])
        switch.connect("notify::active", self.switch_toggled, "show-first")

        label = Gtk.Label("<b>" + _("Show sidebar on first playback") + "</b>")
        label.set_use_markup(True)

        hbox.pack_start(label, False, False, 5)
        hbox.pack_start(switch, False, False, 5)
        page1.pack_start(hbox, False, False, 10)

        # switch for cache-lyrics
        hbox = Gtk.HBox()
        switch = Gtk.Switch()
        switch.set_active(self.settings["cache-lyrics"])
        switch.connect("notify::active", self.switch_toggled, "cache-lyrics")

        label = Gtk.Label("<b>" + _("Save lyrics ") + "</b>")
        label.set_use_markup(True)

        descr = Gtk.Label("<i>" +
                          _("Whether to automatically save retrieved " +
                          "lyrics in the folder specified below") + "</i>")
        descr.set_alignment(0, 0)
        descr.set_margin_left(15)
        descr.set_line_wrap(True)
        descr.set_use_markup(True)

        hbox.pack_start(label, False, False, 5)
        hbox.pack_start(switch, False, False, 5)
        vbox = Gtk.VBox()
        vbox.pack_start(hbox, False, False, 0)
        vbox.pack_start(descr, False, False, 0)
        page1.pack_start(vbox, False, False, 10)

        # file chooser for lyrics-folder
        hbox = Gtk.HBox()
        file_chooser = Gtk.FileChooserButton()
        file_chooser.set_action(Gtk.FileChooserAction.SELECT_FOLDER)
        file_chooser.set_current_folder(self.settings["lyrics-folder"])
        file_chooser.connect("current-folder-changed", self.folder_set)

        default_button = Gtk.Button(_("default"))
        default_button.connect("clicked",
                               self.set_folder_default,
                               file_chooser)

        label = Gtk.Label("<b>" + _("Folder for lyrics") + "</b>")
        label.set_use_markup(True)

        hbox.pack_start(label, False, False, 5)
        hbox.pack_start(file_chooser, True, True, 5)
        hbox.pack_start(default_button, False, False, 5)
        page1.pack_start(hbox, False, False, 10)

        # switch for ignore-brackets
        hbox = Gtk.HBox()
        switch = Gtk.Switch()
        switch.set_active(self.settings["ignore-brackets"])
        switch.connect("notify::active",
                       self.switch_toggled,
                       "ignore-brackets")

        label = Gtk.Label("<b>" + _("Always ignore parentheses in song title")
                           + "</b>")
        label.set_use_markup(True)

        descr = Gtk.Label("<i>" + _("When turned off, only parentheses " +
                                    "containing specific strings "
                            "(e.g. 'remix', 'live', 'edit', etc) are filtered")
                          + "</i>")
        descr.set_alignment(0, 0)
        descr.set_margin_left(15)
        descr.set_line_wrap(True)
        descr.set_use_markup(True)

        hbox.pack_start(label, False, False, 5)
        hbox.pack_start(switch, False, False, 5)
        vbox = Gtk.VBox()
        vbox.pack_start(hbox, False, False, 0)
        vbox.pack_start(descr, False, False, 0)

        page1.pack_start(vbox, False, False, 10)

        # page 3 for appearance settings
        page2 = Gtk.VBox()

        # switch for hide-label
        hbox = Gtk.HBox()
        switch = Gtk.Switch()
        switch.set_active(self.settings["hide-label"])
        switch.connect("notify::active", self.switch_toggled, "hide-label")

        label = Gtk.Label("<b>" + _("Hide sidebar label") + "</b>")
        label.set_use_markup(True)

        hbox.pack_start(label, False, False, 5)
        hbox.pack_start(switch, False, False, 5)

        page2.pack_start(hbox, False, False, 10)

        # switch for left-sidebar
        hbox = Gtk.HBox()
        switch = Gtk.Switch()
        switch.set_active(self.settings["left-sidebar"])
        switch.connect("notify::active", self.switch_toggled, "left-sidebar")

        label = Gtk.Label("<b>" + _("Show lyrics in left sidebar \
                                    instead of right one")
                          + "</b>")
        label.set_use_markup(True)

        descr = Gtk.Label("<i>" + _("You have to disable and re-enable \
                                    this plugin or restart Rhythmbox "
                                    "to apply changes here") + "</i>")
        descr.set_alignment(0, 0)
        descr.set_margin_left(15)
        descr.set_line_wrap(True)
        descr.set_use_markup(True)

        hbox.pack_start(label, False, False, 5)
        hbox.pack_start(switch, False, False, 5)
        vbox = Gtk.VBox()
        vbox.pack_start(hbox, False, False, 0)
        vbox.pack_start(descr, False, False, 0)

        page2.pack_start(vbox, False, False, 10)

        page3 = Gtk.VBox()
        scroll = Gtk.ScrolledWindow()
        scroll.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)

        store = Gtk.ListStore(str, str, str, str, int)
        for site in lLyrics.searcher.get_sites():
            store.append([site.name, site.start,
                        site.end, site.Id, site.tagNumber])
        tree = Gtk.TreeView(store)  
        # tree.set_grid_lines(Gtk.TreeViewGridLines.BOTH)
        tree.set_rules_hint(True)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Name", renderer, text=0)
        tree.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Start", renderer, text=1)
        tree.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("End", renderer, text=2)
        tree.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Tag id", renderer, text=3)
        tree.append_column(column)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Number", renderer, text=4)
        tree.append_column(column)

        scroll.add(tree)
        vbox = Gtk.VBox()
        vbox.pack_start(scroll, True, True, 0) 
        hbox = Gtk.HBox()
        button = Gtk.Button(_("Add source"))
        hbox.pack_end(button, False, False, 0)

        vbox.pack_start(hbox, False, False, 0)
        
        page3.pack_start(vbox, True, True, 0)

        # create a notebook as top level container
        nb = Gtk.Notebook()
        nb.append_page(page1, Gtk.Label(_("General")))
        nb.append_page(page2, Gtk.Label(_("Appearance")))
        nb.append_page(page3, Gtk.Label(_("Sources")))

        nb.show_all()
        nb.set_size_request(300, -1)

        return nb

    def switch_toggled(self, switch, active, key):
        self.settings[key] = switch.get_active()

    def source_toggled(self, checkbutton, source):
        entries = self.settings["active-sources"]
        if checkbutton.get_active():
            entries.append(source)
        else:
            entries.remove(source)

        self.settings["active-sources"] = entries

    def reorder_sources(self, button, source, hbox, vbox, direction):
        rows = vbox.get_children()
        if direction == "up":
            new_index = rows.index(hbox) - 1
            if new_index == 0:
                button.set_sensitive(False)
                rows[0].get_children()[1].set_sensitive(True)
            if new_index == len(rows) - 2:
                rows[-2].get_children()[2].set_sensitive(False)
                rows[-1].get_children()[2].set_sensitive(True)
        else:
            new_index = rows.index(hbox) + 1
            if new_index == len(rows) - 1:
                button.set_sensitive(False)
                rows[-1].get_children()[2].set_sensitive(True)
            if new_index == 1:
                rows[1].get_children()[1].set_sensitive(False)
                rows[0].get_children()[1].set_sensitive(True)

        vbox.reorder_child(hbox, new_index)

    def folder_set(self, file_chooser):
        new_folder = file_chooser.get_current_folder()
        if self.settings["lyrics-folder"] != new_folder:
            print("folder changed")
            self.settings["lyrics-folder"] = new_folder

    def set_folder_default(self, button, file_chooser):
        file_chooser.set_current_folder(os.path.join(RB.user_cache_dir(),
                                                     "lyrics"))
