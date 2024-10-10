import streamlit as st
import moviepy.editor as mp
import os
from PIL import Image, ImageEnhance, ImageOps

def crop_video(video_path: str, start_time: int, end_time: int, output_path: str) -> float:
    video = mp.VideoFileClip(video_path)
    cropped_video = video.subclip(start_time, end_time)
    cropped_video.write_videofile(output_path, codec="libx264")
    return cropped_video.duration

def extract_first_frame(video_path: str) -> Image.fromarray:
    video = mp.VideoFileClip(video_path)
    first_frame = video.get_frame(0)
    return Image.fromarray(first_frame)


def adjust_transparency(image: Image, transparency: float) -> Image:
    alpha = image.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(transparency)
    image.putalpha(alpha)
    return image


def overlay_videos(base_video_path: str, overlay_video_path: str, position: str, output_path: str,
                   overlay_height: int, overlay_width: int, transparency: float, 
                   add_gray_box: bool, invert_colors: bool, preview=False) -> None:
    main_video = mp.VideoFileClip(base_video_path)
    overlay_video = mp.VideoFileClip(overlay_video_path).resize((overlay_width, overlay_height))

    if preview:
        # select first 2 frames for preview
        main_video = main_video.subclip(0, 0.1)
        overlay_video = overlay_video.subclip(0, 0.1)

    overlay_video = overlay_video.set_opacity(transparency)

    if invert_colors:
        overlay_video = overlay_video.fx(mp.vfx.invert_colors)

    # Calculate position
    if position == "Top-Left":
        pos = (0, 0)
    elif position == "Top-Right":
        pos = (main_video.w - overlay_video.w, 0)
    elif position == "Bottom-Left":
        pos = (0, main_video.h - overlay_video.h)
    elif position == "Bottom-Right":
        pos = (main_video.w - overlay_video.w, main_video.h - overlay_video.h)
    else:
        pos = (main_video.w - overlay_video.w, main_video.h - overlay_video.h)  # Default to Bottom-Right

    if add_gray_box:
        gray_box = mp.ColorClip(size=(overlay_width, overlay_height), color=(128, 128, 128)).set_duration(main_video.duration)
        gray_box = gray_box.set_position(pos)
        final_video = mp.CompositeVideoClip([main_video, gray_box, overlay_video.set_position(pos)])
    else:
        final_video = mp.CompositeVideoClip([main_video, overlay_video.set_position(pos)])

    final_video.write_videofile(output_path, codec="libx264")

    if preview:
        preview_frame = extract_first_frame(output_path)
        st.image(preview_frame, caption="Overlay Preview")