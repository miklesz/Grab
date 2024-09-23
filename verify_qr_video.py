import cv2
import os
import numpy as np

# Constants
VIDEO_PATH = (
    "/Volumes/T7/Graby/2024-08-04_15-40-21.avi"  # Path to the video file to be verified
)
DUMP_DIR = "problematic_frames"  # Directory to save problematic frames
SKIP_FRAMES = 250  # Number of initial and final frames to skip (default: 250)

# Ensure the dump directory exists
os.makedirs(DUMP_DIR, exist_ok=True)


# Function to decode QR code using OpenCV's QRCodeDetector
def decode_qr_code(frame):
    detector = cv2.QRCodeDetector()
    data, points, _ = detector.detectAndDecode(frame)
    return data if data else None


# Function to save problematic frames along with previous and next frames
def save_problematic_frames(
    prev_frame, frame, next_frame, frame_number, issue, qr_code_num
):
    combined_frame = np.zeros((1080, 5760, 3), dtype=np.uint8)
    if prev_frame is not None:
        combined_frame[:, 0:1920] = prev_frame
    combined_frame[:, 1920:3840] = frame
    if next_frame is not None:
        combined_frame[:, 3840:5760] = next_frame

    filename = os.path.join(
        DUMP_DIR, f"frame_{frame_number:05d}_{issue}_at_{qr_code_num}.png"
    )
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

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    while True:
        ret, next_frame = cap.read()
        if not ret:
            break

        if frame_number <= SKIP_FRAMES or frame_number >= total_frames - SKIP_FRAMES:
            frame_number += 1
            continue

        if frame_number > 1 and current_frame is not None:
            qr_code = decode_qr_code(current_frame)

            if qr_code:
                frame_num = int(qr_code.split()[-1])
                frame_numbers.append((frame_num, frame_number))
            else:
                frames_with_no_qr.append(frame_number - 1)
                save_problematic_frames(
                    prev_frame,
                    current_frame,
                    next_frame,
                    frame_number - 1,
                    "no_qr_code",
                    "unknown",
                )

        if frame_number > 2 and current_frame is not None:
            # Analyze the current frame numbers to detect issues
            if len(frame_numbers) >= 2:
                prev_frame_num, prev_idx = frame_numbers[-2]
                curr_frame_num, curr_idx = frame_numbers[-1]

                if curr_frame_num == prev_frame_num:
                    repeated_frames.append(curr_frame_num)
                    save_problematic_frames(
                        prev_frame,
                        current_frame,
                        next_frame,
                        curr_idx,
                        "repeated_at",
                        curr_frame_num,
                    )
                elif curr_frame_num < prev_frame_num:
                    out_of_order_frames.append(curr_frame_num)
                    save_problematic_frames(
                        prev_frame,
                        current_frame,
                        next_frame,
                        curr_idx,
                        "out_of_order_at",
                        curr_frame_num,
                    )
                elif curr_frame_num > prev_frame_num + 1:
                    missing_frame_num = prev_frame_num + 1
                    missing_frames.append(missing_frame_num)
                    save_problematic_frames(
                        prev_frame,
                        current_frame,
                        next_frame,
                        curr_idx,
                        "missing_at",
                        curr_frame_num,
                    )

        prev_frame = current_frame
        current_frame = next_frame
        frame_number += 1

        # Print progress every 100 frames in one line
        if frame_number % 100 == 0:
            print(
                f"Processed {frame_number} frames. Frames with no QR code: {len(frames_with_no_qr)}, "
                f"Missing frames: {len(missing_frames)}, Repeated frames: {len(repeated_frames)}, "
                f"Out of order frames: {len(out_of_order_frames)}"
            )

    cap.release()

    # Final progress update
    print(
        f"Processed {frame_number} frames. Frames with no QR code: {len(frames_with_no_qr)}, "
        f"Missing frames: {len(missing_frames)}, Repeated frames: {len(repeated_frames)}, "
        f"Out of order frames: {len(out_of_order_frames)}"
    )

    # Generate report
    print("\nVerification Report")
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
