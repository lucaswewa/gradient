from xthings import XThing, xproperty, xaction
from xthings.descriptors import PngImageStreamDescriptor
from xthings.server import XThingsServer
from xthings.action import CancellationToken, ActionProgressNotifier
from pydantic import BaseModel, StrictFloat, StrictStr, StrictInt
from fastapi.responses import HTMLResponse
import numpy as np
import time
import logging
import threading
from typing import Any
import datetime


from ..camera.virtual_camera import VirtualCamera
from ..filterwheel.virtual_filterwheel import VirtualFilterwheel

MOCK_CAMERA_NAME = "xthings.components.cameras.mockcamera"
MOCK_COLOR_FILTERWHEEL = "xthings.components.filterwheels.mockColorFilters"
MOCK_ND_FILTERWHEEL = "xthings.components.filterwheels.mockNDFilters"


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


camera = VirtualCamera()
xyzFilterwheel = VirtualFilterwheel("XYZ")
ndFilterwheel = VirtualFilterwheel("ND")

myxthing = MyXThing("_xthings._tcp.local.", "myxthing._xthings._tcp.local.")
myxthing.add_component(camera, MOCK_CAMERA_NAME)
myxthing.add_component(xyzFilterwheel, MOCK_COLOR_FILTERWHEEL)
myxthing.add_component(ndFilterwheel, MOCK_ND_FILTERWHEEL)

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


def gradient_serve():
    pass


if __name__ == "__main__":
    gradient_serve()
