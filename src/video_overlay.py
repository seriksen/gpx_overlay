# video_cropper.py
import streamlit as st
import moviepy.editor as mp
import os
from . import video_utils


def video_overlay():
    st.header("GPX Video Overlay")

    if 'gpx_animation_path' not in st.session_state:
        uploaded_gpx = st.file_uploader("Upload a GPX Animation", type=["mp4","mov"])
        if uploaded_gpx is not None:
            gpx_video_path = os.path.join("temp_gpx.mp4")
            with open(gpx_video_path, "wb") as f:
                f.write(uploaded_gpx.getbuffer())
        
            st.session_state.gpx_animation_path = gpx_video_path

    if 'cropped_video_path' not in st.session_state:
        uploaded_video = st.file_uploader("Upload a Video", type=["mp4","mov"])
        if uploaded_video is not None:
            video_path = os.path.join("temp_video.mp4")
            #with open(video_path, "wb") as f:
            #    f.write(uploaded_video.getbuffer())

            st.session_state.cropped_video_path = video_path
            
    if 'gpx_animation_path' in st.session_state and 'cropped_video_path' in st.session_state:
    
        # Extract the first frame of the each
        gpx_first_frame = video_utils.extract_first_frame(st.session_state.gpx_animation_path)
        video_first_frame = video_utils.extract_first_frame(st.session_state.cropped_video_path)

        st.image(gpx_first_frame, caption="GPX")
        st.image(video_first_frame, caption="Video")

        # Select position for overlay
        position = st.selectbox("Select Overlay Position", ["Top-Left", "Top-Right", "Bottom-Left", "Bottom-Right"], index=3)
        overlay_width = st.slider("Overlay Width", min_value=50, max_value=5000, value=100)
        overlay_height = st.slider("Overlay Height", min_value=50, max_value=5000, value=100)
        transparency = st.slider("Overlay Transparency", min_value=0.0, max_value=1.0, value=1.0)
        add_gray_box = st.checkbox("Put GPX in coloured box")
        invert_colors = st.checkbox("Invert colours")

        video_utils.overlay_videos(st.session_state.cropped_video_path, 
                                    st.session_state.gpx_animation_path, 
                                    position, "previewed_video.mp4", 
                                    overlay_height, overlay_width, transparency,
                                    add_gray_box, invert_colors, preview=True)

        if st.button("Overlay Videos"):
            output_path = "overlayed_video.mp4"
            video_utils.overlay_videos(st.session_state.cropped_video_path, 
                                       st.session_state.gpx_animation_path, 
                                       position, output_path, 
                                       overlay_height, overlay_width, transparency,
                                       add_gray_box, invert_colors, preview=False)
            st.success("Videos overlayed successfully!")
            st.video(output_path)
            with open(output_path, "rb") as f:
                st.download_button("Download Complete Video", f, output_path)