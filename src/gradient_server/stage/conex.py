import serial
import threading

def send_command(ser: serial.Serial, cmd: str):
    ser.write(f"{cmd}\n".encode())
    ser.flush()

def read_response(ser: serial.Serial):
    res = ser.readline().decode()
    return res


class Conex:
    def __init__(self, port):
        super().__init__()
        self._port = port
        self._lock = threading.RLock()
        self._ser = None

    def enter_stage(self):
        with self._lock:
            self._ser = serial.Serial(port=self._port, baudrate=115200)
            send_command(self._ser, "OR")
            send_command(self._ser, "RFH")

    def exit_stage(self):
        with self._lock:
            self._ser.close()

    def get_position(self) -> float:
        send_command(self._ser, "TP")
        res = read_response(self._ser)
        return float(res[2:])
    
    def get_velocity(self) -> float:
        send_command(self._ser, "VA?")
        res = read_response(self._ser)
        return float(res[2:])
    
    def set_velocity(self, v: float):
        send_command(self._ser, f"VA{v:.3f}")

    def get_acceleration(self) -> float:
        send_command(self._ser, "AC?")
        res = read_response(self._ser)
        return float(res[2:])

    def set_acceleration(self, acceleration: float):
        if not 1.5 <= acceleration <= 1500:
            raise ValueError("Acceleration must be between 1.5 and 1500.")
        send_command(self._ser, f"AC{acceleration:.3f}")

    def move_absolute(self, position) -> None:
        send_command(self._ser, f"PA{position:.3f}")

    def move_relative(self, delta) -> None:
        send_command(self._ser, f"PR{delta:0.3f}")

def main():
    ser = serial.Serial(
        port="COM10",
        baudrate=115200
    )

    send_command(ser, "OR")

    send_command(ser, "RFH")

    send_command(ser, "TP")
    res = read_response(ser)

    send_command(ser, "PA1.123")
    # res = read_response(ser)

    send_command(ser, "TP")
    res = read_response(ser)

    send_command(ser, "RT")
    res = read_response(ser)

    ser.close()

if __name__ == "__main__":
    main()
