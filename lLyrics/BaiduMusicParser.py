# Parser for mp3.baidu.com

import BaseParser

class Parser(BaseParser.Parser):
  source = 'mp3.baidu.com'

  def api(self):
    return 'http://sug.music.baidu.com/info/suggestion?format=json&version=2&from=0&word=' + self.quote(self.artist + ' ' + self.title)[0]

  def verify(self, ret):
    if ret is None:
      return False
    try:
      self.resolve(ret)
    except:
      return False
    return True

  def resolve(self, ret):
    return ret['data']['song'][0]['songid']

  def dealResolved(self, songid):
    song = self.fetchJson('http://music.baidu.com/data/music/links?format=json&songIds=' + songid)
    try:
      lrcLink = song['data']['songList'][0]['lrcLink']
    except:
      return ''
    if not lrcLink or not lrcLink.replace(' ', ''):
      return ''
    return self.fetch('http://music.baidu.com' + lrcLink) or ''
