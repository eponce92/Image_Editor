import flet as ft
import os
import fal_client
from app.ui.sidebar import Sidebar
from app.services.fal_service import FalService
from app.services.image_processor import ImageProcessor
from app.config import WINDOW_WIDTH, WINDOW_HEIGHT, UPLOAD_DIR
import logging
import time
import base64

class ImageGeneratorApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.setup_page()
        self.setup_components()
        self.create_layout()

    def setup_page(self):
        self.page.title = "FAL AI Image Generator"
        self.page.theme_mode = "dark"
        self.page.padding = 20
        self.page.window_width = WINDOW_WIDTH
        self.page.window_height = WINDOW_HEIGHT

    def setup_components(self):
        self.sidebar = Sidebar(self.page)
        # Add callback for Canny settings changes
        self.sidebar.canny_controls.on_settings_change = self.on_canny_settings_change
        self.setup_main_content()

    def setup_main_content(self):
        # Setup FilePicker for local files
        self.pick_files_dialog = ft.FilePicker(
            on_result=self.pick_files_result
        )
        self.page.overlay.append(self.pick_files_dialog)
        
        # Setup other components
        self.selected_file = ft.Text(value="No file selected")
        self.source_image = ft.Text()
        self.processed_image = ft.Text()
        self.status_text = ft.Text()
        
        # Image preview components with local file paths
        self.original_preview = ft.Image(
            width=256,
            height=256,
            fit=ft.ImageFit.CONTAIN,
            visible=False,
            border_radius=10,
        )
        logging.info("Original preview component created")
        
        self.preprocessed_preview = ft.Image(
            width=256,
            height=256,
            fit=ft.ImageFit.CONTAIN,
            visible=False,
            border_radius=10,
        )
        logging.info("Preprocessed preview component created")
        
        self.result_preview = ft.Image(
            width=256,
            height=256,
            fit=ft.ImageFit.CONTAIN,
            visible=False,
            border_radius=10,
        )
        logging.info("Result preview component created")
        
        self.prompt_input = ft.TextField(
            label="Prompt",
            width=600,
            hint_text="Describe what you want to generate",
            multiline=True,
            min_lines=2,
            max_lines=4
        )

        self.strength_slider = ft.Slider(
            min=0.1,
            max=1.0,
            value=0.85,
            label="Strength: {value}",
            width=600
        )

    def pick_files_result(self, e: ft.FilePickerResultEvent):
        if e.files:
            file_path = e.files[0].path  # Get local file path
            self.selected_file.value = f"Selected file: {e.files[0].name}"
            self.source_image.value = file_path
            
            # Convert original image to base64 for preview
            with open(file_path, "rb") as img_file:
                img_data = base64.b64encode(img_file.read()).decode()
            
            # Update preview with base64 data
            self.original_preview.src_base64 = img_data
            self.original_preview.visible = True
            
            # Auto-process image if enabled and ControlNet is selected
            if (self.sidebar.preprocess_toggle.value and 
                self.sidebar.controlnet_type.value != "none"):
                try:
                    self.preprocess_image(None)
                except Exception as e:
                    self.status_text.value = f"Auto-preprocessing failed: {str(e)}"
        else:
            self.selected_file.value = "No file selected!"
            self.original_preview.visible = False
            self.preprocessed_preview.visible = False
            self.result_preview.visible = False
            self.source_image.value = None
            self.processed_image.value = None
            self.status_text.value = ""

        self.page.update()

    def on_queue_update(self, update):
        if isinstance(update, fal_client.InProgress):
            for log in update.logs:
                self.status_text.value = log["message"]
                self.page.update()

    def preprocess_image(self, e):
        if not self.source_image.value:
            self.status_text.value = "Please select an image first!"
            self.page.update()
            return

        if self.sidebar.controlnet_type.value == "none":
            self.status_text.value = "Please select a ControlNet type first!"
            self.page.update()
            return

        try:
            self.status_text.value = "Preprocessing image..."
            self.preprocessed_preview.visible = False
            self.page.update()

            # Get Canny parameters from UI if using Canny edge detection
            params = None
            if self.sidebar.controlnet_type.value == "canny":
                params = self.sidebar.canny_controls.get_params()

            # Process the image based on selected controlnet type
            processed_path = ImageProcessor.process_image(
                self.source_image.value,
                self.sidebar.controlnet_type.value,
                params=params
            )
            
            self.processed_image.value = processed_path
            
            # Convert image to base64 for preview
            with open(processed_path, "rb") as img_file:
                img_data = base64.b64encode(img_file.read()).decode()
            
            # Update preview with base64 data
            self.preprocessed_preview.src_base64 = img_data
            self.preprocessed_preview.visible = True
            
            self.status_text.value = "Preprocessing complete!"
            self.page.update()

        except Exception as e:
            self.status_text.value = f"Preprocessing error: {str(e)}"
            self.page.update()
            logging.error(f"Preprocessing error: {str(e)}")

    def generate_image(self, e):
        if not self.source_image.value:
            self.status_text.value = "Please select an image first!"
            self.page.update()
            return

        if self.sidebar.controlnet_type.value != "none" and not self.processed_image.value:
            self.status_text.value = "Please preprocess the image first!"
            self.page.update()
            return

        try:
            self.status_text.value = "Generating image..."
            self.result_preview.visible = False
            self.page.update()

            # Set credentials
            FalService.set_credentials(self.sidebar.api_key.value)

            result = FalService.generate_image(
                prompt=self.prompt_input.value,
                image_path=self.source_image.value,
                strength=self.strength_slider.value,
                controlnet_type=self.sidebar.controlnet_type.value,
                controlnet_scale=self.sidebar.controlnet_scale.value,
                control_image_path=self.processed_image.value,
                on_queue_update=self.on_queue_update
            )

            self.result_preview.src = result["images"][0]["url"]
            self.result_preview.visible = True
            self.status_text.value = "Image generated successfully!"
            self.page.update()

        except Exception as e:
            self.status_text.value = f"Error: {str(e)}"
            self.page.update()

    def create_layout(self):
        # Image previews row with containers for borders
        previews_row = ft.Row(
            [
                ft.Container(
                    content=ft.Column([
                        ft.Text("Original Image", weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=self.original_preview,
                            border=ft.border.all(2, ft.colors.GREY_400),
                            border_radius=10,
                            padding=5
                        )
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=10,
                    border_radius=10,
                    bgcolor=ft.colors.SURFACE_VARIANT
                ),
                
                ft.Container(
                    content=ft.Column([
                        ft.Text("Preprocessed Image", weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=self.preprocessed_preview,
                            border=ft.border.all(2, ft.colors.GREY_400),
                            border_radius=10,
                            padding=5
                        )
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=10,
                    border_radius=10,
                    bgcolor=ft.colors.SURFACE_VARIANT
                ),
                
                ft.Container(
                    content=ft.Column([
                        ft.Text("Generated Image", weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=self.result_preview,
                            border=ft.border.all(2, ft.colors.GREY_400),
                            border_radius=10,
                            padding=5
                        )
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=10,
                    border_radius=10,
                    bgcolor=ft.colors.SURFACE_VARIANT
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
            scroll=ft.ScrollMode.AUTO
        )

        # Create scrollable content
        main_content = ft.Container(
            content=ft.Column(
                [
                    ft.Text("FAL AI Image Generator", size=32, weight=ft.FontWeight.BOLD),
                    ft.Text("Transform images using AI", size=16),
                    ft.Divider(),
                    ft.ElevatedButton(
                        "Select Image",
                        icon=ft.icons.UPLOAD_FILE,
                        on_click=lambda _: self.pick_files_dialog.pick_files(
                            allow_multiple=False,
                            allowed_extensions=["png", "jpg", "jpeg"],
                            dialog_title="Select an image"
                        )
                    ),
                    self.selected_file,
                    previews_row,
                    ft.Divider(),
                    ft.Row([
                        ft.ElevatedButton(
                            "Preprocess Image",
                            on_click=self.preprocess_image,
                            icon=ft.icons.IMAGE_SEARCH,
                        ),
                        ft.ElevatedButton(
                            "Generate Image",
                            on_click=self.generate_image,
                            icon=ft.icons.AUTO_FIX_HIGH,
                        ),
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    self.prompt_input,
                    ft.Text("Transformation Strength"),
                    self.strength_slider,
                    self.status_text,
                ],
                spacing=20,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO
            ),
            padding=20,
        )

        # Add to page with sidebar
        self.page.add(
            ft.Row(
                [
                    self.sidebar.build(),
                    ft.VerticalDivider(width=1),
                    main_content
                ],
                expand=True,
                scroll=ft.ScrollMode.AUTO
            )
        )

    def on_canny_settings_change(self):
        """Handle real-time updates when Canny settings change"""
        if (self.source_image.value and 
            self.sidebar.controlnet_type.value == "canny"):
            self.preprocess_image(None)

def main(page: ft.Page):
    ImageGeneratorApp(page)

if __name__ == "__main__":
    ft.app(target=main, upload_dir=UPLOAD_DIR)
