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

  url = f"https://archive-api.open-meteo.com/v1/archive?latitude={loc['lat']}&longitude={loc['lon']}&start_date=2023-01-01&end_date=2023-12-31&daily=precipitation_sum,temperature_2m_mean&timezone=UTC"
  response = requests.get(url).json()

  try:
    #  Acess the daily data
    daily_data = response['daily']


    # Calculate annual sums and averages

    annual_precip = sum(response['daily']['precipitation_sum'])
    temp_list = daily_data['temperature_2m_mean']
    avg_temp = sum(temp_list) / len(temp_list)


    # Append

    data_list.append({"Location": loc['name'],
    "Annual_Precip_mm": round(annual_precip, 2),
    "Avg_Temp_C": round(avg_temp, 2)

    })
  except KeyError:
    print(f"Could not retrieve data for {loc['name']}. API Response: {response}")


# Create DataFrame
df = pd.DataFrame(data_list)

print("--- Bioclimate Variable Analysis (2023) ---")
print(df)

import matplotlib.pyplot as plt
import seaborn as sns

# Set the style
sns.set_theme(style="whitegrid")

# Create the figure
plt.figure(figsize=(10, 7))

# Plot the points
plot = sns.scatterplot(
    data=df,
    x="Avg_Temp_C",
    y="Annual_Precip_mm",
    hue="Location",
    s=200,
    palette="viridis"
)

# Add labels and title
plt.title("Whittaker-style Biome Distribution (2023 Data)", fontsize=16)
plt.xlabel("Average Annaul Temperature (°C)", fontsize=12)
plt.ylabel("Annaul Precipitation (mm)", fontsize=12)

# Annotate each point with its name

for i in range(df.shape[0]): # df.shape[0] is 4
  plt.text(
      df.Avg_Temp_C[i] + 0.2,
      df.Annual_Precip_mm[i] + 20,
      df.Location[i],
      fontsize=10
  )

##########################################################################################
# The "Gradient" Project: Building a Transect
##########################################################################################

import numpy as np

# Start: Deep Amazon Rainforest (-3.0, -60.0)
# End: Edge of the Brazilian Cerrado/Savanna (-15.0, -50.0)
lat_start, lon_start = -3.0, -60.0
lat_end, lon_end     = -15.0, -50.0

# Generate 10 evenly spaced points
lats = np.linspace(lat_start, lat_end, 10)
lons = np.linspace(lon_start, lon_end, 10)

transect_locations = []
for i in range(10):
  transect_locations.append({
    "name": f"Point {i + 1}",
    "lat": lats[i],
    "lon": lons[i]
  })

# Fetch and plot "fall-off", graphing precipitation versus latitude

transect_data = []

for loc in transect_locations:
  url = url = f"https://archive-api.open-meteo.com/v1/archive?latitude={loc['lat']}&longitude={loc['lon']}&start_date=2023-01-01&end_date=2023-12-31&daily=precipitation_sum&timezone=UTC"
  res = requests.get(url).json()

  if 'daily' in res:
    total_p = sum(res['daily']['precipitation_sum'])
    transect_data.append({"Latitude": loc['lat'], "Precip": total_p})

df_transect = pd.DataFrame(transect_data)

# Visualizing the change
plt.figure(figsize=(10, 5))
plt.plot(df_transect['Latitude'], df_transect['Precip'], marker='o', color='green', linestyle='--')
plt.title("The Amazon-to-Savanna Rainfall Gradient")
plt.xlabel("Latitude (Moving South)")
plt.ylabel("Annual Precipitation (mm)")
plt.grid(True)
plt.show()



#########################################################################################
# Define a longer transect: From Equator (Rainforest) to Subtropics (Savanna/Shrub)
# from Amazon equator down into the seasonal Chaco/Cerrado
#########################################################################################
lats = np.linspace(0, -20, 10) 
lons = np.linspace(-60, -60, 10) # Staying on the same longitude line

transect_data = []

for i in range(len(lats)):
    url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lats[i]}&longitude={lons[i]}&start_date=2023-01-01&end_date=2023-12-31&daily=precipitation_sum&timezone=UTC"
    res = requests.get(url).json()
    
    if 'daily' in res:
        precip_values = res['daily']['precipitation_sum']
        total_p = sum(precip_values)
        
        # Calculate Seasonality (Coefficient of Variation)
        # Higher values = more extreme dry/wet seasons
        monthly_precip = [sum(precip_values[j:j+30]) for j in range(0, 360, 30)]
        std_dev = np.std(monthly_precip)
        mean_p = np.mean(monthly_precip)
        seasonality = (std_dev / mean_p) * 100 if mean_p > 0 else 0
        
        transect_data.append({
            "Latitude": lats[i], 
            "Total_Precip": total_p, 
            "Seasonality_Index": seasonality
        })

df_gradient = pd.DataFrame(transect_data)

fig, ax1 = plt.subplots(figsize=(12, 6))

# Plot Total Precipitation
ax1.set_xlabel('Latitude (Moving away from Equator)')
ax1.set_ylabel('Annual Precipitation (mm)', color='tab:blue')
ax1.plot(df_gradient['Latitude'], df_gradient['Total_Precip'], color='tab:blue', marker='o', linewidth=3, label='Total Rain')
ax1.tick_params(axis='y', labelcolor='tab:blue')

# Create a second y-axis for Seasonality
ax2 = ax1.twinx()
ax2.set_ylabel('Seasonality Index (Higher = More Seasonal)', color='tab:red')
ax2.plot(df_gradient['Latitude'], df_gradient['Seasonality_Index'], color='tab:red', marker='s', linestyle='--', label='Seasonality')
ax2.tick_params(axis='y', labelcolor='tab:red')

plt.title("Bio-Climatic Shift: Rainfall Amount vs Seasonality")
fig.tight_layout()
plt.show()




