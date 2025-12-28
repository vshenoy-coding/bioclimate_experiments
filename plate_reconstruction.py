"""
File: plate_reconstruction.py
Description: Generates global continental maps at specific geologic ages
Model: Merdith et al., 2021 (Full Tectonic Model)
Library: gplately / pyGPlates
"""

#!pip install pygplates
import pygplates

#!pip install gplately
import gplately.download

import inspect

"""
# In latest version, server is called RemoteModelServer
try:
    server = gplately.download.RemoteModelServer()
    print("Available Model Names:")
    for model in server.list_models():
        print(f" - {model}")


except AttributeError:
    # If that still fails, the library might have moved it to the DataServer class level
    print("Trying alternative listing...")
    from gplately.download import DataServer
    # This often prints the keys directly
    help(gplately.download.DataServer)
"""

# Initialize the DataServer with a valid model name
# "Merdith2021" is the most robust for deep-time (Scotese-era) maps and goes back 
# 1 billion years

model_name = "Merdith2021"

data_server = gplately.download.DataServer(model_name)

# Get the core construction files
rot_model, topo_features, static_polys = data_server.get_plate_reconstruction_files()

# Create the PlateReconstruction object

model = gplately.PlateReconstruction(rot_model, topo_features, static_polys)

# Get the visual geometries (Coastlines/Continents)
coastlines, continents, COBs = data_server.get_topology_geometries()

# SAFETY CHECK: If a model doesn't provide continents/coastlines, 
# we create an empty FeatureCollection so the plotter doesn't crash.
if coastlines is None:
    coastlines = pygplates.FeatureCollection()
if continents is None:
    continents = pygplates.FeatureCollection()

# Set your target time (e.g., 250 Ma - The Permian Triassic boundary)
time = 250

# Setup the plotter
# Note: PlotTopologies requires the model, time, and the feature collections

try:
    gPlot = gplately.PlotTopologies(model, time=time, continents=continents, 
                                coastlines=coastlines, COBs=COBs)
except TypeError:
    # If that fails, try without COBs - some versions only take 4 arguments
    gplot = gplately.PlotTopologies(model, time=time, continents=continents, 
                                    coastlines=coastlines)

print(inspect.signature(gplately.PlotTopologies.__init__))
# (self, plate_reconstruction, coastlines=None, continents=None, COBs=None, 
# time: float = 140.0, anchor_plate_id=None, 
# plot_engine: gplately.mapping.plot_engine.PlotEngine = <gplately.mapping.cartopy_plot.CartopyPlotEngine
# at

# Figure setup
fig = plt.figure(figsize=(15, 8))
ax = plt.axes(projection=ccrs.Mollweide())
ax.set_global()

# Styling the background
ax.set_facecolor('#f0f8ff') # Light Alice Blue for oceans
ax.gridlines(draw_labels=False, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')

# Plotting the layers with safety checks
# Check if gPlot has the methods before calling them

# Check for Continent Polygons (The "Land" Color)
if hasattr(gPlot, 'plot_continents'):
  gPlot.plot_continents(ax, facecolor='#e6ccb2', edgecolor='none', alpha=0.8)

# Check for COBs (The Continental Shelves)
if hasattr(gPlot, 'plot_cobs'):
    gPlot.plot_cobs(ax, color='#1f77b4', linewidth=0.7, alpha=0.4)

# Check for Coastlines (modern reference lines)
if hasattr(gPlot, 'plot_coastlines'):
  gPlot.plot_coastlines(ax, color='#222222', linewidth=0.5)

# Add a paleo-equator for orientation
# This uses standard matplotlib/cartopy logic (independent of gPlot)
ax.plot([-180, 180], [0, 0], color='red', linewidth=1,
        transform=ccrs.PlateCarree(), alpha=0.6)

plt.title(f"Reconstruction at {time} Ma\n(Model: {model_name})", fontsize=16, pad=20)
plt.show()


