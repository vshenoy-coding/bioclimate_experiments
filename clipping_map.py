#!pip install rioxarray
import rioxarray

#!pip install geemap
import geemap

# geemap has a sample cloud optimized GeoTIFF (COG) that can be used to practice spatial logic

url = 'https://github.com/giswqs/data/raw/main/raster/srtm90.tif' 

# read the file in the url into rioxarray
# finds the coordinate reference system (CRS), cell size, and "No Data" values
# the output is a 3D object with dimensions (band, y, x)

data = rioxarray.open_rasterio(url)

# Treat this 'elevation' data as a proxy for a Bioclim variable (like BIO1)
# to build an analysis pipeline.

# # Define the min/max Longitude (x) and Latitude (y)
# These coordinates roughly cover a mountainous region
min_lon, max_lon = -120.0, -110.0
min_lat, max_lat = 35.0, 45.0

# Use .rio.clip_box() to clip the data to a bounding box set by min_lon, max_lon, min_lat, and max_lat
clipped_data = data.rio.clip_box(
    minx=min_lon,
    miny=min_lat,
    maxx=max_lon,
    maxy=max_lat
)

# Create canvas for map
plt.figure(figsize=(10, 5)) # figsize=(10, 5) means ten inches wide, five inches tall

# GeoTIFFs can have multiple layers (bands). Satellite images often have RGB (red green blue) bands.
# Bioclimate variables usually have just one band.

clipped_data.sel(band=1).plot(cmap = 'terrain')
plt.title('Use Sample Data to Build Project Logic')
plt.show()
