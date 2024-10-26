import flet as ft
from app.utils.settings_manager import SettingsManager
from app.config import CannySettings
from app.services.image_processor import CannyParams  # Add this import

class Sidebar:
    def __init__(self, page):
        self.page = page
        settings = SettingsManager.load_settings()
        
        self.api_key = ft.TextField(
            label="FAL API Key",
            password=True,
            value=settings.get("fal_api_key", ""),
            width=250
        )

        self.controlnet_type = ft.Dropdown(
            label="ControlNet Type",
            width=250,
            options=[
                ft.dropdown.Option("none", "None"),
                ft.dropdown.Option("canny", "Canny Edge"),
                ft.dropdown.Option("depth", "Depth"),
                ft.dropdown.Option("pose", "Pose"),
            ],
            value="none"
        )

        self.controlnet_scale = ft.Slider(
            min=0.0,
            max=1.0,
            value=0.7,
            label="ControlNet Scale: {value}",
            width=250
        )

        self.preprocess_toggle = ft.Switch(
            label="Auto-preprocess image",
            value=True
        )

        self.canny_controls = CannyControls()
        self.canny_controls.visible = False

        def on_controlnet_change(e):
            self.canny_controls.visible = self.controlnet_type.value == "canny"
            page.update()

        self.controlnet_type.on_change = on_controlnet_change

    def save_settings(self, e):
        settings = {
            "fal_api_key": self.api_key.value
        }
        SettingsManager.save_settings(settings)
        self.page.show_snack_bar(ft.SnackBar(content=ft.Text("Settings saved!")))

    def build(self):
        return ft.Container(
            content=ft.Column([
                ft.Text("Settings", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                self.api_key,
                ft.Divider(),
                ft.Text("ControlNet Settings", size=16, weight=ft.FontWeight.BOLD),
                self.controlnet_type,
                self.controlnet_scale,
                self.preprocess_toggle,
                self.canny_controls,  # Add Canny controls
                ft.Divider(),
                ft.ElevatedButton(
                    "Save Settings",
                    on_click=self.save_settings
                ),
            ], spacing=20),
            padding=20,
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=10,
            width=300,
        )

class CannyControls(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.low_threshold = ft.Slider(
            min=CannySettings.LOW_THRESHOLD_RANGE[0],
            max=CannySettings.LOW_THRESHOLD_RANGE[1],
            value=CannySettings.DEFAULT_LOW_THRESHOLD,
            label="Low Threshold: {value}",
            width=250,
            on_change=self.slider_changed
        )
        
        self.high_threshold = ft.Slider(
            min=CannySettings.HIGH_THRESHOLD_RANGE[0],
            max=CannySettings.HIGH_THRESHOLD_RANGE[1],
            value=CannySettings.DEFAULT_HIGH_THRESHOLD,
            label="High Threshold: {value}",
            width=250,
            on_change=self.slider_changed
        )
        
        self.blur_size = ft.Dropdown(
            label="Blur Size",
            width=250,
            options=[
                ft.dropdown.Option(str(i), f"{i}x{i}")
                for i in range(
                    CannySettings.BLUR_SIZE_RANGE[0],
                    CannySettings.BLUR_SIZE_RANGE[1] + 1,
                    CannySettings.BLUR_SIZE_RANGE[2]
                )
            ],
            value=str(CannySettings.DEFAULT_BLUR_SIZE),
            on_change=self.slider_changed
        )

        self.dilate_iterations = ft.Slider(
            min=CannySettings.DILATE_ITERATIONS_RANGE[0],
            max=CannySettings.DILATE_ITERATIONS_RANGE[1],
            value=CannySettings.DEFAULT_DILATE_ITERATIONS,
            label="Edge Thickness: {value}",
            width=250,
            on_change=self.slider_changed
        )

    def build(self):
        return ft.Column([
            ft.Text("Canny Edge Settings", size=14, weight=ft.FontWeight.BOLD),
            ft.Text("Low Threshold: Determines sensitivity to weak edges", 
                   size=12, color=ft.colors.GREY_400),
            self.low_threshold,
            ft.Text("High Threshold: Determines strong edge detection", 
                   size=12, color=ft.colors.GREY_400),
            self.high_threshold,
            ft.Text("Blur Size: Reduces noise (higher = smoother edges)", 
                   size=12, color=ft.colors.GREY_400),
            self.blur_size,
            ft.Text("Edge Thickness: Number of dilation iterations", 
                   size=12, color=ft.colors.GREY_400),
            self.dilate_iterations,
        ], spacing=5)

    def get_params(self):
        return CannyParams(
            low_threshold=int(self.low_threshold.value),
            high_threshold=int(self.high_threshold.value),
            blur_size=int(self.blur_size.value),
            dilate_iterations=int(self.dilate_iterations.value)
        )

    def on_change(self, e=None):
        if hasattr(self, 'on_settings_change'):
            self.on_settings_change()

    def slider_changed(self, e):
        if hasattr(self, 'on_settings_change'):
            self.on_settings_change()
