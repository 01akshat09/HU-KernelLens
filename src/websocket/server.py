import asyncio
import websockets
import json
from src.notifications.email import send_email_alert

class WebSocketServer:
    def __init__(self, cpu_monitor, network_monitor, user_monitor, priv_monitor):
        self.connected_clients = set()
        self.cpu_monitor = cpu_monitor
        self.network_monitor = network_monitor
        self.user_monitor = user_monitor
        self.priv_monitor = priv_monitor

    async def handler(self, websocket):
        """Handle WebSocket client connections."""
        print(f"✅ Client connected: {websocket.remote_address}")
        self.connected_clients.add(websocket)
        try:
            while True:
                self.cpu_monitor.collect_data()
                data = {
                    "cpuUtilization": self.cpu_monitor.cpu_data,
                    "cpuAlarms": self.cpu_monitor.cpu_alarms,
                    "networkPackets": self.network_monitor.collect_data(),
                    "userActivity": self.user_monitor.collect_data(),
                    "privilegedEvents": self.priv_monitor.collect_data()
                }
                if data["cpuAlarms"]:
                    send_email_alert(data["cpuAlarms"])
                await websocket.send(json.dumps(data))
                await asyncio.sleep(5)
        except websockets.exceptions.ConnectionClosed:
            print(f"❌ Client disconnected: {websocket.remote_address}")
        finally:
            self.connected_clients.remove(websocket)

    async def run(self):
        """Start the WebSocket server and poll BPF buffers."""
        print("🔁 WebSocket server running on ws://localhost:6790")
        async with websockets.serve(self.handler, "localhost", 6790):
            while True:
                self.network_monitor.network_bpf.perf_buffer_poll(timeout=100)
                self.user_monitor.user_bpf.perf_buffer_poll(timeout=100)
                self.priv_monitor.priv_bpf.perf_buffer_poll(timeout=100)
                await asyncio.sleep(0.1)

async def start_websocket_server():
    """Initialize monitors and start the WebSocket server."""
    from src.cpu_monitor.cpu_monitor import init_cpu_monitor
    from src.network_monitor.network_monitor import init_network_monitor
    from src.user_monitor.user_monitor import init_user_monitor
    from src.priv_monitor.priv_monitor import init_priv_monitor

    cpu_monitor = init_cpu_monitor()
    network_monitor = init_network_monitor()
    user_monitor = init_user_monitor()
    priv_monitor = init_priv_monitor()

    server = WebSocketServer(cpu_monitor, network_monitor, user_monitor, priv_monitor)
    await server.run()


