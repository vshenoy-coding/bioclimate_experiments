import pandas as pd
import requests

# Example: Get precipitation for a point in the Amazon (Rainforest)
# and a point in the Sahel (Savanna/Shrubland)
# as well as some more biomes
locations = [
  {"name": "Amazon", "lat": -3.46, "lon": -62.21},
  {"name": "Sahel", "lat": 15.00, "lon": 0.00},
  {"name": "Sahara (Desert)", "lat": 23.41, "lon": 25.66},
  {"name": "Congo (Rainforest)", "lat": -0.22, "lon": 23.61}
]

data_list = []

for loc in locations:
  url = f"https://archive-api.open-meteo.com/v1/archive?latitude={loc['lat']}&longitude={loc['lon']}&start_date=2023-01-01&end_date=2023-12-31\
  &daily=precipitation_sum,temperature_2m_mean,daily&timezone=UTC"

  response = requests.get(url).json()

  # Calculate annual sums and averages
  annual_precip = sum(response['daily']['precipitation_sum'])
  avg_temp = sum(response['daily']['temperature_2m_mean']) / len(response['daily']['temperature_2m_mean'])

  # Append
  data_list.append({"Location": loc['name'], 
                    "Annual_Precip_mm": round(annual_precip, 2),
                    "Avg_Temp_C": round(avg_temp, 2)
                    })

df = pd.DataFrame(data_list)


print("--- Bioclimate Variable Analysis (2023) ---")
print(df)
