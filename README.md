# BotW Map

## Setup

This requires gdal to compute and work with tiff formats.  It can probably
be done without gdal, but its a bit easier. gdal can be quite large to install.
If this is an issue, let me know and we can probably come up with a solution
without expensive requirements.

## Create Topography

    python ./terrain_merge.py

Should generate a 4096x4096 grayscale image of the heightmap / topography

    heightmap.tiff

This follows the format from https://zeldamods.org/wiki/HGHT

## Create Water Layers

   python ./heightmap_water_all.py

Should generate a 3072x3072 grayscale images of the materials and the water height

   heightmap_material.tiff
   heightmap_water_y.tiff

This follows the format from https://zeldamods.org/wiki/Water.extm

## Create Layers

   sh ./georef_water_topo_layers.sh

This creates lots of files for the "liquid" or water layers, including lava

   heightmap_water_???_epsg32662_800.tiff

- Georeference layers to EPSG 32662 (Plate Carree)
  - Setting bounds for each layer
- Convert from uint16 to float and scale by 800
  - heightmap.tiff
  - heightmap_water_y.tiff
- Set the image size to be from -8000/8000 in meters for all images
- Fill in some holes with gdal_pixel_edit.py
- Compute Topo - Water
  - Negative is Water is above Topography
- Use material layers to select different water layers
  where water is above topography

- Color the topography

   color_topo_map.sh

This should produce

   heightmap800_epsg32662_rgb.tiff

and RGB tiff image with the topography colored by the colorscale in botw_colormap.txt.  This scale goes from dark brown to light brown / white. See colormap_data.png and compute_colormap.py to determine how the map was created.  