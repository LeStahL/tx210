# tx210 - convert text to glsl source code - nofont variant. Simple
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

# parse command line
parser = argparse.ArgumentParser(description='Shader Text Generation Tool.')
#parser.add_argument('-f', '--fontfile', dest='fontfile')
parser.add_argument('-s', '--size', dest='size')
parser.add_argument('-o', '--output', dest='outfile')
parser.add_argument('-p', '--plot', dest='plot', action='store_true')
args, rest = parser.parse_known_args()

text = rest[0]
unit = float(args.size)/6.

# compute outlines
lin = []
quad = []
xpos = 0.
def rescale(lin0, quad0) :
    global lin, quad, xpos, unit
    lin0 = [ [ (xpos + lini[0]) * unit, lini[1] * unit ] for lini in lin0 ]
    lin += lin0
    quad0 = [ [ (xpos + quadi[0]) * unit, quadi[1] * unit ] for quadi in quad0 ]
    quad += quad0
    return 
for c in text :
    if c == 'a' :
        lin0 = [ [2.,0.], [2.,2.] ]
        quad0 = [ [1.,2.], [0.,2.], [0.,1.], [0.,1.], [0.,0.], [1.,0.], [1.,0.], [2.,0.], [2., 1.], [1.,2.], [2.,2.], [2.,1.] ]
        rescale(lin0, quad0)
        xpos += 3.
    elif c == 'A' :
        lin0 = [ [0.,0.], [0.,3.], [2.,0.], [2.,3.], [0.,2.], [2.,2.] ]
        quad0 = [ [2.,3.], [2.,4.], [1.,4.], [1.,4.], [0.,4.], [0.,3.] ]
        rescale(lin0, quad0)
        xpos += 3.
    elif c == 'b' :
        lin0 = [ [0.,0.], [0.,4.], [0.,0.], [1.,0.], [0.,2.], [1.,2.] ]
        quad0 = [ [1.,0.], [2.,0.], [2.,1.], [2.,1.], [2.,2.], [1.,2.] ]
        rescale(lin0, quad0)
        xpos += 3.
    elif c == 'B' :
        lin0 = [ [0.,0.], [0.,4.], [0.,0.], [1.,0.], [0.,2.], [1.,2.], [0.,4.], [1.,4.] ]
        quad0 = [ [1.,0.], [2.,0.], [2.,1.], [2.,1.], [2.,2.], [1.,2.], [1.,2.], [2.,2.], [2.,3.], [2.,3.], [2.,4.], [1.,4.] ]
        rescale(lin0, quad0)
        xpos += 3.
    elif c == 'c' :
        lin0 = [ [2.,2.], [1.,2.], [2.,0.], [1.,0.] ]
        quad0 = [ [1.,2.], [0.,2.], [0.,1.], [0.,1.], [0.,0.], [1.,0.] ]
        rescale(lin0, quad0)
        xpos += 3.
    elif c == 'C' :
        lin0 = [ [2.,0.], [1.,0.], [2.,4.], [1.,4.], [0.,1.], [0.,3.] ]
        quad0 = [ [1., 0.], [0.,0.], [0.,1.], [0.,3.], [0.,4.], [1.,4.] ]
        rescale(lin0, quad0)
        xpos += 3.
    elif c == 'd' :
        lin0 = [ [1.,2.], [2.,2.], [1.,0.], [2.,0.], [2.,0.], [2.,4.] ]
        quad0 = [ [1.,0.], [0.,0.], [0.,1.], [0.,1.], [0.,2.], [1.,2.] ]
        rescale(lin0, quad0)
        xpos += 3.
    elif c == 'D' :
        lin0 = [ [0.,0.], [0., 4.], [0., 4.], [1., 4.], [0., 0.], [1., 0.], [2., 1.], [2., 3.] ]
        quad0 = [ [1., 4.], [2., 4.], [2., 3.], [1., 0.], [2., 0.], [2., 1.] ]
        rescale(lin0, quad0)
        xpos += 3.
    elif c == 'e' :
        lin0 = [ [1.,0.], [2.,0.], [0., 1.], [2., 1.] ]
        quad0 = [ [2.,1.],[2.,2.],[1.,2.], [1.,2.], [0.,2.], [0.,1.],[0.,1.],[0.,0.],[1.,0.] ]
        rescale(lin0, quad0)
        xpos += 3.
    elif c == 'E' :
        lin0 = [ [0.,0.], [0.,4.], [0.,0.], [2.,0.], [0.,2.], [2.,2.], [0.,4.], [2.,4.] ]
        quad0 = []
        rescale(lin0, quad0)
        xpos += 3.
    elif c == 'f' :
        lin0 = [ [1.,1.],[1.,3.], [0.,2.], [2.,2.] ]
        quad0 = [ [0.,0.],[1.,0.],[1.,1.], [1.,3.], [1.,4.], [2.,4.] ]
        rescale(lin0, quad0)
        xpos += 3.
    elif c == 'F' :
        lin0 = [ [0.,0.], [0.,4.], [0.,4.], [2.,4.], [0.,2.], [2.,2.] ]
        quad0 = []
        rescale(lin0, quad0)
        xpos += 3.
    elif c == 'g' :
        lin0 = [ [2.,2.], [2.,-1.], [1.,-2.], [0.,-2.] ]
        quad0 = [ [2.,1.], [2.,2.], [1.,2.], [1.,2.], [0.,2.], [0.,1.], [0.,1.], [0.,0.], [1.,0.], [1.,0.], [2.,0.], [2.,1.], [2.,-1.], [2.,-2.], [1.,-2.] ]
        rescale(lin0, quad0)
        xpos += 3.
    elif c == 'G' :
        lin0 = [ [1.,2.], [2.,2.], [2.,2.], [2.,1.], [0.,1.], [0.,3.], [1.,4.], [2.,4.] ]
        quad0 = [ [0.,3.], [0.,4.], [1.,4.], [1.,0.], [0.,0.], [0.,1.], [1.,0.], [2.,0.], [2.,1.] ]
        rescale(lin0, quad0)
        xpos += 3.
    elif c == 'h' :
        lin0 = [ [0.,0.], [0.,4.], [2.,0.], [2.,1.], [1.,2.], [0.,2.] ]
        quad0 = [ [2.,1.], [2.,2.], [1.,2.] ]
        rescale(lin0, quad0)
        xpos += 3.
    elif c== 'H' :
        lin0 = [ [0.,0.], [0.,4.], [2.,0.], [2.,4.], [0.,2.], [2.,2.] ]
        quad0 = [] 
        rescale(lin0, quad0)
        xpos += 3.
    elif c == 'i' :
        lin0 = [ [0.,1.], [0.,2.], [0.,3.], [0.,3.] ]
        quad0 = [ [0.,1.], [0.,0.], [1.,0.] ]
        rescale(lin0, quad0)
        xpos += 2.
    elif c == 'I' :
        lin0 = [ [1.,0.], [1.,4.], [0., 0.], [2.,0.], [0.,4.], [2.,4.] ]
        quad0 = []
        rescale(lin0, quad0)
        xpos += 3.
    elif c == 'j' :
        lin0 = [ [1.,2.], [1.,-1.], [1.,3.], [1.,3.] ]
        quad0 = [ [1.,-1.], [1.,-2.], [0.,-2.] ]
        rescale(lin0, quad0)
        xpos += 2.
    elif c == 'J' :
        lin0 = [ [0.,4.], [1.,4.], [1.,4.], [1.,1.] ]
        quad0 = [ [1.,1.], [1.,0.], [0.,0.] ]
        rescale(lin0, quad0)
        xpos += 2.
    elif c == 'k' :
        lin0 = [ [0.,0.], [0.,4.], [0.,1.], [1.,1.] ]
        quad0 = [ [1.,1.],[2.,1.], [2.,2.], [1.,1.], [2.,1.], [2.,0.] ]
        rescale(lin0, quad0)
        xpos += 3.
    elif c == 'K' :
        lin0 = [ [0.,0.], [0.,4.], [0.,2.], [1.,2.], [2.,3.], [2.,4.], [2.,0.], [2.,1.] ]
        quad0 = [ [1.,2.],[2.,2.], [2.,3.], [1.,2.], [2.,2.], [2.,1.] ]
        rescale(lin0, quad0)
        xpos += 3.
    elif c == 'l' :
        lin0 = [ [0.,1.], [0.,4.] ]
        quad0 = [ [0.,1.], [0.,0.], [1.,0.] ]
        rescale(lin0, quad0)
        xpos += 2.
    elif c == 'L' :
        lin0 = [ [0.,0.],[0.,4.] ,[0.,0.],[2.,0.]]
        quad0 = []
        rescale(lin0, quad0)
        xpos += 3.
    elif c == 'm' :
        lin0 = [ [0.,0.], [0.,2.], [2.,0.], [2.,1.], [4.,0.], [4.,1.] ]
        quad0 = [ [0.,1.], [0.,2.], [1.,2.], [1.,2.], [2.,2.], [2.,1.], [2.,1.], [2.,2.], [3., 2.], [3.,2.], [4.,2.], [4.,1.] ]
        rescale(lin0, quad0)
        xpos += 5.
    elif c == 'M':
        lin0 = [ [0.,0.], [0.,4.], [2.,2.], [2.,3.], [4.,0.], [4.,4.], [0., 4.], [1.,4.], [3.,4.], [4.,4.] ]
        quad0 = [ [1.,4.], [2.,4.], [2.,3.], [2.,3.], [2.,4.], [3.,4.] ]
        rescale(lin0, quad0)
        xpos += 5.
    elif c == 'n' :
        lin0 = [ [0.,0.], [0., 2.], [2.,1.], [2.,0.] ]
        quad0 = [ [1.,2.], [2.,2.], [2.,1.], [0., 1.], [0.,2.], [1.,2.]]
        rescale(lin0, quad0)
        xpos += 3.
    elif c == 'N' :
        lin0 = [ [0.,0.], [0.,4.], [1.,3.], [1.,1.], [2.,0.], [2.,4.] ]
        quad0 = [ [0.,4.], [1.,4.], [1.,3.], [1.,1.], [1.,0.], [2.,0.] ]
        rescale(lin0, quad0)
        xpos += 3.
    elif c == 'o' :
        lin0 = []
        quad0 = [ [1.,0.],[0.,0.],[0.,1.], [0.,1.],[0.,2.],[1.,2.], [1.,2.],[2.,2.],[2.,1.], [2.,1.],[2.,0.],[1.,0.] ]
        rescale(lin0, quad0)
        xpos += 3.
    elif c == 'O' :
        lin0 = [ [0.,1.], [0.,3.], [2.,1.], [2.,3.] ]
        quad0 = [ [0.,1.], [0.,0.], [1.,0.], [1.,0.], [2.,0.], [2.,1.], [2.,3.], [2.,4.], [1.,4.], [1.,4.],[0.,4.],[0.,3.] ]
        rescale(lin0, quad0)
        xpos += 3.
    elif c == 'p' :
        lin0 = [ [0.,-2.], [0.,2.], [0.,2.], [1.,2.], [0.,0.], [1.,0.] ]
        quad0 = [ [1.,0.], [2.,0.], [2.,1.], [2.,1.], [2.,2.], [1.,2.] ]
        rescale(lin0, quad0)
        xpos += 3.
    elif c == 'P' :
        lin0 = [ [0.,0.], [0.,4.], [0.,4.], [1.,4.], [0.,2.], [1.,2.] ]
        quad0 = [ [1.,2.], [2.,2.], [2.,3.], [2.,3.],[2.,4.],[1.,4.] ]
        rescale(lin0, quad0)
        xpos += 3.
    elif c == 'q' :
        lin0 = [ [2.,2.], [2.,-2.], [2.,2.],[1.,2.] ]
        quad0 = [ [2.,1.],[2.,0.],[1.,0.],[1.,0.],[0.,0.],[0.,1.],[0.,1.],[0.,2.],[1.,2.] ]
        rescale(lin0, quad0)
        xpos += 3.
    elif c == 'Q' :
        lin0 = [ [0.,1.], [0.,3.], [2.,1.], [2.,3.] ]
        quad0 = [ [0.,1.],[0.,0.],[1.,0.], [1.,0.], [2.,0.],[2.,1.], [2.,3.],[2.,4.],[1.,4.], [1.,4.], [0.,4.], [0.,3.], [1.,1.],[1.,0.],[2.,0.] ]
        rescale(lin0, quad0)
        xpos += 3.
    elif c == 'r' :
        lin0 = [ [0.,0.], [0.,2.] ]
        quad0 = [ [0.,1.], [0.,2.], [1.,2.] ]
        rescale(lin0, quad0) 
        xpos += 2.
    elif c == 'R' :
        lin0 = [ [0.,0.], [0.,4.], [0.,4.], [1.,4.], [0.,2.], [1.,2.], [2.,1.], [2.,0.] ]
        quad0 = [ [1.,4.], [2.,4.], [2.,3.], [2.,3.], [2.,2.], [1.,2.], [1.,2.], [2.,2.], [2.,1.] ]
        rescale(lin0, quad0)
        xpos += 3.
    elif c == 's' :
        lin0 = [ [0.,0.], [1.,0.], [1.,2.], [2.,2.] ]
        quad0 = [ [1.,0.], [3.,.5], [1.,1.], [1.,1.], [-1.,1.5], [1.,2.] ]
        rescale(lin0, quad0)
        xpos += 3.
    ##elif c == 'S' :
        #lin0 = [ [0.,0.], [1.,0.]
    xpos += .25

# plot outlines
plt.rc('axes', prop_cycle=(cycler.cycler('color', ['r', 'g', 'b', 'c', 'm', 'y', 'k'])))
fig = plt.figure(figsize=(16,4))
plt.axes().set_aspect('equal', 'datalim')
plt.grid(which='major', alpha=unit)

for i in range(len(lin)/2) :
    a = lin[2*i]
    b = lin[2*i+1]

    xp = [ (1.-t)*a[0] + t*b[0] for t in np.arange(0.,1.01, 1./100.)]
    yp = [ (1.-t)*a[1] + t*b[1] for t in np.arange(0.,1.01, 1./100.)]

    plt.plot(xp, yp, 'o', markersize=.2)
    
for i in range(len(quad)/3) :
    a = quad[3*i]
    b = quad[3*i+1]
    c = quad[3*i+2]
    
    xp = [ pow(1.-t,2.)*a[0]+2.*(1.-t)*t*b[0]+t*t*c[0] for t in np.arange(0.,1.01, 1./100.)]
    yp = [ pow(1.-t,2.)*a[1]+2.*(1.-t)*t*b[1]+t*t*c[1] for t in np.arange(0.,1.01, 1./100.)]
    
    plt.plot(xp, yp, 'o', markersize=.2)
    
#print lin, quad
    
plt.show()
