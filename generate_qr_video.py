import cv2
import numpy as np
import qrcode
from PIL import Image

# Constants
FPS = 50  # Frames per second
SHORT_DURATION_SECONDS = 5  # Duration in seconds for the short video
LONG_DURATION_SECONDS = 60 * 10  # Duration in seconds for the long video

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
def generate_qr_code(data, size=600):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    img = img.resize((size, size), Image.LANCZOS)
    img = np.array(img.convert("RGB"))
    return img


# Function to generate frames and write to video
def generate_video(frame_count, video_writer, video_type):
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 5  # Increased font size
    font_color = (255, 255, 255)
    thickness = 10  # Increased thickness
    position = (50, 1050)

    for frame_number in range(frame_count):
        # Copy the base background image to the frame
        frame = background.copy()

        # Generate the QR code with frame number
        qr_code = generate_qr_code(f"Frame {frame_number}", size=600)

        # Place the QR code in the bottom-right corner of the frame
        qr_h, qr_w = qr_code.shape[:2]
        frame[-qr_h - 50 : -50, -qr_w - 50 : -50] = qr_code

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

        if frame_number % 100 == 0 or frame_number == frame_count - 1:
            print(
                f"Generated frame {frame_number + 1} of {frame_count} for {video_type} video"
            )

    print(f"{video_type} video generation completed.")


# Generate short video (lossless)
generate_video(SHORT_FRAME_COUNT, video_writer_short, "Short")

# Generate long video (lossy)
generate_video(LONG_FRAME_COUNT, video_writer_long, "Long")

# Release the video writers
video_writer_short.release()
video_writer_long.release()

print("All video generation completed.")
