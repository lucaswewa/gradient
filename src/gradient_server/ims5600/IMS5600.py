#----------------------------------------------------------------------
# Python Example Code Library
#----------------------------------------------------------------------
#
sensor_name = "IMS5600"
#
#----------------------------------------------------------------------
#
#                   ..:::::::::::::::::::::::..            
#               .:::::::...              ..:::::::..       
#            .:::::.                            .:::::.    
#          .:::. .....        .....        ...:::. .::::   
#         .::.   .:::.        .:::.     .:::::::::    :::. 
#        .::.    .:::.        .:::.    .::::           .::.
#        ::.     .:::.        .:::.    .:::.            .::
#        ::      .:::.        .:::.     .::::..          ::
#        ::      .:::.        .:::.      .:::::::        ::
#        ::.     .:::.        .:::.    .:::::.          .::
#         ::.    .:::.        .:::.  .:::::            .::.
#          :::.  .:::.        .:::.  ::::::          .:::. 
#           .:::..::::.      .::::. .:::::::.      .:::.   
#             .::::::::::::::::..:::::. :::::::::::::.     
#                :::   ..::..     ...     .:::::::.        
#                :::                                       
#                .::        
#
#----------------------------------------------------------------------
# Barak Pizzuto
#______________________________________________________________________
# Micro-Epsilon
#
# barak.pizzuto@micro-epsilon.com
# 8120 Brownleigh Dr.
# Raleigh, NC 27617
#______________________________________________________________________
#----------------------------------------------------------------------

#======================================================================
#----------------------------------------------------------------------

# This example aims to provide a quick introduction to the IMS5600 in 
# communicating via the MEDAQLib libraries provided by Micro-Epsilon.
# This example shows the basics of opening communication with the 
# sensor, setting basic settings, requesting basic information from the 
# sensor, and pulling measurement data from the sensor. 

# TODO This example expects you have already set the sensor up in 
# SensorTool and have properly dark referenced the sensor and selected 
# the correct sensor in the settings. If you have not done this already
# please do so now!

#----------------------------------------------------------------------
#======================================================================

#======================================================================
#----------------------------------------------------------------------
#
# imports
#
#----------------------------------------------------------------------
#======================================================================
from MEDAQLib import MEDAQLib, ME_SENSOR, ERR_CODE
import time
import keyboard
#======================================================================
#----------------------------------------------------------------------
#
# Connection to the sensor
#
#----------------------------------------------------------------------
#======================================================================
print(f"Creating sensor instance for {sensor_name}...")
#----------------------------------------------------------------------
# CreateSensorInstance takes in an integer parameter to know which 
# sensor we connect to. Here we can get the integer value from the 
# ME_SENSOR class. 
#----------------------------------------------------------------------
sensor_instance = MEDAQLib.CreateSensorInstance(ME_SENSOR.SENSOR_IMC5600)
#----------------------------------------------------------------------
# At this point we can enable or disable logging on the sensor instance
# Log files can become quite large, so unless you are troubleshooting 
# it is recommended to leave this off, though it provides valuable 
# information and can be enabled if requesting support from ME.
#----------------------------------------------------------------------
sensor_instance.SetParameterInt("IP_EnableLogging", 0) #set to 1 to enable
sensor_instance.SetParameterString("IP_LogFile","C:\\")
#----------------------------------------------------------------------
# Then MEDAQLib needs to be told which interface we are actually trying
# to connect to. Here we will connect for example over Ethernet so we 
# will tell MEDAQLib about the appropriate interface and connection 
# parameters.
#----------------------------------------------------------------------
sensor_instance.SetParameterString("IP_Interface", "TCP/IP")
#TODO change IP to correct value which the controller is set to!
ip_addr = "169.254.168.150"
sensor_instance.SetParameterString("IP_RemoteAddr", ip_addr)
#Tell MEDAQLib it should detect the interface and ensure the sensor 
# sends data over the correct interface
sensor_instance.SetParameterInt("IP_AutomaticMode", 3)
#----------------------------------------------------------------------
# Then we can attempt to open the connection to the sensor
#----------------------------------------------------------------------
print(f"Attempting to open sensor instance for {sensor_name}...")
sensor_instance.OpenSensor()
if sensor_instance.GetLastError() == ERR_CODE.ERR_NOERROR:
	print(f"\tSuccessfully opened connection to {sensor_name} on {ip_addr}")
else:
	print(sensor_instance.GetLastError())

#======================================================================
#----------------------------------------------------------------------
#
# Setting Frames per packet
#
#----------------------------------------------------------------------
#======================================================================
#----------------------------------------------------------------------
# Depending on use case, it is possible that if polling very fast for
# example, the confocal returns stale data. This is a product of the
# Ethernet interface occasionally waiting for packets to fill before 
# sending them. A workaround to this is to simply set one frame per 
# packet. This forces data values to send immediately rather than 
# waiting for multiple to queue up before transferring to MEDAQLib. 
#----------------------------------------------------------------------
# Force sensor to output a single measurement per ethernet packet. Tell 
# Medaqlib about the command we want to set
#----------------------------------------------------------------------
sensor_instance.SetParameterString("S_Command", "Set_FramesPerPacketEthernet")
#----------------------------------------------------------------------
# Tell MEDAQLib about the parameter for the function
#----------------------------------------------------------------------
sensor_instance.SetParameterInt("SP_FramesPerPacket_ETH", 1)
#----------------------------------------------------------------------
# Execute the last given function and parameters on the sensor
#----------------------------------------------------------------------
sensor_instance.SensorCommand()

#======================================================================
#----------------------------------------------------------------------
#
# Getting parameters from the sensor (optional)
#
#----------------------------------------------------------------------
#======================================================================
print(f"Getting parameters from {sensor_name}...")
#----------------------------------------------------------------------
# MEDAQLib provides access to many parameters from the sensor that can 
# be retrieved. For an easy example, we will collect the serial number 
# of the sensor. From the MEDAQLib docs, the IMS5600 function 
# Get_AllParameters tells MEDAQLib to get parameter information from the 
# sensor at which point we can query it from the dll. First we will call
# this function, and then get the parameter. Parameters which can be 
# retrieved are marked by the prefix "SA"
#----------------------------------------------------------------------
#----------------------------------------------------------------------
# Tell MEDAQLib about the command we want to call
#----------------------------------------------------------------------
sensor_instance.SetParameterString("S_Command", "Get_AllParameters")
#----------------------------------------------------------------------
# Tell MEDAQLib about the parameters needed for the function, marked
# with the prefix "SP"
#----------------------------------------------------------------------
sensor_instance.SetParameterInt("SP_Additional", 1)
#----------------------------------------------------------------------
# Execute last set function and parameters
#----------------------------------------------------------------------
sensor_instance.SensorCommand()
#----------------------------------------------------------------------
# Then we can retrieve the information we want (in this case 
# SA_SerialNumber)
#----------------------------------------------------------------------
serial_number = sensor_instance.GetParameterString("SA_SerialNumber", 50)
print(f"\tThe {sensor_name} serial number is {serial_number}")

#======================================================================
#----------------------------------------------------------------------
#
# Setting up outputs for the sensor
#
#----------------------------------------------------------------------
#======================================================================
#----------------------------------------------------------------------
# We can also determine which outputs we want out of the sensor. Often 
# times a sensor can output many values which are available to the
# sensor. For the IMS5600 unless necessary I would suggest simply
# setting up the outputs in the web interface and saving these settings
# to the sensor as you can visualize the settings much easier. I would
# suggest starting here, and if you need to change these programmatically
# using the web interface to understand the settings fully before setting
#----------------------------------------------------------------------
# For this example a simple example will be given to reset the outputs 
# to default and simply leave distance output enabled
#----------------------------------------------------------------------
# here the reset meta command is used to adapt Set_Output_ETH to 
# Reset_Output_ETH. This automatically calls SetParameter____ etc...
# for each parameter to factory defaults. This is helpful as then we 
# don't need to manually input every possible parameter since there are
# many additional values which can be transfered. We can then simply 
# overwrite the parameters we want to change.
#----------------------------------------------------------------------
sensor_instance.SetParameterString("S_Command", "Reset_Output_ETH")
#----------------------------------------------------------------------
# Overwrite desired parameters
#----------------------------------------------------------------------
sensor_instance.SetParameterInt("SP_OutputPeak1_Ch1_ETH", 1) #set distance signal enabled
#----------------------------------------------------------------------
# Call function to set ouputs
#----------------------------------------------------------------------
sensor_instance.SensorCommand()

#======================================================================
#----------------------------------------------------------------------
#
# Acquiring data from the sensor (block based)
#
#----------------------------------------------------------------------
#======================================================================
#----------------------------------------------------------------------
# When we want many values from a very fast process then TransferData
# is used to collect blocks of information at a time. Here many values 
# which are in the buffer can be transfered in one go, and then on 
# transfer are removed from the internal buffers. Care should be taken
# then to transfer data out of the buffers faster than the sensor 
# is generating the data. Uncomment lines below if block based transfer
# is needed
#----------------------------------------------------------------------
# # how many values (frames) we want to transfer from the sensor
# EXPECTED_BLOCK_SIZE = 1000
# #----------------------------------------------------------------------
# # Here we can start our measurement loop
# #----------------------------------------------------------------------
# bDone = False
# while bDone is not True:
# 	if keyboard.is_pressed("enter"):
# 		break
# 	#call DataAvail to check how much data is available in the buffer
# 	available_data = sensor_instance.DataAvail()
# 	#if there is no error and we have exceeded the expected data we should transfer!
# 	if sensor_instance.GetLastError() == ERR_CODE.ERR_NOERROR and available_data > EXPECTED_BLOCK_SIZE:
# 		transfer_data = sensor_instance.TransferData(EXPECTED_BLOCK_SIZE)
# 		if sensor_instance.GetLastError() == ERR_CODE.ERR_NOERROR:
# 			raw_data = transfer_data[0]
# 			scaled_data = transfer_data[1]
# 			values_transferred = transfer_data[2]
# 			print(f"{sensor_name} data: \n\traw data: {raw_data}\n\tscaled_data: {scaled_data}")
# 		else:
# 			print(sensor_instance.GetError(1024))
# 	else:
# 		print(sensor_instance.GetError(1024))
# 	time.sleep(.1)

#======================================================================
#----------------------------------------------------------------------
#
# Acquiring data from the sensor (block based)
#
#----------------------------------------------------------------------
#======================================================================
#----------------------------------------------------------------------
# If data is not needed at full speed from the sensor it is also 
# possible to simply poll for the latest value from the sensor. This 
# requires no thought regarding buffer transfer speeds, but simply asks
# for the most recent value from the sensor. 
#----------------------------------------------------------------------
# how many (frames) we want to transfer from the sensor. If we transfer
# multiple values per measurement for example this must be increased to 
# get all data
#----------------------------------------------------------------------
EXPECTED_BLOCK_SIZE = 1
#----------------------------------------------------------------------
# Here we can start our measurement loop
#----------------------------------------------------------------------
bDone = False
while bDone is not True: 
	if keyboard.is_pressed("enter"):
		break
	transfer_data = sensor_instance.Poll(EXPECTED_BLOCK_SIZE)
	raw_data = transfer_data[0]
	scaled_data = transfer_data[1]

	print(f"{sensor_name} data: \n\traw data: {raw_data}\n\tscaled_data: {scaled_data}")
	time.sleep(1)


#======================================================================
#----------------------------------------------------------------------
#
# Closing sensor instance
#
#----------------------------------------------------------------------
#======================================================================
#----------------------------------------------------------------------
# It is always good practice to close the sensor instance. MEDAQLib 
# will automatically try to "clean up" the instancing on program close,
# but it may be necessary if disconnecting and connecting to sensor 
# within software to fully close and release the sensor instance. In
# this example there is an infinite loop above, but of course an out 
# can be added which then calls the below to fully close and release 
# the instance
#----------------------------------------------------------------------
sensor_instance.CloseSensor()
sensor_instance.ReleaseSensorInstance()