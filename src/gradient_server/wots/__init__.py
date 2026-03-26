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

class MyThing(lt.Thing):
    """A test WoT thing."""

    def __init__(self, thing_server_interface):
        super().__init__(thing_server_interface)
        self.tg = None
        self.running = False

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
        uri = "ws://localhost:7125/websocket" 
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
        id = cmd['id']

        await ws.send(json.dumps(cmd).encode())
        while True:
            msg = await rx.receive()
            if "id" in msg.keys() and msg['id'] == id:
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
    def info(self, portal: lt.deps.BlockingPortal) -> Any:
        info = {"jsonrpc":"2.0","method":"server.info","params":{},"id":1}

        task, status = portal.start_task(self.send_cmd, self.ws, self.rx, info)
        return task._result

    @lt.action
    def g28(self, portal: lt.deps.BlockingPortal) -> Any:
        g28 = {"jsonrpc":"2.0","method":"printer.gcode.script","params":{"script":"G28"},"id":2}

        task, result=portal.start_task(self.send_cmd, self.ws, self.rx, g28)
        return task._result
    
