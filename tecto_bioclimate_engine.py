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
