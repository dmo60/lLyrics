lLyrics
===============

lLyrics is a plugin for [Rhythmbox](http://projects.gnome.org/rhythmbox/), which displays lyrics for the current playing song in the right sidebar.

Rhythmbox ships with a lyrics plugin, that is more or less broken and doesn't integrate well into the UI, so I decided to write a new one.



![Screenshot](http://www.dmo60.de/lLyricsScreenshot.png)




Lyrics sources
---------------

  - Lyricwiki.org
  - Letras.terra.com.br
  - Metrolyrics.com
  - Chartlyrics.com
  - Lyrdb.com
  - Sogou.com (provides synchronized lyrics which is not implemented yet)

More may come in the future...




Installation
---------------

To install this plugin, open a terminal (in the directory where Makefile is located) and run `make install`. This will install the plugin for the current user only which is sufficiant in most of the cases. 
To install lLyrics systemwide for all users, run `make install-systemwide`.

Afterwards enable "lLyrics" plugin in Rhythmbox under 'Edit > Plugins'.

If you want to uninstall it, run `make uninstall`.

Note that Rhythmbox version 2.90 or higher is required to run lLyrics!




Credits
---------------

I was inspired by the awesome Songbird plugin [MLyrics](https://github.com/FreeleX/MLyrics).
Thanks to all who contribute, report issues or help in any other way to make this plugin better.

You will always find the latest version on [GitHub](https://github.com/dmo60/lLyrics).
Please report bugs, issues or feature requests there.

Help with translations is always appreciated!

All lyrics are property and copyright of their owners.
