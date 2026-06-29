
gdal_translate -of GTiff -a_ullr \
               -10000 10000 10000 -10000 \
               ./heightmap_water_min.tiff \
               -a_srs EPSG:32662 \
               ./heightmap_water_min_epsg32662.tiff

gdal_translate -of GTiff -a_ullr \
               -10000 10000 10000 -10000 \
               ./heightmap_water_max.tiff \
               -a_srs EPSG:32662 \
               ./heightmap_water_max_epsg32662.tiff

gdal_translate -of GTiff -a_ullr \
               -10000 10000 10000 -10000 \
               ./heightmap_topo_min.tiff \
               -a_srs EPSG:32662 \
               ./heightmap_topo_min_epsg32662.tiff

gdal_translate -of GTiff -a_ullr \
               -10000 10000 10000 -10000 \
               ./heightmap_topo_max.tiff \
               -a_srs EPSG:32662 \
               ./heightmap_topo_max_epsg32662.tiff


gdal_translate -of GTiff -a_ullr \
               -6000 6000 6000 -6000 \
               ./heightmap_water_x.tiff \
               -a_srs EPSG:32662 \
               ./heightmap_water_x_epsg32662.tiff

gdal_translate -of GTiff -a_ullr \
               -6000 6000 6000 -6000 \
               ./heightmap_water_z.tiff \
               -a_srs EPSG:32662 \
               ./heightmap_water_z_epsg32662.tiff

gdal_translate -of GTiff -a_ullr \
               -6000 6000 6000 -6000 \
               ./heightmap_water_chk.tiff \
               -a_srs EPSG:32662 \
               ./heightmap_water_chk_epsg32662.tiff


