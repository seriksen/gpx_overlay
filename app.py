# app.py
import streamlit as st
from src.video_cropper import video_cropper
from src.gpx_handler import gpx_handler
from src.gpx_animation import gpx_annimation
from src.video_overlay import video_overlay

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Video Cropper", "GPX Handler", "GPX_Annimatation", "Video_Overlay"])
    
    if page == "Video Cropper":
        video_cropper()
    elif page == "GPX Handler":
        gpx_handler()
    elif page == "GPX_Annimatation":
        gpx_annimation()   # Placeholder for GPX animation feature
    elif page == "Video_Overlay":
        video_overlay()  # Placeholder for GPX animation feature


if __name__ == "__main__":
    main()
