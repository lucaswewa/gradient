from pydantic import BaseModel


class PrescriptionLens(BaseModel):
    name: str = ""
    serial_number: str = ""
    display_name: str = ""
    description: str = ""
    spheric_power: float = 0.0
    cylindric_power: float = 0.0
    cylindric_axis: float = 0.0
