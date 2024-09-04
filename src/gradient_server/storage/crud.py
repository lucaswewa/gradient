from sqlalchemy.orm import Session

from .schemas import DarkFieldCalibrationItem
from ..models.calibration import (
    DarkFieldCalibrationCreate,
    DarkFieldCalibrationUpdate,
)

from typing import Union, List, Optional


def list_darkfieldcalibrationitems(
    db: Session, offset: int = 0, limit: int = 100
) -> List[DarkFieldCalibrationItem]:
    return db.query(DarkFieldCalibrationItem).offset(offset).limit(limit).all()


def create_darkfieldcalibrationitem(
    db: Session, data: DarkFieldCalibrationCreate
) -> DarkFieldCalibrationItem:
    db_item = DarkFieldCalibrationItem(**data.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def retrieve_darkfieldcalibrationitem(
    db: Session, id: int
) -> Optional[DarkFieldCalibrationItem]:
    data = db.query(DarkFieldCalibrationItem).get(id)
    return data


def update_darkfieldcalibrationitem(
    db: Session,
    item: Union[int, DarkFieldCalibrationItem],
    data: DarkFieldCalibrationUpdate,
) -> Optional[DarkFieldCalibrationItem]:
    if isinstance(item, int):
        item = retrieve_darkfieldcalibrationitem(db, item)

    if item is None:
        return None

    # bug: we need change fields set in the data only
    for key, value in data:
        if value is not None:
            setattr(item, key, value)
    db.commit()
    return item


def drop_darkfieldcalibrationitem(db: Session, item_id: int) -> None:
    db.query(DarkFieldCalibrationItem).filter(
        DarkFieldCalibrationItem.id == item_id
    ).delete()
    db.commit()
    return None
