from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session
import numpy as np
import io

from ..models.calibration import (
    DarkFieldCalibrationCreate,
    DarkFieldCalibration,
    DarkFieldCalibrationUpdate,
)
from . import crud, schemas
from .database import engine, SessionLocal

schemas.Base.metadata.create_all(bind=engine)

app = FastAPI()

x = np.random.randn(56000000).reshape(8000, 7000)
x = x / 10
x = x + 0.5
x[x < 0] = 0
x[x > 1] = 1

x = x * (1 << 12)
x = x.astype(np.uint16)
print(x.mean())
import time


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/items", response_model=List[schemas.Item])
async def items_action_list(
    limit: int = 100, offset: int = 0, db: Session = Depends(get_db)
):
    items = crud.list_items(db, offset, limit)
    return items


@app.get("/items/{item_id}", response_model=schemas.Item)
async def items_action_retrieve(item_id: int, db: Session = Depends(get_db)):
    item = crud.get_item(db, item_id)
    if item is None:
        raise HTTPException(status_code=404)

    return item


@app.post("/items", response_model=schemas.Item)
async def item_action_create(data: schemas.ItemCreate, db: Session = Depends(get_db)):
    s = time.time()

    memfile = io.BytesIO()
    np.save(memfile, x)
    image = memfile.getvalue()
    data.image = image
    item = crud.create_item(db, data)
    e = time.time()
    print(e - s)

    return item


@app.put("/items/{item_id}", response_model=schemas.Item)
async def items_action_update(
    item_id: int, data: schemas.ItemUpdate, db: Session = Depends(get_db)
):
    item = crud.update_item(db, item_id, data)
    if item is None:
        raise HTTPException(status_code=404)
    return item


@app.delete("/items/{item_id}", status_code=204)
async def items_action_delete(item_id: int, db: Session = Depends(get_db)):
    crud.drop_item(db, item_id)
    return None


@app.post("/dfcitems", response_model=DarkFieldCalibration)
async def dark_field_calibration_item_create(
    data: DarkFieldCalibrationCreate, db: Session = Depends(get_db)
):
    s = time.time()

    memfile = io.BytesIO()
    np.save(memfile, x)
    image = memfile.getvalue()
    data.image_data = image
    item = crud.create_darkfieldcalibrationitem(db, data)
    e = time.time()
    print(e - s)

    return item


@app.get("/dfcitems/{item_id}", response_model=DarkFieldCalibration)
async def dark_field_calibration_item_retrieve(id: int, db: Session = Depends(get_db)):
    item = crud.retrieve_darkfieldcalibrationitem(db, id)
    if item is None:
        raise HTTPException(status_code=404)

    return item


@app.put("/dfcitems/{item_id}", response_model=DarkFieldCalibrationUpdate)
async def dark_field_calibration_item_update(
    id: int, data: DarkFieldCalibrationUpdate, db: Session = Depends(get_db)
):
    item = crud.update_darkfieldcalibrationitem(db, id, data)
    if item is None:
        raise HTTPException(status_code=404)
    return item


@app.post("/dfc", response_model=DarkFieldCalibration)
async def dfc_create(data: DarkFieldCalibrationCreate, db: Session = Depends(get_db)):
    s = time.time()

    memfile = io.BytesIO()
    np.save(memfile, x)
    image = memfile.getvalue()
    data.image_data = image
    item = crud.create_dfc(db, data)
    e = time.time()
    print(e - s)

    item.image_data = "data:image/;base64,kdjksdfjlsfjskl"
    return item
