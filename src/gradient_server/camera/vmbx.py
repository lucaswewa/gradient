"""VimbaX Camera.

This module defines a Thing that is responsible for using the stage and
camera together to perform an autofocus routine.

See repository root for licensing information.
"""
import numpy as np
import vmbpy
import time

import threading
import cv2

class VmbX:    
    def __init__(self, frame_handler=None):
        super().__init__()
        self.vimba: vmbpy.VmbSystem = vmbpy.VmbSystem.get_instance()
        self.camera: vmbpy.Camera = None

        self.lock = threading.Lock()

        self._exposure_time = 0.0
        self._gain = 0.0
        self._pixel_format = None

        self._frame_handler = frame_handler

        self.accu_frame_counts = 0
        self.sw_counter = 0

    def enter_camera(self):
        with self.lock:
            if not self.vimba._context_entered:
                self.vimba.__enter__()
                print("info: ENTERED vimbasystem context")
            else:
                print("error: ALREADY in vimbasystem context")
            if self.camera is None:
                cameras = self.vimba.get_all_cameras()
                self.camera = cameras[0]
                self.camera.set_access_mode(vmbpy.AccessMode.Full)

            if not self.camera._context_entered:
                self.camera.__enter__()
                print("info: ENTERED camera context")
                ft = self.camera.get_feature_by_name("DeviceReset")
                ft.run()
                self.camera._close()

                import time
                time.sleep(10)
                cameras = self.vimba.get_all_cameras()
                self.camera = cameras[0]
                self.camera.set_access_mode(vmbpy.AccessMode.Full)
                self.camera.__enter__()
            else:
                print("error: ALREADY in camera context")

            self.camera.stop_streaming()
            self.camera.TriggerMode.set("Off")
            self.camera.TriggerSelector.set("AcquisitionStart")

            self._exposure_time = self.get_exposure_time_in_us()
            self._gain = self.get_gain()
            self._pixel_format = self.get_pixel_format()
        

    def start_streaming(self):
        if not self.camera._context_entered:
            print("error: NOT in camera context")
            return
        
        if not self.camera.is_streaming():
            self.camera.UserSetSelector.set('Default')
            
            # 2. Execute Load Command
            self.camera.UserSetLoad.run()            
            self.camera.start_streaming(handler=self.frame_handler, buffer_count=10)
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
    
    def exit_camera(self):
        with self.lock:
            if self.camera and self.camera._context_entered:
                self.camera.__exit__(None, None, None)
                print("info: Exited the camera context")
            else:
                print("error: NOT in camera context")

            if self.vimba._context_entered:
                self.vimba.__exit__(None, None, None)
                print("info: EXITED the vimbasystem context")
            else:
                print("error: NOT in vimbasystem context")

    def set_exposure_time_in_us(self, exposure_time_in_us):
        if exposure_time_in_us != self._exposure_time:
            self.camera.ExposureTime.set(exposure_time_in_us)
            return self.get_exposure_time_in_us()

    def get_exposure_time_in_us(self):
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

        frame = self.camera.get_frame()
        frame_data = frame.as_numpy_ndarray()
        frame_data = frame_data.reshape(frame_data.shape[0:2])

        return frame_data
    
    def frame_handler(self, cam: vmbpy.Camera, stream: vmbpy.Stream, frame: vmbpy.Frame):
        image = frame.as_numpy_ndarray()
        image = image.reshape(image.shape[0:2])
        self.accu_frame_counts += 1
        if self._frame_handler:
            self._frame_handler(image)
        cam.queue_frame(frame)

    def sw_frame_handler(self, cam: vmbpy.Camera, stream: vmbpy.Stream, frame: vmbpy.Frame):
        print(f"7: {time.time()}")
        image = frame.as_numpy_ndarray()
        image = image.reshape(image.shape[0:2])
        self.accu_frame_counts += 1
        if self._frame_handler:
            self._frame_handler(image)
        cv2.imwrite(f"sw_{self.sw_counter}.png", image)
        self.sw_counter += 1
        time.sleep(1)
        cam.queue_frame(frame)


    def arm(self):
        self.camera.TriggerMode.set("On")
        self.camera.TriggerSelector.set("FrameStart")
        self.camera.TriggerSource.set("Software")
        print(f"1: {time.time()}")
        self.camera.start_streaming(handler=self.sw_frame_handler, buffer_count=10)

    def software_trigger(self):
        print(f"3: {time.time()}")
        self.camera.TriggerSoftware.run()
        print(f"4: {time.time()}")

    def disarm(self):
        time.sleep(0.001)
        print(f"5: {time.time()}")
        self.camera.stop_streaming()
        print(f"6: {time.time()}")
