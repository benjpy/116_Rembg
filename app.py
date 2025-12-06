import streamlit as st
from rembg import remove
from PIL import Image
import io
import numpy as np
import os

from streamlit_cropper import st_cropper

st.set_page_config(page_title="Background Remover", page_icon="📸")

st.title("📸 Background Remover")
st.write("Take a photo and remove the background instantly!")

def process_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes))
    return remove(image)

# Input method selection
input_method = st.radio("Choose input method:", ("Upload Image", "Take Photo"))

img_file_buffer = None

if input_method == "Take Photo":
    img_file_buffer = st.camera_input("Take a picture")
else:
    img_file_buffer = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if img_file_buffer is not None:
    # To read image file buffer with OpenCV:
    bytes_data = img_file_buffer.getvalue()
    
    with st.spinner("Removing background..."):
        try:
            # Remove background
            nobg_image = process_image(bytes_data)
            
            st.success("Background removed!")
            
            # Layout for side-by-side comparison (optional, but good for UX)
            col1, col2 = st.columns(2)
            with col1:
                st.image(img_file_buffer, caption="Original Image")
            with col2:
                st.image(nobg_image, caption="Background Removed")

            # Cropping
            st.subheader("Crop Image")
            enable_cropping = st.checkbox("Enable Cropping")
            
            final_image = nobg_image

            if enable_cropping:
                # Get a cropped image from the frontend
                cropped_image = st_cropper(nobg_image, realtime_update=True, box_color='#0000FF', aspect_ratio=None)
                final_image = cropped_image
                st.write("Preview of cropped image:")
                st.image(final_image)

            # Background options
            st.subheader("Customize Background")
            bg_option = st.radio("Choose background style:", ("Transparent", "Solid Color"))

            if bg_option == "Solid Color":
                bg_color = st.color_picker("Pick a color", "#ffffff")
                
                # Create a solid color background
                new_bg = Image.new("RGBA", final_image.size, bg_color)
                # Composite the image
                final_image = Image.alpha_composite(new_bg, final_image)
                st.image(final_image, caption="Final Image with Color Background")
            else:
                st.image(final_image, caption="Final Image (Transparent)")

            # Convert to bytes for download
            buf = io.BytesIO()
            final_image.save(buf, format="PNG")
            byte_im = buf.getvalue()

            # Determine filename
            original_filename = "camera_capture.png"
            if hasattr(img_file_buffer, "name"):
                 original_filename = img_file_buffer.name

            file_name_root, _ = os.path.splitext(original_filename)
            new_filename = f"{file_name_root}_nobg.png"

            st.download_button(
                label="Download Image",
                data=byte_im,
                file_name=new_filename,
                mime="image/png"
            )

        except Exception as e:
            st.error(f"An error occurred: {e}")
