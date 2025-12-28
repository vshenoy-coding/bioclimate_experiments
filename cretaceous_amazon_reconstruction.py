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


import requests

def get_paleo_location(lat, lon, age):
  # This calls the official GPlates engine directly
  url = "https://gws.gplates.org/reconstruct/reconstruct_points/"
  params = {
  "points": f"{lon},{lat}",
  "time": age,
  "model": "MULLER2016"
  }
  data = requests.get(url, params=params).json()
  return data['coordinates'][0][1], data['coordinates'][0][0]

# 100 million years ago Amazon
# call get_paleo_location function and pass it modern lat-lon points of Amazon

p_lat, p_lon = get_paleo_location(-3.0, -60.0, 100)
print(f"Paleo-Latitude: {p_lat}, Paleo-Longitude: {p_lon}")


##########################################################################################
# Paleoclimate Modeling
##########################################################################################

# Combine teconic rotation with a climate estimate based on published Cretaceous model data

def climate_paleo_data(lat, lon, age):
  # 1. Rotate the point to find its  ancient latitude
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

  modern_equatorial_avg = 27
  est_cretaceous_temp = modern_equatorial_avg + 6 # Result: 33°C

  # Estimate Precipitation
  # The widening Atlantic 'gateway' created high humidity
  est_cretaceous_precip = 2800

  return {
    "paleo_lat": round(p_lat, 2),
    "paleo_temp": est_cretaceous_temp,
    "paleo_precip": est_cretaceous_precip
  }

# Run for the Amazon
results = climate_paleo_data(-3.0, -60.0, 100)

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
modern_temp = 27
modern_precip = 1834

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
