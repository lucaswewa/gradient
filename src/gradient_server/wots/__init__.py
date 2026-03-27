"""A package containing all thhe WoT(s)."""

import logging

import labthings_fastapi as lt
import anyio
import time
from anyio.from_thread import BlockingPortal
import random
from typing import Optional, Any
from types import TracebackType
import json
import websockets

LOGGER = logging.getLogger(__name__)

async def async_method(t):
    print("async method start")
    await anyio.sleep(t)
    print("async method done!")

def sync_method(t, r, portal: BlockingPortal):
    print(f"Sync method: start {r}")
    time.sleep(t)
    portal.call(async_method, t)
    print(f"sync method: done! {r}")

class CircularBuffer:
    def __init__(self, capacity):
        self.capacity = capacity
        self.buffer = [None] * capacity
        self.head = 0  # Index to the next write position
        self.count = 0 # Current number of elements in the buffer

    def append(self, value):
        self.buffer[self.head] = value
        self.head = (self.head + 1) % self.capacity
        if self.count < self.capacity:
            self.count += 1

    def get(self):
        # Return elements in order from oldest to newest
        if self.count == 0:
            return []
        
        # Calculate the starting index of the oldest element
        start_index = (self.head - self.count + self.capacity) % self.capacity
        
        # If the buffer has wrapped around, concatenate two slices
        if start_index + self.count <= self.capacity:
            return self.buffer[start_index : start_index + self.count]
        else:
            return self.buffer[start_index:] + self.buffer[:self.head]

class MyThing(lt.Thing):
    """A test WoT thing."""

    def __init__(self, thing_server_interface):
        super().__init__(thing_server_interface)
        self.tg = None
        self.running = False
        self._cmd_id = 0
        self._temp1 = 0.0
        self._temp2 = 0.0
        self._temp_history1 = CircularBuffer(100)
        self._temp_history2 = CircularBuffer(100)

    async def __aenter__(self):
        await self.start()        
        return self
    
    async def __aexit__(
        self,
        _exc_type: type[BaseException],
        _exc_value: Optional[BaseException],
        _traceback: Optional[TracebackType],
    ) -> None:
        await self.end()
        return

    def get_streams(self):
        send_stream, receive_stream = anyio.create_memory_object_stream[object](max_buffer_size=1000)

        return send_stream, receive_stream

    async def connect(self):
        # uri = "ws://localhost:7125/websocket" 
        uri = "ws://192.168.1.93/websocket" 
        ws: websockets.ClientConnection = await websockets.connect(uri)

        return ws

    async def start(self, task_status=anyio.TASK_STATUS_IGNORED):
        task_status.started()
        self.tx, self.rx = self.get_streams()

        try:
            self.ws = await self.connect()
        except Exception as e:
            print(e)

        self.tg = anyio.create_task_group()

        self.running = True
        await self.tg.__aenter__()
        self.tg.start_soon(self.task_coro)

    async def end(self, task_status=anyio.TASK_STATUS_IGNORED):
        task_status.started()
        self.running = False

        await self.tg.__aexit__(None, None, None)

    async def send_cmd(self, ws, rx, cmd, task_status=anyio.TASK_STATUS_IGNORED):
        cmd["id"] = self._cmd_id
        self._cmd_id += 1

        await ws.send(json.dumps(cmd).encode())
        while True:
            msg = await rx.receive()
            if "id" in msg.keys() and msg['id'] == cmd["id"]:
                print(msg)
                task_status.started()
                return msg
            
    async def task_coro(self, task_status=anyio.TASK_STATUS_IGNORED):
        task_status.started()

        while self.running:
            try:
                # Receive a message from the server
                message = await self.ws.recv()
                obj = json.loads(message)
                if "method" in obj.keys():
                    if obj["method"] == "notify_status_update":
                        if "motion_report" in obj["params"][0].keys() and "live_position" in obj["params"][0]["motion_report"].keys():
                            print("live_position:", obj["params"][0]["motion_report"]["live_position"])
                        if "heater_bed" in obj["params"][0].keys() and "temperature" in obj["params"][0]["heater_bed"].keys():
                            self._temp1 = obj["params"][0]["heater_bed"]["temperature"]
                            self._temp_history1.append(self._temp1)
                        if "extruder" in obj["params"][0].keys() and "temperature" in obj["params"][0]["extruder"].keys():
                            self._temp2 = obj["params"][0]["extruder"]["temperature"]
                            self._temp_history2.append(self._temp2)

                await self.tx.send(obj)
            except websockets.exceptions.ConnectionClosed as e:
                print(f"Connection closed: {e}")
                await self.ws.close()
                self.ws = None
                raise
            except ConnectionRefusedError:
                print("Connection refused. Is the server running?")
                raise
            except Exception as ee:
                print(ee)
                raise
            
    
    @lt.property
    def temp1(self) -> float:
        return self._temp1
    
    @lt.property
    def temp2(self) -> float:
        return self._temp2
    
    @lt.property
    def temp1_history(self) -> list[float]:
        return self._temp_history1.get()
    
    @lt.property
    def temp2_history(self) -> list[float]:
        return self._temp_history2.get()

    @lt.property
    def ai(self) -> str:
        """Get AI."""
        LOGGER.info("get ai")
        return "ai"

    @lt.action
    def start_ws(self, portal: lt.deps.BlockingPortal) -> Any:

        task, status = portal.start_task(self.start)
        print(task)
        return task._result

    @lt.action
    def end_ws(self, portal: lt.deps.BlockingPortal) -> Any:

        task, status = portal.start_task(self.end)
        print(task)
        return task._result

    @lt.action
    def conn(self, portal: lt.deps.BlockingPortal) -> Any:
        conn = {"jsonrpc":"2.0","method":"server.connection.identify","params":{"client_name":"mainsail111","version":"2.17.0","type":"web","url":"https://github.com/mainsail-crew/mainsail"},"id":0}

        task, status = portal.start_task(self.send_cmd, self.ws, self.rx, conn)
        print(task)
        return task._result

    @lt.action
    def begin_session(self, portal: lt.deps.BlockingPortal) -> Any:
        sub = {"jsonrpc":"2.0","method":"printer.objects.subscribe","params":{"objects":{"gcode":None,"webhooks":None,"configfile":None,"mcu":None,"stepper_enable":None,"tmc2209 stepper_x":None,"tmc2209 stepper_y":None,"tmc2209 stepper_z":None,"tmc2209 stepper_z1":None,"tmc2209 stepper_z2":None,"tmc2209 extruder":None,"heaters":None,"heater_bed":None,"probe":None,"gcode_move":None,"bed_mesh":None,"fan":None,"heater_fan hotend_fan":None,"controller_fan controller_fan":None,"idle_timeout":None,"z_tilt":None,"display_status":None,"gcode_macro PRINT_START":None,"gcode_macro PRINT_END":None,"print_stats":None,"virtual_sdcard":None,"pause_resume":None,"gcode_macro CANCEL_PRINT":None,"gcode_macro PAUSE":None,"gcode_macro RESUME":None,"gcode_macro SET_PAUSE_NEXT_LAYER":None,"gcode_macro SET_PAUSE_AT_LAYER":None,"gcode_macro SET_PRINT_STATS_INFO":None,"gcode_macro _TOOLHEAD_PARK_PAUSE_CANCEL":None,"gcode_macro _CLIENT_EXTRUDE":None,"gcode_macro _CLIENT_RETRACT":None,"gcode_macro _CLIENT_LINEAR_MOVE":None,"query_endstops":None,"motion_report":None,"toolhead":None,"extruder":None,"system_stats":None,"manual_probe":None}},"id":30}
        task, status = portal.start_task(self.send_cmd, self.ws, self.rx, sub)
        print(task)
        return task._result


    @lt.action
    def info(self, portal: lt.deps.BlockingPortal) -> Any:
        info = {"jsonrpc":"2.0","method":"server.info","params":{},"id":1}

        task, status = portal.start_task(self.send_cmd, self.ws, self.rx, info)
        return task._result

    @lt.action
    def g28(self, portal: lt.deps.BlockingPortal) -> Any:
        g28 = {"jsonrpc":"2.0","method":"printer.gcode.script","params":{"script":"G28"},"id":2}

        task, result=portal.start_task(self.send_cmd, self.ws, self.rx, g28)
        return task._result
    
    @lt.action
    def z_pos(self, z_pos: int, portal: lt.deps.BlockingPortal) -> Any:
        z150 = {"jsonrpc":"2.0","method":"printer.gcode.script","params":{"script":f"_CLIENT_LINEAR_MOVE Z={z_pos} F=1500 ABSOLUTE=1"},"id":34}
        task, result=portal.start_task(self.send_cmd, self.ws, self.rx, z150)
        return task._result

    @lt.action
    def m84(self, portal: lt.deps.BlockingPortal) -> Any:
        m84 = {"jsonrpc":"2.0","method":"printer.gcode.script","params":{"script":"m84"},"id":36}
        task, result=portal.start_task(self.send_cmd, self.ws, self.rx, m84)
        return task._result

    @lt.action
    def z_pos_n(self, z_pos_start: int, z_pos_end: int, n: int, portal: lt.deps.BlockingPortal) -> Any:
        for i in range(n):
            cmd1 = {"jsonrpc":"2.0","method":"printer.gcode.script","params":{"script":f"_CLIENT_LINEAR_MOVE Z={z_pos_start} F=1500 ABSOLUTE=1"},"id":34}
            task, result=portal.start_task(self.send_cmd, self.ws, self.rx, cmd1)
            time.sleep(0.25)
            cmd2 = {"jsonrpc":"2.0","method":"printer.gcode.script","params":{"script":f"_CLIENT_LINEAR_MOVE Z={z_pos_end} F=1500 ABSOLUTE=1"},"id":34}
            task, result=portal.start_task(self.send_cmd, self.ws, self.rx, cmd2)
            time.sleep(0.25)

        return task._result

    @lt.action
    def xy_pos(self, portal: lt.deps.BlockingPortal, x_pos: int = None, y_pos: int = None) -> Any:
        x = f"X={x_pos}" if x_pos is not None else ""
        y = f"Y={y_pos}" if y_pos is not None else ""
        xy = x + " " + y
        xy = xy.strip()
        cmd = {"jsonrpc":"2.0","method":"printer.gcode.script","params":{"script":f"_CLIENT_LINEAR_MOVE {xy} F=6000 ABSOLUTE=1"},"id":38}
        task, result = portal.start_task(self.send_cmd, self.ws, self.rx, cmd)
        return task._result
