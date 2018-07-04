# tx210 - convert text to glsl source code  
#
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
#/

from Tkinter import Tk, Label, Button
import argparse
import freetype
import numpy as np
import matplotlib.pyplot as plt
import cycler
from math import factorial

def bezier(pts, t) :
    order = len(pts)
    ret = [0., 0.]
    for i in range(order) :
        scale = factorial(order-1)/factorial(i)/factorial(order-i-1)*pow(1.-t,order-i-1)*pow(t, i)
        for j in range(2) :
            ret[j] +=  scale*pts[i][j]
    return ret

plt.rc('axes', prop_cycle=(cycler.cycler('color', ['r', 'g', 'b', 'y'])))

parser = argparse.ArgumentParser(description='Shader Text Generation Tool.')
parser.add_argument('-f', '--fontfile', dest='fontfile')
parser.add_argument('-s', '--size', dest='size')
parser.add_argument('-o', '--output', dest='outfile')
args, rest = parser.parse_known_args()

text = rest[0]
fig = plt.figure(figsize=(16,4))

font = freetype.Face(args.fontfile)
font.set_char_size(1000)
xpos = 0

size = .05;
if args.size != None :
    size = float(args.size)

otext = "float d=1.;\n"
otext2 = "const vec2 quad["
quad = []
lin = []
for char in text :
    otext += "//"+char+"\n"
    font.load_char(char)
    glyph = font.glyph
    outline = glyph.outline
    points = np.array(outline.points, dtype=[('x',float), ('y',float)]) 
    x, y = points['x'], points['y']
    
    for i in range(len(x)) :
        x[i] = x[i]/1000.*size
        y[i] = y[i]/1000.*size
    
    w = 300./1000.*size
    if len(x) > 0 :
        w = abs(x.max() - x.min())*1.1
    
    for i in range(len(x)) :
        x[i] += xpos
    
    for ic in range(len(outline.contours)) :
        c0 = 0
        c1 = 0
        if(ic > 0) : 
            c0 = outline.contours[ic-1]+1
        if ic == len(outline.contours)-1 : 
            c1 = len(x)
        else : 
            c1 = outline.contours[ic]+1
        
        xa = x[c0:c1]
        ya = y[c0:c1]
        
        tx = outline.tags[c0:c1]
        
        segments = []
        stack = []
        for i in range(len(tx)) :
            tag = tx[i]
            stack += [ tag ]
            
            if tag : 
                segments += [ stack ]
                stack = [ tag ]
        stack += [ tx[0] ]
        segments += [ stack ]
        xp = []
        yp = []
        
        j = 0
        for i in range(len(segments)) :
            segment = segments[i]
            data = []
            if len(segment) == 2 :
                p0 = [xa[j], ya[j]]
                j = (j+1)%len(xa)
                p1 = [xa[j], ya[j]]
                xp += [ (1.-t)*p0[0]+t*p1[0] for t in np.arange(0., 1., 1./100.) ]
                yp += [ (1.-t)*p0[1]+t*p1[1] for t in np.arange(0., 1., 1./100.) ]
                otext += "d = min(d, dsg(vec2("+"%.3f" %p0[0]+","+"%.3f" %p0[1]+"), vec2("+"%.3f" %p1[0]+","+"%.3f" %p1[1]+"), uv));\n"
                lin += [ p0, p1 ]
            elif len(segment) > 2:
                p = []
                for k in range(len(segment)-1) :
                    p += [ [xa[j], ya[j]] ]
                    j = (j+1)%len(xa)
                p += [ [xa[j], ya[j]] ]
                
                pf = []
                for k in range(1, len(segment)-1) :
                    pf += [ [ .5*(p[k][0]+p[k+1][0]), .5*(p[k][1]+p[k+1][1]) ] ]
                
                otext += "d = min(d, dsp(vec2("+"%.3f" %p[0][0]+","+"%.3f" %p[0][1]+"), vec2("+"%.3f" %p[1][0]+","+"%.3f" %p[1][1]+"), vec2("+"%.3f" %pf[0][0]+","+"%.3f" %pf[0][1]+"), uv));\n"
                xp += [ pow(1.-t,2.)*p[0][0]+2.*(1.-t)*t*p[1][0]+t*t*pf[0][0] for t in np.arange(0., 1., 1./100.) ]
                yp += [ pow(1.-t,2.)*p[0][1]+2.*(1.-t)*t*p[1][1]+t*t*pf[0][1] for t in np.arange(0., 1., 1./100.) ]
                quad += [ p[0], p[1], pf[0] ]
                
                for k in range(1, len(segment)-2) :
                    xp += [ pow(1.-t,2.)*pf[k-1][0]+2.*(1.-t)*t*p[k+1][0]+t*t*pf[k][0] for t in np.arange(0., 1., 1./100.) ]
                    yp += [ pow(1.-t,2.)*pf[k-1][1]+2.*(1.-t)*t*p[k+1][1]+t*t*pf[k][1] for t in np.arange(0., 1., 1./100.) ]
                    otext += "d = min(d, dsp(vec2("+"%.3f" %pf[k-1][0]+","+"%.3f" %pf[k-1][1]+"), vec2("+"%.3f" %p[k+1][0]+","+"%.3f" %p[k+1][1]+"), vec2("+"%.3f" %pf[k][0]+","+"%.3f" %pf[k][1]+"), uv));\n"
                    quad += [ pf[k-1], p[k+1], pf[k] ]
                xp += [ pow(1.-t,2.)*pf[-1][0]+2.*(1.-t)*t*p[-2][0]+t*t*p[-1][0] for t in np.arange(0., 1., 1./100.) ]
                yp += [ pow(1.-t,2.)*pf[-1][1]+2.*(1.-t)*t*p[-2][1]+t*t*p[-1][1] for t in np.arange(0., 1., 1./100.) ]
                otext += "d = min(d, dsp(vec2("+"%.3f" %pf[-1][0]+","+"%.3f" %pf[-1][1]+"), vec2("+"%.3f" %p[-2][0]+","+"%.3f" %p[-2][1]+"), vec2("+"%.3f" %p[-1][0]+","+"%.3f" %p[-1][1]+"), uv));\n"
                quad += [ pf[-1], p[-2], p[-1] ]
        plt.plot(xp, yp, 'o')
    xpos += w
fig.savefig('text.png', width=2000.)

otext2 += str(len(quad)) + "] = vec2[" + str(len(quad)) + "]("
for i in range(len(quad)) :
    if i!=0 :
        otext2 += ','
    otext2 += "vec2(%.3f"%quad[i][0] + ",%.3f)" % quad[i][1]
otext2 += "),\nlin[" + str(len(lin)) + "] = vec2[" + str(len(lin)) + "]("
for i in range(len(lin)) :
    if i!=0 :
        otext2 += ','
    otext2 += "vec2(%.3f"%lin[i][0] + ",%.3f)" % lin[i][1]
otext2 += ");\nfloat d = 1.;\nfor(int i=0; i<" + str(len(quad)/3) + "; ++i) d=min(d,dsp(quad[3*i], quad[3*i+1], quad[3*i+2], uv));\nfor(int i=0; i<" + str(len(lin)/2) + "; ++i) d=min(d,dsg(lin[2*i], lin[2*i+1], uv));\n"

if args.outfile == None :
    print otext
    print otext2
else :
    with open(args.outfile, "wt") as f:
        f.write(otext)
        f.close()
    with open(args.outfile + ".arr", "wt") as f:
        f.write(otext2)
        f.close()
