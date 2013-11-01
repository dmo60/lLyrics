lLyrics
===============

lLyrics is a plugin for [Rhythmbox](http://projects.gnome.org/rhythmbox/), which displays lyrics for the current playing song in the right sidebar.

Rhythmbox ships with a lyrics plugin, that is more or less broken and doesn't integrate well into the UI, so I decided to write a new one.

lLyrics has a lot of features and is customizable to a great extend.



![Screenshot](http://www.dmo60.de/lLyricsScreenshot.png)




Lyrics sources
---------------

  - Lyricwiki.org
  - Letras.terra.com.br
  - Metrolyrics.com
  - AZLyrics.com
  - Lyricsmania.com
  - Darklyrics.com
  - Chartlyrics.com
  - Leoslyrics.com
  - Lyrdb.com
  
It is also possible to retrieve lyrics from the built-in Rhythmbox lyrics plugin, but this is not recommended since it has some bugs and may cause instabilities.




Installation
---------------

In Ubuntu based distribution, you can install this plugin via [a PPA by fossfreedom](https://launchpad.net/~fossfreedom/+archive/rhythmbox-plugins). Other distributions may provide similar options (e.g. Arch AUR).

To manually install the plugin, download the zip-file by pressing the "ZIP"-button on the upper part of this page and extract it.
Change to the extracted folder, open a terminal (in the directory where Makefile is located) and run `make install`. 

This will install the plugin for the current user only which is sufficiant in most of the cases. 
It will ask for your sudo password, but don't worry, it is only required to install the schema file that is needed to save your preferences.

To install lLyrics systemwide for all users, run `make install-systemwide`.

Afterwards enable "lLyrics" plugin in Rhythmbox under 'Edit > Plugins'.

If you want to uninstall it, run `make uninstall`.

Note that Rhythmbox version 2.90 or higher is required to run lLyrics!




Features
---------------
  - Support for a lot of different lyrics sites (see above)
  - Integration into the Rhythmbox UI
  - Lyrics sources can be prioritised and deactivated
  - Automatically display lyrics on playback or only on-demand
  - Save retrieved lyrics to a file (can be deactivated)
  - Possibility to edit lyrics
  - Appearance customizable to adapt to your desires or your available screen space
  - Basic support for synchronized lyrics
  - more...




Credits
---------------

I was inspired by the awesome Songbird plugin [MLyrics](https://github.com/FreeleX/MLyrics).
Thanks to all who contribute, report issues or help in any other way to make this plugin better.

You will always find the latest version on [GitHub](https://github.com/dmo60/lLyrics).
Please report bugs, issues or feature requests there.

Help with translations is always appreciated!

All lyrics are property and copyright of their owners.
