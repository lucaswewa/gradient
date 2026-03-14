import os
import PySpin
import sys
import platform
import time
# import cv2
from PIL import Image
import threading


class Cam:
    def __init__(self):
        self.counter = 0

    def enter(self):
        self.system = PySpin.System.GetInstance()
        self.cams = self.system.GetCameras()
        self.cam = self.cams[0]
        self.cam.Init()

    def exit(self):
        self.cam.Deinit()
        del self.cam
        self.cams.Clear()
        self.system.ReleaseInstance()

    def set_exposure_time(self, exp_time: float):
        self.cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
        self.cam.ExposureTime.SetValue(exp_time)

    def get_exposure_time(self):
        return self.cam.ExposureTime.GetValue()
    
    def set_gain(self, gain: float):
        self.cam.GainAuto.SetValue(PySpin.GainAuto_Off)
        self.cam.Gain.SetValue(gain)

    def get_gain(self):
        return self.cam.Gain.GetValue()

    def start_streaming(self, handler):
        self._t_streaming = True
        self._t = threading.Thread(target=self._streaming_t, args=[handler])
        self._t.start()

    def stop_streaming(self):
        self._t_streaming = False
        self._t.join()

    def _streaming_t(self, handler):
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

    def arm(self):
        # Configure trigger
        self.cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)
        self.cam.TriggerSelector.SetValue(PySpin.TriggerSelector_FrameStart)
        self.cam.TriggerSource.SetValue(PySpin.TriggerSource_Software)
        self.cam.TriggerMode.SetValue(PySpin.TriggerMode_On)

        # Acquire images
        self.cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)
        self.cam.BeginAcquisition()

    def disarm(self):
        self.cam.EndAcquisition()

        # Reset trigger
        self.cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)

    def software_trigger(self):
        self.cam.TriggerSoftware.Execute()

        image_result = self.cam.GetNextImage(1000)
        if image_result.IsIncomplete():
            print("Bad image")
        else:
            width = image_result.GetWidth()
            height = image_result.GetHeight()
            image_result.Save(f"a_{self.counter:02d}.png")
            self.counter += 1
        image_result.Release()
