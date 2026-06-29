
COMPRESS=" -co COMPRESS=DEFLATE -co PREDICTOR=2 "
COMPRESS2=" --co=COMPRESS=DEFLATE --co=PREDICTOR=2 "

# Apply a Coordinate system to the heightmap (4096x4096)
gdal_translate -of GTiff -a_ullr -8000 8000 8000 -8000 heightmap.tiff \
               -a_srs EPSG:32662 heightmap_epsg32662.tiff $COMPRESS

# Apply a Coordinate system to the watermap (3072x3072)
gdal_translate -of GTiff -a_ullr -6000 6000 6000 -6000 heightmap_water_y.tiff \
               -a_srs EPSG:32662 ./heightmap_water_y_epsg32662.tiff $COMPRESS

# Apply a Coordinate system to the material map (3072x3072)
gdal_translate -of GTiff -a_ullr -6000 6000 6000 -6000 heightmap_material.tiff \
               -a_srs EPSG:32662 ./heightmap_material_epsg32662.tiff $COMPRESS


# Convert from uint16 (0-65535) to (0-800)
gdal_calc --calc "(A / 65535.0) * 800" \
          -A ./heightmap_epsg32662.tiff \
          --outfile ./heightmap800_epsg32662.tiff \
          --type Float64 --overwrite $COMPRESS2

# Set extent of material to be the same as the heightmap
gdal_calc --calc "T" \
          -T ./heightmap_material_epsg32662.tiff \
          -Z ./heightmap800_epsg32662.tiff \
          --outfile ./heightmap_material_epsg32662_4096.tiff \
          --extent=union --overwrite  $COMPRESS2

python gdal_pixel_edit.py ./heightmap_material_epsg32662_4096.tiff material

# Set extent of water height to be the same as the heightmap
gdal_calc --calc "W * 1.0" \
          -W ./heightmap_water_y_epsg32662.tiff \
          -Z ./heightmap800_epsg32662.tiff \
          --outfile ./heightmap_water_y_epsg32662_4096.tiff \
          --extent=union --overwrite $COMPRESS2

python gdal_pixel_edit.py ./heightmap_water_y_epsg32662_4096.tiff elevation

# Convert from uint16 (0-65535) to (0-800)
gdal_calc --calc "(A / 65535.0) * 800" \
          -A ./heightmap_water_y_epsg32662_4096.tiff \
          --outfile ./heightmap_water_y_epsg32662_800.tiff \
          --type Float64 --overwrite $COMPRESS2

# Convert find difference between topography and waterlayer
#   negative here mean waterlayer above the topography
#   waterlayer may be multiple items
gdal_calc --calc "A - B" \
          -A ./heightmap800_epsg32662.tiff \
          -B ./heightmap_water_y_epsg32662_800.tiff \
          --outfile ./heightmap_water_negy_epsg32662_800.tiff \
          --type Float64 --overwrite --projectionCheck $COMPRESS2


gdal_calc --calc "(T == 1) * (W < 0) * W" \
          -T ./heightmap_material_epsg32662_4096.tiff \
          -W ./heightmap_water_negy_epsg32662_800.tiff \
          --outfile=heightmap_water_basic_y_epsg32662.tiff \
          --type Float64 --overwrite --projectionCheck $COMPRESS2
gdal_calc --calc "(T == 2) * (W < 0) * W" \
          -T ./heightmap_material_epsg32662_4096.tiff \
          -W ./heightmap_water_negy_epsg32662_800.tiff \
          --outfile=heightmap_water_hot_y_epsg32662.tiff \
          --type Float64 --overwrite --projectionCheck $COMPRESS2
gdal_calc --calc "(T == 3) * (W < 0) * W" \
          -T ./heightmap_material_epsg32662_4096.tiff \
          -W ./heightmap_water_negy_epsg32662_800.tiff \
          --outfile=heightmap_poison_y_epsg32662.tiff \
          --type Float64 --overwrite --projectionCheck $COMPRESS2
gdal_calc --calc "(T == 4) * (W < 0) * W" \
          -T ./heightmap_material_epsg32662_4096.tiff \
          -W ./heightmap_water_negy_epsg32662_800.tiff \
          --outfile=heightmap_lava_y_epsg32662.tiff \
          --type Float64 --overwrite --projectionCheck $COMPRESS2
gdal_calc --calc "(T == 5) * (W < 0) * W" \
          -T ./heightmap_material_epsg32662_4096.tiff \
          -W ./heightmap_water_negy_epsg32662_800.tiff \
          --outfile=heightmap_water_ice_y_epsg32662.tiff \
          --type Float64 --overwrite --projectionCheck $COMPRESS2
gdal_calc --calc "(T == 6) * (W < 0) * W" \
          -T ./heightmap_material_epsg32662_4096.tiff \
          -W ./heightmap_water_negy_epsg32662_800.tiff \
          --outfile=heightmap_bog_y_epsg32662.tiff \
          --type Float64 --overwrite --projectionCheck $COMPRESS2
gdal_calc --calc "(T == 7) * (W < 0) * W" \
          -T ./heightmap_material_epsg32662_4096.tiff \
          -W ./heightmap_water_negy_epsg32662_800.tiff \
          --outfile=heightmap_water_clear_y_epsg32662.tiff \
          --type Float64 --overwrite --projectionCheck $COMPRESS2
gdal_calc --calc "(T == 8) * (W < 0) * W" \
          -T ./heightmap_material_epsg32662_4096.tiff \
          -W ./heightmap_water_negy_epsg32662_800.tiff \
          --outfile=heightmap_water_sea_y_epsg32662.tiff \
          --type Float64 --overwrite --projectionCheck $COMPRESS2
