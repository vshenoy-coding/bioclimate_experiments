import os
import numpy as np
import matplotlib.pyplot as plt

!pip install cartopy
import cartopy.crs as ccrs

!pip install pygplates
import pygplates

import logging
logging.getLogger('gplately').setLevel(logging.CRITICAL)

!pip install gplately
import gplately

from IPython.display import Video, display

def generate_tectonic_frames(target_lat, target_lon, location_name="Target Location", start_time=300, model_name="Merdith2021"):
    """
    # Initializes the Plate Model
    # Generates animation frames tracking a specific lat/lon through time.
    """
    # --- Initialization ---
    print(f"Initializing {model_name} model...")
    data_server = gplately.download.DataServer(model_name)
    rot_model, topo_features, static_polys = data_server.get_plate_reconstruction_files()
    model = gplately.PlateReconstruction(rot_model, topo_features, static_polys)
    coastlines, continents, COBs = data_server.get_topology_geometries()

    # Create folder for frames
    frame_dir = 'animation_frames'
    if not os.path.exists(frame_dir):
        os.makedirs(frame_dir)
    else:
        # Clean existing frames to prevent mixing old/new runs
        for f in os.listdir(frame_dir):
            if f.endswith('.png'):
                os.remove(os.path.join(frame_dir, f))

    # --- Plate Identification
    # We find out which plate point belongs to today

    point_today = pygplates.PointOnSphere(target_lat, target_lon)
    feature_today = pygplates.Feature()
    feature_today.set_geometry(point_today)
    
    partitioned_feature = pygplates.partition_into_plates(static_polys, rot_model, feature_today)
    plate_id = partitioned_feature[0].get_reconstruction_plate_id()
    print(f"{location_name} identified on Plate ID: {plate_id}")

    history_lats, history_lons = [], []

    # Define time steps (Past to Present)
    # range() creates integers, which we will convert to floats inside the loop
    time_steps = range(start_time, -1, -10)

    print(f"Tracking {location_name} from {start_time} Ma to Present...")

    for time in time_steps:

        recon_time = float(time)

        fig = plt.figure(figsize=(12, 7))
        ax = plt.axes(projection=ccrs.Mollweide())
        ax.set_facecolor('#f0f8ff')

        # Plot Geography
        gPlot = gplately.PlotTopologies(model, time=time, continents=continents,
                                        coastlines=coastlines, COBs=COBs)
        gPlot = gplately.PlotTopologies(model, time=time, continents=continents,
                                        coastlines=coastlines, COBs=COBs)
        
        gPlot.plot_continents(ax, facecolor='#e6ccb2', edgecolor='none', alpha=0.9)
        gPlot.plot_coastlines(ax, color='#222222', linewidth=0.5)

 
        # Dynamic Point Reconstruction
        try:
            
            # Move the point by getting the specific rotation for its Plate ID
            rotation = model.rotation_model.get_rotation(recon_time, plate_id)
            reconstructed_point = rotation * point_today
            p_lat, p_lon = reconstructed_point.to_lat_lon()

            history_lats.append(p_lat)
            history_lons.append(p_lon)

            # Plot the trail (history
            if len(history_lons) > 1:
                ax.plot(history_lons, history_lats, color='blue', linewidth=1.5,
                        linestyle='--', transform=ccrs.PlateCarree(), alpha=0.5)
            

            # Plot the current position (the red dot)
            ax.plot(p_lon, p_lat, 'ro', markersize=10, transform=ccrs.PlateCarree(),
                    markeredgecolor='white', zorder=10)
            
        except Exception as e:
            print(f"Could not reconstruct point at {time} Ma: {e}")

        # UI Elements
        ax.text(0.05, 0.05, f"{time} Ma", transform=ax.transAxes,
                fontsize=24, fontweight='bold', color='darkred',
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

        plt.title(f"Paleogeographic Journey of {location_name}", fontsize=16)

        # Save Frame
        plt.savefig(f"{frame_dir}/frame_{time:03d}.png", bbox_inches='tight', dpi=100)
        plt.close()

    print("Frames complete. Compiling video...")

    # Compile Video (Colab/Linux compatible)
    video_name = "location_tracker_movie.mp4"
    os.system(f"ffmpeg -y -r 7 -pattern_type glob -i '{frame_dir}/*.png' "
              f"-vf 'pad=ceil(iw/2)*2:ceil(ih/2)*2' "
              f"-vcodec libx264 -crf 24 -pix_fmt yuv420p {video_name}")

# --- Execution ---
if __name__ == "__main__":
    # Example: Norman, OK
    generate_tectonic_frames(35.22, -97.44, "Norman, OK", start_time=300)

    # Display if in Colab
    if os.path.exists("location_tracker_movie.mp4"):
        display(Video("location_tracker_movie.mp4", embed=True))
