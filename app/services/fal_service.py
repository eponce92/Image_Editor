import fal_client
import os
import requests
from app.config import FAL_MODEL_PATH, CONTROLNET_PATH, DEFAULT_IMAGE_SIZE, FAL_API_KEY_ENV
import logging
import time
import asyncio

class FalService:
    MAX_RETRIES = 120
    RETRY_DELAY = 1

    @staticmethod
    def set_credentials(api_key):
        os.environ[FAL_API_KEY_ENV] = api_key

    @staticmethod
    def upload_to_fal(file_path):
        """Upload a file to FAL's temporary storage and get a public URL."""
        try:
            logging.info(f"Uploading file: {file_path}")
            url = fal_client.upload_file(file_path)
            logging.info(f"File uploaded successfully: {url}")
            return url
        except Exception as e:
            logging.error(f"Upload failed: {str(e)}")
            raise

    @staticmethod
    def generate_image(
        prompt,
        image_path,
        strength,
        controlnet_type="none",
        controlnet_scale=0.7,
        control_image_path=None,
        on_queue_update=None
    ):
        try:
            # Upload the source image
            logging.info(f"Uploading source image: {image_path}")
            source_url = FalService.upload_to_fal(image_path)
            logging.info(f"Source image uploaded: {source_url}")

            # Base request arguments
            request_args = {
                "prompt": prompt,
                "image_url": source_url,
                "image_size": "square_hd",
                "num_inference_steps": 28,
                "seed": 1234,
                "loras": [],
                "controlnets": [],
                "controlnet_unions": [],
                "ip_adapters": [],
                "guidance_scale": 3.5,
                "real_cfg_scale": 3.5,
                "num_images": 1,
                "enable_safety_checker": True,
                "strength": strength
            }

            # Add ControlNet configuration if specified
            if controlnet_type != "none":
                control_image = control_image_path or image_path
                logging.info(f"Uploading control image: {control_image}")
                control_url = FalService.upload_to_fal(control_image)
                logging.info(f"Control image uploaded: {control_url}")

                request_args["controlnet_unions"] = [{
                    "path": CONTROLNET_PATH,
                    "controls": [{
                        "control_mode": controlnet_type,
                        "control_image_url": control_url,
                        "conditioning_scale": controlnet_scale
                    }]
                }]

            # Use subscribe method directly as it handles the queue management
            logging.info("Starting image generation...")
            result = fal_client.subscribe(
                FAL_MODEL_PATH,
                arguments=request_args,
                with_logs=True,
                on_queue_update=on_queue_update
            )

            if result and "images" in result:
                logging.info("Generation completed successfully")
                return result
            else:
                raise Exception("No images in response")

        except Exception as e:
            logging.error(f"Error in generate_image: {str(e)}")
            raise

    @staticmethod
    def on_queue_update(update):
        """Default queue update handler"""
        if isinstance(update, fal_client.InProgress):
            for log in update.logs:
                logging.info(f"Progress: {log['message']}")
        elif isinstance(update, fal_client.Queued):
            logging.info(f"Queued at position: {update.position}")
        elif hasattr(update, 'error'):
            logging.error(f"Error in queue: {update.error}")
