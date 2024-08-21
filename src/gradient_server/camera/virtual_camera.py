import threading
import time
import numpy as np
import cv2 as cv
from .camera_protocol import CameraProtocol
from .camera_protocol import CameraState
from .camera_protocol import PixelFormat
from typing import Set


class VirtualCamera(CameraProtocol):
    def __init__(self):
        self._thread: threading.Thread = None
        self._lock = threading.RLock()
        self._frame = None
        self._status = CameraState.CLOSED
        self._pixel_format = PixelFormat.MONO12
        self._exposure = 5.0
        self._cb: Set[callable] = set()
        self._cbb = None
        self._delay = 0.002
        self._onhold = False

    def thread_run(self):
        idle_step = 0

        while self._status != CameraState.CLOSED:
            if self._status == CameraState.STREAMING:
                frame = np.random.rand(480, 640, 3) * 255
                self._frame = frame.astype(np.uint8)
                self._frame = cv.cvtColor(self._frame, cv.COLOR_BGR2GRAY)
                try:
                    with self._lock:
                        for cb in self._cb:
                            cb(self._frame.copy())
                except Exception as e:
                    print(f"ah! {e}")
            elif self._status == CameraState.CAPTURING1:
                frame = np.random.rand(480, 640, 3) * 0
                self._frame = frame.astype(np.uint8)
                self._frame = cv.cvtColor(self._frame, cv.COLOR_BGR2GRAY)
                try:
                    with self._lock:
                        for cb in self._cb:
                            cb(self._frame.copy())
                except Exception as e:
                    print(f"ah! {e}")
                self._status = CameraState.IDLE1
            elif self._status == CameraState.CAPTURING2:
                frame = np.random.rand(480, 640, 3) * 255
                self._frame = frame.astype(np.uint8)
                try:
                    with self._lock:
                        for cb in self._cb:
                            cb(self._frame.copy())
                        if self._cbb is not None:
                            self._cbb(self._frame.copy())
                except Exception as e:
                    print(f"ah! {e}")
                self._status = CameraState.IDLE2
            elif self._status == CameraState.IDLE1:
                try:
                    with self._lock:
                        for cb in self._cb:
                            cb(self._frame.copy())
                except Exception as e:
                    print(f"ah! {e}")
                if idle_step < 20:
                    idle_step += 1
                else:
                    self._status = CameraState.CAPTURING2
                    idle_step = 0
            elif self._status == CameraState.IDLE2:
                try:
                    with self._lock:
                        for cb in self._cb:
                            cb(self._frame.copy())
                except Exception as e:
                    print(f"ah! {e}")
                if idle_step < 30:
                    idle_step += 1
                else:
                    self._status = CameraState.STREAMING
                    idle_step = 0

            time.sleep(self._delay)

    def open(self):
        with self._lock:
            self._status = CameraState.OPENED

    def close(self):
        with self._lock:
            self._status = CameraState.CLOSED

    def get_state(self):
        return self._status

    def get_pixel_format(self) -> PixelFormat:
        return self._pixel_format

    def set_pixel_format(self, format: PixelFormat):
        self._pixel_format = format

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
        self._cb.add(cb)

    def start_stream(self):
        with self._lock:
            self._status = CameraState.STREAMING
        self._thread = threading.Thread(target=self.thread_run)
        self._thread.setDaemon(True)
        self._thread.start()

    def stop_stream(self):
        with self._lock:
            self._status = CameraState.OPENED
            self._cb = set()
            self._thread = None

    def capture(self):
        frame = []

        def cb(data):
            frame.append(data)

        with self._lock:
            self._cbb = cb
            self._status = CameraState.CAPTURING1
        while len(frame) < 1:
            time.sleep(0)
        with self._lock:
            self._cbb = None
        return frame[0]
