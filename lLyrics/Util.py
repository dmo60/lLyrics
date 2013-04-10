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



# def parse_lrc(data):
#     tag_regex = r"(\[\d+\:\d+\.*\d*])"   # [xx:xx] or [xx:xx.xx]
#     match = re.search(tag_regex, data)
    
#     # no tags
#     if match is None:
#         return (data, None)
    
#    # data = data[match.start():]
#    # re.sub(r'\n\r$', r'\n$', data )
#    # print data 
#     splitted = re.split(tag_regex, data)[1:]
    
#     tags = []
#     lyrics = ''
#     for i in range(len(splitted)):
#         if i % 2 == 0:
#             # tag
#             tags.append((time_to_seconds(splitted[i]), splitted[i+1]))
#         else:
#             # lyrics
#             lyrics += splitted[i]
    
#     return (lyrics, tags)
    
    
def parse_lrc(data):
    tag_regex = r"(\[\d+\:\d+\.*\d*\])"   # [xx:xx] or [xx:xx.xx]
    lyric_start_tag = re.search(tag_regex, data)
    
    # no tags
    if lyric_start_tag is None:
        return (data, None)
   
    tags = []
    linsta_i  = lyric_start_tag.start()
    linend_i  = data.find('\n', linsta_i )
    while linend_i != -1:
        # song 
        song_i = data.rfind(']', linsta_i, linend_i)
        song_i += 1
        if song_i != 0 and song_i < linend_i and data[song_i] != '\r':
            # no song content and space line situation remove 
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
            
                tags.append((time_to_seconds( data[timsta_i:timend_i+1]), data[song_i:linend_i]) )
               
                timsta_i = timend_i+1
        
        
        
        linsta_i = linend_i + 1 
        linend_i  = data.find('\n', linsta_i )
        
        
  # sort 
    tags.sort() 
    lyrics = ''
    for _,song in tags:
        lyrics += song + '\n'
    return (lyrics, tags)
    
    
def time_to_seconds(time):
    time = time[1:-1].replace(":", ".")
    t = time.split(".")
    return 60 * int(t[0]) + int(t[1])
    
    
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
