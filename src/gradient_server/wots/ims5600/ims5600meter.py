from gradient_server.ims5600.me_ims5600 import IMS5600
import labthings_fastapi as lt
import anyio
from .. import GradientThing

class IMS5600Meter(lt.Thing):
    def __init__(self, thing_server_interface):
        super().__init__(thing_server_interface=thing_server_interface)
        self.ims5600 = IMS5600()  

    # async def life_span(self):
    #     try:
    #         async with self.ims5600:
    #             print("IMS5600 before yield")
    #             yield
    #             print("after yield")
    #             await anyio.sleep(1)
    #     except anyio.get_cancelled_exc_class():
    #         print("thing_life_span cancelled")
    #         raise
    #     except Exception as e:
    #         print("thing_life_span execution", e)
    #         raise

    def __enter__(self):
        self.ims5600.__enter__()

    def __exit__(self, exc_type, exc, tb):
        self.ims5600.__exit__(exc_type, exc, tb)

    @lt.action
    def start_streaming(self):
        self.ims5600.start_streaming()

    @lt.action
    def stop_streaming(self):
        self.ims5600.stop_streaming()  

    @lt.action
    def capture_frame(self) -> float:
        frame = self.ims5600.capture_frame()
        if frame.shape[0] == 0:
            raise RuntimeError("No data captured from sensor.")
        return frame.mean()