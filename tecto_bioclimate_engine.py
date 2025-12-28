# Take a modern location and calculate its position at any age defined.

#!pip install pygplates
import pygplates

def reconstruct_location(lat, lon, age):
  # 1. Load the tectonic model
  # These files define how plates move (rotation) and where they are (polygons).
  # You can download these files from EarthByte or GPlates repositories.
  rotation_model = pyplates.RotationModel("Muller_2016_Rotations.rot")
  static_polygons = "Muller_2016_Static_Polygons.gpml"

  # 2 Create a Point Feature for your modern location
  point = pygplates.PointOnSphere(lat, lon)
  point_feature = pygplates.Feature()
  point_feature.set_geometry(point)

  # 3. Partition the Point
  # This indentifies which tectonic plate 'owns' your coordinate.
  partitioned_features = pygplates.partition_into_plates(
        static_polygons,
        rotation_model,
        point_feature
  )

  # 4. Reconstruct to the target age
  reconstructed_geometries = []
  pygplates.reconstruct(partitioned_features, rotation_model, reconstructed_geometries, age)

  # 5. Extract the new coordinates
  paleo_lat, paleo_lon = reconstructed_geometries[0].get_reconstructed_geometry().to_lat_lon()

  return paleo_lat, paleo_lon

# Example: Where was New York 200 million years ago?
p_lat, p_lon = reconstruct_location(40.7, -74.0, 200)
print(f"Paleo-Coordinates: {plat}, {plon}")

# Plot the global configuration (entire world map) through reconstructing a 
# Coastline Feature Collection.

# Coastlines: represent the edge of the continental crust.
# Paleogeography Polygons: represent areas of deep ocean versus shallow seas.

# Visualize with Cartopy: once pyplates obtains the reconstructed geometries, the
# reconstructed geometries are passed to Cartopy to render the map.

import matplotlib.pyplot as plt
import cartopy.crs as ccrs

def plot_paleo_map(age):
  fig = plt.figure(figsize=(12, 6)))
  ax = plt.axes(projection=ccrs.Mollweide()) # Mollweide preserves area

  # Load and reconstruct global coastlines
  coastlines = pygplates.FeatureCollection("Global_Coastlines.gpml")
  reconstructed_coastlines = []
  pygplates.reconstruct(coastlines, rotation_model, reconstructed_coastlines, age)

  # Render each coastline segment
  for poly in reconstructed_coastlines:
    lat_lon = poly.get_reconstrcuted_geometry().to_lat_lon_array()
    plt.fill(lat_lon[:,1], lat_lon[:,0], color=;green', transform=ccrs.Geodetic())

plt.title(f"Earth at {age} Ma")
plt.show()
