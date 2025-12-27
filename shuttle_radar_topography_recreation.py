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

# verify this
print(np.shape(data)) # (1, 2456, 4269)
print(np.ndim(data))  # 3

# Treat this 'elevation' data as a proxy for a Bioclim variable (like BIO1)
# to build an analysis pipeline.

# Create canvas for map
plt.figure(figsize=(10, 5)) # figsize=(10, 5) means ten inches wide, five inches tall

# GeoTIFFs can have multiple layers (bands). Satellite images often have RGB (red green blue) bands.
# Bioclimate variables usually have just one band.

# data.sel(band=1) selects this first band

# add .plot to data.sel(band=1) to add Latitude, Longitude labels to the X, Y axes based on metadata in file

# cmap sets colormap. For elevation, 'terrain' can be used. For climate, Red/Blue 'RdBu_r' can be used.
# Here only terrain data is displayed from url, so it makes sense to use 'terrain' colormap.

data.sel(band=1).plot(cmap = 'terrain')
plt.title('Use Sample Data to Build Project Logic')
plt.show()


