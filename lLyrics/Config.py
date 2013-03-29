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

DCONF_DIR = 'org.gnome.rhythmbox.plugins.llyrics'

class Config(object):
    
    def __init__(self):
        self.settings = Gio.Settings(DCONF_DIR)
    
    def check_active_sources(self):        
        # remove invalid entries
        changed = False
        entries = self.settings["active-sources"]
        for source in entries:
            if not source in lLyrics.LYRICS_SOURCES:
                entries.remove(source)
                changed = True
                print "remove invalid entry in active-sources: " + source
        
        # update key, if changed
        if changed:
            self.settings["active-sources"] = entries
            
    def check_scanning_order(self):
        # remove invalid entries
        changed = False
        entries = self.settings["scanning-order"]
        for source in entries:
            if not source in lLyrics.LYRICS_SOURCES:
                entries.remove(source)
                changed = True
                print "remove invalid entry in scanning-order: " + source
                
        # fill up missing keys
        for source in lLyrics.LYRICS_SOURCES:
            if source not in entries:
                entries.append(source)
                changed = True
                print "append missing entry in scanning-order: " + source
        
        # update key, if changed
        if changed:
            self.settings["scanning-order"] = entries
            
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
            print "invalid path in lyrics-folder, set to default"
        
        if changed:
            self.settings["lyrics-folder"] = folder
        
    
    def get_settings(self):
        return self.settings
    
    def get_lyrics_sources(self):
        self.check_active_sources()
        self.check_scanning_order()
        lyrics_sources = []
        for source in self.settings["scanning-order"]:
            if source in self.settings["active-sources"]:
                lyrics_sources.append(source)
        
        return lyrics_sources
    
    def get_cache_lyrics(self):
        return self.settings["cache-lyrics"]
    
    def get_lyrics_folder(self):
        self.check_lyrics_folder()
        return self.settings["lyrics-folder"]
    
  
    
class ConfigDialog(GObject.Object, PeasGtk.Configurable):
    __gtype_name__ = 'lLyricsConfigDialog'
    object = GObject.property(type=GObject.Object)

    def __init__(self):
        GObject.Object.__init__(self)
        self.settings = Gio.Settings(DCONF_DIR)

    def do_create_configure_widget(self):
        dialog = Gtk.VBox()
        
        # switch for cache-lyrics
        hbox = Gtk.HBox()
        switch = Gtk.Switch()
        switch.set_active(self.settings["cache-lyrics"])
        switch.connect("notify::active", self.switch_toggled, "cache-lyrics")
        
        label = Gtk.Label(_("Save lyrics "))
        
        hbox.pack_start(label, False, False, 5)
        hbox.pack_start(switch, False, False, 5)
        dialog.pack_start(hbox, False, False, 5)
        
        # file chooser for lyrics-folder
        hbox = Gtk.HBox()
        file_chooser = Gtk.FileChooserButton()
        file_chooser.set_action(Gtk.FileChooserAction.SELECT_FOLDER)
        file_chooser.set_current_folder(self.settings["lyrics-folder"])
        file_chooser.connect("current-folder-changed", self.folder_set)
        
        default_button = Gtk.Button(_("default"))
        default_button.connect("clicked", self.set_folder_default, file_chooser)
        
        label = Gtk.Label(_("Folder for lyrics"))
        
        hbox.pack_start(label, False, False, 5)
        hbox.pack_start(file_chooser, True, True, 5)
        hbox.pack_start(default_button, False, False, 5)
        dialog.pack_start(hbox, False, False, 5)
        
        # check buttons for lyric sources
        label = Gtk.Label(_("Sources:"))
        label.set_alignment(0, 0)
        label.set_padding(5, 0)
        label.set_use_markup(True)
        
        vbox = Gtk.VBox()
        vbox.set_margin_left(30)
        for source in self.settings["scanning-order"]:
            hbox = Gtk.HBox()
            check = Gtk.CheckButton(source)
            check.set_active(source in self.settings["active-sources"])
            check.connect("toggled", self.source_toggled, source)
            hbox.pack_start(check, True, True, 3)
            
            button_up = Gtk.Button(u'\u2191')
            button_up.connect("clicked", self.reorder_sources, source, hbox, vbox, "up")
            hbox.pack_start(button_up, False, False, 3)
            if self.settings["scanning-order"].index(source) == 0:
                button_up.set_sensitive(False)
            
            button_down = Gtk.Button(u'\u2193')
            button_down.connect("clicked", self.reorder_sources, source, hbox, vbox, "down")
            hbox.pack_start(button_down, False, False, 3)
            if self.settings["scanning-order"].index(source) == len(self.settings["scanning-order"]) - 1:
                button_down.set_sensitive(False)
            
            vbox.pack_start(hbox, False, False, 0)
        
        label2 = Gtk.Label(_("Warning: 'External' calls the Rhythmbox built-in lyrics plugin.\n"
                             "I can not guarantee that the provided engines work properly! "
                             "They might have bugs or make the plugin crash!\n"
                             "If you experience any problems, try to deselect some lyrics sites "
                             "in the 'lyrics' plugin's preference dialog or deactivate the 'External' source."))
        label2.set_alignment(0, 0)
        label2.set_padding(5, 0)
        label2.set_line_wrap(True)
        label2.set_use_markup(True)
        
        dialog.pack_start(label, False, False, 0)
        dialog.pack_start(vbox, False, False, 0)
        dialog.pack_start(label2, False, False, 0)
        
        dialog.show_all()
        dialog.set_size_request(300, -1)
        
        return dialog
    
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
        
        entries = self.settings["scanning-order"]
        entries.remove(source)
        entries.insert(new_index, source)
        self.settings["scanning-order"] = entries
        
    def folder_set(self, file_chooser):
        new_folder = file_chooser.get_current_folder()
        if self.settings["lyrics-folder"] != new_folder:
            print "folder changed"
            self.settings["lyrics-folder"] = new_folder
    
    def set_folder_default(self, button, file_chooser):
        file_chooser.set_current_folder(os.path.join(RB.user_cache_dir(), "lyrics"))
        
        
        
        