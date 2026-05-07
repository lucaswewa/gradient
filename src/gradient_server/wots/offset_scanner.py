import time
from typing import Literal
import numpy as np
import labthings_fastapi as lt

from .stage.conex_stage import ConexStage
from .ims5600.ims5600meter import IMS5600Meter

class Scanner(lt.Thing):
    """Illumination control in the simulator."""

    _stage: ConexStage = lt.thing_slot()
    _ims5600: IMS5600Meter = lt.thing_slot()

    @lt.action
    def scan(self, s1: float, e1: float, s2: float, e2: float, steps: int, filename: str) -> None:
        self._stage.move_abs(s1)
        time.sleep(3)
        print(f"Position: {self._stage.position}")
        m = []

        r1 = (e1 - s1)/steps
        r2 = (e2 - s2)/steps

        for i in range(steps):
            position = self._stage.position
            time.sleep(0.05)
            measurement = self._ims5600.capture_frame()
            time.sleep(0.05)
            print(f"Position: {position}, Measurement: {measurement}")
            m.append([position, measurement])
            self._stage.move_rel(r1)
            time.sleep(0.2)

        self._stage.move_abs(s2)
        time.sleep(1)

        for i in range(steps):
            position = self._stage.position
            time.sleep(0.05)
            measurement = self._ims5600.capture_frame()
            time.sleep(0.05)
            print(f"Position: {position}, Measurement: {measurement}")
            m.append([position, measurement])
            self._stage.move_rel(r2)
            time.sleep(0.2)


        result = np.array(m)
        np.savetxt(filename, result, delimiter=',', header='position,distance', comments='')

        return m