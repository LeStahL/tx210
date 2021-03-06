# gencomp - convert text to c texture content
# Copyright (C) 2017/2018 Alexander Kraus <nr4@z10.info>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# texture data format: 
# 1 byte, char: number of contained glyphs n
# 2 byte, short: size of the glyphs
# 
# TODO: add a separate glyph index here to speed up letter rendering
# for each contained glyph:
#     1 byte, char value: character index in ascii
#     2 bytes, short value: glyph point data length m
#     2*m bytes, float16 values: glyph x data
#     2*m bytes, float16 values: glyph y data
#     m bytes, char values: outline tags
#     1 byte, char value: number of contours o in glyph outline
#     2*o bytes, short values: contour end points
# 1 byte: 0
#
# this means, the length of the texture array is
# (2 + n * (4 + 5*m + 2*o))/2
# 

import argparse
import freetype
import numpy as np
import struct
import sys

# Notify and quit
def close(str):
    print(str)
    exit()

# CMD arg parser
parser = argparse.ArgumentParser(description='Memory Texture Text Generation Tool by Team210.')
parser.add_argument('-f', '--fontfile', dest='fontfile')
parser.add_argument('-o', '--output', dest='outfile')
args, rest = parser.parse_known_args()

# Check args for consistency
text = ""
if rest != []:
    text = list(set(rest[0]))
    print("Unique character list is:", text)
else:
    text = [ chr(i) for i in range(32,127) ]
    print("No text specified. Taking standard character list:", text)
write_file = True
if args.fontfile == None:
    close("No font file specified. Doing nothing.")
if args.outfile == None:
    print("No output file selected. Writing to stdout instead.")
    write_file = False

# Open font file
font = freetype.Face(args.fontfile)

# Specify format
ftype = '>h'

# Pack the texture
def pack_texture(size):
    global font, text
    # Process text
    data = []
    lengths = []
    for char in text:
        print("Processing char: "+char)
        
        # Load glyph outline
        font.load_char(char)
        glyph = font.glyph
        outline = glyph.outline
        
        # Get outline points
        points = np.array(outline.points, dtype=[('x',float), ('y',float)]) 
        x = list(points['x'])
        y = list(points['y'])
        
        # pack glyph data
        n = len(x)
        ncont = len(outline.contours)

        glyph_data = struct.pack('H', n)
        fmt = '{:d}e'.format(n)
        if n != 0:
            glyph_data += struct.pack(fmt, *x)
            glyph_data += struct.pack(fmt, *y)
            glyph_data += struct.pack('{:d}B'.format(n), *outline.tags)
        glyph_data += struct.pack('B', ncont)
        if ncont != 0:
            glyph_data += struct.pack('{:d}H'.format(ncont), *outline.contours)
        
        data += [ glyph_data ]
        lengths += [ len(glyph_data) ]
    
    # 1 Byte, char: Number of contained glyphs
    texture = struct.pack('B', len(text))
    
    # Pack index
    offset = 1+3*len(text)
    print("Index:")
    for i in range(len(text)):
    texture += struct.pack('B', ord(text[i]))
    texture += struct.pack('H', offset)
    offset += lengths[i]
    print("> '"+text[i]+"' - "+str(lengths[i])+" bytes at "+str(offset)) 
    
    # Pack data
    for i in range(len(text)):
        texture += data[i]
    return texture

# Function to minimize
def f(size):
    font.set_char_size(size)
    texture = pack_texture(size)

# Pack glyphs for specified alphabet into binary sequence
texture = pack_texture(font, text, size)

length = int(size/2)
texs = str(int(np.ceil(np.sqrt(float(size)/4.))))

print("packed font is "+str(size)+" bytes.")
print("Required texture size:" + texs)

array = struct.unpack('{:d}h'.format(length), texture)
text = "//Generated by tx210 (c) 2018 NR4/Team210\n\n#ifndef FONT_H\n#define FONT_H\n\n"
text += "const short font_texture[{:d}]".format(length)+" = {"
for val in array[:-1]:
    text += str(val) + ',' 
text += str(array[-1]) + '};\n'
text += "const int font_texture_size = " + str(texs) + ";"
text += '\n#endif\n'

if write_file:
    with open(args.outfile, "wt") as f:
        f.write(text)
        f.close()
else:
    print(text)
