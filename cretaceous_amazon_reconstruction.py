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
paleo_lat, paleo_lon = get_paleo_location(-3.0, -60.0, 100)
print(f"Paleo-Latitude: {paleo_lat}, Paleo-Longitude: {paleo_lon}")
  
