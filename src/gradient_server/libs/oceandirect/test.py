from oceandirect import od_logger
from oceandirect.OceanDirectAPI import OceanDirectAPI, OceanDirectError, FeatureID

import time
from oceandirect.od_logger import od_logger
from oceandirect.OceanDirectAPI import OceanDirectAPI, OceanDirectError

# Create stream logger
logger = od_logger()

def get_spectra_accelerate(device, num_spectra):
    """
    Retrieves spectra using accelerated mode (with averaging over multiple scans).
    
    Parameters:
    device: Spectrometer device object.
    num_spectra (int): Number of scans to average.
    """
    try:
        # Set the number of scans to average (accelerated mode)
        device.set_scans_to_average(num_spectra)

        # Get the number of pixels in the spectrum
        numb_pixel = len(device.get_formatted_spectrum())

        # Retrieve the formatted spectrum from the device
        print("Starting accelerated spectra collection & simultaneous averaging...")
        spectra_m = device.get_formatted_spectrum()
        print("Accelerated spectra collection & averaging finished.")

    except OceanDirectError as e:
        # Log any errors that occur during the spectra collection
        logger.error(e.get_error_details())

def get_spectra_single(device, numb_spectra):
    """
    Retrieves spectra one by one without averaging until all spectra have been collected and stored in a list (single scan mode).
    
    Parameters:
    device: Spectrometer device object.
    numb_spectra (int): Number of spectra to capture.
    """
    try:
        # Set the device to single scan mode (1 scan)
        device.set_scans_to_average(1)

        # Get the number of pixels in the spectrum
        numb_pixel = len(device.get_formatted_spectrum())

        # Initialize a list to store the summed spectra
        summed_spectrum = [0.0 for _ in range(numb_pixel)]

        print("Starting single spectra collection...")
        # Retrieve the spectra one by one
        for i in range(numb_spectra):
            current_spectrum = device.get_formatted_spectrum()
            # Sum the current spectrum with the summed spectrum
            for j in range(numb_pixel):
                summed_spectrum[j] += current_spectrum[j]
        
        # Notify that averaging is about to begin
        print(f"Averaging {numb_spectra} single scans...")
        # Average the summed spectrum
        averaged_spectrum = [value / numb_spectra for value in summed_spectrum]
        print("Single spectra collection finished.")

        return averaged_spectrum  # Return the averaged spectrum for further use

    except OceanDirectError as e:
        # Log any errors that occur during the spectra collection
        logger.error(e.get_error_details())

def printBinary(value):
    bitCount = 32 #32 bits
    numValue = int(value)

    print("bits (%d) = " % numValue, end='')
    for i in range(32, -1, -1):
        print("%d " % ((numValue >> i) & 0x01), end='')

    print(" ")


def gpio(device):
    tempCount = device.Advanced.get_gpio_pin_count()
    print("gpio(device): pin count          =  %d " % tempCount)

    try:
        outputVector = device.Advanced.gpio_get_output_enable2()
        printBinary(outputVector)
        print("---------------------------------------------------------------\n\n")
    except OceanDirectError as err:
        [errorCode, errorMsg] = err.get_error_details()
        print("gpio(device): exception / %d = %s" % (errorCode, errorMsg))

    try:
        device.Advanced.gpio_set_output_enable1(0, 1)
        bitOutput1 = device.Advanced.gpio_get_output_enable1(0)
        print("gpio(device): set output vector bits / mask     =  00000000 / 0(True)")
        print("gpio(device): get bit(0) output                 =  0(%s)" % bitOutput1)
        outputVector = device.Advanced.gpio_get_output_enable2()
        print("gpio(device): get output vector expected output =  00000001")
        printBinary(outputVector)
        print("\n")

        device.Advanced.gpio_set_output_enable1(2, 1)
        device.Advanced.gpio_set_output_enable1(3, 1)
        bitOutput1 = device.Advanced.gpio_get_output_enable1(2)
        bitOutput2 = device.Advanced.gpio_get_output_enable1(3)
        print("gpio(device): set output vector bits / mask     =  00000001 / 2(True),3(True)")
        print("gpio(device): get bit(2,3) output               =  2(%s) / 3(%s)" % (bitOutput1, bitOutput2) )
        outputVector = device.Advanced.gpio_get_output_enable2()
        print("gpio(device): get output vector expected output =  00001101")
        printBinary(outputVector)
        print("\n")

        device.Advanced.gpio_set_output_enable1(0, 0)
        device.Advanced.gpio_set_output_enable1(1, 1)
        device.Advanced.gpio_set_output_enable1(3, 0)
        bitOutput1 = device.Advanced.gpio_get_output_enable1(0)
        bitOutput2 = device.Advanced.gpio_get_output_enable1(1)
        bitOutput3 = device.Advanced.gpio_get_output_enable1(3)
        print("gpio(device): set output vector bits / mask     =  00001101 / 0(False),True(1),3(False)")
        print("gpio(device): get bit(0,1,3) output             =  0(%s) / 1(%s) / 3(%s)" % (bitOutput1, bitOutput2, bitOutput3))
        outputVector = device.Advanced.gpio_get_output_enable2()
        print("gpio(device): get output vector expected output =  00000110")
        printBinary(outputVector)
        print("\n")

        device.Advanced.gpio_set_output_enable1(0, 1)
        device.Advanced.gpio_set_output_enable1(3, 1)
        bitOutput1 = device.Advanced.gpio_get_output_enable1(0)
        bitOutput2 = device.Advanced.gpio_get_output_enable1(3)
        print("gpio(device): set output vector bits / mask     =  00000110 / 0(True),3(True)")
        print("gpio(device): get bit(0,3) output               =  0(%s) / 3(%s)" % (bitOutput1, bitOutput2))
        outputVector = device.Advanced.gpio_get_output_enable2()
        print("gpio(device): get output vector expected output =  00001111")
        printBinary(outputVector)
        print("")
        print("---------------------------------------------------------------\n\n")
    except OceanDirectError as err:
        [errorCode, errorMsg] = err.get_error_details()
        print("gpio(device): gpio_output_bits() / %d = %s" % (errorCode, errorMsg))

    try:
        device.Advanced.gpio_set_value1(0, 1)
        device.Advanced.gpio_set_value1(1, 1)
        value1 = device.Advanced.gpio_get_value1(0)
        value2 = device.Advanced.gpio_get_value1(1)
        print("gpio(device): set value vector values / mask   =  00000000 / 0(True), 1(True)")
        print("gpio(device): get bit(0,1) value               =  0(%s) / 1(%s)" % (value1, value2))
        valueVector = device.Advanced.gpio_get_value2()
        print("gpio(device): get value vector expected values =  00000011")
        printBinary(valueVector)
        print("")

        device.Advanced.gpio_set_value1(2, 1);
        device.Advanced.gpio_set_value1(3, 1);
        value1 = device.Advanced.gpio_get_value1(2)
        value2 = device.Advanced.gpio_get_value1(3)
        print("gpio(device): set value vector values / mask   =  00000011 / 2(True),3(True)")
        print("gpio(device): get bit(2,3) value               =  2(%s) / 3(%s)" % (value1, value2))
        valueVector = device.Advanced.gpio_get_value2()
        print("gpio(device): get value vector expected values =  00001111")
        printBinary(valueVector)
        print("")

        device.Advanced.gpio_set_value1(0, 0)
        device.Advanced.gpio_set_value1(2, 0)
        value1 = device.Advanced.gpio_get_value1(0)
        value2 = device.Advanced.gpio_get_value1(2)
        print("gpio(device): set value vector values / mask   =  00001111 / 0(False), 2(False)")
        print("gpio(device): get bit(0,2) value               =  0(%s) / 2(%s)" % (value1, value2))
        valueVector = device.Advanced.gpio_get_value2()
        print("gpio(device): get value vector expected values =  00001010")
        printBinary(valueVector)
        print("")

        device.Advanced.gpio_set_value1(1, 0)
        device.Advanced.gpio_set_value1(3, 0)
        value1 = device.Advanced.gpio_get_value1(1)
        value2 = device.Advanced.gpio_get_value1(3)
        print("gpio(device): set value vector values / mask   =  00001010 / 1(False), 3(False)")
        print("gpio(device): get bit(1,3) value               =  1(%s) / 3(%s)" % (value1, value2))
        valueVector = device.Advanced.gpio_get_value2()
        print("gpio(device): get value vector expected values =  00000000")
        printBinary(valueVector)
        print("\n")

    except OceanDirectError as err:
        [errorCode, errorMsg] = err.get_error_details()
        print("gpio(device): exception / %d = %s" % (errorCode, errorMsg))

    #Output bit masks
    try:
        #15 = 1111
        device.Advanced.gpio_set_output_enable2(15)
        print("gpio(device): set output mask(15)        =  00001111")

        mask = device.Advanced.gpio_get_output_enable2()
        print("gpio(device): expecting output mask (15) =  %d" % mask)
    except OceanDirectError as err:
        [errorCode, errorMsg] = err.get_error_details()
        print("gpio(device): exception / %d = %s" % (errorCode, errorMsg))

    #Value bit masks
    try:
        #12 = 1100
        device.Advanced.gpio_set_value2(12)
        print("")
        print("gpio(device): set value mask(12)        =  00001100")

        mask = device.Advanced.gpio_get_value2()
        print("gpio(device): expecting value mask (12) =  %d" % mask)
    except OceanDirectError as err:
        [errorCode, errorMsg] = err.get_error_details()
        print("gpio(device): exception / %d = %s" % (errorCode, errorMsg))
    print("")

def main():
    od = OceanDirectAPI()

    device_count = od.find_usb_devices()
    device_ids = od.get_device_ids()

    print(device_count)

    device = od.open_device(device_ids[0])
    serial_number = device.get_serial_number()

    print(serial_number)

    api_version = od.get_api_version_numbers()
    print(api_version)

    device.set_electric_dark_correction_usage(False)
    device.set_nonlinearity_correction_usage(True)

    numb_spectra = 200
    int_time_us=50000
    device.set_integration_time(int_time_us)
    start_single = time.time()  # Start timer for single capture
    print("Single Capture: %d scans" % numb_spectra)
    averaged_spectrum = get_spectra_single(device, numb_spectra)
    single_time = time.time() - start_single
    print(f"Single spectra collection time: {single_time:.4f} seconds")

    # Time and perform accelerated spectra collection
    start_accelerated = time.time()  # Start timer for accelerated capture
    print("Accelerated Capture: %d scans" % numb_spectra)
    get_spectra_accelerate(device, numb_spectra)  # Call function to capture accelerated spectra
    accelerated_time = time.time() - start_accelerated  # Calculate elapsed time for accelerated capture
    print(f"Accelerated spectra collection time: {accelerated_time:.4f} seconds")
    # Note: This time reflects the device averaging multiple scans in a shorter time frame.

    # Calculate and print the time difference between single and accelerated collection
    time_difference = single_time - accelerated_time
    print(f"Time difference (Single - Accelerated): {time_difference:.4f} seconds")

    # Calculate the difference factor
    if accelerated_time > 0:
        difference_factor = single_time / accelerated_time
        print(f"Accelerated is {difference_factor:.4f} times faster than single scan.") 
    else:
        print("Error: Accelerated collection time is zero, cannot calculate difference factor.")
        
    wavelengths = device.get_wavelengths()
    print(wavelengths)
    for i in [10000, 20000, 30000, 40000, 50000]:
        device.set_integration_time(i)
        spectra = device.get_formatted_spectrum()
        print(spectra[1000])


    # supported = device.is_feature_id_enabled(FeatureID.DATA_BUFFER)
    # print(supported)

    gpio(device)
    print(device)

    del od

if __name__ == "__main__":
    main()
    