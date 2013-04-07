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
_DEBUG = True 
class Config(object):
    
    def __init__(self):
        self.settings = Gio.Settings (DCONF_DIR)
    
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
        folder = self.settings["lyrics-folder-change"]
        changed = False
        if _DEBUG == True:
            import sys
            func_name = sys._getframe().f_code.co_name
            debug_file = open ( "debug_file", "a+" )
            debug_file.write ( func_name + ": " + folder + '\n'); 
            debug_file.close()
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
            print "invalid path in lyrics-folder-change, set to default"
        
        if changed:
            self.settings["lyrics-folder-change"] = folder
        
    def check_icon_path(self):
        path = self.settings["icon-path"]
        changed = False
        
        # expand user directory
        if "~" in path:
            path = os.path.expanduser(path)
            changed = True
            
        # path not set or invalid
        if not path or not os.path.exists(path) or path == "default":
            path = os.path.join(os.path.dirname(__file__) + "/lLyrics-icon.png")
            path = os.path.expanduser(path)
            changed = True
            print "file for toolbar icon does not exist, set to default"
        
        if changed:
            self.settings["icon-path"] = path
    
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
    
    def get_show_first(self):
        return self.settings["show-first"]
    
    def get_cache_lyrics(self):
        return self.settings["cache-lyrics"]
    
    def get_lyrics_folder(self):
        self.check_lyrics_folder()
        return self.settings["lyrics-folder-change"]
    
    def get_ignore_brackets(self):
        return self.settings["ignore-brackets"]
    
    def get_show_toolbar_icon(self):
        return self.settings["show-toolbar-icon"]
    
    def get_icon_path(self):
        self.check_icon_path()
        return self.settings["icon-path"]
    
    def get_toolbar_separators(self):
        left = self.settings["separator-left"]
        if left:
            left = "<separator />"
        else:
            left = ""
            
        right = self.settings["separator-right"]
        if right:
            right = "<separator />"
        else:
            right = ""
            
        return (left, right)
    
    def get_toplevel_menu(self):
        return self.settings["toplevel-menu"]
    
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
        
        descr = Gtk.Label("<i>" + _("Whether to automatically save retrieved lyrics in the folder specified below") + "</i>")
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
        
        # file chooser for lyrics-folder-change
        hbox = Gtk.HBox()
        file_chooser = Gtk.FileChooserButton()
        file_chooser.set_action(Gtk.FileChooserAction.SELECT_FOLDER)
        file_chooser.set_current_folder(self.settings["lyrics-folder-change"])
        file_chooser.connect("current-folder-changed", self.folder_set)
        
        default_button = Gtk.Button(_("default"))
        default_button.connect("clicked", self.set_folder_default, file_chooser)
        
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
        switch.connect("notify::active", self.switch_toggled, "ignore-brackets")
        
        label = Gtk.Label("<b>" + _("Always ignore parentheses in song title") + "</b>")
        label.set_use_markup(True)
        
        descr = Gtk.Label("<i>" + _("When turned off, only parentheses containing specific strings "
                             "(e.g. 'remix', 'live', 'edit', etc) are filtered") + "</i>")
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
        
        # page 2 for sources settings
        page2 = Gtk.VBox()
        
        # check buttons for lyric sources
        label = Gtk.Label("<b>" + _("Sources:") + "</b>")
        label.set_alignment(0, 0)
        label.set_padding(5, 0)
        label.set_use_markup(True)
        
        vbox = Gtk.VBox()
        vbox.set_margin_left(30)
        vbox.set_margin_top(5)
        vbox.set_margin_bottom(5)
        for source in self.settings["scanning-order"]:
            hbox = Gtk.HBox()
            check = Gtk.CheckButton(_(source))
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
        
        warn = Gtk.Label("<i>" + 
                           _("Warning: 'External' calls the Rhythmbox built-in lyrics plugin.\n"
                             "I can not guarantee that the provided engines work properly! "
                             "They might have bugs or make the plugin crash!\n"
                             "If you experience any problems, try to unselect some lyrics sites "
                             "in the 'lyrics' plugin's preference dialog or deactivate the 'External' source.") 
                           + "</i>")
        warn.set_alignment(0, 0)
        warn.set_margin_left(15)
        warn.set_line_wrap(True)
        warn.set_use_markup(True)
        
        vbox2 = Gtk.VBox()
        vbox2.pack_start(label, False, False, 0)
        vbox2.pack_start(vbox, False, False, 0)
        vbox2.pack_start(warn, False, False, 0)
        
        page2.pack_start(vbox2, False, False, 10)
        
        # page 3 for appearance settings
        page3 = Gtk.VBox()
        
        # switch for show-toolbar-icon
        hbox = Gtk.HBox()
        switch = Gtk.Switch()
        switch.set_active(self.settings["show-toolbar-icon"])
        switch.connect("notify::active", self.switch_toggled, "show-toolbar-icon")
        
        label = Gtk.Label("<b>" + _("Show toolbar icon") + "</b>")
        label.set_use_markup(True)
        
        descr = Gtk.Label("<i>" + _("When turned off, the lyrics sidebar can only be toggled "
                                    "using the 'View' menu or by pressing 'Ctrl+L'") + "</i>")
        descr.set_alignment(0, 0)
        descr.set_margin_left(15)
        descr.set_line_wrap(True)
        descr.set_use_markup(True)
        
        hbox.pack_start(label, False, False, 5)
        hbox.pack_start(switch, False, False, 5)
        vbox = Gtk.VBox()
        vbox.pack_start(hbox, False, False, 0)
        vbox.pack_start(descr, False, False, 0)
        
        page3.pack_start(vbox, False, False, 10)
        
        # file chooser for toolbar icon
        hbox = Gtk.HBox()
        file_chooser = Gtk.FileChooserButton()
        file_chooser.set_action(Gtk.FileChooserAction.OPEN)
        # only allow images
        file_filter = Gtk.FileFilter()
        file_filter.add_pixbuf_formats()
        file_filter.set_name(_("Image files"))
        file_chooser.add_filter(file_filter)
        file_chooser.set_filename(self.settings["icon-path"])
        file_chooser.connect("file-set", self.icon_set)
        
        default_button = Gtk.Button(_("default icon"))
        default_button.connect("clicked", self.set_icon_default, file_chooser)
        
        label = Gtk.Label("<b>" + _("Toolbar icon") + "</b>")
        label.set_use_markup(True)
        
        descr = Gtk.Label("<i>" + _("You have to disable and re-enable this plugin or restart Rhythmbox "
                                    "to apply changes here") + "</i>")
        descr.set_alignment(0, 0)
        descr.set_margin_left(15)
        descr.set_line_wrap(True)
        descr.set_use_markup(True)
        
        hbox.pack_start(label, False, False, 5)
        hbox.pack_start(file_chooser, True, True, 5)
        hbox.pack_start(default_button, False, False, 5)
        vbox = Gtk.VBox()
        vbox.pack_start(hbox, False, False, 0)
        vbox.pack_start(descr, False, False, 0)
        
        page3.pack_start(vbox, False, False, 10)
        
        # checkbuttons for toolbar separators
        hbox = Gtk.HBox()
        
        label = Gtk.Label("<b>" + _("Show toolbar separators") + "</b>")
        label.set_use_markup(True)
        
        check = Gtk.CheckButton(_("left"))
        check.set_active(self.settings["separator-left"])
        check.connect("toggled", self.switch_toggled, None, "separator-left")
        
        check2 = Gtk.CheckButton(_("right"))
        check2.set_active(self.settings["separator-right"])
        check2.connect("toggled", self.switch_toggled, None, "separator-right")
        
        hbox.pack_start(label, False, False, 5)
        hbox.pack_start(check, False, False, 5)
        hbox.pack_start(check2, False, False, 5)
        page3.pack_start(hbox, False, False, 10)
        
        # switch for toplevel-menu
        hbox = Gtk.HBox()
        switch = Gtk.Switch()
        switch.set_active(self.settings["toplevel-menu"])
        switch.connect("notify::active", self.switch_toggled, "toplevel-menu")
        
        label = Gtk.Label("<b>" + _("Show lyrics menu as toplevel menu") + "</b>")
        label.set_use_markup(True)
        
        descr = Gtk.Label("<i>" + _("When turned off, the lyrics menu is moved to the 'Control' menu") + "</i>")
        descr.set_alignment(0, 0)
        descr.set_margin_left(15)
        descr.set_line_wrap(True)
        descr.set_use_markup(True)
        
        hbox.pack_start(label, False, False, 5)
        hbox.pack_start(switch, False, False, 5)
        vbox = Gtk.VBox()
        vbox.pack_start(hbox, False, False, 0)
        vbox.pack_start(descr, False, False, 0)
        
        page3.pack_start(vbox, False, False, 10)
        
        # switch for hide-label
        hbox = Gtk.HBox()
        switch = Gtk.Switch()
        switch.set_active(self.settings["hide-label"])
        switch.connect("notify::active", self.switch_toggled, "hide-label")
        
        label = Gtk.Label("<b>" + _("Hide sidebar label") + "</b>")
        label.set_use_markup(True)
        
        hbox.pack_start(label, False, False, 5)
        hbox.pack_start(switch, False, False, 5)
        
        page3.pack_start(hbox, False, False, 10)
        
        # switch for left-sidebar
        hbox = Gtk.HBox()
        switch = Gtk.Switch()
        switch.set_active(self.settings["left-sidebar"])
        switch.connect("notify::active", self.switch_toggled, "left-sidebar")
        
        label = Gtk.Label("<b>" + _("Show lyrics in left sidebar instead of right one") + "</b>")
        label.set_use_markup(True)
        
        descr = Gtk.Label("<i>" + _("You have to disable and re-enable this plugin or restart Rhythmbox "
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
        
        page3.pack_start(vbox, False, False, 10)
        
        # create a notebook as top level container        
        nb = Gtk.Notebook()
        nb.append_page(page1, Gtk.Label(_("General")))
        nb.append_page(page2, Gtk.Label(_("Sources")))
        nb.append_page(page3, Gtk.Label(_("Appearance")))
        
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
        
        entries = self.settings["scanning-order"]
        entries.remove(source)
        entries.insert(new_index, source)
        self.settings["scanning-order"] = entries
        
    def folder_set(self, file_chooser):
        new_folder = file_chooser.get_current_folder()
        if self.settings["lyrics-folder-change"] != new_folder:
            print "folder changed"
            self.settings["lyrics-folder-change"] = new_folder
    
    def set_folder_default(self, button, file_chooser):
        file_chooser.set_current_folder(os.path.join(RB.user_cache_dir(), "lyrics"))
    
    def icon_set(self, file_chooser):
        new_path = file_chooser.get_filename()
        if self.settings["icon-path"] != new_path:
            print "icon changed"
            self.settings["icon-path"] = new_path
    
    def set_icon_default(self, button, file_chooser):
        default_path = os.path.dirname(__file__) + "/lLyrics-icon.png"
        file_chooser.set_filename(default_path)
        self.settings["icon-path"] = default_path
        
        
        
