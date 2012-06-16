# install schema
sudo cp ./lLyrics/org.gnome.rhythmbox.plugins.llyrics.gschema.xml /usr/share/glib-2.0/schemas/
sudo glib-compile-schemas /usr/share/glib-2.0/schemas/

# install plugin
mkdir -p ~/.local/share/rhythmbox/plugins/
rm -r -f ~/.local/share/rhythmbox/plugins/lLyrics/
cp -r ./lLyrics/ ~/.local/share/rhythmbox/plugins/
