
# QR Code Frame Verification

This project generates videos with QR codes embedded in each frame and verifies the presence and order of QR codes in the frames. It is useful for testing frame grabbers and ensuring the integrity of captured frames.

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Generating Videos](#generating-videos)
  - [Verifying Videos](#verifying-videos)
- [License](#license)
- [Author](#author)

## Requirements

- Python 3.x
- OpenCV
- Pillow
- qrcode
- numpy

## Installation

1. Clone the repository:

```bash
git clone https://github.com/your-repo-url.git
cd your-repo-url
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Generating Videos

To generate short (5 seconds, lossless) and long (10 seconds, lossy) videos with QR codes embedded in each frame, run the following script:

```bash
python generate_qr_video.py
```

### Verifying Videos

To verify the generated video and check for any missing, repeated, or out-of-order frames, run the following script:

```bash
python verify_qr_video.py
```

The script will analyze the video and save problematic frames in the `problematic_frames` directory.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Author

Miklesz / Damage
