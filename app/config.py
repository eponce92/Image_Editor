import os

# App settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
SETTINGS_FILE = "settings.json"

# Create necessary directories
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Image settings
DEFAULT_IMAGE_SIZE = {
    "width": 512,
    "height": 512
}

# FAL AI settings
FAL_MODEL_PATH = "fal-ai/flux-general/image-to-image"
CONTROLNET_PATH = "Shakker-Labs/FLUX.1-dev-ControlNet-Union-Pro"
FAL_API_KEY_ENV = "FAL_API_KEY"  # Changed from separate ID/secret

# Preprocessing settings
class CannySettings:
    DEFAULT_LOW_THRESHOLD = 100
    DEFAULT_HIGH_THRESHOLD = 200
    DEFAULT_BLUR_SIZE = 5
    DEFAULT_BLUR_SIGMA = 0
    DEFAULT_DILATE_KERNEL = 2
    DEFAULT_DILATE_ITERATIONS = 1

    # Parameter ranges for UI controls
    LOW_THRESHOLD_RANGE = (0, 255)
    HIGH_THRESHOLD_RANGE = (0, 255)
    BLUR_SIZE_RANGE = (3, 11, 2)  # Must be odd numbers
    BLUR_SIGMA_RANGE = (0, 5)
    DILATE_KERNEL_RANGE = (1, 5)
    DILATE_ITERATIONS_RANGE = (0, 3)
