#!/usr/bin/env python3


import numpy as np
import matplotlib.pyplot as plt
from osgeo import gdal, osr
gdal.UseExceptions()


ds = gdal.Open("heightmap800_epsg32662.tiff")
ny, nx, nbands = ds.RasterYSize, ds.RasterXSize, ds.RasterCount
pr = ds.GetProjection()
gt = ds.GetGeoTransform()
print(ny,nx, nbands, gt)
y = np.array(ds.GetRasterBand(1).ReadAsArray())
#print(y.shape)

ds1 = gdal.Open("botw_map.tiff")
ny1, nx1, nbands1 = ds1.RasterYSize, ds1.RasterXSize, ds1.RasterCount
pr1 = ds1.GetProjection()
gt1 = ds1.GetGeoTransform()
print(ny1,nx1, nbands1, gt1)
r1 = np.array(ds1.GetRasterBand(1).ReadAsArray())
g1 = np.array(ds1.GetRasterBand(2).ReadAsArray())
b1 = np.array(ds1.GetRasterBand(3).ReadAsArray())
#print(r1.shape)

#crs = osr.SpatialReference()
#crs.ImportFromWkt(ds.GetProjectionRef())

#crs1 = osr.SpatialReference()
#crs1.ImportFromWkt(ds1.GetProjectionRef())

#t = osr.CoordinateTransformation(crs, crs1)

red = []
blue = []
green = []
elev = []

for j in range(ny):
    for i in range(nx):
        x0 = gt[0] + (i + 0.5) * gt[1]
        y0 = gt[3] + (j + 0.5) * gt[5]

        i1 = int((x0 - gt1[0])/gt1[1])
        j1 = int((y0 - gt1[3])/gt1[5])
        if i1 < 0 or i1 >= nx1 or j1 < 0 or j1>=ny:
            continue
        #print(i,j, i1,j1)
        elev.append( y[j,i] )
        red.append(r1[j1,i1])
        green.append(g1[j1,i1])
        blue.append(b1[j1,i1])
        #break

bins = 64
rheatmap, xedges, yedges = np.histogram2d(elev, red, bins=bins, range=[[0,800],[0,256]])
gheatmap, xedges, yedges = np.histogram2d(elev, green, bins=bins, range=[[0,800],[0,256]])
bheatmap, xedges, yedges = np.histogram2d(elev, blue, bins=bins, range=[[0,800],[0,256]])


yele = np.arange(800)
rb0 = 40
rslope = (210-rb0)/800
gb0 = 25
gslope = (200-gb0)/800
bb0 = -30
bslope = (190-bb0)/800

plt.subplot(2,2,1)
plt.pcolormesh(xedges, yedges, np.log10(rheatmap.T), cmap='hot_r')
plt.title('red')
plt.colorbar()
plt.plot(yele, yele * rslope + rb0)
plt.xlim(0,800)
plt.ylim(0,256)

plt.subplot(2,2,2)
plt.pcolormesh(xedges, yedges, np.log10(gheatmap.T), cmap='hot_r')
plt.title('green')
plt.colorbar()
plt.plot(yele, yele * gslope + gb0)
plt.xlim(0,800)
plt.ylim(0,256)

plt.subplot(2,2,3)
plt.pcolormesh(xedges, yedges, np.log10(bheatmap.T), cmap='hot_r')
plt.title('blue')
plt.colorbar()
plt.plot(yele, yele * bslope + bb0)
plt.xlim(0,800)
plt.ylim(0,256)

plt.subplot(2,2,4)
yr = yedges[np.argmax(rheatmap,1)]
yg = yedges[np.argmax(gheatmap,1)]
yb = yedges[np.argmax(bheatmap,1)]
xxedges = xedges[:-1]
plt.plot(xxedges, yr,'r.')
plt.plot(xxedges, yg,'g.')
plt.plot(xxedges, yb,'b.')
plt.xlim(0,800)
plt.ylim(0,256)

idx = (xxedges > 125) & (xxedges < 590)

idx2 = (xxedges > 125) & ( ( (xxedges > 400) & (yb > 65)) | (xxedges <= 400) )

pr = np.polyfit(xxedges[idx], yr[idx],1)
pg = np.polyfit(xxedges[idx], yg[idx],1)
pb = np.polyfit(xxedges[idx2], yb[idx2],1)

print(pr[0],pr[1])
print(pg[0],pg[1])
print(pb[0],pb[1])

plt.plot(xxedges, np.polyval(pr, xxedges), 'r-')
plt.plot(xxedges, np.polyval(pg, xxedges), 'g-')
plt.plot(xxedges, np.polyval(pb, xxedges), 'b-')

plt.show()

xout = np.arange(0,801,10)
with open("botw_colormap.txt","w") as f:
    for xv in xout:
        rv = max(int(np.polyval(pr, xv)),0)
        gv = max(int(np.polyval(pg, xv)),0)
        bv = max(int(np.polyval(pb, xv)),0)
        print(f"{xv} {rv} {gv} {bv}", file=f)
