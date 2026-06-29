#!/usr/bin/env python3

import os
import glob
import struct
import numpy as np
from PIL import Image

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


def even_bits(x):
    x = ((x & 0x44444444) >> 1) | ((x & 0x11111111) >> 0);
    # x = 0b ..ab ..cd ..ef ..gh ..ij ..kl ..mn ..op

    x = ((x & 0x30303030) >> 2) | ((x & 0x03030303) >> 0);
    # x = 0b .... abcd .... efgh .... ijkl .... mnop

    x = ((x & 0x0F000F00) >> 4) | ((x & 0x000F000F) >> 0);
    # x = 0b .... .... abcd efgh .... .... ijkl mnop

    x = ((x & 0x00FF0000) >> 8) | ((x & 0x000000FF) >> 0);
    # x = 0b .... .... .... .... abcd efgh ijkl mnop
    return x

def terrain_merge(verbose = False):
    files = glob.glob("terrain/5400*.hght/*.hght")
    nz = np.zeros((16,16))
    n = 256 * 256
    z = np.zeros((256*16, 256*16))
    for file in files:
        zid0 = os.path.splitext(os.path.basename(file))[0][-2:]
        zid1 = int(zid0, 16 )
        x,y = zorder( zid1 )
        if verbose:
            print("{:4} {:4} {:2} {:2} {:08b} {}".format(zid0, zid1, x, y, zid1, file))
        with open(file, 'rb') as f:
            data = f.read()
            v = struct.unpack('<65536H', data)
            v = np.reshape(v, (256,256))
            nz[x,y] += 1
            x0,y0 = x*256,y*256
            x1,y1 = x0+256,y0+256
            z[y0:y1, x0:x1] = v
    return z

def heightmap_water_all(verbose = False):
    SCALE = 4
    W,H = 0x40 * 6 * 2 * SCALE, 0x40 * 6 * 2 * SCALE
    img1 = np.zeros((H,W))  # Material
    imgy = np.zeros((H,W))  # Water level
    for folder, _, files in os.walk('terrain_water'):
        if folder == 'terrain_water':
            continue
        for file in files:
            if file == '.gitignore':
                continue
            tile = int(file[-13:-11],0x10)%4
            k = int(file[-13:-11], 0x10)
            x, y = 0, 0

            xi = even_bits(k)
            yi = even_bits(k >> 1)

            xi -= 2
            yi -= 2

            xi *= 0x40 * SCALE
            yi *= 0x40 * SCALE

            f = open(folder+'/'+file, 'rb')
            # print(xi, xi + 0x40 * SCALE, yi, yi + 0x40*SCALE)
            for y in range(yi, yi + 0x40 * SCALE, SCALE):
                for x in range(xi, xi + 0x40 * SCALE, SCALE):
                    height = struct.unpack("<H", f.read(2))[0]
                    x_flow = 2 * (int.from_bytes(f.read(2),'little') / 0xffff) - 1
                    z_flow = 2 * (int.from_bytes(f.read(2),'little') / 0xffff) - 1
                    cksum_v = struct.unpack(">B", f.read(1))[0]
                    material = int.from_bytes(f.read(1),'little')

                    # Add 1 to material to identify non-set materials
                    img1[y:y+SCALE, x:x+SCALE] = material + 1
                    imgy[y:y+SCALE, x:x+SCALE] = height
            f.close()
        #
    return img1, imgy

MAX_UINT16 = 2**16

topo = terrain_merge()
topo = 800 * (topo / MAX_UINT16)

material, water = heightmap_water_all()
water = 800 * (water / MAX_UINT16)

print("topo    ", topo.shape, np.min(topo), np.max(topo))
print('material', material.shape, np.min(material), np.max(material))
print('water   ', water.shape, np.min(water), np.max(water))

# Pad from 3072 to 4096; add 512 to each side
material = np.pad(material, ((512,512), (512,512)), 'constant', constant_values = 0)
water = np.pad(water, ((512,512), (512,512)), 'constant', constant_values = 0)

print('material', material.shape, np.min(material), np.max(material))
print('water   ', water.shape, np.min(water), np.max(water))

negy = topo - water

materials = [ 'notset',
    'water', 'hotwater', 'poison', 'lava', 'coldwater', 'bog_mud', 'clearwater', 'seawater',
]
def reds(y):
    return [ np.clip(128 +  y*(255+128), a_min=0,a_max=255), 0 + y * 245, 0 + y * 245 ]
def blues(y):
    return [ 8 + y * (255-8), 48 + y * (255-48), np.clip(100 +  y*(255+100), a_min=0,a_max=255) ]
def greens(y):
    return [ 0 + y * 245, np.clip(128 +  y*(255+128), a_min=0,a_max=255), 0 + y * 245 ]
def topocolor(y):
    return [
        41 + y * (201-41),
        24 + y * (196-24),
        np.clip(-25.5 + y * (181-(-25.5)), a_min=0, a_max=255),
    ]

colormap = {
    'water': { 'cmap': blues, 'vmax': 6 },
    'hotwater': {'cmap': blues, 'vmax': 3 },
    'poison': {'cmap':greens, 'vmax': 6 },
    'lava': {'cmap':reds, 'vmax': 6 },
    'coldwater': {'cmap':blues, 'vmax': 6 },
    'bog_mud': {'cmap':greens, 'vmax': 6 },
    'clearwater': {'cmap':blues, 'vmax': 6 },
    'seawater': {'cmap':blues, 'vmax': 6 },
}

ny,nx = topo.shape


topo_img = np.zeros((ny,ny,4))

r,g,b = topocolor(topo/800)
topo_img[:,:,0] = r
topo_img[:,:,1] = g
topo_img[:,:,2] = b
topo_img[:,:,3] = 255

for i in range(1,8+1):
    # Find indicies where material matches and water is above topography
    idx = (material == i) & (negy <= 0)
    Y = np.ones(np.shape(topo))
    Y[idx] = negy[idx]

    rgba = np.zeros((ny,nx,4))

    cmap = colormap[materials[i]]['cmap']
    vmax = colormap[materials[i]]['vmax']

    yscale = -negy[idx] / vmax
    yscale = np.clip(yscale, a_min=0, a_max=1)
    r,g,b = cmap( 1-yscale )

    rgba[:,:,0] = 0
    rgba[idx,0] = r
    rgba[idx,1] = g
    rgba[idx,2] = b
    rgba[idx,3] = 255

    #im = Image.fromarray(rgba.astype('uint8'), 'RGBA')
    #im.save(f"{materials[i]}.png")

    topo_img[idx,0] = r
    topo_img[idx,1] = g
    topo_img[idx,2] = b

im = Image.fromarray(topo_img.astype('uint8'), 'RGBA')
im.save(f"topo.png")

