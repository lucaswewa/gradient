from pydantic import BaseModel
from typing import Any


class DarkFieldCalibration(BaseModel):
    name: str = ""
    display_name: str = ""
    description: str = ""
    binning_x: int = 1
    binning_y: int = 1
    image_width: int = 0
    image_height: int = 0
    image_data: Any = None


class FlatFieldCalibration(BaseModel):
    name: str = ""
    display_name: str = ""
    description: str = ""

    measurement_location_center_x: int = 0
    measurement_location_center_y: int = 0
    measurement_size_x: int = 100
    measurement_size_y: int = 100
    measurement_shape: str = "circle"

    spectra_range: Any = None
    calibration_type: str = "luminance"
    uniform_luminance_source: str = "integrating sphere"
    lens_name: str = "lens1"
    lens_aperature: str = "3 mm"  # or "f/16"
    binning_x: int = 0
    binning_y: int = 0
    image_width: int = 0
    image_height: int = 0
    image_data: Any = None


class ColorShiftCalibration(BaseModel):
    name: str = ""
    display_name: str = ""
    color_filter: str = "X"
    nd_filter: str = "ND1"
    shift_x: int = 0
    shift_y: int = 0


class DistortionCalibration(BaseModel):
    number_x: int = 0
    number_y: int = 0
    x_min: int = 0
    y_min: int = 0
    x_max: int = 0
    y_min: int = 0
    camera_orientation: str = "none"
    camera_mirror: str = "left-right"
    coefficients: list[float] = [1, 1, 1, 1]
    matrix: list[list[float]] = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]


class SingleFilterBrightnessCalibration(BaseModel):
    nd_filter: str = "ND1"
    color_filter: str = "Y"
    lens_aperature: str = "3 mm"
    measurement_location_center_x: int = 0
    measurement_location_center_y: int = 0
    measurement_size_x: int = 100
    measurement_size_y: int = 100
    measurement_shape: str = "circle"
    luminance_coefficient_nits_per_graylevel: float = 1.0


class FourColorCalibration(BaseModel):
    nd_filter: str = "ND1"
    lens_aperature: str = "3 mm"
    measurement_location_center_x: int = 0
    measurement_location_center_y: int = 0
    measurement_size_x: int = 100
    measurement_size_y: int = 100
    measurement_shape: str = "circle"
    color_matrix: list[list[float]] = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    color_space: str = "cxcylv (CIE1931)"  # or "u'v' (CIE1976)"


class ImageScalingCalibration(BaseModel):
    object_to_pixel_magnification: float = 100
    pixel_size_um: float = 3.45
    image_size_x: int = 1000
    image_size_y: int = 1000


class StrayLightCalibration(BaseModel):
    interpolation_method: str = "lininterpolate"
    number_filters: int = 0


class MultiPointCalibration(BaseModel):
    calibration_points: dict[str, tuple[int, int]] = {}
    calibration_type: str = "one filter Y"  # or "three filters XYZ"
    calibration_data: dict[str, Any] = {}
    interpolation_method: str = "cubic"


class BrightnessRescalingCalibration(BaseModel):
    color_filter: str = "X"
    nd_filter: str = "ND1"
    scale_coefficient: float = 1.0
