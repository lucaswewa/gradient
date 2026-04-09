import os
import PySpin
import sys
import platform
import time
# import cv2
from PIL import Image
import threading
from typing import Callable, Any
import anyio

from . import Camera

class SpinnakerCamera(Camera):
    def __init__(self):
        self.counter = 0

    async def __aenter__(self):
        await anyio.to_thread.run_sync(self.__enter__)

    async def __aexit__(self, exc_type, exc, tb):
        await anyio.to_thread.run_sync(self.__exit__, exc_type, exc, tb)

    def __enter__(self):
        self.system = PySpin.System.GetInstance()
        self.cams = self.system.GetCameras()
        self.cam = self.cams[0]
        self.cam.Init()

    def __exit__(self, exc_type, exc, tb):
        self.cam.Deinit()
        del self.cam
        self.cams.Clear()
        self.system.ReleaseInstance()

    def set_exposure_time(self, exposure_time_in_us: float) -> None:
        self.cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
        self.cam.ExposureTime.SetValue(exposure_time_in_us)

    def get_exposure_time(self) -> None:
        return self.cam.ExposureTime.GetValue()
    
    def set_gain(self, gain_in_db: float) -> None:
        self.cam.GainAuto.SetValue(PySpin.GainAuto_Off)
        self.cam.Gain.SetValue(gain_in_db)

    def get_gain(self) -> float:
        return self.cam.Gain.GetValue()

    def start_streaming(self, handler: Callable[[Any], None]) -> None:
        self._t_streaming = True
        self._t = threading.Thread(target=self._streaming_t, args=[handler])
        self._t.start()

    def stop_streaming(self) -> None:
        self._t_streaming = False
        self._t.join()

    def _streaming_t(self, handler: Callable[[Any], None]):
        self.cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)

        nodemap_tldevice = self.cam.GetTLDeviceNodeMap()
        nodemap = self.cam.GetNodeMap()

        sNodemap = self.cam.GetTLStreamNodeMap()
        # Change bufferhandling mode to NewestOnly
        node_bufferhandling_mode = PySpin.CEnumerationPtr(sNodemap.GetNode('StreamBufferHandlingMode'))        
        # Retrieve entry node from enumeration node
        node_newestonly = node_bufferhandling_mode.GetEntryByName('NewestOnly')

        node_newestonly_mode = node_newestonly.GetValue()

        # Set integer value from entry node as new value of enumeration node
        node_bufferhandling_mode.SetIntValue(node_newestonly_mode)

        node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode'))

        # Retrieve entry node from enumeration node
        node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')

        # Retrieve integer value from entry node
        acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()        

        # Set integer value from entry node as new value of enumeration node
        node_acquisition_mode.SetIntValue(acquisition_mode_continuous)        

        self.cam.BeginAcquisition()

        while self._t_streaming:
            image_result = self.cam.GetNextImage(1000)
            #  Ensure image completion
            if image_result.IsIncomplete():
                print('Image incomplete with image status %d ...' % image_result.GetImageStatus())

            else:                    

                # Getting the image data as a numpy array
                image_data = image_result.GetNDArray()
                img = Image.fromarray(image_data)
                # img.save(f'n_{self.counter:02d}.png')
                handler(image_data)

            #  Release image
            #
            #  *** NOTES ***
            #  Images retrieved directly from the camera (i.e. non-converted
            #  images) need to be released in order to keep from filling the
            #  buffer.
            image_result.Release()    
        e = time.time()

        self.cam.EndAcquisition()   

    def is_streaming(self) -> bool:
        return self._t_streaming
    
    def acquire(self, cb, count):
        self.cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)

        nodemap_tldevice = self.cam.GetTLDeviceNodeMap()
        nodemap = self.cam.GetNodeMap()

        sNodemap = self.cam.GetTLStreamNodeMap()
        # Change bufferhandling mode to NewestOnly
        node_bufferhandling_mode = PySpin.CEnumerationPtr(sNodemap.GetNode('StreamBufferHandlingMode'))        
        # Retrieve entry node from enumeration node
        node_newestonly = node_bufferhandling_mode.GetEntryByName('NewestOnly')

        node_newestonly_mode = node_newestonly.GetValue()

        # Set integer value from entry node as new value of enumeration node
        node_bufferhandling_mode.SetIntValue(node_newestonly_mode)

        node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode'))

        # Retrieve entry node from enumeration node
        node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')

        # Retrieve integer value from entry node
        acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()        

        # Set integer value from entry node as new value of enumeration node
        node_acquisition_mode.SetIntValue(acquisition_mode_continuous)        

        self.cam.BeginAcquisition()

        # node_device_serial_number = PySpin.CStringPtr(nodemap_tldevice.GetNode('DeviceSerialNumber'))
        # device_serial_number = node_device_serial_number.GetValue()

        s = time.time()
        for i in range(count):
            image_result = self.cam.GetNextImage(1000)
            #  Ensure image completion
            if image_result.IsIncomplete():
                print('Image incomplete with image status %d ...' % image_result.GetImageStatus())

            else:                    

                # Getting the image data as a numpy array
                image_data = image_result.GetNDArray()
                img = Image.fromarray(image_data)
                # img.save(f'n_{self.counter:02d}.png')
                cb(image_data)
                self.counter += 1

            #  Release image
            #
            #  *** NOTES ***
            #  Images retrieved directly from the camera (i.e. non-converted
            #  images) need to be released in order to keep from filling the
            #  buffer.
            image_result.Release()    
        e = time.time()
        print(count/(e-s))

        self.cam.EndAcquisition()    

    def arm(self) -> None:
        # Configure trigger
        self.cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)
        self.cam.TriggerSelector.SetValue(PySpin.TriggerSelector_FrameStart)
        self.cam.TriggerSource.SetValue(PySpin.TriggerSource_Software)
        self.cam.TriggerMode.SetValue(PySpin.TriggerMode_On)

        # Acquire images
        self.cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)
        self.cam.BeginAcquisition()

    def disarm(self) -> None:
        self.cam.EndAcquisition()

        # Reset trigger
        self.cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)

    def trigger_and_capture(self, count: int):
        result = []
        for i in range(count):
            self.cam.TriggerSoftware.Execute()

            image_result = self.cam.GetNextImage(1000)
            if image_result.IsIncomplete():
                print("Bad image")
            else:
                width = image_result.GetWidth()
                height = image_result.GetHeight()
                self.counter += 1
                image_data = image_result.GetData()
                image_data = image_data.reshape((height, width))
            image_result.Release()
            result.append(image_data.copy())

        return result
