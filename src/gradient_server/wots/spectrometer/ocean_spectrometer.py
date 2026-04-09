from gradient_server.spectrometer.ocean_insight import OceanInsightSpectrometer
import labthings_fastapi as lt

class OceanSpectrometer(lt.Thing):
    def __init__(self, thing_server_interface):
        super().__init__(thing_server_interface)
        self.spectrometer = OceanInsightSpectrometer()

    @lt.action
    def connect(self):
        self.spectrometer.connect()

    @lt.action
    def disconnect(self):
        self.spectrometer.disconnect()

    @lt.property
    def integration_time(self) -> int:
        return self.spectrometer.device.get_integration_time()
    
    @integration_time.setter
    def integration_time(self, value: int): 
        self.spectrometer.device.set_integration_time(value)

    @lt.action
    def get_spectrum(self):
        spectra = self.spectrometer.get_spectrum()
        return [self.spectrometer.wavelengths, spectra]