# tx210 - convert text to c texture content
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
# 1 byte: number of contained glyphs n
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

# globals
size = 1

# CMD arg parser
parser = argparse.ArgumentParser(description='Memory Texture Text Generation Tool by Team210.')
parser.add_argument('-f', '--fontfile', dest='fontfile')
parser.add_argument('-o', '--output', dest='outfile')
args, rest = parser.parse_known_args()

# Notify and quit
def close(str):
    print(str)
    exit()

text = ""
if rest != []:
    text = rest[0]
write_file = True

# Check args for consistency
if text == "":
    print("No text specified. Packing standard chars:")
    text = ''.join([ chr(i) for i in range(32, 127) ])
    print("'"+text+"'")
if args.fontfile == None:
    close("No font file specified. Doing nothing.")
if args.outfile == None:
    print("No output file selected. Writing to stdout instead.")
    write_file = False    

# Open font file
font = freetype.Face(args.fontfile)

# Load them big, rescale them to float
loadscale = 1000000
font.set_char_size(loadscale)

# Pack number of chars; max is full ascii
texture = struct.pack('B', len(text))

# Process text
for char in text:
    print("Processing char: "+char)
    
    # Load glyph outline
    font.load_char(char)
    glyph = font.glyph
    outline = glyph.outline
    
    # Get outline points
    points = np.array(outline.points, dtype=[('x',float), ('y',float)]) 
    x = list(points['x']/float(loadscale))
    y = list(points['y']/float(loadscale))
    
    # pack glyph data
    n = len(x)
    ncont = len(outline.contours)

    texture += struct.pack('B', ord(char))
    texture += struct.pack('H', n)
    fmt = '{:d}e'.format(n)
    if n != 0:
        texture += struct.pack(fmt, *x)
        texture += struct.pack(fmt, *y)
        texture += struct.pack('{:d}B'.format(n), *outline.tags)
    texture += struct.pack('B', ncont)
    if ncont != 0:
        texture += struct.pack('{:d}H'.format(ncont), *outline.contours)
    
    size += 4 + 5*n + 2*ncont

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
