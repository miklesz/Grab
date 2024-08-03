import cv2
import qrcode
import numpy as np
from PIL import Image
import os

# Constants
FPS = 50  # Frames per second
SHORT_DURATION_SECONDS = 5  # Duration in seconds for the short video
LONG_DURATION_SECONDS = 10  # Duration in seconds for the long video

SHORT_FRAME_COUNT = (
    SHORT_DURATION_SECONDS * FPS
)  # Total number of frames for the short video
LONG_FRAME_COUNT = (
    LONG_DURATION_SECONDS * FPS
)  # Total number of frames for the long video

CHROMA_IMAGE_PATH = "chroma-444.png"  # Path to the chroma image
OUTPUT_SHORT_VIDEO_PATH = "output_short_video.mkv"  # Path to the short output video
OUTPUT_LONG_VIDEO_PATH = "output_long_video.mp4"  # Path to the long output video

# Load the chroma image
chroma = cv2.imread(CHROMA_IMAGE_PATH)
if chroma is None or chroma.shape[:2] != (720, 1280):
    raise ValueError("Chroma image must be 1280x720 resolution.")

# Create the background frame (1920x1080) with black background
background = np.zeros((1080, 1920, 3), dtype=np.uint8)

# Place the chroma image in the left-upper corner of the background
background[0:720, 0:1280] = chroma

# Define the video writers with different codecs
fourcc_lossless = cv2.VideoWriter_fourcc(*"FFV1")  # FFV1 codec for lossless video
fourcc_lossy = cv2.VideoWriter_fourcc(*"mp4v")  # mp4v codec for lossy video

video_writer_short = cv2.VideoWriter(
    OUTPUT_SHORT_VIDEO_PATH, fourcc_lossless, FPS, (1920, 1080)
)
video_writer_long = cv2.VideoWriter(
    OUTPUT_LONG_VIDEO_PATH, fourcc_lossy, FPS, (1920, 1080)
)


# Function to generate QR code
def generate_qr_code(text, size=600):  # Further increase the size of the QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white").convert("L")
    img = img.resize((size, size), Image.LANCZOS)
    return np.array(img)


# Function to generate frames and write to video
def generate_video(frame_count, video_writer, video_type):
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 2
    font_color = (255, 255, 255)
    thickness = 3
    position = (50, 1050)

    for frame_number in range(frame_count):
        # Create QR code with the frame number
        qr_code = generate_qr_code(
            f"{video_type} Frame {frame_number}", size=600
        )  # Further increase the size of the QR code
        qr_code_colored = cv2.cvtColor(qr_code, cv2.COLOR_GRAY2BGR)

        # Copy the base background image to the frame
        frame = background.copy()

        # Overlay QR code on the frame in the right-bottom corner
        x_offset = 1920 - qr_code_colored.shape[1] - 10  # 10 pixels from the right edge
        y_offset = (
            1080 - qr_code_colored.shape[0] - 10
        )  # 10 pixels from the bottom edge
        frame[
            y_offset : y_offset + qr_code_colored.shape[0],
            x_offset : x_offset + qr_code_colored.shape[1],
        ] = qr_code_colored

        # Put frame number text on the frame
        cv2.putText(
            frame,
            f"Frame {frame_number}",
            position,
            font,
            font_scale,
            font_color,
            thickness,
            lineType=cv2.LINE_AA,
        )

        # Write the frame to the video
        video_writer.write(frame)

        print(f"Generated frame {frame_number} for {video_type} video")

    print(f"{video_type} video generation completed.")


# Generate short video (lossless)
generate_video(SHORT_FRAME_COUNT, video_writer_short, "Short")

# Generate long video (lossy)
generate_video(LONG_FRAME_COUNT, video_writer_long, "Long")

# Release the video writers
video_writer_short.release()
video_writer_long.release()

print("All video generation completed.")
