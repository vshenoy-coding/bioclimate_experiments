# Take a modern location and calculate its position at any age defined.

# No-File Solution: Mathematical Plate Motion

# No .rot or .gpm files needed
# Kinematic plate equations used to approximate drift of the 
# North American plate (where New York sits) using a linear regression of its historical
# motion

import math
import matplotlib.pyplot as plt

# Install Cartopy and its dependencies
# !apt-get install -y libproj-dev proj-data proj-bin
# !apt-get install -y libgeos-dev
# !pip install --no-binary cartopy cartopy
import cartopy.crs as ccrs

# !pip install geopy
from geopy.geocoders import Nominatim

def calculate_approx_paleo_position(location_name, age_ma):
  # 1. Get Modern Coordinates
  geolocator = Nominatim(user_agent="paleo_approx_model")
  loc = geolocator.geocode(location_name)
  if not loc: return None

  m_lat, m_lon = loc.latitude, loc.longitude




########################################################################################
"""Original Code
def reconstruct_location(lat, lon, age):
  # 1. Load the tectonic model
  # These files define how plates move (rotation) and where they are (polygons).
  # You can download these files from EarthByte or GPlates repositories.
  rotation_model = pygplates.RotationModel("Muller_2016_Rotations.rot")
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
  fig = plt.figure(figsize=(12, 6))
  ax = plt.axes(projection=ccrs.Mollweide()) # Mollweide preserves area

  # Load and reconstruct global coastlines
  coastlines = pygplates.FeatureCollection("Global_Coastlines.gpml")
  reconstructed_coastlines = []
  pygplates.reconstruct(coastlines, rotation_model, reconstructed_coastlines, age)

  # Render each coastline segment
  for poly in reconstructed_coastlines:
    lat_lon = poly.get_reconstrcuted_geometry().to_lat_lon_array()
    plt.fill(lat_lon[:,1], lat_lon[:,0], color='green', transform=ccrs.Geodetic())

plt.title(f"Earth at {age} Ma")
plt.show()

# Add a Data Manager section to the code. This uses requests to pull the standardized
# "GPlates Sample Data" directly from the official GPlates GitHub or EarthByte servers.

# Since these datasets are often compressed in .zip format, the code includes a way to
# download, extract, and verify presence of .rot (rotations), .gpml (features), and
# .shp (shapefiles) needed for bioclimate analysis.
"""
##########################################################################################

##########################################################################################
# Code if Github or EarthBytes link worked
##########################################################################################
"""
!pip install pygplates
import pygplates

import os
import requests
import zipfile
import math
import matplotlib.pyplot as plt

# Install Cartopy and its dependencies
!apt-get install -y libproj-dev proj-data proj-bin
!apt-get install -y libgeos-dev
!pip install --no-binary cartopy cartopy
import cartopy.crs as ccrs

#!pip install geopy
from geopy.geocoders import Nominatim

# --- Section 1: Data Downloading & Initialization ---

def download_tectonic_assets(data_dir="/content/paleo_data"):
    # Downloads the standard Muller-EarthByte tectonic model files.
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # Repository for Muller 2016 Tectonic Model (Sample Data)
    url = "https://github.com/GPlates/gplates-sample-data/archive/refs/heads/master.zip"
    zip_path = os.path.join(data_dir, "gplates_data.zip")

    if not os.path.exists(zip_path):
        print("🛰️ Downloading Tectonic Model (Muller 2016)...")
        r = requests.get(url, stream=True)
        with open(zip_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
              f.write(chunk)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(data_dir)
        print("✅ Data Downloaded and Extracted.")
    else:
        print("📁 Tectonic files already exist.")

    # Define file paths for the model
    # Note: These paths are specific to the structure of the plates-sample-data repo.
    root = os.path.join(data_dir, "gplates-sample-data-master")
    return {
        "rotations": os.path.join(root, "Rotations", "Global_EarthByte_230-0Ma_GK07_2016.rot"),
        "polygons": os.path.join(root, "FeatureCollections", "StaticPolygons",
                               "Global_EarthByte_GPlates_PresentDay_StaticPlatePolygons.gpml"),
        "coastlines": os.path.join(root, "FeatureCollections", "Coastlines", 
                                 "Global_Coastlines_LowRes.gpml")
    }

# --- 2. Reconstruction Engine ---
def run_paleo_reconstruction(location_name, age_ma, files):
    geolocator = Nominatim(user_agent="colab_paleo_explorer")
    loc = geolocator.geocode(location_name)

    if not loc:
      return f"Location {location_name} not found."

    modern_lat, modern_lon = loc.latitude, loc.longitude

    # Load PyGPlates Rotation Model
    rotation_model = pygplates.RotationModel(files["rotations"])

    # Step 1: Create a feature for the modern point
    point_feature = pygplates.Feature()
    point_feature.set_geometry(pygplates.PointOnSphere(modern_lat, modern_lon))

    # Step 2: Assign a Plate ID based on the Static Polygons
    # This is critical for bioclimate: different plates for different drift velocities.
    partitioned_features = pygplates.partition_into_plates(
        files["polygons"],
        rotation_model,
        point_feature
    )

    # Step 3: Reconstruct the point to the target age
    reconstructed_geometries = []
    pygplates.reconstruct(partitioned_features, rotation_model, reconstructed_geometries, \
                        age_ma)
    p_lat, p_lon = reconstructed_geometries[0].get_reconstructed_geometry().to_lat_lon()

    # --- 3. Bioclimate Analysis ---
    # Calculate latitudinal temperature gradient
    # MAT = T_equator * cos(lat)
    # Deep time adjustment: Creatceous/Paleogene was ~5-10°C warmer globally
    global_warming_offset = 6.0 if 50 <= age_ma <= 100 else 0.0
    paleo_mat = (28 * math.cos(math.radians(p_lat))) + global_warming_offset

    return {
        "model_coords": (modern_lat, modern_lon),
        "paleo_coords": (round(p_lat, 2), round(p_lon, 2)),
        "paleo_mat": round(paleo_mat, 2),
        "plate_id": partitioned_features[0].get_reconstruction_plate_id()
    }

# --- 4. Model Visualization ---

def plot_paleo_map(age, files, target_paleo_coords=None):
    fig = plt.figure(figsize=(12, 6))
    ax = plt.axes(projection=ccrs.Mollweide())
    ax.stock_img() # Adds a basic ocean/land visual background

    rotation_model = pygplates.RotationModel(files["rotations"])
    coastlines = pygplates.FeatureCollection(files["coastlines"])

    reconstructed_coastlines = []
    pygplates.reconstruct(coastlines, rotation_model, reconstructed_coastlines, age)

    for poly in reconstructed_coastlines:
        geom = poly.get_reconstructed_geometry()
        # Handle both polygons and polylines
        for point_list in geom.to_lat_lon_list():
            lats, lons = zip(*point_list)
            plt.plot(lons, lats, color='black', linewidth=0.5, transform=ccrs.Geodetic())

        if target_paleo_coords:
            plt.plot(target_paleo_coords[1], target_paleo_coords[0], 'r*', markersize=12, transform=ccrs.Geodetic())

        plt.title(f"Global Plate Configuration at {age} Ma")
        plt.show()

# --- Execution ---
model_files = download_tectonic_assets()

# User Input
place = "New York, NY"
time = 150 # Jurassic Period

results = run_paleo_reconstruction(place, time, model_files)

if results:
  print(f"\n🌍 Bioclimate Reconstruction: {place.upper()}")
  print(f"--- {time} Million Years Ago ---")
  print(f"Modern Coordinates: {results['model_coords']}")
  print(f"Paleo-Coordinates: {results['paleo_coords']}")
  print(f"Reconstructed Plate ID: {results['plate_id']}")
  print(f"Estimated Mean Annual Temperature (MAT): {results['paleo_mat']}°C")

  # Add function call to visualize the map.
  plot_paleo_map(time, model_files, results['paleo_coords'])
else:
  print("Location not found.")
"""
