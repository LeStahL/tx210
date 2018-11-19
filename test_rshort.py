import struct
import numpy
import matplotlib.pyplot as plt

def rshort(v):
    return float(ord(v[0])) + 256.*float(ord(v[1]))
    #return (255.*float(ord(v[0])) + (65535.-255.)*float(ord(v[1])))/255.

x = []
y = []
for i in range(65536):
    data = struct.pack('<H', i);
    v = struct.unpack('cc', data);
    x += [i]
    y += [ rshort(v) - float(i) ]
    
fig = plt.figure()
plt.plot(x,y,'r-')
plt.show()

print(min(y), max(y))

input('Press any key to quit.')
