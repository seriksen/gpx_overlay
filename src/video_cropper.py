# video_cropper.py
import streamlit as st
import moviepy.editor as mp
import os
import video_utils

def video_cropper():
    st.header("Video Cropper")
    
    uploaded_file = st.file_uploader("Upload a video", type=["mp4", "mov", "avi", "mkv"])
    duration = st.text_input("Enter desired duration (in seconds)", value="", type="default")
    
    if uploaded_file is not None:
        video_path = os.path.join("temp_video.mp4")
        with open(video_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        video = mp.VideoFileClip(video_path)
        duration = int(video.duration)
        st.session_state['video_fps'] = video.fps
        
        st.video(video_path)
        st.write(f"Video Duration: {duration} seconds")
        st.write(f"Video FPS: {st.session_state.video_fps}")
        
        start_time, end_time = st.slider(
            "Select range",
            0, duration, (0, duration),
            format="%d seconds"
        )
        
        if st.button("Crop Video"):
            cropped_video_path = "cropped_video.mp4"
            cropped_duration = video_utils.crop_video(video_path, start_time, end_time, cropped_video_path)
            st.session_state['cropped_video_duration'] = cropped_duration
            st.session_state['cropped_video_path'] = cropped_video_path
            st.success("Video cropped successfully!")
            st.video(cropped_video_path)
            st.session_state['video_cropped_duration_seconds'] = cropped_duration
            st.session_state.cropped_video_path = cropped_video_path
            
            with open(cropped_video_path, "rb") as f:
                st.download_button("Download Cropped Video", f, cropped_video_path)
        
        if st.button("Store Video Info"):
            st.session_state['cropped_video_duration'] = duration
            st.session_state['cropped_video_path'] = video_path
            st.success("Information Stored successfully!")
            st.session_state['video_cropped_duration_seconds'] = duration
    
    if duration is not None:
        if st.button("Store Video Info"):
            st.session_state['video_fps'] = 30
            st.session_state['cropped_video_duration'] = int(duration)
            st.session_state['cropped_video_path'] = None
            st.success("Information Stored successfully!")
            st.session_state['video_cropped_duration_seconds'] = int(duration)
