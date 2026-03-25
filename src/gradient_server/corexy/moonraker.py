import asyncio
import anyio
import websockets
import json

running = False

def get_streams():
    send_stream, receive_stream = anyio.create_memory_object_stream[object](max_buffer_size=1000)

    return send_stream, receive_stream

async def connect():
    uri = "ws://192.168.1.93/websocket" 
    ws: websockets.ClientConnection = await websockets.connect(uri)

    return ws

async def disconnect(ws):
    await ws.close()

async def task_coro(ws, tx, task_status=anyio.TASK_STATUS_IGNORED):
    global running
    task_status.started()

    try:
        while running:
            # Receive a message from the server
            message = await ws.recv()
            obj = json.loads(message)
            await tx.send(obj)
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Connection closed: {e}")
    except ConnectionRefusedError:
        print("Connection refused. Is the server running?")
    except Exception as ee:
        print(ee)

async def send_cmd(ws, rx, cmd):
    id = cmd['id']

    await ws.send(json.dumps(cmd).encode())
    while True:
        msg = await rx.receive()
        if "id" in msg.keys() and msg['id'] == id:
            print(msg)
            break



async def main():
    global running
    tx, rx = get_streams()

    ws = await connect()

    running = True
    async with anyio.create_task_group() as tg:
        tg.start_soon(task_coro, ws, tx)

        conn = {"jsonrpc":"2.0","method":"server.connection.identify","params":{"client_name":"mainsail111","version":"2.17.0","type":"web","url":"https://github.com/mainsail-crew/mainsail"},"id":0}
        info = {"jsonrpc":"2.0","method":"server.info","params":{},"id":1}
        g28 = {"jsonrpc":"2.0","method":"printer.gcode.script","params":{"script":"G28"},"id":2}
        move1 = {"jsonrpc":"2.0","method":"printer.gcode.script","params":{"script":"_CLIENT_LINEAR_MOVE Z=140 F=1500 ABSOLUTE=1"},"id":3}
        move2 = {"jsonrpc":"2.0","method":"printer.gcode.script","params":{"script":"_CLIENT_LINEAR_MOVE Z=100 F=1500 ABSOLUTE=1"},"id":4}
        m84 = {"jsonrpc":"2.0","method":"printer.gcode.script","params":{"script":"M84"},"id":5}

        await send_cmd(ws, rx, conn)
        await send_cmd(ws, rx, info)
        await send_cmd(ws, rx, g28)
        await send_cmd(ws, rx, move1)
        await send_cmd(ws, rx, move2)
        await send_cmd(ws, rx, m84)
        running = False

anyio.run(main)
