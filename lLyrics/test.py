# -*- coding: utf-8 -*- 


import Util
import lLyrics


if __name__ == '__main__':
   #  fp = open (u'/home/anzizhao/.lyrics/许志安-上弦月.lrc'.encode('utf-8'), "r+")
   # # fp = open (u'/home/anzizhao/.lyrics/黄小琥-没那么简单.lrc'.encode('utf-8'), "r+")
   #  context = fp.read()
   #  fp.close()
   #  (lyrics, tags) = Util.parse_lrc(context)
    

   #  for i in  range(len(tags)):
   #      print tags[i][0], tags[i][1]
    # fp = open (u'/home/anzizhao/.lyrics/黄小琥-没有那么.lrc'.encode('utf-8'), "r+")
    # context = fp.read()
    # fp.close()
    # (lyrics, tags) = Util.parse_lrc(context)
    # print lyrics
    # print tags 
    # b = u'PYTHON酷'
    # print Util.filter_to_chinese(b)
    
    lyric = lLyrics.lLyrics()
    artist, title = lyric.clean_song_data ( u'许志安+梅艳芳'.encode('utf-8'), u'女人之苦'.encode('utf-8'))
    print artist, title 

    artist, title = lyric.clean_song_data ( u'泰勒 史薇芙特'.encode('utf-8'), u'Christmases When You Were Mine'.encode('utf-8'))
    print artist, title 
 
