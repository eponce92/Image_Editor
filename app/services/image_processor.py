import cv2
import numpy as np
from PIL import Image
import os
from app.config import CannySettings
import logging
from dataclasses import dataclass

@dataclass
class CannyParams:
    low_threshold: int = CannySettings.DEFAULT_LOW_THRESHOLD
    high_threshold: int = CannySettings.DEFAULT_HIGH_THRESHOLD
    blur_size: int = CannySettings.DEFAULT_BLUR_SIZE
    blur_sigma: int = CannySettings.DEFAULT_BLUR_SIGMA
    dilate_kernel: int = CannySettings.DEFAULT_DILATE_KERNEL
    dilate_iterations: int = CannySettings.DEFAULT_DILATE_ITERATIONS

class CannyEdgePreprocessor:
    def __init__(self, params: CannyParams = None):
        self.params = params or CannyParams()

    def process(self, image):
        """Process image with Canny edge detection and enhancements."""
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(
            gray, 
            (self.params.blur_size, self.params.blur_size), 
            self.params.blur_sigma
        )

        # Apply Canny edge detection
        edges = cv2.Canny(
            blurred,
            self.params.low_threshold,
            self.params.high_threshold
        )

        # Dilate edges to make them more prominent
        if self.params.dilate_iterations > 0:
            kernel = np.ones(
                (self.params.dilate_kernel, self.params.dilate_kernel), 
                np.uint8
            )
            edges = cv2.dilate(edges, kernel, iterations=self.params.dilate_iterations)

        # Create white background with black edges
        final_image = np.zeros_like(image)  # Create blank BGR image
        final_image.fill(255)  # Fill with white
        
        # Set edges to black (all channels)
        final_image[edges > 0] = [0, 0, 0]

        return final_image

class ImageProcessor:
    @staticmethod
    def process_image(image_path, process_type="canny", params=None):
        logging.info(f"Processing image: {image_path} with type: {process_type}")
        
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        if process_type == "canny":
            return ImageProcessor.apply_canny(image_path, params)
        elif process_type == "depth":
            # TODO: Implement depth processing
            return image_path
        elif process_type == "pose":
            # TODO: Implement pose processing
            return image_path
        else:
            logging.warning(f"Unknown process type: {process_type}")
            return image_path

    @staticmethod
    def apply_canny(image_path, params=None):
        try:
            logging.info(f"Applying Canny edge detection to: {image_path}")
            
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Failed to load image: {image_path}")

            # Create Canny processor with parameters
            canny_processor = CannyEdgePreprocessor(params)
            
            # Process the image
            final_image = canny_processor.process(image)
            
            # Save processed image
            base_path = os.path.splitext(image_path)[0]
            output_path = f"{base_path}_canny.png"
            
            # Ensure the output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            cv2.imwrite(output_path, final_image)
            logging.info(f"Saved processed image to: {output_path}")
            
            return output_path
            
        except Exception as e:
            logging.error(f"Error in apply_canny: {str(e)}")
            raise

    @staticmethod
    def adjust_canny_params(image_path, params: CannyParams) -> tuple:
        """
        Helper method to visualize Canny edge detection with different parameters.
        Returns both the processed image and the parameters used.
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Failed to load image: {image_path}")

            processor = CannyEdgePreprocessor(params)
            processed = processor.process(image)
            
            return processed, params
            
        except Exception as e:
            logging.error(f"Error in adjust_canny_params: {str(e)}")
            raise
