from pydantic import BaseModel


class CameraModel(BaseModel):
    name: str = ""
    display_name: str = ""
    serial_number: str = ""
    description: str = ""
    camera_type: str = "virtual"

    trigger_mode: str = "software"

    gain: float = 1.0

    saturation_level: float = 0.75
    max_exposure_time_ms: float = 5000
    min_exposure_time_ms: float = 11.111
    exposure_time_multiple_enabled: bool = False
    exposure_time_multiple_ms: float = 11.111
    exposure_time_ms: float = 5
    exposure_mode: str = "fixed"

    pixel_format: str = "mono12"

    binning_x: int = 1
    binning_y: int = 1

    focus_mode: str = "fixed"

    temperature_mode: str = "auto"
    temperature: float = 20.0
    set_temperature: float = 20.0
