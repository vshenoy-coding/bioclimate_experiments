import matplotlib.pyplot as plt
import xarray as xr

# 1. Create a grid of latitudes and longitudes
lats = np.linspace(-90, 90, 180)
lons = np.linspace(-180, 180, 360)

# 2. Generate synthetic temperature data 
# Formula: Warmer at equator (0 lat), colder at poles
# We use a cosine function of latitude to simulate global climate
lon2d, lat2d = np.meshgrid(lons, lats)
temp_values = 30 * np.cos(np.deg2rad(lat2d)) + np.random.normal(0, 2, lat2d.shape)

# 3. Package it into an xarray (mimicking WorldClim format)
bio1_fake = xr.DataArray(
    temp_values, 
    coords=[lats, lons], 
    dims=['lat', 'lon'], 
    name="BIO1"
)

# 4. Plot the "global" result
plt.figure(figsize=(10, 5))
bio1_fake.plot(cmap='RdBu_r')
plt.title("Synthetic Global Mean Temperature (BIO1 Proxy)")
plt.show()


# 5. Select a region using .sel()
# Unlike .clip_box(), .sel() works directly on the defined coordinates
africa_climate = bio1_fake.sel(lat=slice(-35, 35), lon=slice(-20, 50))

# 6. Plot the selected region
plt.figure(figsize=(7, 7))
africa_climate.plot(cmap='YlOrRd')
plt.title("Clipped Region: African Climate Proxy")
plt.show()

###
# Global Cooling and Warming in an Idealized Model
###

# Define the temperature range for the colorbar to keep it consistent
# This ensures a +4 degree map looks visibly redder than a -4 degree map
min_temp = -10 
max_temp = 45

# From the Severe Icehouse Climate of the Last Glacial Maximum (-6°C colder than preindustrial at its peak) to the Hothouse Climate PETM (up to 12°C warmer than preindustrial at its peak)
for i in range(-6, 13, 1):
  print(f'Create a {i}°C scenario')
  scenario = bio1_fake + i

  # Initialize the figure
  plt.figure(figsize=(12, 5))
  
  # Plot with a fixed scale
  # 'RdBu_r' is a standard "Red-Blue" diverging palette for temperature
  scenario.plot(cmap='RdBu_r', vmin=min_temp, vmax=max_temp)
    
  # Formatting the title and labels
  plt.title(f'Bioclimatic Scenario: Annual Mean Temperature ({i}°C)')
  plt.xlabel("Longitude")
  plt.ylabel("Latitude")
    
  # Show the plot for this specific iteration
  plt.title(f'Future Scenario: Annual Mean Temperature ({i}°C)')
  plt.show()


###
# Subplot would be even more concise and save space
###

# Create the figure and a 3x6 grid of subplots
fig, axes = plt.subplots(4, 5, figsize=(24, 12))
axes = axes.flatten()  # Turn the 4x5 matrix into a simple list of 20 spots
# Go up to 13°C warmer than preindustrial to cover all 4x5 spots

# Loop through 18 scenarios (from -6 to +13)
for idx, i in enumerate(range(-6, 14, 1)):
    scenario = bio1_fake + i
    ax = axes[idx]
    
    # Plot onto the specific subplot (ax=ax)
    # add_colorbar=False keeps the layout clean; we can add one big one later
    scenario.plot(ax=ax, cmap='RdBu_r', vmin=min_temp, vmax=max_temp, add_colorbar=False)
    
    # Clean up the subplots
    ax.set_title(f'Scenario: {i}°C', fontsize=10)
    ax.set_xticks([]) # Remove coordinates to save space
    ax.set_yticks([])
    ax.set_xlabel('')
    ax.set_ylabel('')

# Add a single colorbar for the whole figure
sm = plt.cm.ScalarMappable(cmap='RdBu_r', norm=plt.Normalize(vmin=min_temp, vmax=max_temp))
cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7]) # [left, bottom, width, height]
fig.colorbar(sm, cax=cbar_ax, label='Temperature (°C)')

plt.suptitle("Global Temperature Sensitivity Analysis (-6°C to +12°C)", fontsize=20, y=0.95)
plt.subplots_adjust(wspace=0.1, hspace=0.3)
plt.show()

###
For loop adopted from the individual warming scenario code below:
#
# Create a +2 degree warming scenario
#warming_scenario = bio1_fake + 2.0

# Calculate the difference to visualize the "Anomalies"
# In this case, it will be +2.0 everywhere
#anomaly2 = warming_scenario - bio1_fake

#plt.figure(figsize=(10, 5))
#warming_scenario.plot(cmap='magma')
#plt.title("Future Scenario: Annual Mean Temperature (+2.0°C)")
#plt.show()

# Create a +3 degree warming scenario
#warming_scenario = bio1_fake + 2.0

# Calculate the difference to visualize the "Anomalies"
# In this case, it will be +3.0 everywhere
#anomaly3 = warming_scenario - bio1_fake

plt.figure(figsize=(10, 5))
warming_scenario.plot(cmap='magma')
plt.title("Future Scenario: Annual Mean Temperature (+3.0°C)")
plt.show()

# Create a +3 degree warming scenario
warming_scenario = bio1_fake + 2.0

# Calculate the difference to visualize the "Anomalies"
# In this case, it will be +4.0 everywhere
anomaly4 = warming_scenario - bio1_fake

plt.figure(figsize=(10, 5))
warming_scenario.plot(cmap='magma')
plt.title("Future Scenario: Annual Mean Temperature (+4.0°C)")
plt.show()

