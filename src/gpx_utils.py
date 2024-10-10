"""
GPX Utils
"""
import streamlit as st
import gpxpy
import gpxpy.gpx
import pandas as pd
import plotly.express as px
from datetime import timedelta
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline
import numpy as np
from moviepy.editor import VideoClip
import plotly.graph_objects as go
from math import radians, sin, cos, atan2, degrees
from moviepy.editor import ImageSequenceClip


def parse_gpx(gpx_file: str) -> pd.DataFrame:

    gpx = gpxpy.parse(gpx_file)
    points = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                points.append({
                    'latitude': point.latitude,
                    'longitude': point.longitude,
                    'elevation': point.elevation,
                    'time': point.time,
                    'speed': point.speed if point.speed is not None else 0  # Handle missing speed
                })
    return pd.DataFrame(points)

def gpx_to_pd(gpx: gpxpy.gpx.GPX) -> pd.DataFrame:
    points = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                points.append({
                    'latitude': point.latitude,
                    'longitude': point.longitude,
                    'elevation': point.elevation,
                    'time': point.time,
                    'speed': point.speed if point.speed is not None else 0  # Handle missing speed
                })
    return pd.DataFrame(points)


def gpx_visualization(df: pd.DataFrame, map_style: str = 'open-street-map', line_color: str = '#FF0000') -> px.line_mapbox:

    fig = px.line_mapbox(df, lat="latitude", lon="longitude", height=500)
    fig.update_layout(mapbox_style=map_style, margin={"r":0,"t":0,"l":0,"b":0}, 
                      mapbox_center={"lat": df['latitude'].mean(), "lon": df['longitude'].mean()}, 
                      mapbox_zoom=12)
    fig.update_traces(line=dict(color=line_color))

    return fig


def save_gpx(df: pd.DataFrame, filename: str) -> None:

    new_gpx = gpxpy.gpx.GPX()
    new_track = gpxpy.gpx.GPXTrack()
    new_gpx.tracks.append(new_track)
    new_segment = gpxpy.gpx.GPXTrackSegment()
    new_track.segments.append(new_segment)
    
    for _, row in df.iterrows():
        new_point = gpxpy.gpx.GPXTrackPoint(
            latitude=row['latitude'],
            longitude=row['longitude'],
            elevation=row['elevation'],
            time=row['time']
        )
        new_segment.points.append(new_point)
    
    with open(filename, "w") as f:
        f.write(new_gpx.to_xml())

def gpx_animation(df: pd.DataFrame, fps: int = 30, filename: str='gpx_animation',
                  create_compass: bool=False,
                  animation_style: str='Matplotlib Animation', bg_color: str='None',
                  bg_alpha: float=1,
                  main_line_color: str='#FF0000', bg_line_color: str='#000000',
                  gpx_map_line_width: float=2, 
                  compass_heading_color: str='#0000FF', compass_axis_fontsize: int=10,
                  compass_line_width: float=1,
                  compass_axis_thickness: float=1, overwrite_duration: bool=False) -> None:
    """
    Requires matplotlib <= 3.6.0 for transparent animation.
    """

    latitudes = df['latitude'].values
    longitudes = df['longitude'].values
    times = df['time'].apply(lambda t: t.timestamp()).values
    total_duration = times[-1] - times[0]
    if overwrite_duration:
        total_duration = 10 # just make a 10-second preview

    num_frames = int(fps * total_duration)
    interval = 1000 / fps

    # Optionally interpolate/smooth the data
    if len(latitudes) > 2:
        # Cubic Spline interpolation for smoother path
        cs_lat = CubicSpline(np.arange(len(latitudes)), latitudes)
        cs_lon = CubicSpline(np.arange(len(longitudes)), longitudes)

        # Adjust factor as needed
        new_indices = np.linspace(0, len(latitudes) - 1, num=int(total_duration * fps))  
        latitudes = cs_lat(new_indices)
        longitudes = cs_lon(new_indices)
    else:
        # Handle very few points gracefully
        new_indices = np.arange(len(latitudes))
    latitudes, longitudes = np.array(latitudes), np.array(longitudes)

    if animation_style == 'Matplotlib Animation':
        process_gpx_mpl_animation(filename, fps, num_frames, interval, latitudes, longitudes,
                                  bg_color, bg_alpha, main_line_color, bg_line_color,
                                  gpx_map_line_width, compass_heading_color, compass_line_width,
                                  compass_axis_thickness, compass_axis_fontsize, create_compass)
    elif animation_style == 'Matplotlib Moviepy':
        process_gpx_mpl_movpy(filename, fps, num_frames, interval, latitudes, longitudes, bg_color, bg_alpha,
                            main_line_color, bg_line_color,
                            gpx_map_line_width, compass_heading_color, compass_line_width,
                            compass_axis_thickness, compass_axis_fontsize, create_compass)

    
def process_gpx_mpl_movpy(filename, fps, num_frames, interval, latitudes, longitudes, 
                        bg_color, bg_alpha,
                        main_line_color, bg_line_color,
                        gpx_map_line_width, compass_heading_color, compass_line_width,
                        compass_axis_thickness, compass_axis_fontsize, create_compass):
    

    fig, ax = plt.subplots(figsize=(10, 6), dpi=150, facecolor=bg_color, edgecolor='none')
    ax.patch.set_alpha(bg_alpha)
    ax.plot(longitudes, latitudes, color=bg_line_color, lw=gpx_map_line_width)
    black_line, = ax.plot([], [], color=main_line_color, lw=gpx_map_line_width)
    ax.axis('off')

    def update(num):
        black_line.set_data(longitudes[:num], latitudes[:num])
        return black_line,

    progress_bar = st.progress(0, text=f"Creating Animation with {num_frames} frames...")

    # Save each frame as a transparent PNG image
    frames = []
    for frame_num in range(num_frames):
        update(frame_num)
        fig.canvas.draw()
        frame = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
        frame = frame.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        frames.append(frame)
        progress_bar.progress((frame_num + 1) / num_frames)

    plt.close(fig)

    clip = ImageSequenceClip(frames, fps=fps)
    clip = clip.set_opacity(bg_alpha)
    clip.write_gif(filename + '.gif', fps=fps)

    if create_compass:
        latitudes, longitudes = np.array(latitudes), np.array(longitudes)
        new_df = pd.DataFrame()
        new_df['latitude'] = latitudes
        new_df['longitude'] = longitudes
        df = calculate_bearings(new_df)

        # Create the figure and axis
        fig1, ax1 = plt.subplots(figsize=(10, 3), dpi=150, facecolor=bg_color, edgecolor='none')
        ax1.patch.set_alpha(bg_alpha)

        # Directions and angles for compass
        directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        angles = np.array([0, 45, 90, 135, 180, 225, 270, 315])

        # Set compass limits and ticks
        ax1.set_xlim([-45, 135])
        ax1.set_ylim([0, 1])
        ax1.set_xticks(angles)  # Center the compass around the bearing
        ax1.set_xticklabels(directions)
        ax1.tick_params(axis='x', which='major', labelsize=compass_axis_fontsize)

        # Set spine visibility and position
        ax1.spines['top'].set_position(('outward', -20))
        ax1.spines['bottom'].set_position(('outward', -20))
        ax1.spines['left'].set_visible(False)
        ax1.spines['right'].set_visible(False)

        # Set axis thickness
        ax1.spines['top'].set_linewidth(compass_axis_thickness)
        ax1.spines['bottom'].set_linewidth(compass_axis_thickness)

        # Remove y-ticks
        ax1.set_yticks([])

        # Initialize the bearing line
        bearing_line, = ax1.plot([], [], color=compass_heading_color, lw=compass_line_width)

        def update(num):
            bearing = df['bearing'].iloc[num]  # Get the current bearing from the DataFrame
            if bearing is None:
                bearing = df['bearing'].iloc[num-1]
            bearing_line.set_data([bearing, bearing], [0, 1])  # Use a list for x and y positions
            ax1.set_xlim((bearing - 45) % 360, (bearing + 45) % 360)
            return bearing_line,


        progress_bar = st.progress(0, text=f"Creating Animation with {num_frames} frames...")

        frames = []
        for frame_num in range(num_frames):
            update(frame_num)
            fig1.canvas.draw()
            frame = np.frombuffer(fig1.canvas.tostring_rgb(), dtype='uint8')
            frame = frame.reshape(fig1.canvas.get_width_height()[::-1] + (3,))
            frames.append(frame)
            progress_bar.progress((frame_num + 1) / num_frames)

        plt.close(fig)

        clip = ImageSequenceClip(frames, fps=fps)
        clip = clip.set_opacity(bg_alpha)
        clip.write_gif(filename + '_compass.gif', fps=fps)






def process_gpx_mpl_animation(filename, fps, num_frames, interval, latitudes, longitudes, 
                              bg_color, bg_alpha,
                              main_line_color, bg_line_color,
                              gpx_map_line_width, compass_heading_color, compass_line_width,
                              compass_axis_thickness, compass_axis_fontsize, create_compass):
    
    fig, ax = plt.subplots(figsize=(10, 6), dpi=150, facecolor=bg_color, edgecolor='none')
    #fig.patch.set_alpha(0)
    ax.patch.set_alpha(bg_alpha)
    ax.plot(longitudes, latitudes, color=bg_line_color, lw=gpx_map_line_width)
    black_line, = ax.plot([], [], color=main_line_color, lw=gpx_map_line_width)
    ax.axis('off')

    def update(num):
        black_line.set_data(longitudes[:num], latitudes[:num])
        progress_bar.progress((num + 1) / num_frames)
        return black_line,

    progress_bar = st.progress(0, text=f"Creating Animation with {num_frames} frames...")

    anim = animation.FuncAnimation(fig, update, frames=num_frames, interval=interval, blit=True)
    writer = animation.FFMpegWriter(fps=fps, metadata=dict(artist='Me'), extra_args=['-vf', 'format=rgba'])
    anim.save(filename + '.mov', writer=writer, savefig_kwargs={'transparent': False})
    plt.close(fig)


    if create_compass:

        latitudes, longitudes = np.array(latitudes), np.array(longitudes)
        new_df = pd.DataFrame()
        new_df['latitude'] = latitudes
        new_df['longitude'] = longitudes
        df = calculate_bearings(new_df)

        # Create the figure and axis
        fig1, ax1 = plt.subplots(figsize=(10, 3), dpi=150, facecolor=bg_color, edgecolor='none')
        ax1.patch.set_alpha(bg_alpha)

        # Directions and angles for compass
        directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        angles = np.array([0, 45, 90, 135, 180, 225, 270, 315])

        # Set compass limits and ticks
        ax1.set_xlim([-45, 135])
        ax1.set_ylim([0, 1])
        ax1.set_xticks(angles)  # Center the compass around the bearing
        ax1.set_xticklabels(directions)
        ax1.tick_params(axis='x', which='major', labelsize=compass_axis_fontsize)

        # Set spine visibility and position
        ax1.spines['top'].set_position(('outward', -20))
        ax1.spines['bottom'].set_position(('outward', -20))
        ax1.spines['left'].set_visible(False)
        ax1.spines['right'].set_visible(False)

        # Set axis thickness
        ax1.spines['top'].set_linewidth(compass_axis_thickness)
        ax1.spines['bottom'].set_linewidth(compass_axis_thickness)

        # Remove y-ticks
        ax1.set_yticks([])

        # Initialize the bearing line
        bearing_line, = ax1.plot([], [], color=compass_heading_color, lw=compass_line_width)

        def update(num):
            bearing = df['bearing'].iloc[num]  # Get the current bearing from the DataFrame
            if bearing is None:
                bearing = df['bearing'].iloc[num-1]
            bearing_line.set_data([bearing, bearing], [0, 1])  # Use a list for x and y positions
            ax1.set_xlim((bearing - 45) % 360, (bearing + 45) % 360)
            progress_bar.progress((num + 1) / num_frames)
            return bearing_line,

        progress_bar = st.progress(0, text=f"Creating Compass with {num_frames} frames...")
        anim = animation.FuncAnimation(fig1, update, frames=num_frames, interval=interval, blit=True)
        writer = animation.FFMpegWriter(fps=fps, metadata=dict(artist='Me'), extra_args=['-vf', 'format=rgba'])
        anim.save(filename + '_compass.mov', writer=writer, savefig_kwargs={'transparent': False})



def calculate_bearing(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    d_lon = lon2 - lon1
    x = sin(d_lon) * cos(lat2)
    y = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(d_lon)
    initial_bearing = atan2(x, y)
    return (degrees(initial_bearing) + 360) % 360

def calculate_bearings(df: pd.DataFrame) -> pd.DataFrame:
    bearings = []
    for i in range(1, len(df)):
        lat1, lon1 = df.iloc[i-1]['latitude'], df.iloc[i-1]['longitude']
        lat2, lon2 = df.iloc[i]['latitude'], df.iloc[i]['longitude']
        bearing = calculate_bearing(lat1, lon1, lat2, lon2)
        bearings.append(bearing)
    
    df['bearing'] = [bearings[0]] + bearings
    return df