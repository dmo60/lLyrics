# Parser for geci.me

import BaseParser

class Parser(BaseParser.Parser):
  source = 'geci.me'

  def api(self):
    return 'http://geci.me/api/lyric/%s/%s' % self.quote(self.title, self.artist)

  def verify(self, ret):
    if ret is None:
      return False
    if not ('code' in ret and ret['code'] == 0):
      return False
    if not ('count' in ret and ret['count'] >= 1):
      return False
    try:
      self.resolve(ret)
    except:
      return False
    return True

  def resolve(self, ret):
    return ret['result'][0]['lrc'] or ''
