# Independent Coding Project
# Bioclimatic Variables (MAT, MAP, Seasonality)
# Datasets often come in raster format (such as .tif files from WorldClim)

# install raster package to read, write, and manipulate geospatial raster data
#!pip install rasterio

# install geopandas to better manage spatial boundaries in geospatial data
#!pip install geopandas

#install rioxarray to extend xarray for geospatial analysis
#!pip install rioxarray

# install pyproj Python wrapper for the PROJ library 
# to enable efficient, accurate cartographic projections, 
# coordinate transformations, and geodetic calculations within 
#!pip install pyproj

# install earthpy for scientific analysis and visualization of remote sensing
# data
#!pip install earthpy

# install folium and geemap to create interactive web maps
#!pip install folium
#!pip install geemap

# install chelsa-cmip6 bioclimate package to create high-resolution 
# bioclimatic data from CMIP6 models
# requires dask and netCDF4


#!pip install netCDF4
#!pip install dask
#!pip install chelsa-cmip6

# install Google Earth Engine (ee)
#!pip install ee

import xarray as xr
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio as rio
import matplotlib.pyplot as plt
import folium


# Access real-world data from WorldClim
#!wget https://biogeo.ucdavis.edu/data/worldclim/v2.1/base/wc2.1_10m_bio.zip
#!unzip wc2.1_10m_bio.zip

# Didn't work, so import ee and geemap

#import ee
#import geemap

# Install the latest versions to fix the StringIO/Python 2 compatibility error
#!pip install -U earthengine-api geemap

import ee

# Trigger the authentication flow
#ee.Authenticate()
#ee.Initialize(project='first-clim-project-20251227') 
# Replace with your GCP project ID (here 'first-clim-project-<YYYYMMDD'>)

# Since this can have issues, start with simulated data

# Create a fake grid of latitudes and longitudes

lats = np.linspace(-90, 90, 180)
lons = np.linspace(-180, 180, 360)

# Generate synthetic "Mean Annual Temperature" (BIO1) 
# Average of all monthly mean temperatures (Max Temp - Min Temp) over a one-year period.

lon2d, lat2d = np.meshgrid(lons, lats)

temp_data = 30 - 0.5 * np.abs(lat2d) + np.random.normal(0, 2, lat2d.shape)

# Create an Xarray Dataset (this mimics the structure of real Bioclim data)
bio1_mock = xr.DataArray(temp_data, coords=[lats, lons], dims=['lat', 'lon'], \
                         name="bio1")

# Plot
bio1_mock.plot(cmap='RdBu_r')
plt.title("Synthetic Bioclimatic Variable (BIO1)")
plt.show()

