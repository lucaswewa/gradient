from xthings import XThing, xproperty, xaction, xlcrud
from xthings.descriptors import PngImageStreamDescriptor
from xthings.server import XThingsServer
from xthings.action import CancellationToken, ActionProgressNotifier
from pydantic import BaseModel, StrictFloat, StrictStr, StrictInt
from fastapi.responses import HTMLResponse
import numpy as np
import time
import logging
import threading
from typing import List
import uuid

from ..camera.virtual_camera import VirtualCamera
from ..filterwheel.virtual_filterwheel import VirtualFilterwheel
from ..stage.virtual_stage import VirtualStage
from ..prescription.virtual_rxcompensation import VirtualRxCompensation
from ..models.calibration import (
    DarkFieldCalibration,
    DarkFieldCalibrationCreate,
    DarkFieldCalibrationUpdate,
)

MOCK_CAMERA_NAME = "xthings.components.cameras.mockcamera"
MOCK_COLOR_FILTERWHEEL = "xthings.components.filterwheels.mockColorFilters"
MOCK_ND_FILTERWHEEL = "xthings.components.filterwheels.mockNDFilters"
MOCK_STAGE = "xthings.components.stages.mockStage"
MOCK_RX_COMPENSATION = "xthings.components.prescription.mockRxCompensation"

import io
import time
from fastapi import FastAPI, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session
from ..storage.database import engine, SessionLocal
from ..storage import crud, schemas

schemas.Base.metadata.create_all(bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class User(BaseModel):
    id: int
    name: str


user1 = User(id=1, name="Jane")
user2 = User(id=2, name="John")


class MyXThing(XThing):
    png_stream_cv = PngImageStreamDescriptor(ringbuffer_size=100)
    _xyz: User

    def __init__(self, service_type, service_name):
        XThing.__init__(self, service_type, service_name)

    def setup(self):
        super().setup()
        self._streaming = False
        self._delay = 0.1
        self._xyz = user1

        xyzFilters: VirtualFilterwheel = self.find_component(MOCK_COLOR_FILTERWHEEL)
        xyzFilters.set_position_mapping({0: "X", 1: "Y", 2: "Z", 3: "CLEAR"})
        xyzFilters.open()
        ndFilters: VirtualFilterwheel = self.find_component(MOCK_ND_FILTERWHEEL)
        ndFilters.set_position_mapping(
            {0: "CLEAR", 1: "ND1", 2: "ND2", 3: "ND3", 4: "BLOCK"}
        )
        ndFilters.open()

        return self

    def teardown(self):
        self._xyz = None
        super().teardown()
        return self

    @xproperty(model=StrictFloat)
    def xyz(self):
        return self._xyz

    @xyz.setter
    def xyz(self, v):
        self._xyz = v

    @xproperty(model=StrictFloat)
    def exposure_time(self):
        camera: VirtualCamera = self.find_component(MOCK_CAMERA_NAME)
        exposure = camera.get_exposure()
        return exposure

    @exposure_time.setter
    def exposure_time(self, exposure):
        camera: VirtualCamera = self.find_component(MOCK_CAMERA_NAME)
        camera.set_exposure(exposure)

    @xproperty(model=StrictStr)
    def pixel_format(self):
        camera: VirtualCamera = self.find_component(MOCK_CAMERA_NAME)
        format = camera.get_pixel_format()
        return format

    @pixel_format.setter
    def pixel_format(self, format):
        camera: VirtualCamera = self.find_component(MOCK_CAMERA_NAME)
        camera.set_pixel_format(format)

    @xaction()
    def open_camera(
        self, apn: ActionProgressNotifier, ct: CancellationToken, logger: logging.Logger
    ):
        camera: VirtualCamera = self.find_component(MOCK_CAMERA_NAME)
        camera.open()

    @xaction()
    def close_camera(
        self, apn: ActionProgressNotifier, ct: CancellationToken, logger: logging.Logger
    ):
        camera: VirtualCamera = self.find_component(MOCK_CAMERA_NAME)
        camera.close()

    @xaction()
    def start_stream_camera(
        self, apn: ActionProgressNotifier, ct: CancellationToken, logger: logging.Logger
    ):
        def cb(frame):
            try:
                if self.png_stream_cv.add_frame(frame=frame):
                    apn("add frame")
            except Exception as e:
                print(threading.currentThread(), f"exception {e}")

        apn("start streaming")
        camera: VirtualCamera = self.find_component(MOCK_CAMERA_NAME)
        camera.register_frame_callback(cb)
        camera.start_stream()

    @xaction()
    def stop_stream_camera(
        self, apn: ActionProgressNotifier, ct: CancellationToken, logger: logging.Logger
    ):
        camera: VirtualCamera = self.find_component(MOCK_CAMERA_NAME)
        camera.stop_stream()
        self._streaming = False

    @xaction(input_model=None, output_model=StrictFloat)
    def capture_camera(
        self, apn: ActionProgressNotifier, ct: CancellationToken, logger: logging.Logger
    ):
        camera: VirtualCamera = self.find_component(MOCK_CAMERA_NAME)
        frame = camera.capture()
        return frame.mean()

    @xaction(input_model=User, output_model=User)
    def cancellable_action(
        self,
        s: User,
        apn: ActionProgressNotifier,
        cancellation_token: CancellationToken,
        logger: logging.Logger,
    ):
        t = self.settings["a"]
        logger.info("func start")
        logger.info(f"start to sleep {t} seconds")
        n = 0
        while n < 100:
            time.sleep(t)
            cancellation_token.check(0)
            n += 1
        self.foo = s
        print("end")
        logger.info("func end")
        return s

    @xproperty(model=StrictStr)
    def color_filter(self) -> StrictStr:
        xyzFilters: VirtualFilterwheel = self.find_component(MOCK_COLOR_FILTERWHEEL)
        filter = xyzFilters.get_position_by_name()

        return filter

    @xaction(input_model=StrictStr)
    def move_color_filter(self, color_filter, apn, ct, logger):
        xyzFilters: VirtualFilterwheel = self.find_component(MOCK_COLOR_FILTERWHEEL)
        xyzFilters.set_position_by_name(color_filter)

    @xproperty(model=StrictStr)
    def nd_filter(self) -> StrictStr:
        ndFilters: VirtualFilterwheel = self.find_component(MOCK_ND_FILTERWHEEL)
        filter = ndFilters.get_position_by_name()
        return filter

    @xaction(input_model=StrictStr)
    def move_nd_filter(self, nd_filter, apn, ct, logger):
        ndFilters: VirtualFilterwheel = self.find_component(MOCK_ND_FILTERWHEEL)
        ndFilters.set_position_by_name(nd_filter)

    @xproperty(model=StrictFloat)
    def stage(self) -> StrictFloat:
        stage: VirtualStage = self.find_component(MOCK_STAGE)
        pos = stage.get_position()
        return pos

    @xaction(input_model=StrictFloat)
    def move_stage_abs(self, pos_abs, apn, ct, logger):
        stage: VirtualStage = self.find_component(MOCK_STAGE)
        stage.move_position_abs(pos_abs)

    @xaction(input_model=StrictFloat)
    def move_stage_rel(self, pos_rel, apn, ct, logger):
        stage: VirtualStage = self.find_component(MOCK_STAGE)
        stage.move_position_rel(pos_rel)

    @xproperty(model=StrictFloat)
    def rx_sph_power(self):
        rxCompensation: VirtualRxCompensation = self.find_component(
            MOCK_RX_COMPENSATION
        )
        sph_power = rxCompensation.get_spherical_rx()
        return sph_power

    @xproperty(model=StrictFloat)
    def rx_cyl_power(self):
        rxCompensation: VirtualRxCompensation = self.find_component(
            MOCK_RX_COMPENSATION
        )
        cyl_power = rxCompensation.get_cylindrical_rx_power()
        return cyl_power

    @xproperty(model=StrictFloat)
    def rx_cyl_axis(self):
        rxCompensation: VirtualRxCompensation = self.find_component(
            MOCK_RX_COMPENSATION
        )
        cyl_axis = rxCompensation.get_cylindrical_rx_axis()
        return cyl_axis

    @xaction(input_model=StrictFloat)
    def move_rx_sph_power(self, sph_power, apn, ct, logger):
        rxCompensation: VirtualRxCompensation = self.find_component(
            MOCK_RX_COMPENSATION
        )
        rxCompensation.move_spherical_rx(sph_power)

    @xaction(input_model=StrictFloat)
    def move_rx_cyl_power(self, cyl_power, apn, ct, logger):
        rxCompensation: VirtualRxCompensation = self.find_component(
            MOCK_RX_COMPENSATION
        )
        rxCompensation.move_cylindrical_rx_power(cyl_power)

    @xaction(input_model=StrictFloat)
    def move_rx_cyl_axis(self, cyl_axis, apn, ct, logger):
        rxCompensation: VirtualRxCompensation = self.find_component(
            MOCK_RX_COMPENSATION
        )
        rxCompensation.move_cylindrical_rx_axis(cyl_axis)

    @xproperty(model=List[DarkFieldCalibration])
    def darkfieldcalibrations(self):
        db = get_db()
        items = crud.list_darkfieldcalibrationitems(next(db), 0, 100)
        for item in items:
            item.image_data = b"test"

        return items

    @xaction(input_model=DarkFieldCalibrationCreate, output_model=DarkFieldCalibration)
    def create_darkfieldcalibration(self, dfc, apn, ct, logger):
        db = get_db()
        s = time.time()

        # convert np.ndarray to byte array
        memfile = io.BytesIO()
        np.save(memfile, x)
        image = memfile.getvalue()
        dfc.image_data = image
        item = crud.create_darkfieldcalibrationitem(next(db), dfc)
        e = time.time()
        print(e - s)

        # use dummy data for HTTP response
        item.image_data = "data:image/;base64,kdjksdfjlsfjskl"
        dfc.image_data = b"xyz"
        return DarkFieldCalibration.model_validate(item)

    @xaction(input_model=DarkFieldCalibrationUpdate, output_model=DarkFieldCalibration)
    def update_darkfieldcalibration(self, dfc, apn, ct, logger):
        db = get_db()
        item = crud.update_darkfieldcalibrationitem(next(db), dfc.id, dfc)
        if item is None:
            raise HTTPException(status_code=404)
        item.image_data = "data:image/;base64,kdjksdfjlsfjskl"
        return DarkFieldCalibration.model_validate(item)

    @xaction(input_model=StrictInt)
    def delete_darkfieldcalibration(self, id, apn, ct, logger):
        db = get_db()
        crud.drop_darkfieldcalibrationitem(next(db), id)

    @xlcrud(item_model=StrictStr)
    def ffc(self):
        return {}

    @ffc.create_func
    def ffc(self, v: str):
        id = uuid.uuid4()
        return {"id": id, "v": v}

    @ffc.retrieve_func
    def ffc(self, id: uuid.UUID):
        return {"id": id, "v": "vvvvv"}

    @ffc.update_func
    def ffc(self, id: uuid.UUID, v: str):
        return {"id": id, "v": v + "_updated"}

    @ffc.delete_func
    def ffc(self, id: uuid.UUID):
        return {"id": id}


camera = VirtualCamera()
xyzFilterwheel = VirtualFilterwheel("XYZ Filters")
ndFilterwheel = VirtualFilterwheel("ND Filters")
stage = VirtualStage("Focusing Stage")
rxCompensation = VirtualRxCompensation("RX Compensation")

myxthing = MyXThing("_xthings._tcp.local.", "myxthing._xthings._tcp.local.")
myxthing.add_component(camera, MOCK_CAMERA_NAME)
myxthing.add_component(xyzFilterwheel, MOCK_COLOR_FILTERWHEEL)
myxthing.add_component(ndFilterwheel, MOCK_ND_FILTERWHEEL)
myxthing.add_component(stage, MOCK_STAGE)
myxthing.add_component(rxCompensation, MOCK_RX_COMPENSATION)

xthings_server = XThingsServer(settings_folder="./settings")
xthings_server.add_xthing(myxthing, "/myxthing")
myxthing.foo = User(id=2, name="Smith")

app = xthings_server.app

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <p>{"messageType": "addActionObservation", "data": {"start_stream_camera": true}}</p>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/myxthing/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

"""
{"messageType": "addPropertyObservation", "data": {"xyz": true}}
{"messageType": "addActionObservation", "data": {"start_stream_camera": true}}
"""


@app.get("/wsclient", tags=["websockets"])
async def get():
    return HTMLResponse(html)


######## Experimental endpoints


# def adapt_array(arr):
#     """
#     http://stackoverflow.com/a/31312102/190597 (SoulNibbler)
#     """
#     out = io.BytesIO()
#     np.save(out, arr)
#     out.seek(0)
#     return sqlite3.Binary(out.read())


# def convert_array(text):
#     out = io.BytesIO(text)
#     out.seek(0)
#     return np.load(out)


# sqlite3.register_adapter(np.ndarray, adapt_array)
# sqlite3.register_converter("array", convert_array)

x = np.random.randn(56000000).reshape(8000, 7000)
x = x / 10
x = x + 0.5
x[x < 0] = 0
x[x > 1] = 1

x = x * (1 << 12)
x = x.astype(np.uint16)


@app.get("/darkfieldcallibrations", response_model=List[DarkFieldCalibration])
async def list_dfc(limit: int = 100, offset: int = 0, db: Session = Depends(get_db)):
    items = crud.list_darkfieldcalibrationitems(db, offset, limit)
    for i in range(len(items)):
        items[i].image_data = f"adsf_{i}"
    return items


@app.post("/darkfieldcalibrations", response_model=DarkFieldCalibration)
async def create_dfc(data: DarkFieldCalibrationCreate, db: Session = Depends(get_db)):
    s = time.time()

    # convert np.ndarray to byte array
    memfile = io.BytesIO()
    np.save(memfile, x)
    image = memfile.getvalue()
    data.image_data = image
    item = crud.create_darkfieldcalibrationitem(db, data)
    e = time.time()
    print(e - s)

    # use dummy data for HTTP response
    item.image_data = "data:image/;base64,kdjksdfjlsfjskl"

    return item


@app.get("/darkfieldcallibrations/{item_id}", response_model=DarkFieldCalibration)
async def retrieve_dfc(item_id: int, db: Session = Depends(get_db)):
    item = crud.retrieve_darkfieldcalibrationitem(db, item_id)
    if item is None:
        raise HTTPException(status_code=404)

    # convert bytet array to np.ndarray
    memfile = io.BytesIO()
    data = item.image_data
    memfile.write(data)
    memfile.seek(0)
    arr = np.load(memfile)
    print(arr.mean())

    # use dummy data for HTTP response
    dfc = DarkFieldCalibration.model_validate(item)
    dfc.image_data = "data:image/;base64,kdjksdfjlsfjskl"
    return dfc


@app.put("/darkfieldcallibrations/{item_id}", response_model=DarkFieldCalibration)
async def update_dfc(
    id: int, data: DarkFieldCalibrationUpdate, db: Session = Depends(get_db)
):
    item = crud.update_darkfieldcalibrationitem(db, id, data)
    if item is None:
        raise HTTPException(status_code=404)
    item.image_data = "data:image/;base64,kdjksdfjlsfjskl"
    return item


@app.delete("/darkfieldcallibrations/{item_id}", status_code=204)
async def drop_dfc(item_id: int, db: Session = Depends(get_db)):
    crud.drop_darkfieldcalibrationitem(db, item_id)
    return None


######## Experimental endpoints


def gradient_serve():
    pass


if __name__ == "__main__":
    gradient_serve()
