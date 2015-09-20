import urllib.request, urllib.parse
import json

import Util

class Parser:
  source = 'unknown source'
  isJson = True       # See `self.read`
  isSimple = False    # See `self.resolve`
  isNoArtistAllowed = True  # If set true, continue to search the song itself without its artist.

  def __init__(self, artist, title):
    self.artist = artist
    self.title = title
    self.lyrics = ''

  def parse(self):
    ret = self.read(self.api())
    lrc = self.load(ret) if self.verify(ret) else ''
    if lrc:
      return lrc
    if self.isNoArtistAllowed and self.artist:
      self.artist = ''
      return self.parse()
    return ''

  # To support self.api.
  def quote(self, *args):
    return tuple(map(urllib.parse.quote, args))

  # Fetch text from url.
  def fetch(self, url):
    if not url:
      return None
    target = '%s API "%s"' % (self.source, url)
    print('call %s... ' % target)
    try:
      raw = urllib.request.urlopen(url, None, 3).read()
    except:
      print('could not connect to %s.' % target)
      return None
    return Util.bytes_to_string(raw)

  def fetchJson(self, url):
    raw = self.fetch(url)
    return None if raw is None else json.loads(raw)

  # Fetch text from `self.api` for `self.load`, parse it as JSON if `self.isJson`.
  def read(self, url):
    return self.fetchJson(url) if self.isJson else self.fetch(url)

  # Get the real lyric from verified `self.read(self.api())`.
  def load(self, ret):
    raw = self.resolve(ret)
    return (raw if self.isSimple else self.dealResolved(raw)) or ''

  #####################################################################
  # A child class MAY overwrite the functions below.

  # Verify `self.read(self.api())`.
  def verify(self, ret):
    return not not ret

  # If `self.isSimple`, this should return the real lyric.
  # Otherwise, the return value will be processed again by `self.dealResolved`.
  # See also `self.load`.
  def resolve(self, ret):
    return ret

  def dealResolved(self, raw):
    return self.fetch(raw)

  #####################################################################
  # A child class MUST overwrite the functions below.

  # MUST return a url
  def api(self):
    return ''
