# GPX Overlay

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://gpx-overlay.streamlit.app/)

A web-app to overlay GPX data onto videos.

**Note**: This app is not longer developed. 
A newer version using garmin fit data has been developed;
see [garmin_video_overlay](https://github.com/seriksen/garmin_video_overlay).

## Description
The idea behind this web-app was to make it easy to combine gopro footage with an activity tracked on a wearable.
Most manufactures of smart watches allow you to download a `GPX` file which contains information such as [lat,long].

The app read this `GPX` file to create a map and a compass for the activity. 
This can then be overlaid on a mp4 or mov file. 

Both the `GPX` and `MP4/MOV` can be cut down to the length required within the app.
