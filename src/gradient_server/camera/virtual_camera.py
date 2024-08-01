import threading
import time
import numpy as np
import cv2 as cv
from .camera_protocol import CameraProtocol
from .camera_protocol import CameraState


class VirtualCamera(CameraProtocol):
    def __init__(self):
        self._thread: threading.Thread = None
        self._lock = threading.RLock()
        self._frame = None
        self._status = CameraState.CLOSED
        self._exposure = None
        self._cb = None
        self._delay = 0.3
        self._onhold = False

    def thread_run(self):
        while (
            self._status == CameraState.STREAMING
            or self._status == CameraState.CAPTURING
        ):
            with self._lock:
                if self._status == CameraState.CAPTURING:
                    for i in range(10):
                        time.sleep(0.1)
                    print("zzz.......")
                    time.sleep(1)
                    frame = np.random.rand(480, 640, 3) * 50
                    print("======== capture frame")
                    # time.sleep(0.5)
                    self._status = CameraState.STREAMING
                else:
                    frame = np.random.rand(480, 640, 3) * 255
                    print("stream frame")

                self._frame = frame.astype(np.uint8)
                self._frame = cv.cvtColor(self._frame, cv.COLOR_BGR2GRAY)
                try:
                    if self._cb is not None:
                        print("callback...")
                        self._cb(self._frame.copy())
                except Exception as e:
                    print(f"ah! {e}")

            time.sleep(self._delay)

    def open(self):
        with self._lock:
            self._status = CameraState.OPENED

    def close(self):
        with self._lock:
            self._status = CameraState.CLOSED

    def get_state(self):
        return self._status

    def get_exposure(self) -> float:
        return self._exposure

    def set_exposure(self, exposure: float):
        self._exposure = exposure

    def set_binning(self, binning_hori, binning_vert):
        self._binning_hori = binning_hori
        self._binning_vert = binning_vert

    def get_binning(self) -> tuple[int, int]:
        return self._binning_hori, self._binning_vert

    def register_frame_callback(self, cb):
        self._cb = cb

    def start_stream(self):
        with self._lock:
            self._status = CameraState.STREAMING
        self._thread = threading.Thread(target=self.thread_run)
        self._thread.setDaemon(True)
        self._thread.start()

    def stop_stream(self):
        with self._lock:
            self._status = CameraState.OPENED
            self._cb = None
            self._thread = None

    def capture(self):
        with self._lock:
            self._status = CameraState.CAPTURING
