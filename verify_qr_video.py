import cv2
import os
import numpy as np

# Constants
VIDEO_PATH = "output_long_video.mp4"  # Path to the video file to be verified
DUMP_DIR = "problematic_frames"  # Directory to save problematic frames

# Ensure the dump directory exists
os.makedirs(DUMP_DIR, exist_ok=True)


# Function to decode QR code using OpenCV's QRCodeDetector
def decode_qr_code(frame):
    detector = cv2.QRCodeDetector()
    data, points, _ = detector.detectAndDecode(frame)
    return data if data else None


# Function to save problematic frames along with previous and next frames
def save_problematic_frames(prev_frame, frame, next_frame, frame_number, issue):
    combined_frame = np.zeros((1080, 5760, 3), dtype=np.uint8)
    combined_frame[:, 0:1920] = prev_frame
    combined_frame[:, 1920:3840] = frame
    combined_frame[:, 3840:5760] = next_frame

    filename = os.path.join(DUMP_DIR, f"frame_{frame_number:05d}_{issue}.png")
    cv2.imwrite(filename, combined_frame)
    print(f"Saved problematic frames {frame_number} due to {issue}")


# Function to verify video
def verify_video(video_path):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return

    frame_number = 0
    frame_numbers = []

    frames_with_no_qr = []
    missing_frames = []
    repeated_frames = []
    out_of_order_frames = []

    prev_frame = None
    current_frame = None
    next_frame = None

    while True:
        ret, next_frame = cap.read()
        if not ret:
            break

        if frame_number > 1:
            qr_code = decode_qr_code(current_frame)

            if qr_code:
                frame_num = int(qr_code.split()[-1])
                frame_numbers.append(frame_num)
            else:
                frames_with_no_qr.append(frame_number - 1)
                save_problematic_frames(
                    prev_frame,
                    current_frame,
                    next_frame,
                    frame_number - 1,
                    "no_qr_code",
                )

        prev_frame = current_frame
        current_frame = next_frame
        frame_number += 1

        # Print progress every 100 frames
        if frame_number % 100 == 0:
            print(
                f"Processed {frame_number} frames. Frames with no QR code: {len(frames_with_no_qr)}, "
                f"Missing frames: {len(missing_frames)}, Repeated frames: {len(repeated_frames)}, "
                f"Out of order frames: {len(out_of_order_frames)}"
            )

    cap.release()

    # Analyze frame numbers
    previous_frame_number = None
    for i, frame_num in enumerate(frame_numbers):
        if previous_frame_number is not None:
            if frame_num == previous_frame_number:
                repeated_frames.append(frame_num)
                save_problematic_frames(
                    prev_frame, current_frame, next_frame, frame_num, "repeated"
                )
            elif frame_num < previous_frame_number:
                out_of_order_frames.append(frame_num)
                save_problematic_frames(
                    prev_frame, current_frame, next_frame, frame_num, "out_of_order"
                )
            elif (
                frame_num > previous_frame_number + 1
                and previous_frame_number + 1 not in frames_with_no_qr
            ):
                missing_frames.extend(range(previous_frame_number + 1, frame_num))
                save_problematic_frames(
                    prev_frame, current_frame, next_frame, frame_num, "missing"
                )

        previous_frame_number = frame_num

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
