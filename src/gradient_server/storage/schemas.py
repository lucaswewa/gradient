from typing import Optional

from pydantic import BaseModel
from datetime import datetime

from sqlalchemy import Column, Integer, String, BLOB, DateTime
from sqlalchemy.sql import func
from .database import Base


class DarkFieldCalibrationItem(Base):
    __tablename__ = "dark_field_cali_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    display_name = Column(String, index=False)
    description = Column(String, index=False)
    binning_x = Column(Integer, index=False)
    binning_y = Column(Integer, index=False)
    image_width = Column(Integer, index=False)
    image_height = Column(Integer, index=False)
    image_data = Column(BLOB)

    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
