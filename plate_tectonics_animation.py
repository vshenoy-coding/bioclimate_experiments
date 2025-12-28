#! pip install gplately cartopy pygplates
import gplately
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import pygplates
import os
from IPython.display import Video

# Initialize the data server and model
model_name = "Muller2019"
data_server = gplately.download.DataServer(model_name)
rot_model, topo_features, static_polys = data_server.get_plate_reconstruction_files()
model = gplately.PlateReconstruction(rot_model, topo_features, static_polys)
coastlines, continents, COBs = data_server.get_topology_geometries()

# Create a folder to store images
frame_dir = '/content/animation_frames'
os.makedirs(frame_dir, exist_ok=True)

# Define the time steps (e.g., every 10 million years)
time_steps = range(250, -1, -10)

print("Starting frame generation...")

for time in time_steps:
  # Create the plotter for this specific time
  gPlot = gplately.PlotTopologies(model, time=time, continents=continents,
                                  coastlines=coastlines, COBs=COBs)

  fig = plt.figure(figsize=(10, 5))
  ax = plt.axes(projection=ccrs.Mollweide())
  ax.set_global()
  ax.set_facecolor('#f0f8ff')

  # Use the hasattr safety checks you requested
  if hasattr(gPlot, 'plot_continents'):
    gPlot.plot_continents(ax, facecolor='#e6ccb2', edgecolor='none', alpha=0.9)
  if hasattr(gPlot, 'plot_coastlines'):
    gPlot.plot_coastlines(ax, color='#222222', linewidth=0.5)

  plt.title(f"Geological Time: {time} Ma")

  # Save the frame
  plt.savefig(f"{frame_dir}/frame_{time:03d}.png", bbox_inches='tight', dpi=100)
  plt.close() # Close to save memory
  print(f"Frame for {time} Ma saved.")

print("All frames generated")

# Convert Frames to Video

# This command takes the images and compiles them at 7 frames per second
# The -vf "pad=..." filter ensures the width and height are divisible by 2
!ffmpeg -y -r 7 -pattern_type glob -i '/content/animation_frames/*.png' \
-vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" \
-vcodec libx264 -crf 25 -pix_fmt yuv420p plate_movie.mp4

# Display video in Colab

# Check if file was created and display it
if os.path.exists("plate_movie.mp4"):
  print("Success! Displaying movie...")
  display(Video("plate_movie.mp4", embed=True))
else:
  print("Video file not found. Check the ffmpeg output above for errors.")
