import cv2
import os
import numpy as np

# Constants
VIDEO_PATH = "output_long_video.mp4"  # Path to the video file to be verified
DUMP_DIR = "problematic_frames"  # Directory to save problematic frames

# Ensure the dump directory exists
os.makedirs(DUMP_DIR, exist_ok=True)


# Function to decode QR code from an image using OpenCV
def decode_qr_code(frame):
    qr_code_detector = cv2.QRCodeDetector()
    data, points, _ = qr_code_detector.detectAndDecode(frame)
    return data if points is not None else None


# Function to save problematic frames
def save_problematic_frame(frame, frame_number, issue):
    filename = os.path.join(DUMP_DIR, f"frame_{frame_number:05d}_{issue}.png")
    cv2.imwrite(filename, frame)
    print(f"Saved problematic frame {frame_number} due to {issue}")


# Function to verify video
def verify_video(video_path):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return

    frame_number = 0
    qr_codes = []

    frames_with_no_qr = []
    missing_frames = []
    repeated_frames = []
    out_of_order_frames = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        qr_code = decode_qr_code(frame)

        if qr_code:
            qr_codes.append((frame_number, qr_code, frame))
        else:
            qr_codes.append((frame_number, "No QR Code", frame))
            frames_with_no_qr.append(frame_number)
            save_problematic_frame(frame, frame_number, "no_qr_code")

        frame_number += 1

        # Print progress every 100 frames
        if frame_number % 100 == 0:
            print(
                f"Processed {frame_number} frames. Frames with no QR code: {len(frames_with_no_qr)}, Missing frames: {len(missing_frames)}, Repeated frames: {len(repeated_frames)}, Out of order frames: {len(out_of_order_frames)}"
            )

    cap.release()

    # Analyze QR codes
    previous_frame_number = None
    previous_qr_number = None
    for i, (frame_number, qr_code, frame) in enumerate(qr_codes):
        if qr_code == "No QR Code":
            continue

        qr_frame_number = int(qr_code.split()[-1])

        if previous_qr_number is not None:
            if qr_frame_number == previous_qr_number:
                repeated_frames.append(frame_number)
                save_problematic_frame(frame, frame_number, "repeated")
            elif qr_frame_number < previous_qr_number:
                out_of_order_frames.append(frame_number)
                save_problematic_frame(frame, frame_number, "out_of_order")
            elif qr_frame_number > previous_qr_number + 1:
                missing_frames.extend(range(previous_qr_number + 1, qr_frame_number))
                save_problematic_frame(frame, frame_number, "missing")

        previous_qr_number = qr_frame_number

    # Generate report
    print("Verification Report")
    print("===================")
    print(f"Total frames analyzed: {frame_number}")
    print(f"Frames with no QR code: {len(frames_with_no_qr)}")
    if frames_with_no_qr:
        print(f"Frames with no QR code: {frames_with_no_qr}")
    print(f"Missing frames: {len(missing_frames)}")
    if missing_frames:
        print(f"Missing frame numbers: {missing_frames}")
    print(f"Repeated frames: {len(repeated_frames)}")
    if repeated_frames:
        print(f"Repeated frame numbers: {repeated_frames}")
    print(f"Out of order frames: {len(out_of_order_frames)}")
    if out_of_order_frames:
        print(f"Out of order frame numbers: {out_of_order_frames}")


if __name__ == "__main__":
    verify_video(VIDEO_PATH)
