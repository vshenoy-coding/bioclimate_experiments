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

#########################################################################################
# Identify the "Limiting Factor": the single month with the lowest rainfall for each point
# If the driest month receives less than 60mm, that is considered a "dry" month for
# tropical ecosystems.
#########################################################################################

transect_data_drylimit = []

for loc in transect_locations:
  url = url = f"https://archive-api.open-meteo.com/v1/archive?latitude={loc['lat']}&longitude={loc['lon']}&start_date=2023-01-01&end_date=2023-12-31&daily=precipitation_sum&timezone=UTC"
  res = requests.get(url).json()

  if 'daily' in res:
    precip_values = res['daily']['precipitation_sum']

  # Group daily data into 12 months (roughly 30 days each)
  monthly_totals = [sum(precip_values[i:i+30]) for i in range(0, 360, 30)]

  driest_month_value = min(monthly_totals)
  annual_total = sum(precip_values)

  transect_data_drylimit.append({
    "Latitude": loc['lat'],
    "Annual_Precip": annual_total,
    "Driest_Month_mm": driest_month_value
  })

df_drylimit = pd.DataFrame(transect_data_drylimit)

plt.figure(figsize=(12, 6))

# Plot the driest month values
plt.plot(df_drylimit['Latitude'], df_drylimit['Driest_Month_mm'], marker='s', color='orange', label='Driest Month Rainfall')

# Add the biological threshold line (60mm)
plt.axhline(y=60, color='red', linestyle='--', label='Rainforest Threshold (60mm)')

plt.title("The 'Dry Season' Barrier Across the Transect")
plt.xlabel("Latitude (Equator to South)")
plt.ylabel("Precipitation (mm)")
plt.legend()

# For tropical ecosystems:
# The Evergreen Zone: If the driest month stays above 60mm, 
# the biome is likely an Evergreen Tropical Rainforest.

# The Deciduous Zone: If it drops below 60mm for 1-3 months, 
# you get Tropical Seasonal Forests.

# The Savanna Zone: If the driest month hits 0mm and stays low for 5+ months, 
# you are firmly in Savanna territory, regardless of how high the annual total was.

# Calculate drought duration

drought_analysis = []

for loc in transect_locations:
    url = f"https://archive-api.open-meteo.com/v1/archive?latitude={loc['lat']}&longitude={loc['lon']}&start_date=2023-01-01&end_date=2023-12-31&daily=precipitation_sum&timezone=UTC"
    res = requests.get(url).json()

    if 'daily' in res:
        precip_values = res['daily']['precipitation_sum']
        
        # Create 12 monthly totals
        monthly_totals = [sum(precip_values[i:i+30]) for i in range(0, 360, 30)]
        
        # Count months where precipitation is less than 60mm
        dry_months_count = sum(1 for month in monthly_totals if month < 60)

        drought_analysis.append({
            "Latitude": loc['lat'], 
            "Dry_Months": dry_months_count
        })

df_drought = pd.DataFrame(drought_analysis)

# Visualize how many months of "biological stress" the vegetation faces as you move south

plt.figure(figsize=(10, 6))
plt.bar(df_drought['Latitude'].astype(str), df_drought['Dry_Months'], color='peru')

plt.title("Number of Dry Months (< 60mm) Along the Transect")
plt.xlabel("Latitude")
plt.ylabel("Count of Dry Months")
plt.xticks(
  ticks = range(len(df_drought)),
  labels=[f"{round(float(lat), 2)}" for lat in df_drought['Latitude']],
  rotation=45)

plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()
  
#########################################################################################
# Mapping the Predictions: Put the points on a map
#########################################################################################

import folium

# 1. Setup the Map centered on your transect
m = folium.Map(location=[-9, 60], zoom_start=5, tiles='CartoDB positron')

# 2. Add points with colors based on Dry Month count
for index, row in df_drought.iterrows():
  # Define colors
  if row['Dry_Months'] <= 3:
    color = 'darkgreen' # Rainforest
    label = "Evergreen Rainforest"
  elif 4 <= row['Dry_Months'] <= 6:
    color = 'orange'    # Deciduous
    label = "Tropical Deciduous Forest"
  else: 
    color = 'red'       # Savanna
    label = "Savanna / Shrubland"

  folium.CircleMarker(
    location=[row['Latitude'], -60], # Using the constant longitude from your transect
    radius=8,
    popup=f"Lat: {round(row['Latitude'], 2)}<br>Dry Months: {row['Dry_Months']}<br>Predicted: {label}",
    color=color,
    fill=True,
    fill_opacity=0.7
  ).add_to(m)

# Display the map
m
  
#########################################################################################
# Is it getting drier? Compare to 2003
#########################################################################################
comparison_data = []

for loc in transect_locations:
    # 1. Fetch 2003 Data
    url_2003 = f"https://archive-api.open-meteo.com/v1/archive?latitude={loc['lat']}&longitude={loc['lon']}&start_date=2003-01-01&end_date=2003-12-31&daily=precipitation_sum&timezone=UTC"
    res_2003 = requests.get(url_2003).json()
    
    # 2. Fetch 2023 Data (Re-running to ensure perfect alignment)
    url_2023 = f"https://archive-api.open-meteo.com/v1/archive?latitude={loc['lat']}&longitude={loc['lon']}&start_date=2023-01-01&end_date=2023-12-31&daily=precipitation_sum&timezone=UTC"
    res_2023 = requests.get(url_2023).json()

    if 'daily' in res_2003 and 'daily' in res_2023:
        # Calculate Dry Months for 2003
        m_2003 = [sum(res_2003['daily']['precipitation_sum'][i:i+30]) for i in range(0, 360, 30)]
        dry_2003 = sum(1 for m in m_2003 if m < 60)
        
        # Calculate Dry Months for 2023
        m_2023 = [sum(res_2023['daily']['precipitation_sum'][i:i+30]) for i in range(0, 360, 30)]
        dry_2023 = sum(1 for m in m_2023 if m < 60)

        comparison_data.append({
            "Latitude": round(loc['lat'], 2),
            "Dry_Months_2003": dry_2003,
            "Dry_Months_2023": dry_2023,
            "Change": dry_2023 - dry_2003
        })

df_comp = pd.DataFrame(comparison_data)
print(df_comp)

# Visualize the shift through a grouped bar chart

# Setting up the plot
x = np.arange(len(df_comp['Latitude']))
width = 0.35

fig, ax = plt.subplots(figsize=(12, 6))
rects1 = ax.bar(x - width/2, df_comp['Dry_Months_2003'], width, label='2003 (Past)', color='skyblue')
rects2 = ax.bar(x + width/2, df_comp['Dry_Months_2023'], width, label='2023 (Recent)', color='salmon')

ax.set_ylabel('Number of Dry Months (< 60mm)')
ax.set_title('20-Year Shift in Dry Season Duration')
ax.set_xticks(x)
ax.set_xticklabels(df_comp['Latitude'])
ax.legend()

plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()

# To conclude the investigation, you now have three distinct pieces of evidence
# of expanding dry zones:

# Whittaker Plot: Shows the locations are on the edge of the tropical forest/savanna space.
# The Gradient: Shows the physical drop in rainfall moving south.
# The Temporal Shift: Shows that the "Dry Season Barrier" is expanding north.
