import numpy as np
import vmbpy
import time

from typing import Callable
import threading
import cv2
import anyio

class VmbX:
    def __init__(self, device_id: str = None, frame_handler: Callable = None):
        self.vimba: vmbpy.VmbSystem = vmbpy.VmbSystem.get_instance()
        self.camera: vmbpy.Camera = None

        self.lock = threading.RLock()

        self._exposure_time = 0.0
        self._gain = 0.0
        self._pixel_format = None

        self._device_id = device_id
        self._frame_handler = frame_handler

    async def __aenter__(self):
        await anyio.to_thread.run_sync(self.__enter__)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await anyio.to_thread.run_sync(self.__exit__, exc_type, exc, tb)
        
    def __enter__(self):
        with self.lock:
            if not self.vimba._context_entered:
                self.vimba.__enter__()
            if self.camera is None:
                if self._device_id is not None:
                    self.camera = self.vimba.get_camera_by_id(self._device_id)
                else:
                    cameras = self.vimba.get_all_cameras()
                    self.camera = cameras[0]
                self.camera.set_access_mode(vmbpy.AccessMode.Full)

            if not self.camera._context_entered:
                self.camera.__enter__()

        return self
    
    def __exit__(self, exc_type, exc, tb):
        with self.lock:
            if self.camera is not None and self.camera._context_entered:
                self.camera.__exit__(exc_type, exc, tb)
            if self.vimba._context_entered:
                self.vimba.__exit__(exc_type, exc, tb)
         
    def _streaming_frame_handler(self, cam: vmbpy.Camera, stream: vmbpy.Stream, frame: vmbpy.Frame):
        image = frame.as_numpy_ndarray()
        image = image.reshape(image.shape[0:2])

        if self._frame_handler is not None:
            self._frame_handler(image)

        cam.queue_frame(frame)

    def start_streaming(self):
        self.camera.start_streaming(handler=self._streaming_frame_handler, buffer_count=10)

    def stop_streaming(self):
        if self.camera.is_streaming():
            self.camera.stop_streaming()

    def is_streaming(self) -> bool:
        return self.camera.is_streaming()
    
    def set_exposure_time(self, exposure_time: float):
        self.camera.ExposureTime.set(exposure_time)
        return self.get_exposure_time()
    
    def get_exposure_time(self) -> float:
        self._exposure_time = self.camera.ExposureTime.get()
        return self._exposure_time
    
    def set_pixel_format(self, pixel_format: str):
        self.camera.PixelFormat.set(pixel_format)
        return self.get_pixel_format()
    
    def get_pixel_format(self) -> str:
        self._pixel_format = self.camera.PixelFormat.get()
        return self._pixel_format
    
    def set_gain(self, gain: float):
        self.camera.Gain.set(gain)
        return self.get_gain()
    
    def get_gain(self) -> float:
        self._gain = self.camera.Gain.get()
        return self._gain
    
    def grab_one(self):
        if not self.camera._context_entered:
            print("error: NOT in camera context")
            return None

        frame = self.camera.get_frame()
        frame_data = frame.as_numpy_ndarray()
        frame_data = frame_data.reshape(frame_data.shape[0:2])

        return frame_data    

    def sw_frame_handler(self, cam: vmbpy.Camera, stream: vmbpy.Stream, frame: vmbpy.Frame):
        print(f"7: {time.time()}")
        image = frame.as_numpy_ndarray()
        image = image.reshape(image.shape[0:2])
        if self._frame_handler:
            self._frame_handler(image)
        time.sleep(1)
        cam.queue_frame(frame)

    def arm(self):
        self.camera.AcquisitionMode.set("Continuous")
        self.camera.TriggerSelector.set("FrameStart")
        self.camera.TriggerSource.set("Software")
        self.camera.TriggerMode.set("On")
        print(f"1: {time.time()}")
        self.camera.start_streaming(handler=self.sw_frame_handler, buffer_count=10)
        print(f"1.1: started streaming")

    def software_trigger(self):
        print(f"3: {time.time()}")
        self.camera.TriggerSoftware.run()
        print(f"4: {time.time()}")

    def disarm(self):
        time.sleep(0.001)
        print(f"5: {time.time()}")
        self.camera.stop_streaming()
        self.camera.TriggerMode.set("Off")
        self.camera.TriggerSelector.set("AcquisitionStart")
        print(f"6: {time.time()}")

