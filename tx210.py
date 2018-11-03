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

import argparse
import freetype
import numpy as np
import struct
import sys

# CMD arg parser
parser = argparse.ArgumentParser(description='Memory Texture Text Generation Tool by Team210.')
parser.add_argument('-f', '--fontfile', dest='fontfile')
parser.add_argument('-o', '--output', dest='outfile')
args, rest = parser.parse_known_args()

# Notify and quit
def close(str):
    print(str)
    exit()

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

# Scale font to fit into unsigned short range
loadscale = int(.6666*65535)
font.set_char_size(loadscale)

# Specify format
endian = '<' # little endian
datatype = 'H' # unsigned short
fmt = endian + datatype

# Arrays for the data
x_all = [] # all glyph x values
y_all = [] # all glyph y values
tags_all = [] # all glyph control data
contours_all = [] # all glyph contour specifications
deltax_all = [] # Short range offset to actual glyph data 
deltay_all = [] # Short range offset to actual glyph data
offsets = [] # Keep track of the glyph block length for building the index
offset = 1+2*len(text) # Offset in texture

text = sorted(text)

# Get glyph outlines and move them above the zero threshold to fit into unsigned short range
for char in text:
    print("Processing char: " + char)

    # Load glyph outline
    font.load_char(char)
    glyph = font.glyph
    outline = glyph.outline
    
    # Get outline points
    points = np.array(outline.points, dtype=[('x',float), ('y',float)]) 
    x = [int(np.floor(xi)) for xi in list(points['x']) ]
    y = [int(np.floor(xi)) for xi in list(points['y']) ]
    
    # Determination how far glyph is out of bounds
    xlower = 65535.
    xupper = -65535.
    ylower = 65535.
    yupper = -65535.
    
    if x != []:
        xlower = min(xlower, min(x))
        xupper = max(xupper, max(x))
        print("xlower",xlower,"xupper",xupper)
    else:
        xlower = 0
        xupper = 0
    if y != []:
        ylower = min(ylower, min(y))
        yupper = max(yupper, max(y))
        print("ylower",ylower,"yupper",yupper)
    else:
        ylower = 0
        yupper = 0
    
    # Save the offsets.
    deltax_all +=  [ int(xlower) ] 
    deltay_all +=  [ int(ylower) ] 
    
    # Modify the value ranges.
    x = [ xi - xlower for xi in x ]
    y = [ yi - ylower for yi in y ]
    x_all += [ x ]
    y_all += [ y ]
    
    # Get remaining data (tags, contours)
    tags_all += [ outline.tags ]
    contours_all += [ outline.contours ]
    
    # fill in the section lengths
    # that is number of x values, number of y values, number of tags, number of contours,
    # offset onto (x,y) for short range
    offsets += [offset]
    offset += (8 + len(x) + len(y) + len(outline.tags) + len(outline.contours))
    print("lens are:", len(x), len(y), len(outline.tags), len(outline.contours))
    print("offset is:", offset)

print("Finished collecting necessary data.")

# Assemble texture.
# Length of glyph index
texture = struct.pack(fmt, len(text))
# Glyph index
for i in range(len(text)):
    # Pack ascii value of char
    texture += struct.pack(fmt, ord(text[i]))
    # Pack offset of glyph data in texture (in number of shorts)
    texture += struct.pack(fmt, offsets[i])
    print("Glyph '"+text[i]+"' with ordinal "+str(ord(text[i]))+" is at index ",offsets[i]," (byte ",2*offsets[i],", pixel ",offsets[i]/2.,").", "vals: ", int(deltax_all[i]<0), abs(deltax_all[i]), int(deltay_all[i]<0), abs(deltay_all[i]), len(x_all[i]))
# Glyph data
for i in range(len(text)):
    # Pack short range offset
    texture += struct.pack(fmt, int(deltax_all[i]<0)) # Need to pack sign separately!
    texture += struct.pack(fmt, abs(deltax_all[i]))
    texture += struct.pack(fmt, int(deltay_all[i]<0)) # Need to pack sign separately!
    texture += struct.pack(fmt, abs(deltay_all[i]))
    # Pack number of x values
    texture += struct.pack(fmt, len(x_all[i]))
    # Pack x values
    for xi in x_all[i]:
        texture += struct.pack(fmt, xi)
    # Pack number of y values
    texture += struct.pack(fmt, len(y_all[i]))
    # Pack y values
    for yi in y_all[i]:
        texture += struct.pack(fmt, yi)
    # Pack number of tags
    texture += struct.pack(fmt, len(tags_all[i]))
    # Pack tags
    for ti in tags_all[i]:
        texture += struct.pack(fmt, ti)
    # Pack number of contours
    texture += struct.pack(fmt, len(contours_all[i]))
    # Pack contours
    for ci in contours_all[i]:
        texture += struct.pack(fmt, ci)

print("Finished packing texture.")

# Write output to c header file or stdout
# Fill last 4-byte-block with zero
length = int(len(texture)) # in bytes
while ((length % 4) != 0):
    texture += bytes(10)
    length += 1
print("Packed font is "+str(length)+" bytes.")

# Get necessary texture size from data
texs = str(int(np.ceil(np.sqrt(float(length)/4.))))
print("Required texture size: " + texs)

# Output header file
array = []
for i in range(int(np.ceil(length/2))):
    array += [ struct.unpack(fmt, texture[2*i:2*i+2]) ][0] 
text = "//Generated by tx210 (c) 2018 NR4/Team210\n\n#ifndef FONT_H\n#define FONT_H\n\n"
text += "const unsigned short font_texture[{:d}]".format(int(np.ceil(length/2)))+" = {"
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
