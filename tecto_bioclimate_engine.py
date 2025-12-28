# Take a modern location and calculate its position at any age defined.

# No-File Solution: Mathematical Plate Motion

# No .rot or .gpm files needed
# Kinematic plate equations used to approximate drift of the 
# North American plate (where New York sits) using a linear regression of its historical
# motion.

# This is a straight line apprxoaimtion. The real GPlates files use Euler Poles, where
# every lectonic plate rotates around a unique "hinge". Using Euler Poles, a location that
# a plate is on doesn't just move north/south/east/west, it also rotates as it moves.

# Code offline-ready and doesn't need to rely on external geocoding service

import math
import numpy as np
import matplotlib.pyplot as plt

# Install Cartopy and its dependencies
# !apt-get install -y libproj-dev proj-data proj-bin
# !apt-get install -y libgeos-dev
# !pip install --no-binary cartopy cartopy
import cartopy.crs as ccrs

# !pip install geopy
from geopy.geocoders import Nominatim

from IPython.display import clear_output

def get_granular_temp_offset(age_ma):
    """
    Interpolates climate offsets based on major thermal events.
    Values represent the global anomaly relative to the modern baseline.
    """
    # Key anchor points (Age_Ma: Temp_Offset)
    # Anchor points for interpolation (Age_Ma: Temp_Offset_Celsius)
    # Includes high-resolution spikes for PETM and EECO
    anchors = {
        0: 0.0, 34: 0.5, 52: 12.0, 56: 15.0, 66: 8.0, 
        92: 13.0, 145: 6.0, 201: 9.0, 252: 16.0, 300: -4.0, 360: 2.0,
        444: -6.0, 520: 10.0, 800: -15.0
    }
    
    ages = sorted(anchors.keys())
    # Linear interpolation to find the specific offset for any age
    return float(np.interp(age_ma, ages, [anchors[a] for a in ages]))

def calculate_approx_paleo_position(location_name, age_ma, lat=None, lon=None):

    # 1. Coordinate Handling
    # Common city coordinates to bypass geocoder if needed
    # Defines local database (always defined first before they're used 
    # to avoid UnboundLocalError)
    city_db = {
        "New York, NY": (40.71, -74.01),
        "London, UK": (51.51, -0.13),
        "Syndney, AU": (-33.87, 151.21),
        "Lagos, NG": (6.45, 3.38),
        "Buenos Aires, AR": (-34.60, -58.38)
    }

    m_lat, m_lon = None, None

    # Priority A: User-provided manual coordinates
    if lat is not None and lon is not None:
        m_lat, m_lon = lat, lon

    # Priority B: Try the Geocoder
    if m_lat is None:
        try:
            # Use a unique user_agent to help avoid 403 errors
            geolocator = Nominatim(user_agent="paleo_explorer_v2_unique")
            loc = geolocator.geocode(location_name, timeout=5)
            if loc:
                m_lat, m_lon = loc.latitude, loc.longitude
                print(f"📡 Geocoder successful for {location_name}")
        except Exception as e:
            print(f"⚠️ Geocoder blocked or failed ({type(e).__name__}). Switching to Local DB...")

    # Priority C: Local Database Fallback
    if m_lat is None:
        if location_name in city_db:
            m_lat, m_lon = city_db[location_name]
            print(f"✅ Local database match found for {location_name}")
        else:
            print(f"❌ Error: Could not find coordinates for '{location_name}'.")
            return None

    # 2. Mathematical Approximation of North American Plate Motion
    # Historically, North America has drifted north/west since the Jurassic.
    # Estimate a drift rate of ~0.2 degrees of latitude per million years.
    # Dynamic Drift Rate Selection; default rates (North America)
    lat_drift_rate = 0.18 # Degree North per Ma
    lon_drift_rate = 0.35 # Degrees West per Ma

    # First attempt at dynamic adjustment based on modern coordinates.
    if m_lat > 20 and -20 < m_lon < 50:
        # Europe / Eurasia (moves slower north/east)
        lat_drift_rate, lon_drift_rate = 0.12, -0.15
        print("📍 Applying Eurasian plate drift rates.")

    elif m_lat < 0 and 110 < m_lon < 155:
        # Australia (fastest plate, moves rapidly north)
        lat_drift_rate, lon_drift_rate = 0.65, -0.20
        print("📍 Applying Australian plate drift rates.")

    elif -60 < m_lat < 15 and -90 < m_lon < -30:
        lat_drift_rate, lon_drift_rate = 0.10, 0.25  
        print("📍 Applying South American plate drift rates.")
    
    elif -35 < m_lat < 38 and -20 < m_lon < 55:
        lat_drift_rate, lon_drift_rate = 0.08, -0.05 # Africa
        print("📍 Applying African plate drift rates.")

    else:
        print("📍 Applying default (North American) plate drift rates.")

    # 3. Physics calculations
    p_lat = m_lat - (lat_drift_rate * age_ma)
    p_lon = m_lon + (lon_drift_rate * age_ma)

    # --- Supercontinent Convergence Logic ---
    # 1. Pangea Window (Approx 180Ma to 350Ma)
    if 180 < age_ma <= 450:
        # Peaks at 250 Ma
        pull_strength = math.sin(math.pi * (age_ma - 180) / 270) 
        p_lat = p_lat * (1 - pull_strength) + (0 * pull_strength)
        p_lon = p_lon * (1 - pull_strength) + (0 * pull_strength)

    # 2. Rodinia Window (Approx 750Ma to 1000Ma)
    elif 750 < age_ma <= 1000:
        # Peaks at 850-900 Ma
        # Strength of 'pull' toward the Rodinian center
        pull_strength = math.sin(math.pi * (age_ma - 750) / 250)
        p_lat = p_lat * (1 - pull_strength) + (0 * pull_strength)
        p_lon = p_lon * (1 - pull_strength) + (0 * pull_strength)
  
    # Based on Phanerozoic climate trends (Icehouse vs Hothouse)
    temp_offset = get_granular_temp_offset(age_ma)

    # 3. Temperature gradient calculation
    # MAT = 28 * cos(lat) + Greenhouse Offset
    paleo_mat = (28 * math.cos(math.radians(p_lat))) + temp_offset

    # Haversine Distance (km)
    R = 6371
    dlat, dlon = math.radians(p_lat-m_lat), math.radians(p_lon-m_lon)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(m_lat)) * math.cos(math.radians(p_lat)) * math.sin(dlon/2)**2
    dist_km = R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))

    return {
        "modern": (round(m_lat, 2), round(m_lon, 2)),
        "paleo": (round(p_lat, 2), round(p_lon, 2)),
        "mat": round(paleo_mat, 2),
        "offset": temp_offset,
        "dist": round(dist_km, 0)
    }

import ipywidgets as widgets
from IPython.display import display, clear_output

# Create persistent UI elements so that input box is not hidden by map
city_input = widgets.Text(value='New York, NY', description='City:')
age_input = widgets.FloatText(value=56.0, description='Age (Ma):')
run_button = widgets.Button(description="Calculate Paleo-Position", button_style='primary')
exit_button = widgets.Button(description="Exit Program", button_style='danger')
output_area = widgets.Output()

def calculate_spherical_drift(m_lat, m_lon, age_ma):
    # 1. The Wilson Cycle (Supercontinent Pulse)
    # Continents cluster roughly every 450-500 million years.
    cycle_period = 500 
    oscillation = math.sin(2 * math.pi * age_ma / cycle_period)
    
    # 2. Rotational Drift
    # Instead of linear drift, we treat motion as an angular shift
    drift_scale = 0.25 # Degrees per Ma
    
    # Calculate paleo-lat/lon with a circular/oscillating component
    p_lat = m_lat * math.cos(math.radians(drift_scale * age_ma)) + (20 * oscillation)
    p_lon = m_lon + (drift_scale * age_ma * oscillation)
    
    # 3. Spherical Safety (Clamping)
    p_lat = max(min(p_lat, 90), -90)
    p_lon = ((p_lon + 180) % 360) - 180
    
    return p_lat, p_lon

def on_button_clicked(b):
    with output_area:
        clear_output(wait=True) # Clears ONLY the map/results area
        city_name = city_input.value
        age_val = age_input.value

        res = calculate_approx_paleo_position(city_name, age_val)

        if res:
            m_lat, m_lon = res['modern']
            p_lat, p_lon = calculate_spherical_drift(m_lat, m_lon, age_val)

            # Calculate "Paleo-Speed" (Velocity)
            test_age = age_val - 1 if age_val >= 1 else age_val + 1
            p_lat_next, p_lon_next = calculate_spherical_drift(m_lat, m_lon, test_age)
            
            # Use Haversine to find distance moved in 1 Million Years.
            R = 6371 # Earth radius in km
            dlat = math.radians(p_lat_next - p_lat)
            dlon = math.radians(p_lon_next - p_lon)
            a = math.sin(dlat/2)**2 + math.cos(math.radians(p_lat)) * math.cos(math.radians(p_lat_next)) * math.sin(dlon/2)**2
            delta_dist_km = R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))
            
            # Convert km/Ma to cm/year (1 km/Ma = 0.1 cm/year).
            speed_cm_yr = delta_dist_km * 0.1

            print(f"✅ {city_name} at {age_val} Ma")
            print(f"📊 Modern Location: {m_lat}°, {m_lon}°")
            print(f"🌡️ MAT: {res['mat']}°C | 📏 Drift: {res['dist']} km")
            
            # --- Enhanced Geological Status ---
            if age_val <= 60:
                print("🏙️ Phase: Modern World Configuration")
            elif 60 < age_val < 200:
                print("🧩 Phase: Pangea Breakup (Atlantic Ocean Opening)")
            elif 200 <= age_val <= 300:
                print("🏔️ Phase: Pangea Assembly (Supercontinent Peak)")
            elif 300 < age_val <= 541:
                print("🌊 Phase: Paleozoic Drift (Pre-Pangea / Panthalassic Era)")
            elif 541 < age_val <= 750:
                print("🐟 Phase: Rodinia Breakup (Creating the Iapetus Ocean)")
            elif 750 < age_val <= 900:
                print("🧊 Phase: Rodinia Peak / Cryogenian 'Snowball Earth'")
            else:
                print("⏳ Phase: Deep Proterozoic / Pre-Rodinia")
            
            print(f"🧭 Paleo-Location: ({round(p_lat, 2)}, {round(p_lon, 2)})")
            print(f"🚀 Paleo-Speed: {round(speed_cm_yr, 2)} cm/year")
            print("-" * 30)
            
            # Render the Map
            fig = plt.figure(figsize=(10, 5))
            ax = plt.axes(projection=ccrs.Mollweide())
            ax.stock_img()
            ax.plot(p_lon, p_lat, 'r*', ms=15, transform=ccrs.Geodetic())
            plt.title(f"{city_name} at {age_val} Ma")
            plt.show()
            plt.close(fig)
        else:
            print(f"❌ Error: Location '{city_name}' not found.")

def on_exit_clicked(b):
    city_input.close()
    age_input.close()
    run_button.close()
    exit_button.close()
    output_area.clear_output()
    print("🌍 Explorer Closed. Re-run the cell to start again.")

run_button.on_click(on_button_clicked)
exit_button.on_click(on_exit_clicked)

# 2. Display the dashboard
print(" --- 🌍 Paleo-Location Explorer Dashboard ---")
display(widgets.VBox([city_input, age_input, run_button, exit_button, output_area]))


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
