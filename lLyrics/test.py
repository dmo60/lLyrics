# -*- coding: utf-8 -*- 


import Util
import lLyrics
import lrc123Parser
import bzmtvParser 
import chardet

from gi.repository import Gdk
from gi.repository import Gtk


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
    
    # lyric = lLyrics.lLyrics()
    # artist, title = lyric.clean_song_data ( u'许志安+梅艳芳'.encode('utf-8'), u'女人之苦'.encode('utf-8'))
    # print artist, title 

    # artist, title = lyric.clean_song_data ( u'泰勒 史薇芙特'.encode('utf-8'), u'Christmases When You Were Mine'.encode('utf-8'))
    # print artist, title 

# test the lrc file show .
    # filename = u'/home/anzizhao/.lyrics/taylor_swift-mean.lrc'.encode('utf-8')
    # fp = open (filename , "r+" )
    # context = fp.read()
    # fp.close()
    # print "orginal lrc file: \n %s" %  context 
    # lyric_dict , tags = Util.parse_lrc(context)
    # lyrics = ""
    # for item in tags:
    #     lyrics += lyric_dict[ item[1] ]  + '\n'
        
    # print "read the lrc file , get lyric: \n %s" % (lyrics) 

    # print Util.make_lrc_file (filename , lyrics, tags )

# test the search lyrics
    # artist1 = u'Taylor Swift'.encode('utf-8')
    # title1 = u'Christmases When You Were Mine'.encode('utf-8')
   
    # artist2 = u'蔡琴'.encode('utf-8')
    # title2 = u'你的眼神'.encode('utf-8')
    # looplist = [ [ artist1, title1 ], [artist2, title2 ]]
    
    # for artist, title in looplist :
    #     artist, title = Util.clean_song_data ( artist, title )
        
    #     print artist, title 
    #   #  print "lrc123.com web station parser:"
    #   #  p = lrc123Parser.Parser( artist, title )
    #   #  l  = p.parse()
    #   #  print l 
    #     print "lrc.bmztv.com web station parser:"
    #     p = bzmtvParser.Parser( artist, title )
    #     l  = p.parse()
    #     print l 


# test the file code 
    # filename = u'/home/anzizhao/.lyrics/taylor_swift-mean.lrc'.encode('utf-8')
    # fp = open (filename , "r+" )
    # context = fp.read()
    # fp.close()
    # print chardet.detect(context)['encoding']

    # filename = u'/home/anzizhao/.lyrics/taylor_swift-christmases+when+you+were+mine.lrc'.encode('utf-8')
    # fp = open (filename , "r+" )
    # context = fp.read()
    # fp.close()
    # print context[:87]
    # print chardet.detect(context.decode('utf-8').encode('utf-8'))['encoding']
    


# test the gdk intereface 
    filename = u'/home/anzizhao/.lyrics/taylor_swift-mean.lrc'.encode('utf-8')
    fp = open (filename , "r+" )
    context = fp.read()
    fp.close()
    window = Gtk.Window()
    window.set_resizable(True)  
    window.set_title("TextView Widget Basic Example")
    window.set_border_width(0)
    textbuffer = Gtk.TextBuffer()
    textbuffer.set_text ( 'zhaojunan'.encode('utf-8')  )
    textview = Gtk.TextView()
    textview.set_buffer(textbuffer)
    textview.show() 
    window.add (textview)
   
