from xthings import XThing, xproperty, xaction
from xthings.descriptors import PngImageStreamDescriptor
from xthings.server import XThingsServer
from xthings.action import CancellationToken, ActionProgressNotifier
from pydantic import BaseModel, StrictFloat
from fastapi.responses import HTMLResponse
import numpy as np
import time
import logging
import threading
from typing import Any
import datetime


from ..camera.virtual_camera import VirtualCamera

MOCK_CAMERA_NAME = "xthings.components.cameras.mockcamera"


class User(BaseModel):
    id: int
    name: str


user1 = User(id=1, name="Jane")
user2 = User(id=2, name="John")


class MockCamera:
    def __init__(self):
        self._thread: threading.Thread = None
        self._lock = threading.RLock()
        self._is_open: bool = False
        self._is_streaming: bool = False
        self._frame: Any = None
        self._cb = None
        self._delay = 0.04

    def thread_run(self):
        while self._is_open and self._is_streaming:
            frame = np.random.rand(480, 640, 3) * 255
            with self._lock:
                self._frame = frame.astype(np.uint8)
                try:
                    if self._cb is not None:
                        self._cb(self._frame.copy())
                except Exception as e:
                    print(f"ah! {e}")

            time.sleep(self._delay)

    def open(self):
        self._is_open = True

        print("open camera")

    def close(self):
        self._is_open = False

        print("close camera")

    def start_streaming(self, cb):
        self._is_streaming = True
        self._cb = cb
        self._thread = threading.Thread(target=self.thread_run)
        self._thread.setDaemon(True)
        self._thread.start()

    def stop_streaming(self):
        self._is_streaming = False
        self._cb = None
        self._thread = None

    def get_next_frame(self):
        with self._lock:
            return self._frame.copy()

    def capture(self): ...

    def set_exposure_ms(self, exposure_ms: float): ...

    def get_exposure_ms(self) -> float: ...


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

    @xaction()
    def capture_camera(
        self, apn: ActionProgressNotifier, ct: CancellationToken, logger: logging.Logger
    ):
        camera: VirtualCamera = self.find_component(MOCK_CAMERA_NAME)
        camera.capture()

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


camera = MockCamera()
camera = VirtualCamera()

myxthing = MyXThing("_xthings._tcp.local.", "myxthing._xthings._tcp.local.")
myxthing.add_component(camera, MOCK_CAMERA_NAME)

xthings_server = XThingsServer(settings_folder="./settings")
xthings_server.add_xthing(myxthing, "/xthing")
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
            var ws = new WebSocket("ws://localhost:8000/xthing/ws");
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
