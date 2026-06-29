# wget https://static.zeldamods.org/botw_map.png
#   20,000 x 24,000
# For reference and set its coordinate system
#gdal_translate -of GTiff -a_ullr -6000 5000 6000 -5000 botw_map.png \
#               -a_srs EPSG:32662 ./botw_map.tiff


gdaldem color-relief ./heightmap800_epsg32662.tiff \
        botw_colormap.txt \
        heightmap800_epsg32662_rgb.tiff \
        -co COMPRESS=deflate -co PREDICTOR=2 

