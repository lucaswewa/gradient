"""VimbaX Camera.

This module defines a Thing that is responsible for using the stage and
camera together to perform an autofocus routine.

See repository root for licensing information.
"""
import numpy as np
import vmbpy
import time

from typing import Callable
import threading
import cv2
import anyio

class VmbX:    
    def __init__(self, device_id: str = None, frame_handler: Callable = None):
        super().__init__()
        self.vimba: vmbpy.VmbSystem = vmbpy.VmbSystem.get_instance()
        self.camera: vmbpy.Camera = None

        self.lock = threading.Lock()

        self._exposure_time = 0.0
        self._gain = 0.0
        self._pixel_format = None

        self._device_id = device_id
        self._frame_handler = frame_handler

    async def __aenter__(self):
        await anyio.to_thread.run_sync(self.__enter__)

    async def __aexit__(self, exc_type, exc, tb):
        await anyio.to_thread.run_sync(self.__exit__, exc_type, exc, tb)

    def __enter__(self):
        with self.lock:
            if not self.vimba._context_entered:
                self.vimba.__enter__()
                print("info: ENTERED vimbasystem context")
            else:
                print("error: ALREADY in vimbasystem context")
            if self.camera is None:
                if self._device_id is not None:
                    self.camera = self.vimba.get_camera_by_id(self._device_id)
                else:
                    cameras = self.vimba.get_all_cameras()
                    self.camera = cameras[0]
                self.camera.set_access_mode(vmbpy.AccessMode.Full)

            if not self.camera._context_entered:
                self.camera.__enter__()
                # uncomment the following if we want to reset the camera
                # print("info: ENTERED camera context")
                # ft = self.camera.get_feature_by_name("DeviceReset")
                # ft.run()
                # self.camera._close()

                # import time
                # time.sleep(10)
                # if self._device_id is not None:
                #     self.camera = self.vimba.get_camera_by_id(self._device_id)
                # else:
                #     cameras = self.vimba.get_all_cameras()
                #     self.camera = cameras[0]
                # self.camera.set_access_mode(vmbpy.AccessMode.Full)
                # self.camera.__enter__()
            else:
                print("error: ALREADY in camera context")

            self.camera.stop_streaming()

            self._exposure_time = self.get_exposure_time()
            self._gain = self.get_gain()
            self._pixel_format = self.get_pixel_format()
        
    def __exit__(self, exc_type, exc, tb):
        with self.lock:
            if self.camera and self.camera._context_entered:
                self.camera.__exit__(exc_type, exc, tb)
                print("info: Exited the camera context")
            else:
                print("error: NOT in camera context")

            if self.vimba._context_entered:
                self.vimba.__exit__(exc_type, exc, tb)
                print("info: EXITED the vimbasystem context")
            else:
                print("error: NOT in vimbasystem context")

    def start_streaming(self):
        if not self.camera._context_entered:
            print("error: NOT in camera context")
            return
        
        if not self.camera.is_streaming():
            # self.camera.UserSetSelector.set('Default')
            # self.camera.UserSetLoad.run()            

            self.camera.start_streaming(handler=self._streaming_frame_handler, buffer_count=10)
            print("info: the camera STARTED streaming")
        else:
            print("error: the camera is ALREADY in streaming")

    def stop_streaming(self):
        if not self.camera._context_entered:
            print("error: NOT in camera context")
            return

        if self.camera.is_streaming():
            self.camera.stop_streaming()
            print("info: the camera STOPPED streaming")
        else:
            print("error: the camera is NOT in streaming")

    def is_streaming(self):
        if not self.camera._context_entered:
            print("error: NOT in camera context")
            return False

        return self.camera.is_streaming()
    
    def set_exposure_time(self, exposure_time_in_us):
        if exposure_time_in_us != self._exposure_time:
            self.camera.ExposureTime.set(exposure_time_in_us)
            return self.get_exposure_time()

    def get_exposure_time(self):
        self._exposure_time = self.camera.ExposureTime.get()
        return self._exposure_time

    def set_gain(self, val):
        if val != self._gain:
            self.camera.Gain.set(val)
            self.get_gain()

    def get_gain(self):
        self._gain = self.camera.Gain.get()
        return self._gain

    def set_pixel_format(self, pixel_format):
        if pixel_format != self._pixel_format:

            self.camera.set_pixel_format(vmbpy.PixelFormat[pixel_format])
            return self.get_pixel_format()

    def get_pixel_format(self):
        self._pixel_format = self.camera.get_pixel_format().name
        return self._pixel_format
    
    def grab_one(self):
        """Grab one frame from the camera and return it as a numpy ndarray, using camera's current settings."""
        if not self.camera._context_entered:
            print("error: NOT in camera context")
            return None
        
        frame = self.camera.get_frame()
        frame_data = frame.as_numpy_ndarray()
        frame_data = frame_data.reshape(frame_data.shape[0:2])

        return frame_data
    
    def _streaming_frame_handler(self, cam: vmbpy.Camera, stream: vmbpy.Stream, frame: vmbpy.Frame):
        image = frame.as_numpy_ndarray()
        image = image.reshape(image.shape[0:2])
        if self._frame_handler:
            self._frame_handler(image)
        cam.queue_frame(frame)

    def sw_frame_handler(self, cam: vmbpy.Camera, stream: vmbpy.Stream, frame: vmbpy.Frame):
        image = frame.as_numpy_ndarray()
        image = image.reshape(image.shape[0:2])
        if self._frame_handler:
            self._frame_handler(image)
        cam.queue_frame(frame)


    def arm(self):
        self.camera.AcquisitionMode.set("Continuous")
        self.camera.TriggerSelector.set("FrameStart")
        self.camera.TriggerSource.set("Software")
        self.camera.TriggerMode.set("On")
        self.camera.start_streaming(handler=self.sw_frame_handler, buffer_count=10)

    def software_trigger(self):
        self.camera.TriggerSoftware.run()

    def disarm(self):
        time.sleep(0.001)
        self.camera.stop_streaming()
        self.camera.TriggerMode.set("Off")
        self.camera.TriggerSelector.set("AcquisitionStart")
