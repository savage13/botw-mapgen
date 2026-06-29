#!/usr/bin/env python3

from PIL import Image, ImageDraw, ImageFilter, ImageFont
import numpy as np
import sys
import os
import math
import struct

from osgeo import gdal
gdal.UseExceptions()

#import json

#data = json.load(open('data.js','r'))

#topo = Image.open('heightmap_full.png').convert('RGBA')
#print(topo.mode)

SCALE = 4
W,H = 0x40 * 6 * 2 * SCALE, 0x40 * 6 * 2 * SCALE
print(W,H,0x40)

img = Image.new("RGBA", (H,W ))
img1 = np.zeros((H,W), dtype=np.uint8)
imgy = np.zeros((H,W), dtype=np.uint16)
imgx = np.zeros((H,W))
imgz = np.zeros((H,W))
imgc = np.zeros((H,W), dtype=np.uint8)


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


# def colormap(x, name):
#     if x < 0 or x > 1:
#         raise ValueError('Value should be between 0 and 1')
#     colors = data[name]['colors']
#     if data[name]['interpolate']:
#         return cm_interpolate(x, colors)
#     return cm_qualitative(x, colors)

def cm_interpolate(x, colors):
    import math
    lo = math.floor(x * (len(colors) - 1))
    hi = math.ceil(x * (len(colors) - 1))
    clo = colors[lo]
    chi = colors[hi]
    rgb = [round((clo[i] + chi[i]) / 2 * 255) for i in range(3)]
    return rgb
def cm_qualitative(x, colors):
    idx = 0
    while x > (idx + 1) / (len(colors) - 0):
        idx += 1
    cx = colors[idx]
    rgb = [cx[i] * 255 for i in range(3)]
    return rgb

i = 0
for folder, _, files in os.walk('terrain_water'):
    if folder == 'terrain_water':
        continue
    y_high = [0,0,0,1,2,1,
              1,2,2,0,0,0,
              1,1,2,2,1,2,
              3,4,3,3,4,4,
              5,5,5,3,3,4,
              4,3,4,5,5,5][i] * 0x80
    x_high = [0,1,2,0,0,1,
              2,1,2,3,4,5,
              3,4,3,4,5,5,
              0,0,1,2,1,2,
              0,1,2,3,4,3,
              4,5,5,3,4,5][i] * 0x80

    for file in files:
        if file == '.gitignore':
            continue
        tile = int(file[-13:-11],0x10)%4
        if tile == 0:
            x_mid = 0
            y_mid = 0
        elif tile == 1:
            x_mid = 0x40
            y_mid = 0
        elif tile == 2:
            x_mid = 0
            y_mid = 0x40
        elif tile == 3:
            x_mid = 0x40
            y_mid = 0x40
        k = int(file[-13:-11], 0x10)
        x, y = 0, 0

        xi = even_bits(k)
        yi = even_bits(k >> 1)

        xi -= 2
        yi -= 2

        xi *= 0x40 * SCALE
        yi *= 0x40 * SCALE

        #print(int(file[-13:-11], 0x10), xi/0x40, yi/0x40, file, tile, x_mid, y_mid, y_high, x_high )
        f = open(folder+'/'+file, 'rb')

        #for y in range(y_high + y_mid, y_high + y_mid + 0x40):
        #    for x in range(x_high + x_mid, x_high + x_mid + 0x40):
        for y in range(yi, yi + 0x40 * SCALE, SCALE):
            for x in range(xi, xi + 0x40 * SCALE, SCALE):
                height = struct.unpack("<H", f.read(2))[0]
                x_flow = 2 * (int.from_bytes(f.read(2),'little') / 0xffff) - 1
                z_flow = 2 * (int.from_bytes(f.read(2),'little') / 0xffff) - 1
                cksum_v = struct.unpack(">B", f.read(1))[0]
                #cksum_v = int.from_bytes(cksum, 'little') # Possible Checksum ?
                material = int.from_bytes(f.read(1),'little')# * 32
                angle = int(math.atan2(z_flow, x_flow) * 128/math.pi + 128)
                magnitude = int(23*math.log(1+math.hypot(x_flow, z_flow)))
                #print(height)
                #print(x,y, W, H, yi, xi)
                tag = cksum_v & 0x80 != 0
                #if material + 3 != (cksum_v & 0x7f) and (not tag) :
                #    print(material, cksum_v, tag)#, cksum)
                #pass
                rgbs = [
                    [0,0,255],     # 0 water        blue
                    [128,128,255], # 1 Hot water    light blue
                    [255,0,255],   # 2 posion water purple
                    [255,0,0],     # 3 lava         red
                    [0,0,128],     # 4 cold water   dark blue
                    [0,255,0],     # 5 bog          green
                    [255,255,0],   # 6 clear water  yellow
                    [0,255,255],   # 7 ocean        cyan
                    [0,0,0],
                ]
                rgb = rgbs[material]
                #print(material, height, rgb)
                #rgb = [height, height, height]
                rgb.append(64)
                if SCALE == 1:
                    img.putpixel((x,y), tuple(rgb))
                else :
                    img.paste(tuple(rgb), box=(x,y,x+4,y+4))
                    img1[y:y+SCALE,x:x+SCALE] = material + 1
                    imgy[y:y+SCALE,x:x+SCALE] = height
                    imgx[y:y+SCALE,x:x+SCALE] = x_flow
                    imgz[y:y+SCALE,x:x+SCALE] = z_flow
                    imgc[y:y+SCALE,x:x+SCALE] = cksum_v
        f.close()
    i += 1
#img.convert("RGB").filter(ImageFilter.FIND_EDGES).save('heightmap_water.png')

def alpha_composite(src, dst):
    '''
    Return the alpha composite of src and dst.

    Parameters:
    src -- PIL RGBA Image object
    dst -- PIL RGBA Image object

    The algorithm comes from http://en.wikipedia.org/wiki/Alpha_compositing
    '''
    import numpy as np
    # http://stackoverflow.com/a/3375291/190597
    # http://stackoverflow.com/a/9166671/190597
    src = np.asarray(src)
    dst = np.asarray(dst)
    print(src.shape)
    print(dst.shape)
    out = np.empty(src.shape, dtype = 'float')
    alpha = np.index_exp[:, :, 3:]
    rgb = np.index_exp[:, :, :3]
    src_a = src[alpha]/255.0
    dst_a = dst[alpha]/255.0
    out[alpha] = src_a + dst_a * (1-src_a)
    old_setting = np.seterr(invalid = 'ignore')
    out[rgb] = (src[rgb]*src_a + dst[rgb]*dst_a*(1-src_a))/out[alpha]
    np.seterr(**old_setting)
    out[alpha] *= 255
    np.clip(out,0,255)
    # astype('uint8') maps np.nan (and np.inf) to 0
    out = out.astype('uint8')
    out = Image.fromarray(out, 'RGBA')
    return out


cb = 0x40
im2 = Image.new('RGBA', img.size, (255,255,255,128))
pix = im2.load()

a = 0
w = (255,255,255,a)
b = (0,0,0,a)

for i in range(im2.size[1]):
    if i % (cb * 2) >= cb:
        for j in range(im2.size[0]):
            if (j % (cb * 2)) < cb :
                pix[i,j] = b
            else:
                pix[i,j] = w
    else:
        for j in range(im2.size[0]):
            if (j % (cb * 2)) >= cb :
                pix[i,j] = b
            else:
                pix[i,j] = w

draw = ImageDraw.Draw(im2)
for i in range(256):
    xi = even_bits(i)
    yi = even_bits(i >> 1)
    xi -= 2
    yi -= 2
    xi *= 0x40 * SCALE
    yi *= 0x40 * SCALE
    draw.text((xi, yi), f"{i}", fill='red')

draw = ImageDraw.Draw(img)
draw.text((64, 100), 'Water', fill=(0,0,255))
draw.text((64, 130), 'Hot Water', fill=(128,128,255))
draw.text((64, 160), 'Poison', fill=(255,0,255))
draw.text((64, 190), 'Lava', fill=(255,0,0))
draw.text((64, 220), 'Cold Water', fill=(0,0,128))
draw.text((64, 250), 'Bog', fill=(0,255,0))
draw.text((64, 280), 'Clear Water', fill=(255,255,0))
draw.text((64, 310), 'Ocean', fill=(0,255,255))

#img = alpha_composite(im2, img.convert('RGBA'))
#img_out = alpha_composite(img, topo)

#img_out.save('heightmap_water_full.png')

dst_filename = 'heightmap_material.tiff'
format = 'GTiff'
driver = gdal.GetDriverByName(format)
cols,rows = img1.shape
dst_ds = driver.Create(dst_filename, cols, rows, 1, gdal.GDT_UInt8)
dst_ds.GetRasterBand(1).WriteArray(img1)
dst_ds = None


dst_filename = 'heightmap_water_y.tiff'
format = 'GTiff'
driver = gdal.GetDriverByName(format)
cols,rows = imgy.shape
dst_ds = driver.Create(dst_filename, cols, rows, 1, gdal.GDT_UInt16)
dst_ds.GetRasterBand(1).WriteArray(imgy)
dst_ds = None

# dst_filename = 'heightmap_water_x.tiff'
# format = 'GTiff'
# driver = gdal.GetDriverByName(format)
# cols,rows = imgx.shape
# dst_ds = driver.Create(dst_filename, cols, rows, 1, gdal.GDT_Float32)
# dst_ds.GetRasterBand(1).WriteArray(imgx)
# dst_ds = None

# dst_filename = 'heightmap_water_z.tiff'
# format = 'GTiff'
# driver = gdal.GetDriverByName(format)
# cols,rows = imgz.shape
# dst_ds = driver.Create(dst_filename, cols, rows, 1, gdal.GDT_Float32)
# dst_ds.GetRasterBand(1).WriteArray(imgz)
# dst_ds = None

# dst_filename = 'heightmap_water_chk.tiff'
# format = 'GTiff'
# driver = gdal.GetDriverByName(format)
# cols,rows = imgc.shape
# dst_ds = driver.Create(dst_filename, cols, rows, 1, gdal.GDT_UInt8)
# dst_ds.GetRasterBand(1).WriteArray(imgc)
# dst_ds = None

