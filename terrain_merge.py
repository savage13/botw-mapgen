#!/usr/bin/env python3

#import matplotlib.pyplot as plt
import numpy as np
import glob
import struct
import os
import sys
from osgeo import gdal
gdal.UseExceptions()

files = glob.glob("terrain/5400*.hght/*.hght")

def zorder( z ) :
    n = 0
    x,y = 0,0
    #print("zorder {:08b}".format(z))
    while n < 4:
        #print("zorder {:3} {:08b}".format(n,z))
        if True:
            mask = 0x03 << (2*n)
            bit = (z & mask) >> (2*n)
            xi = bit & 0x01
            yi = (bit & 0x02) >> 1
            if n == 0:
                x = xi
                y = yi
            else:
                x = x + xi * (2**n)
                y = y + yi * (2**n)
            #print("zorder {:3} {:08b} {:02b} {:3} {:3} {:3} {:3}".format(n,z,bit,xi,yi,x,y))
        n += 1
    return (x,y)

zs = [
    0b00000000,0b00000001,0b00000010,0b00000011,
    0b00000100,0b00000101,0b00000110,0b00000111,
    0b00001000,0b00001001,0b00001010,0b00001011,
    0b00001100,0b00001101,0b00001110,0b00001111,
    0b00010000,
    0b00010001,
    0b00010010,
    0b00010011,
    0b00101100,
    0b10000100,
]

for z in zs[-2:]:
    #print("{:08b}".format(z))
    x,y = zorder(z)
    #print("==> {:08b} {:3} {:3} ".format(z,x,y))

#sys.exit(0)
nz = np.zeros((16,16))
n = 256 * 256
z = np.zeros((256*16, 256*16))
for file in files:
    zid0 = os.path.splitext(os.path.basename(file))[0][-2:]
    zid1 = int(zid0, 16 )
    x,y = zorder( zid1 )
    print("{:4} {:4} {:2} {:2} {:08b} {}".format(zid0, zid1, x, y, zid1, file))
    #continue
    with open(file, 'rb') as f:
        data = f.read()
        v = struct.unpack('<65536H', data)
        v = np.reshape(v, (256,256))
        #plt.pcolor(v, cmap='gray')
        #plt.show()
        nz[x,y] += 1
        #x = x-2
        #y = y-2
        x0,y0 = x*256,y*256
        x1,y1 = x0+256,y0+256
        z[y0:y1, x0:x1] = v

#print(sum(nz))
# if False:
#     plt.pcolor(z[512:-512:5,512:-512:5],cmap='gray')
#     #plt.pcolor(nz)
#     plt.gca().invert_yaxis()
#     plt.colorbar()
#     plt.show()

dst_filename = 'heightmap.tiff'
format = 'GTiff'
driver = gdal.GetDriverByName(format)
cols,rows = z.shape
dst_ds = driver.Create(dst_filename, cols, rows, 1, gdal.GDT_UInt16)
dst_ds.GetRasterBand(1).WriteArray(z)
dst_ds = None
