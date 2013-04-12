# Utility functions
#
# Chartlyrics API seems to have problems with multiple consecutive requests
# (it apparently requires a 20-30sec interval between two API-calls), 
# so just use SearchLyricDirect since it only needs one API request.

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

import re
import string
import os 

def decode_chars(resp):
    chars = resp.split(";")
    resp = ""
    for c in chars:
        try:
            resp = resp + unichr(int(c))
        except:
            print "unknown character " + c
    return resp



def remove_punctuation(data):
    for c in string.punctuation:
        data = data.replace(c, "")
    
    return data

def lrcfile_head_info ( filepath ):
    # the lrc file is ordinary code utf-8 ,so suppose it is .
    lyrics = ''
    if os.path.exists (filepath):
        try:
            lrcfile = open(filepath, "r")
            lyrics = lrcfile.read()
            lrcfile.close()
        except:
            print "error reading cache file"
            return ""

    tag_regex = r"(\[\d+\:\d+\.*\d*\])"   # [xx:xx] or [xx:xx.xx]
    head_end  = re.search(tag_regex, lyrics)    
  
    return lyrics[ : head_end.start() ]
    
def parse_lrc(data):
    tag_regex = r"(\[\d+\:\d+\.*\d*\])"   # [xx:xx] or [xx:xx.xx]
    lyric_start_tag = re.search(tag_regex, data)
    
    # no tags
    if lyric_start_tag is None:
        return (data, None)
   
    tags = []
    lyric_dict = {}
    lyric_id = 0 
    linsta_i  = lyric_start_tag.start()
    linend_i  = data.find('\n', linsta_i )
    while linend_i != -1:
        # song 
        song_i = data.rfind(']', linsta_i, linend_i)
        song_i += 1
        if song_i != 0 and song_i < linend_i and data[song_i] != '\r':
            # no song content and space line situation remove 
            # fill the dictionary 
            lyric_dict[lyric_id] =  data[song_i:linend_i]
            timsta_i = linsta_i ; 
            
            while timsta_i < song_i:
                timsta_i  = data.find('[', timsta_i, linend_i)
                if timsta_i == -1:
                    print  "no time start tag"
                    return (None, None )
                timend_i  = data.find(']', timsta_i, linend_i )
                if timend_i == -1:
                    print  "no time end tag"
                    return (None, None )
            
                tags.append((time_to_seconds( data[timsta_i:timend_i+1]),lyric_id ) )
                
                timsta_i = timend_i+1
            # lyric_id self add 
            lyric_id += 1
        
        
        linsta_i = linend_i + 1 
        linend_i  = data.find('\n', linsta_i )
        
        
  # sort 
    tags.sort() 

    return (lyric_dict , tags)
    
def make_lrc_file ( original_file_path, edited_lyric,  time_tags ):
    "make the "
    if len(edited_lyric) == 0:
        return ""
    head_info = lrcfile_head_info ( original_file_path )
   
    # this is a dictionary.
    lrc_content = {}
  
    linsta_i = 0; 
    time_id = 0 
    for item in time_tags:
        linend_i = edited_lyric.find( '\n', linsta_i )
        if linend_i == -1:
            continue 
        lyric_line = edited_lyric[linsta_i:linend_i+1]
        # if has this key , add the time 
        if lrc_content.has_key( lyric_line ):
            lrc_content[lyric_line].append ( item[0])
        else :
            lrc_content[lyric_line] = [ item[0] ]
        linsta_i = linend_i + 1 
        time_id += 1 

    list_lrc_content = lrc_content.items()
    list_lrc_content.sort( lrc_dict_compare ) 

    str_lrc_content = ""
    for item in list_lrc_content:
        num_time_id = len(item[1])
        while num_time_id > 0:
            str_lrc_content += time_to_lrc ( item[1][num_time_id -1])
            num_time_id -= 1
        str_lrc_content += item[0]
      
    return head_info + str_lrc_content 
    # lrcfile = open(filepath, "w")
    # lrcfile.write( head_info )
    # lrcfile.write ( str_lrc_content )
    # lrcfile.close() 
       
def time_to_seconds(time):
    time = time[1:-1].replace(":", ".")
    t = time.split(".")
    return 60 * int(t[0]) + int(t[1])
    
def time_to_lrc( time):
    minute = time / 60
    second  = time % 60 
    return "[%d:%.2f]" %  (minute, second)  
    
def is_english(to_check_str):
    for ci in to_check_str:
        if ord( eval (repr(ci))) > 128:
            return False
        
    return True 
        

def filter_to_chinese (to_filter_str):
    # change to unicode 
    to_filter_str = to_filter_str.decode('utf-8')
    filtered_str = u''
    for uci in to_filter_str:
        if  0x4e00<=ord( eval (repr(uci)))<=0x9fa6:
            filtered_str += uci 
  
    return filtered_str.encode('utf-8') 

def lrc_dict_compare ( first, second ):
    """ the first and second is the tuple
        the format is :
        ( key, [time list])
    """
    return cmp( first[1][0], second[1][0] )
