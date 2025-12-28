#!pip install pygplates
import pygplates

#!pip install chronos-python
import chronos

##########################################################################################
# Code logic:

#import requests

# 1. Define Modern Amazon Point
#modern_lat, modern_lon = -3.0, -60.0
#target_time = 100 # Millions of years ago

# 2. Use GPlates API to find the Paleolocation
# This rotates the point based on tectonic plate models
#url = f"https://gws.gplates.org/reconstruct/reconstruct_points/?points={modern_lon},{modern_lat}&time={target_time}&model=PALEOMAP"
#response = requests.get(url).json()

#paleo_lat = response['coordinates'][0][1]
#paleo_lon = response['coordinates'][0][0]

#print(f"100Ma Location: Latitude {paleo_lat}, Longitude {paleo_lon}")

# 3. Whittaker Mapping Logic
# At this time, the global climate was a 'Greenhouse' state.
# We map these coordinates against paleoclimate model data (e.g., HadCM3)
##########################################################################################

# We want to fetch modern lat, lon coordinates without hardcoding them

# !pip install geopy

import requests
from geopy.geocoders import Nominatim

def get_coordinates(location_name):
  # Fetches modern lat/lon for a given string location.
  geolocator = Nominatim(user_agent="paleo_explorer")
  location = geolocator.geocode(location_name)
  if location:
    return location.latitude, location.longitude
  else:
    return None, None
    

def get_paleo_location(location_name, age):
  # 1. Dynamically get modern points
  lat, lon = get_coordinates(location_name)

  if lat is None:
    return f"Location '{location_name}' not found."
  
  # 2. call the official GPlates engine directly
  url = "https://gws.gplates.org/reconstruct/reconstruct_points/"
  params = {
    "points": f"{lon},{lat}",
    "time": age,
    "model": "MULLER2016"
  }
  
  data = requests.get(url, params=params).json()
  p_lon, p_lat = data['coordinates'][0]
  

  # 100 million years ago Amazon
  # call get_paleo_location function and pass it modern lat-lon points of Amazon

  return p_lat, p_lon, lat, lon

# --- Execution ---
place = "Amazon Rainforest"
paleo_lat, paleo_lon, mod_lat, mod_lon = get_paleo_location(place, 100)

print(f"Location: {place}")
print(f"Modern Coordinates: {mod_lat}, {mod_lon}")
print(f"Paleo-Latitude (100Ma): {paleo_lat}")
print(f"Paleo-Longitude (100Ma): {paleo_lon}")

##########################################################################################
# Get temperatures at modern lat, lon
##########################################################################################

import urllib3
# Disable the insecure request warning since we are bypassing SSL verification
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_modern_climate(lat, lon):
    # Updated URL to the standard Open-Meteo Archive endpoint
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "daily": ["temperature_2m_mean", "precipitation_sum"],
        "timezone": "auto"
    }

    # Added verify=False to ignore the SSL UNRECOGNIZED_NAME error
    response = requests.get(url, params=params, verify=False)
    
    if response.status_code != 200:
        print(f"Weather API Error: {response.status_code}")
        return 27.0, 2000.0 # Fallback to standard tropical temp and precip if API fails
        
    data = response.json()

    # 1. Process Temperature
    temps = data['daily']['temperature_2m_mean']
    # Filter out any None values (days with missing data)
    valid_temps = [t for t in temps if t is not None]
    avg_temp = sum(valid_temps) / len(valid_temps) if valid_temps else 27.0

    # 2. Process Precipitation (sum of all daily values for the year)
    precips = data['daily']['precipitation_sum']
    valid_precips = [p for p in precips if p is not None]
    total_precip = sum(valid_precips) if valid_precips else 1840.0

    return round(avg_temp, 2), round(total_precip, 2)

modern_temp, modern_precip = get_modern_climate(mod_lat, mod_lon)

##########################################################################################
# Paleoclimate Modeling
##########################################################################################

# Calculate Baron (1994) Greenhouse Gradient, estimating temperature difference based
# on how far a point is from the equator (p_lat)

def get_greenhouse_delta(paleo_lat):

  # Calculates the temperature increase relative to modern
  # latitudinal averages during the Mid-Cretaceous.

  abs_lat = abs(paleo_lat)

  # Near the Equator (0-15°): Cretaceous was ~4-6°C hotter
  # Near the Poles (70-90°): Cretaceous was ~20-30°C hotter
  # This formula approximates that curve:
  delta = 5 + (0.3 *abs_lat)

  return round(delta, 2)



# Combine teconic rotation with a climate estimate based on published Cretaceous model data

def climate_paleo_data(lat, lon, age):

  # 1. calculate the real modern average instead of hardcoding 27
  real_modern_avg = get_modern_temp(lat, lon)
  
  # 2. Rotate the point to find its ancient paleo-coordinates
  gplates_url = "https://gws.gplates.org/reconstruct/reconstruct_points/"
  g_params = {"points": f"{lon},{lat}", "time": age, "model": "MULLER2016"}
  
  response = requests.get(gplates_url, params = g_params)

  # Check if the request was successful
  if response.status_code != 200:
    return f"Error: Server returned status {response.status_code}"
  
  g_data = requests.get(gplates_url, params=g_params).json()
  p_lon, p_lat = g_data['coordinates'][0]

  # Estimate Paleo-Temperature (Based on Cretaceous Model Grids)
  # In a full research environment, you'd query a NetCDF file here
  # Here, a standard "Greenhouse" delta for the paleolatidue is used

  # Modern Temperature at p_lat is 27

  # Near the equator during the Cretaceous,
  # temperatures were 5-7°C hotter than modern equatorial temps.
  # modern_equatorial_avg = 27

  # Dynamic Calculation: No more hard-coded 6
  temp_delta = get_greenhouse_delta(p_lat)
  est_cretaceous_temp = real_modern_avg + temp_delta 
  
  # Estimate Precipitation
  # The widening Atlantic 'gateway' created high humidity
  # Precipitation also scales with temperature (Clausius-Clapeyron relation)
  # Roughly 7% increase in moisture per 1°C of warming

  precip_factor = 1 + (temp_delta * 0.07)
  est_cretaceous_precip = 1834 * precip_factor # (Precipitation moderling requies complex GCMs)

  return {
    "paleo_lat": round(p_lat, 2),
    "paleo_lon": round(p_lon, 2),
    "delta_applied": temp_delta,
    "modern_temp": round(est_cretaceous_temp, 2),
    "paleo_temp": est_cretaceous_temp,
    "paleo_precip": est_cretaceous_precip
  }

# Run for the Amazon
results = climate_paleo_data(mod_lat, mod_lon, 100)

print(f"--- Cretaceous Amazon Results ---")
print(f"Paleo-latitude: {results['paleo_lat']}°S")
print(f"Estimated Surface Temperature: {round(results['paleo_temp'], 2)}°C")
print(f"Estimated Annual Rainfall: {round(results['paleo_precip'], 2)} mm")



#########################################################################################
# Dual-Whittaker Code: entire x-axis has shifted, considering 100 million years ago
# "Hothouse Earth" climate was entirely outside the modern tropical climate.
########################################################################################

import matplotlib.pyplot as plt
import numpy as np

#1. Modern Data (From earlier 2023 analysis)
# Assuming an average of transect points
# modern_temp = 27
# modern_precip = 1834

# 2. Cretaceous Data (Based on -8.26 Paleo-Latitude)
paleo_temp = results['paleo_temp']
paleo_precip = results['paleo_precip']

plt.figure(figsize=(10, 8))

# Plot modern point
plt.scatter(modern_temp, modern_precip, color='salmon', s=200, label='Modern Amazon (2023)', edgecolor='black', zorder=5)

# Plot Cretaceous point
plt.scatter(paleo_temp, paleo_precip, color='darkred', s=300, marker='*', label='Cretaceous Amazon (100 Ma)', edgecolor='black', zorder=5)

# Add Whittaker Biome Boundaries (simplified)
# These represent the 'envelope' of modern life
plt.axvspan(20, 30, 0, 0.8, color='green', alpha=0.1, label='Modern Tropical Range')

# Formatting the "Deep Time" Plot
plt.title("Whittaker Plot: Modern vs. Cretaceous Amazon", fontsize=15)
plt.xlabel("Mean Annual Temperature (°C)", fontsize=12)
plt.ylabel("Annual Precipitation (mm)", fontsize=12)

# We extend the limits to show how 'extreme' the Cretaceous was
plt.xlim(15, 40)
plt.ylim(0, 3500)

plt.grid(linestyle='--', alpha=0.6)
plt.legend()
plt.annotate('Hothouse Shift', xy=(31, 2300), xytext=(22, 2800),
             arrowprops=dict(facecolor='black', shrink=0.05))

plt.show()

# The direction of that arrow represents the net vector of climate change between 
# two vastly different climates of Earth's history.

# To understand why it points southeast (moving "down" and "right") from the perspective 
# of the modern green box, we have to look at the relationship between the modern data 
# points and the Cretaceous results.
# 1. The "Right" Shift (X-axis: Temperature)
# The arrow points toward the right because the Cretaceous was a "Hothouse" climate.
# Modern Average: ~27°C.
# Cretaceous Average: ~33°C.
# Result: A +6°C increase pushes the point significantly to the right, far outside 
# the modern "Greenbox" thermal limit (which usually caps at 30°C).
# 2. The "Downward" Shift (Y-axis: Precipitation)
# This is where the visual can be counter-intuitive. 
# In the plot of the Hothouse Shift, the arrow points "down" relative to the 
# top of the green box because of how we define "Modern Tropical Rainforests."

# The Modern Green Box: This box typically represents the entire range of modern tropical 
# biomes, which can extend up to 4,500 mm of rain in places like the Chocó or the 
# upper Amazon.
# The 2023 Data Point: The specific modern Amazon point (~1,834 mm) is actually quite 
# "low" in that box because of the drying trend that was discovered.
# The Cretaceous Point: While 2,800 mm is a lot of rain, it is still lower than 
# the "maximum possible" rainfall for a modern tropical rainforest.

# 3. The "Southeast" Vector
# The "Hothouse Shift" arrow is essentially saying:
# "Compared to the theoretical maximum moisture and temperature of a modern forest, 
# the Cretaceous was hotter (moving right) but less rainy than the absolute wettest 
# modern jungles (moving down from the 4000mm ceiling)."
# However, if you compare the 2023 point directly to the Cretaceous star, 
# the arrow would actually point Northeast (Hotter and Wetter). 
# The current arrow in the diagram is likely centered to show the shift from the 
# center of the modern tropical "envelope" to the new Cretaceous reality.

#The Green Box Ceiling: Modern tropical rainforests can receive up to 4500 mm of rain 
# (like in parts of the Pacific coast of Colombia). 
# The "Green Box" in the code represents that entire potential range.

# The Cretaceous Reality: While 2800 mm is a massive amount of rain, 
# it sits in the middle of the Y-axis. It was drier only compared to the absolute 
# wettest rainforests on Earth today.


########################################################################################
# Tectonic Velocity: How fast did the Amazon travel on the South American plate?
# Use Haversine formula to calculate distance between paleo-coordinates and modern
# coordinates...then divide by 100 million years.
########################################################################################

import math

def calculate_velocity(lat1, lon1, lat2, lon2, years):
  # Radius of Earth in kilometers
  R = 6371.0

  # Convert degrees to radians
  phi1, phi2 = math.radians(lat1), math.radians(lat2)
  dphi = math.radians(lat2 - lat1)
  dlambda = math.radians(lon2 - lon1)

  # Haversine formula
  a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
  c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
  distance_km = R * c

  # Convert to centimeters (1 km = 100,000 cm)
  distance_cm = distance_km * 100000
  velocity_cm_year = distance_cm / years

  return distance_km, velocity_cm_year

# Coordinates from results
dist, speed = calculate_velocity(mod_lat, mod_lon, results['paleo_lat'], results['paleo_lon'], 100_000_000)

print(f"--- Tectonic Velocity Report ---")
print(f"Total Distance Traveled: {round(dist, 2)} km")
print(f"Average Drift Speed: {round(speed, 2)} cm/year")

#########################################################################################
# Create a look-up table based on the CENOGRID or Phanerozoic Mean
# This mimics an API call by referencing known global mean temperature (GMT) for specific
# geological eras.
#########################################################################################

def get_global_paleo_temp(age):

  # Returns the estimated global mean temperature (GMT) for a given age (Ma).
  # Based on the Veizer et al. and Westerhold et al. climate curves.

  # Simplified look-up for major climate states.
  # Age: GMT in Celsius
  climate_history = [
      (0, 15.0),      # Modern
      (3, 19.0),       # Pliocene
      (50, 28.0),     # Eocene Hothouse
      (66, 23.0),     # K-Pg Boundary
      (100, 25.0),    # Mid-Cretaceous (Our target)
      (150, 22.0),    # Permian-Triassic
      (360, 14.0),    # Carboniferous (Icehouse)
      (500, 22.0)     # Cambrian
  ]

  # Sort and interpolate to get a smooth value for any 'age'
  ages = [x[0] for x in climate_history]
  temps = [x[1] for x in climate_history]

  # Use numpy to interpolate the temperature for the specific age
  return float(np.interp(age, ages, temps))

def climate_paleo_data_v3(lat, lon, age):
  # 1. Get modern local MAT
  modern_local_temp = get_modern_temp(lat, lon)

  # 2. Get global temperature shift
  modern_global_gmt = 15.0 # Modern global mean
  paleo_global_gmt = get_global_paleo_temp(age)

  # The 'Delta is how much hotter the world was overall
  global_delta = paleo_global_gmt - modern_global_gmt

  # 3. Apply Latitudinal Amplification
  # Greenhouse warming is not uniform: it's stronger at poles and weaker at equator
  # We find the paleo-latitude first

  url = "https://gws.gplates.org/reconstruct/reconstruct_points/"
  params = {"point": f"{lon},{lat}", "time": age, "model": "MULLER2016"}
  g_data = requests.get(url, params=params, verify=False).json()
  p_lat = g_data['coordinates'][0][1]

  # Polar Amplification Factor:
  # High latitudes feel the global delta more than the equator
  amplification = 1.0 - (0.5 * math.cos(math.radians(p_lat)))
  local_delta = global_delta * amplification

  return {
      "age": age,
      "global_mean_temp": paleo_global_gmt,
      "local_temp": round(modern_local_temp + local_delta, 2),
      "delta_applied": round(local_delta, 2)
  }

# Run the final logic
final_results = climate_paleo_data_v3(mod_lat, mod_lon, 100)
print(f"Global GMT at 100Ma: {final_results['global_mean_temp']}°C")
print(f"{place} local temp at 100Ma: {final_results['local_temp']}°C")

########################################################################################
# Check if the paleo-cordinate was under water or dry land by integrating a check against 
# the Paleo-DEM (Digital Elevation Model)
########################################################################################

# Use the MAcrostat API or simplified elevation lookup 
# Create a function that queries the GPlates/Macrostrat ecosystem to determine the
# Paleo-Lithology" or elevation for that speicifc tectonic plate at that time.

def check_paleo_elevation(lat, lon, age):

  # Checks if the reconstructed coordinates were above or below sea level.
  # Uses a simplified logic based on Mid-Cretaceous eustatic sea-level rise.

  # 1. Standard GPlates Reconstruction to get Paleo-latitude/Paleo-longitude

  url = "https://gws.gplates.org/reconstruct/reconstruct_points/"
  params = {"points": f"{lon},{lat}", "time": age, "model": "MULLER2016"}

  try:
      data = requests.get(url, params=params, verify=False).json()
      p_lon, p_lat = data['coordinates'][0]

      # 2. Query Macrostat/GPlates for Paleogeography
      # We check if the point falls within a 'marine' or 'terrestrial' polygon
      pg_url = "https://gws.gplates.org/utils/query_feature/"
      pg_params = {
      "lng": p_lon,
      "lat": p_lat,
      "time": age,
      "model": "MULLER2016",
      "layer": "paleogeography" # Specific GPlates layer for land/sea masks
      }

      pg_response = requests.get(pg_url, params=pg_params, verify=False).json()

      # Logic: If no feature is returned, it's often deep ocean.
      # If a feature is reutrned, we check the 'environment' attribute.
      if not pg_response or 'features' not in pg_response:
        return "Deep Marine", -2000 # Likely Oceanic Crust

      env = pg_response['features'][0]['properties'].get('environment', 'Unknown')

      # Mid-Cretaceous adjustment
      # Even if 'Land', many low-lying areas were flooded (Cretaceous Transgression)
      is_submerged = "Marine" in env or "Sea" in env

      return env, p_lat, p_lon

  except Exception as e:
      return f"Lookup Error: {e}", None, None

# --- Integrated Execution ---
env_type, p_late, p_lon = check_paleo_elevation(mod_lat, mod_lon, 100)

print(f"--- Paleogeography Report (100 Ma) ---")
print(f"Coordinate Environment: {env_type}")

if "Marine" in env_type:
    print("⚠️  NOTICE: This location was likely SUBMERGED under an inland sea.")
    print("The 'Rainforest' results would actually represent a Marine/Coastal biome.")
else:
    print("✅ LANDMASS: This location was above sea level (Terrestrial).")

##########################################################################################
# Querying specific polygons can be patchy in deep-time databases, so the eustatic sea 
# level adjustment can be used instead.
##########################################################################################

def check_submersion_risk(mod_lat, mod_lon, age):
    # 1. Get Modern Elevation using a simple open elevation API
    elev_url = f"https://api.open-elevation.com/api/v1/lookup?locations={mod_lat},{mod_lon}"
    try:
        elev_data = requests.get(elev_url).json()
        modern_elev = elev_data['results'][0]['elevation']
    except:
        modern_elev = 50 # Default for low-lying Amazon basin

    # 2. Define Cretaceous Sea Level Rise (Eustatic)
    # The Mid-Cretaceous was the "high-water mark" of the Phanerozoic
    cretaceous_sea_level_rise = 170 # meters above modern

    # 3. Simple Isostatic/Tectonic Estimate
    # The Amazon has subsided significantly due to sediment loading
    # We apply a "Deep Time" adjustment factor
    paleo_elev_estimate = modern_elev - cretaceous_sea_level_rise

    status = "TERRESTRIAL" if paleo_elev_estimate > 0 else "SUBMERGED (Epicontinental Sea)"
    
    return {
        "modern_elevation": modern_elev,
        "paleo_elevation_est": paleo_elev_estimate,
        "status": status
    }

elevation_report = check_submersion_risk(mod_lat, mod_lon, 100)
print(f"--- Elevation Analysis ---")
print(f"Modern Elevation: {elevation_report['modern_elevation']}m")
print(f"Cretaceous Relative Elevation: {elevation_report['paleo_elevation_est']}m")
print(f"Result: {elevation_report['status']}")


########################################################################################
# Deep Time Explorer: user input prompt, Habitability Index comparing human heat 
# tolerance against a theropod's biology.
########################################################################################

def get_habitability_report():
  geolocator = Nominatim(user_agent="paleo_explorer_v4")

  while True:
    print("\n" + "="*40)
    location_name = input("Enter a location (or 'q' to exit): ").strip()


    if location_name.lower() == 'q':
      print("Exiting program.")
      break

    # 1. Validate Location
    try:
        loc = geolocator.geocode(location_name)
        if not loc:
          print("f❌ '{location_name}' not recognized. Please try a city, country, or landmark.")
          continue
    except Exception as e:
        print(f"Connection error: {e}. Please try again.")
        continue

    lat, lon = loc.latitude, loc.longitude
    target_age = 100 # Mid-Cretaceous

    # 2. Get Real Modern Climate (To avoid NameError in plotting/logic)
    modern_temp, modern_precip = get_modern_climate(lat, lon)

    # 3. Tectonic Reconstruction
    g_url = "https://gws.gplates.org/reconstruct/reconstruct_points/"
    g_params = {"points": f"{lon},{lat}", "time": target_age, "model": "MULLER2016"}

    try:
      g_data = requests.get(g_url, params=g_params).json()
      p_lon, p_lat = g_data['coordinates'][0]
    except:
      print("Error connecting to GPlates server. Skipping tectonic check.")
      continue

    # 4. Land Versus Water Thermal Gradient
    # Check if point was submerged to adjust the "Hothouse Delta"
    is_marine = False
    pg_url = "https://gws.gplates.org/utils/query_feature/"
    pg_params = {"lng": p_lon, "lat": p_lat, "time": target_age, "model": "MULLER2016"}

    try:
      pg_res = requests.get(pg_url, params=pg_params, timeout=5).json()
      if pg_res['features'] and "Marine" in pg_res['features'][0]['properties'].get('environment', ''):
        is_marine = True
    except:
      # Fallback: if API fails, assume land unless it's deep ocean today
      is_marine = False

    # 5. Calculate paleo-temperature
    global_delta = 10.0 # 100Ma was ~10°C hotter globally
    amp = 1.0 - (0.5 *math.cos(math.radians(p_lat))) # Polar amplification
    local_delta = global_delta * amp

    # Water versus land adjustment:
    # oceans have higher heat capacity and therefore higher thermal inertia than land;
    # land heats up much more in a Hothouse climate

    if is_marine:
      local_delta *= 0.65 # Marine cooling/damping effect
      env_label = "🌊 Marine/Coastal"
    else:
      local_delta *= 1.2  # Continental heating effect
      env_label = "🌋 Terrestrial/Inland"

    modern_baseline = 15 + (12 * math.cos(math.radians(lat)))
    paleo_temp = round(modern_baseline + local_delta, 2)

    # 6. Paleobiology database (PBDB) querying actual fossil records.
    # This turns the code from a predictive model to verifiable to actual data.
    pbdb_url = "https://paleobiodb.org/data1.2/occs/list.json"
    
    # Using lngmin/latmin instead of latlng to resolve the 400 error
    pbdb_params = {
        "lngmin": lon - 0.5,
        "lngmax": lon + 0.5,
        "latmin": lat - 0.5,
        "latmax": lat + 0.5,
        "interval": "Cretaceous",
        "show": "ident,class",
        "limit": 10
    }

    fossil_list = []
    try:
        # verify=False handles the SSL issues encountered earlier
        response = requests.get(pbdb_url, params=pbdb_params, verify=False, timeout=10)
        
        if response.status_code == 200:
            data = response.json().get('records', [])
            for r in data:
                # In standard v1.2 (without 'vocab'), the keys are 'tna' and 'cll'
                name = r.get('tna')
                t_class = r.get('cll', 'Unknown')
                if name and name not in fossil_list:
                    fossil_list.append(f"{name} ({t_class})")
            
            fossil_list = fossil_list[:5]
        else:
            print(f"DEBUG: Status {response.status_code}, Response: {response.text}")
            
    except Exception as e:
        fossil_list = [f"Connection error: {e}"]
    
    

    # 6. Habitability Scoring
    # Human: optimal at 22°C. Drastic drop after 35°C (wet bulb/heat stroke limits).
    human_score = max(0, min(100, 100 - (abs(paleo_temp - 22) ** 1.5) * 2))

    # Dinosaur: optimal at 32°C. Large theropods handled heat better than cold.
    dino_score = max(0, min(100, 100 - (abs(paleo_temp - 32) ** 1.3) * 2))

    # 7. Display Results
    print(f"\n --- 100 Ma Report: {location_name.upper()} ---")
    print(f"Modern Coordinates:   {round(lat,2)}, {round(lon,2)}")
    print(f"Paleo-Coordinates:    {round(p_lat,2)},{round(p_lon,2)}")
    print(f"Paleo-Latitude:       {round(lat,2)}°")
    print(f"Above or Under Water: {env_label}")
    print(f"Paleo-temperature:    {paleo_temp}°C ({round(paleo_temp * 9/5 + 32, 1)}°F)")
    print(f"\n --- Ground Truth (🐚 Fossils Found Nearby) ---")
    if fossil_list:
        for f in fossil_list: print(f" - {f}")
    else:
        print("No specific fossils recorded in this sector yet.")
    print(f"\n--- Habitability Indices ---")
    print(f"👤Human:                {round(human_score)}/100")
    print(f"🦖Dinosaur:             {round(dino_score)}/100")

    # 8. Biome override logic
    # Check if the fossils found suggest a marine environment
    marine_classes = ['Bivalvia', 'Cephalopoda', 'Gastropoda', 'Chondrichthyes', 'Actinopterygii']
    found_marine = any(m_class in str(fossil_list) for m_class in marine_classes)

    if found_marine and not is_marine:
      env_label = "🌊 Marine (Overriden by Fossil Evidence)"
      # Adjust temperature slightly: water stays cooler than inland land
      paleo_temp -= 3.0

get_habitability_report()
                            

