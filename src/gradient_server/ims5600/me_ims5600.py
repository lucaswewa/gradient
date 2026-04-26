import numpy as np
import anyio
import threading
import time
from .MEDAQLib import MEDAQLib, ME_SENSOR, ERR_CODE

class IMS5600:
    def __init__(self):
        self.sensor_name = "IMS5600"
        self.sensor_instance = MEDAQLib.CreateSensorInstance(ME_SENSOR.SENSOR_IMC5600)
        #----------------------------------------------------------------------
        # At this point we can enable or disable logging on the sensor instance
        # Log files can become quite large, so unless you are troubleshooting 
        # it is recommended to leave this off, though it provides valuable 
        # information and can be enabled if requesting support from ME.
        #----------------------------------------------------------------------
        self.sensor_instance.SetParameterInt("IP_EnableLogging", 0) #set to 1 to enable
        self.sensor_instance.SetParameterString("IP_LogFile","C:\\")
        self.sensor_instance.SetParameterString("IP_Interface", "TCP/IP")
        #TODO change IP to correct value which the controller is set to!
        self.ip_addr = "169.254.168.150"
        self.sensor_instance.SetParameterString("IP_RemoteAddr", self.ip_addr)
        #Tell MEDAQLib it should detect the interface and ensure the sensor 
        # sends data over the correct interface
        self.sensor_instance.SetParameterInt("IP_AutomaticMode", 3)

        self._streaming = False
        self._stream_thread = None

    def __enter__(self):
        print(f"Attempting to open sensor instance for {self.sensor_name}...")
        self.sensor_instance.OpenSensor()
        if self.sensor_instance.GetLastError() == ERR_CODE.ERR_NOERROR:
            print(f"\tSuccessfully opened connection to {self.sensor_name} on {self.ip_addr}")
        else:
            print(self.sensor_instance.GetLastError())
        # Force sensor to output a single measurement per ethernet packet. Tell 
        # Medaqlib about the command we want to set
        #----------------------------------------------------------------------
        self.sensor_instance.SetParameterString("S_Command", "Set_FramesPerPacketEthernet")
        #----------------------------------------------------------------------
        # Tell MEDAQLib about the parameter for the function
        #----------------------------------------------------------------------
        self.sensor_instance.SetParameterInt("SP_FramesPerPacket_ETH", 1)
        #----------------------------------------------------------------------
        # Execute the last given function and parameters on the sensor
        #----------------------------------------------------------------------
        self.sensor_instance.SensorCommand()

        #----------------------------------------------------------------------
        # Tell MEDAQLib about the command we want to call
        #----------------------------------------------------------------------
        self.sensor_instance.SetParameterString("S_Command", "Get_AllParameters")
        #----------------------------------------------------------------------
        # Tell MEDAQLib about the parameters needed for the function, marked
        # with the prefix "SP"
        #----------------------------------------------------------------------
        self.sensor_instance.SetParameterInt("SP_Additional", 1)
        #----------------------------------------------------------------------
        # Execute last set function and parameters
        #----------------------------------------------------------------------
        self.sensor_instance.SensorCommand()
        #----------------------------------------------------------------------
        # Then we can retrieve the information we want (in this case 
        # SA_SerialNumber)
        #----------------------------------------------------------------------
        serial_number = self.sensor_instance.GetParameterString("SA_SerialNumber", 50)
        print(f"\tThe {self.sensor_name} serial number is {serial_number}")

        #----------------------------------------------------------------------
        # here the reset meta command is used to adapt Set_Output_ETH to 
        # Reset_Output_ETH. This automatically calls SetParameter____ etc...
        # for each parameter to factory defaults. This is helpful as then we 
        # don't need to manually input every possible parameter since there are
        # many additional values which can be transfered. We can then simply 
        # overwrite the parameters we want to change.
        #----------------------------------------------------------------------
        self.sensor_instance.SetParameterString("S_Command", "Reset_Output_ETH")
        #----------------------------------------------------------------------
        # Overwrite desired parameters
        #----------------------------------------------------------------------
        self.sensor_instance.SetParameterInt("SP_OutputPeak1_Ch1_ETH", 1) #set distance signal enabled
        #----------------------------------------------------------------------
        # Call function to set ouputs
        #----------------------------------------------------------------------
        self.sensor_instance.SensorCommand()

    def __exit__(self, exc_type, exc, tb):
        self.sensor_instance.CloseSensor()
        self.sensor_instance.ReleaseSensorInstance()

    def _stream_thread_func(self):
        EXPECTED_BLOCK_SIZE = 1
        while self._streaming:
            transfer_data = self.sensor_instance.Poll(EXPECTED_BLOCK_SIZE)
            raw_data = transfer_data[0]
            scaled_data = transfer_data[1]

            print(f"{self.sensor_name} data: \n\traw data: {raw_data}\n\tscaled_data: {scaled_data}")
            time.sleep(.1)

    def start_streaming(self):
        if not self._streaming:
            self._streaming = True
            self._stream_thread = threading.Thread(target=self._stream_thread_func)
            self._stream_thread.start()

    def stop_streaming(self):
        self._streaming = False
        if self._stream_thread:
            self._stream_thread.join()

    def is_streaming(self):
        return self._streaming

    def capture_frame(self):
        data = []
        for i in range(5):
            EXPECTED_BLOCK_SIZE = 1
            transfer_data = self.sensor_instance.Poll(EXPECTED_BLOCK_SIZE)
            raw_data = transfer_data[0][0]
            scaled_data = transfer_data[1][0]

            if raw_data == 2147483397:
                print("No new data available, retrying...")
                time.sleep(0.1)
                continue
            data.append(scaled_data)
            print(f"{self.sensor_name} data: \n\traw data: {raw_data}\n\tscaled_data: {scaled_data}")
            print(type(raw_data), type(scaled_data))
            time.sleep(.1)

        return np.array(data)

    def _streaming_frame_handler(self, frame):
        pass


