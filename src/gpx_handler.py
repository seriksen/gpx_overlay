# gpx_handler.py
import streamlit as st
import gpx_utils
from datetime import timedelta
import pandas as pd


def setup_slider(df: pd.DataFrame):

    # Get the duration of the GPX file in seconds
    gpx_duration_seconds = int((df['time'].iloc[-1] - df['time'].iloc[0]).total_seconds())

    if 'video_cropped_duration_seconds' in st.session_state:
        video_duration = st.session_state['video_cropped_duration_seconds']
        st.write(f"Cropped Video Duration: {video_duration} seconds")
    else:
        video_duration = gpx_duration_seconds

    # Set the slider for selecting the fixed duration
    fixed_duration_seconds = st.slider("Select Fixed Duration", 0, gpx_duration_seconds, video_duration, format="%d seconds")

    # Set the slider for selecting the start time
    start_time_seconds = st.slider("Select Start Time", 0, gpx_duration_seconds, 0, format="%d seconds")

    # Calculate the end time based on the start time and fixed duration
    end_time_seconds = start_time_seconds + fixed_duration_seconds

    # Convert slider values to datetime
    start_time = df['time'].iloc[0] + timedelta(seconds=start_time_seconds)
    end_time = df['time'].iloc[0] + timedelta(seconds=end_time_seconds)

    return start_time, end_time


def gpx_handler():
    st.header("GPX File Visualizer and Editor")

    if 'gpx_full_df' not in st.session_state:
        st.session_state.gpx_full_df = None
    
    uploaded_gpx = st.file_uploader("Upload a GPX file", type="gpx")
    
    if uploaded_gpx is not None:
        st.session_state.gpx_full_df = gpx_utils.parse_gpx(uploaded_gpx)
        if st.session_state.gpx_full_df.empty:
            st.error("No valid data in GPX file.")
            return

    if st.session_state.gpx_full_df is not None:
        
        # Set sidebar viewing options
        map_style = st.sidebar.selectbox("Select Map Style", ["open-street-map", "carto-positron", "carto-darkmatter", "stamen-terrain", "stamen-toner", "stamen-watercolor"])
        line_colour = st.sidebar.color_picker("Pick a Line Color", "#FF0000")
        
        fig = gpx_utils.gpx_visualization(st.session_state.gpx_full_df, map_style=map_style, line_color=line_colour)
        st.plotly_chart(fig)
        
        # Calculate duration and convert to seconds

        start_time, end_time = setup_slider(st.session_state.gpx_full_df)


        st.session_state.gpx_cropped_df = st.session_state.gpx_full_df[(st.session_state.gpx_full_df['time'] >= start_time) & (st.session_state.gpx_full_df['time'] <= end_time)]
        
        fig_cropped = gpx_utils.gpx_visualization(st.session_state.gpx_cropped_df, map_style=map_style, line_color=line_colour)
        st.plotly_chart(fig_cropped)
        
        if st.button("Save GPX"):
            gpx_utils.save_gpx(st.session_state.gpx_cropped_df, "cropped_gpx.gpx")            
            st.session_state['filepath_cropped_gpx'] = "cropped_gpx.gpx"
            with open("cropped_gpx.gpx", "rb") as f:
                st.download_button("Download Cropped GPX", f, "cropped_gpx.gpx")