from ..libs.oceandirect.od_logger import od_logger
from ..libs.oceandirect.OceanDirectAPI import OceanDirectAPI, OceanDirectError, FeatureID

class OceanInsightSpectrometer:
    def __init__(self, serial_number=None):
        self.od = OceanDirectAPI()
        self.serial_number = serial_number
        self.device = None

    def connect(self):
        device_count = self.od.find_usb_devices()
        device_ids = self.od.get_device_ids()
        self.device = self.od.open_device(device_ids[0])
        self.serial_number = self.device.get_serial_number()
        self.wavelengths = self.device.get_wavelengths()
        self.device.set_electric_dark_correction_usage(False)
        self.device.set_nonlinearity_correction_usage(True)

    def disconnect(self):
        if self.device is not None:
            self.device.close_device()
            self.device = None

    def get_spectra_single(self, numb_spectra):
        """
        Retrieves spectra one by one without averaging until all spectra have been collected and stored in a list (single scan mode).
        
        Parameters:
        device: Spectrometer device object.
        numb_spectra (int): Number of spectra to capture.
        """
        try:
            # Set the device to single scan mode (1 scan)
            self.device.set_scans_to_average(1)

            # Get the number of pixels in the spectrum
            numb_pixel = len(self.device.get_formatted_spectrum())

            # Initialize a list to store the summed spectra
            summed_spectrum = [0.0 for _ in range(numb_pixel)]

            print("Starting single spectra collection...")
            # Retrieve the spectra one by one
            for i in range(numb_spectra):
                current_spectrum = self.device.get_formatted_spectrum()
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
            # logger.error(e.get_error_details())
            pass

    def get_spectrum(self):
        return self.get_spectra_single(5)
    
    def get_integration_time(self):
        return self.device.get_integration_time()
    
    def set_integration_time(self, integration_time):
        self.device.set_integration_time(integration_time)
