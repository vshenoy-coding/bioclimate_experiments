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

def get_modern_temp(lat, lon):
    # Updated URL to the standard Open-Meteo Archive endpoint
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "daily": "temperature_2m_mean",
        "timezone": "auto"
    }

    # Added verify=False to ignore the SSL UNRECOGNIZED_NAME error
    response = requests.get(url, params=params, verify=False)
    
    if response.status_code != 200:
        print(f"Weather API Error: {response.status_code}")
        return 27.0 # Fallback to standard tropical temp if API fails
        
    data = response.json()
    temps = data['daily']['temperature_2m_mean']
    
    # Filter out any None values (days with missing data)
    valid_temps = [t for t in temps if t is not None]
    
    if not valid_temps:
        return 27.0
        
    return sum(valid_temps) / len(valid_temps)

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
print(f"Estimated Surface Temperature: {results['paleo_temp']}°C")
print(f"Estimated Annual Rainfall: {results['paleo_precip']} mm")

#########################################################################################
# Dual-Whittaker Code: entire x-axis has shifted, considering 100 million years ago
# "Hothouse Earth" climate was entirely outside the modern tropical climate
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

# The direction of that arrow represents the net vector of climate change between two vastly different 
# climate of Earth's history.

# To understand why it points southeast (moving "down" and "right") from the perspective 
# of the modern green box, we have to look at the relationship between the modern data 
# points and the Cretaceous results.
# 1. The "Right" Shift (X-axis: Temperature)
# The arrow points toward the right because the Cretaceous was a "Hothouse" climate.
# Modern Average: ~27°C.
# Cretaceous Average: ~33°C.
# Result: A +6°C increase pushes the point significantly to the right, far outside the modern "Greenbox" thermal limit (which usually caps at 30°C).
# 2. The "Downward" Shift (Y-axis: Precipitation)
# This is where the visual can be counter-intuitive. 
# In the plot of the Hothouse Shift, the arrow points "down" relative to the 
# top of the green box because of how we define "Modern Tropical Rainforests."

# The Modern Green Box: This box typically represents the entire range of modern tropical biomes, which can extend up to 4,500 mm of rain in places like the Chocó or the upper Amazon.
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


########################################################################################
# Previously hard-coded
########################################################################################


