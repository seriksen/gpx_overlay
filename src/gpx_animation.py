# gpx_handler.py
import streamlit as st
import gpx_utils
from datetime import timedelta
import pandas as pd

def gpx_annimation():
    st.header("GPX Annimation")

    if 'gpx_cropped_df' not in st.session_state:
        uploaded_gpx = st.file_uploader("Upload a GPX file", type="gpx")

        if uploaded_gpx is not None:
            st.session_state.gpx_cropped_df = gpx_utils.parse_gpx(uploaded_gpx)
            if st.session_state.gpx_cropped_df.empty:
                st.error("No valid data in GPX file.")
                return

    if 'gpx_cropped_df' in st.session_state:
        
        # Set sidebar viewing options
        map_style = st.sidebar.selectbox("Select Map Style", ["open-street-map", "carto-positron", "carto-darkmatter", "stamen-terrain", "stamen-toner", "stamen-watercolor"])
        line_colour = st.sidebar.color_picker("Pick a Line Color", "#FF0000")
        
        fig = gpx_utils.gpx_visualization(st.session_state.gpx_cropped_df, map_style=map_style, line_color=line_colour)
        st.plotly_chart(fig)

        compass_box = st.selectbox("Compass Animation?", ["Yes", "No"])

        st.sidebar.subheader("Animation Options")
        animation_style = st.sidebar.selectbox("Animation Backend", ["Matplotlib Animation", "Matplotlib Moviepy"])
        bg_color = st.sidebar.text_input("Background Color", value="white")
        bg_alpha = st.sidebar.number_input("Background Alpha", min_value=0, max_value=1, value=1)
        main_line_color = st.sidebar.text_input("Pick a Main Line Color", value="black")
        bg_line_color = st.sidebar.text_input("Pick a Background Line Color", value="lightgray")
        gpx_map_line_width = st.sidebar.number_input("GPX Map Line Width", min_value=0, value=10)
        compass_line_width = st.sidebar.number_input("Compass Line Width", min_value=0, value=10)
        compass_axis_thickness = st.sidebar.number_input("Compass Axis Thickness", min_value=0, value=10)
        compass_axis_fontsize = st.sidebar.number_input("Compass Axis Fontsize", min_value=0, value=10)
        compass_heading_color = st.sidebar.text_input("Compass Heading Color", value="red")

        if st.button("Create Sample Animation"):

            # create sample animations
            fig = gpx_utils.gpx_animation(st.session_state.gpx_cropped_df, fps=30, 
                                        filename="tmp_animations",
                                        overwrite_duration=True, 
                                        # General settings
                                        animation_style=animation_style, 
                                        bg_color=bg_color, 
                                        bg_alpha=bg_alpha,
                                        # Map settings
                                        main_line_color=main_line_color, 
                                        bg_line_color=bg_line_color, 
                                        gpx_map_line_width=gpx_map_line_width, 
                                        # Compass settings
                                        compass_line_width=compass_line_width, 
                                        compass_axis_thickness=compass_axis_thickness,
                                        compass_heading_color=compass_heading_color,
                                        compass_axis_fontsize=compass_axis_fontsize,
                                        create_compass=True)
            # Side by side video display
            try:
                st.video("tmp_animations.mov")
                st.video("tmp_animations_compass.mov")
            except:
                st.image("tmp_animations.gif")
                st.image("tmp_animations_compass.gif")

        # Create animation
        if st.button("Create Animation"):
            st.session_state.gpx_animation_path = "gpx_animation"

            if compass_box == "Yes":
                compass = True  
            else:
                compass = False
            if 'fps' not in st.session_state:
                fps = 30
            else:
                fps = st.session_state.fps

            fig = gpx_utils.gpx_animation(st.session_state.gpx_cropped_df, fps=fps, 
                                        filename=st.session_state.gpx_animation_path, 
                                        overwrite_duration=False,                                         
                                        animation_style=animation_style, 
                                        bg_color=bg_color, 
                                        bg_alpha=bg_alpha,
                                        # Map settings
                                        main_line_color=main_line_color, 
                                        bg_line_color=bg_line_color, 
                                        gpx_map_line_width=gpx_map_line_width, 
                                        # Compass settings
                                        compass_line_width=compass_line_width, 
                                        compass_axis_thickness=compass_axis_thickness,
                                        compass_heading_color=compass_heading_color,
                                        compass_axis_fontsize=compass_axis_fontsize,
                                        create_compass=compass)
            st.video(st.session_state.gpx_animation_path + ".mp4")

            with open(st.session_state.gpx_animation_path + ".mp4", "rb") as f:
                st.download_button("Download GPX Animation", f, st.session_state.gpx_animation_path + ".mp4")

            if compass:
                st.video(st.session_state.gpx_animation_path + "_compass.mov")
                with open(st.session_state.gpx_animation_path + "_compass.mov", "rb") as f:
                    st.download_button("Download GPX Animation", f, st.session_state.gpx_animation_path + "_compass.mp4")