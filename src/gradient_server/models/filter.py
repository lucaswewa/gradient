from pydantic import BaseModel


class NDFilter(BaseModel):
    name: str = ""
    serial_number: str = ""
    display_name: str = ""
    description: str = ""
    shift_x: int = 0
    shift_y: int = 0
    transmissioin: float = 1.0
    luminance_scale: float = 1.0


class XYZFilter(BaseModel):
    name: str = ""
    serial_number: str = ""
    display_name: str = ""
    description: str = ""
    shift_x: int = 0
    shift_y: int = 0
    magnification: float = 1.0
