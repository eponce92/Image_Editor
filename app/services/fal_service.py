import fal_client
import os
from app.config import FAL_MODEL_PATH, CONTROLNET_PATH, DEFAULT_IMAGE_SIZE, FAL_API_KEY_ENV

class FalService:
    @staticmethod
    def set_credentials(api_key):
        os.environ[FAL_API_KEY_ENV] = api_key  # Changed to single API key

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
        controlnet_unions = []
        if controlnet_type != "none":
            control_image = control_image_path or image_path
            controlnet_unions = [{
                "path": CONTROLNET_PATH,
                "controls": [{
                    "control_mode": controlnet_type,
                    "control_image_url": f"file://{control_image}",
                    "conditioning_scale": controlnet_scale
                }]
            }]

        result = fal_client.subscribe(
            FAL_MODEL_PATH,
            arguments={
                "prompt": prompt,
                "image_size": DEFAULT_IMAGE_SIZE,
                "num_inference_steps": 28,
                "controlnets": [],
                "controlnet_unions": controlnet_unions,
                "ip_adapters": [],
                "guidance_scale": 3.5,
                "real_cfg_scale": 3.5,
                "num_images": 1,
                "enable_safety_checker": True,
                "image_url": f"file://{image_path}",
                "strength": strength
            },
            with_logs=True,
            on_queue_update=on_queue_update,
        )
        
        return result
