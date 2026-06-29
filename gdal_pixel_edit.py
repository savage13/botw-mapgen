#!/usr/ebin/env python3

import sys
from osgeo import gdal
import numpy as np
gdal.UseExceptions()

ds = gdal.Open(sys.argv[1], gdal.GA_Update)

band = ds.GetRasterBand(1)
y = band.ReadAsArray()

N = 256

if sys.argv[2] == "material":
    ocean = 8
#    water = 1
if sys.argv[2] == "elevation":
    ocean = (105.8976119631 / 800) * 65535
# Southern
y[12*N:13*N, 9*N: 10*N] = ocean
y[13*N:14*N, 8*N: 11*N] = ocean

# Eastern
#y[3*N:4*N, 12*N:13*N] = ocean
y[3*N:12*N, 13*N:14*N] = ocean

# North
#y[3*N:4*N, 2*N:10*N ] = water
#y[3*N:14*N, 2*N:3*N ] = water

band.WriteArray(y)
ds.FlushCache()
ds = None
