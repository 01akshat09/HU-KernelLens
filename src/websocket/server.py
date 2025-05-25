# import asyncio
# import websockets
# import json
# from src.notifications.email import send_email_alert

# class WebSocketServer:
#     def __init__(self, cpu_monitor, network_monitor, user_monitor, priv_monitor, process_monitor, cpu_line_monitor):
#         self.connected_clients = set()
#         self.cpu_monitor = cpu_monitor
#         self.network_monitor = network_monitor
#         self.user_monitor = user_monitor
#         self.priv_monitor = priv_monitor
#         self.process_monitor = process_monitor
#         self.cpu_line_monitor = cpu_line_monitor


#     async def handler(self, websocket):
#         """Handle WebSocket client connections."""
#         print(f"✅ Client connected: {websocket.remote_address}")
#         self.connected_clients.add(websocket)
#         try:
#             while True:
#                 self.cpu_monitor.collect_data()
#                 # self.network_monitor.collect_data()
#                 # self.priv_monitor.collect_data()
#                 # self.user_monitor.collect_data()
#                 # self.priv_monitor.collect_data()
#                 data = {
#                     "cpuUtilization": self.cpu_monitor.cpu_data,
#                     "cpuAlarms": self.cpu_monitor.cpu_alarms,
#                     "networkPackets": self.network_monitor.collect_data(),
#                     "userActivity": self.user_monitor.collect_data(),
#                     "privilegedEvents": self.priv_monitor.collect_data(),
#                     "processEvents": self.process_monitor.collect_data(),
#                     "cpuLineUsage": self.cpu_line_monitor.line_usage_data()
#                 }
                
                
#                 # Send Alerts: 

#                 if data["cpuAlarms"]:
#                     send_email_alert(data["cpuAlarms"], "CPU")
                
#                 current_user_activity = data["userActivity"]

#                 suspicious_user_activities = [event for event in current_user_activity if event.get("suspicious")]

#                 if suspicious_user_activities:
#                     send_email_alert(suspicious_user_activities, "User Activity")                

#                 if data["privilegedEvents"]:
#                     send_email_alert(data["privilegedEvents"], "Privileged Process")

#                 # Send data

#                 await websocket.send(json.dumps(data))
#                 await asyncio.sleep(5)
#         except websockets.exceptions.ConnectionClosed:
#             print(f"❌ Client disconnected: {websocket.remote_address}")
#         finally:
#             self.connected_clients.remove(websocket)

#     async def run(self):
#         """Start the WebSocket server and poll BPF buffers."""
#         print("🔁 WebSocket server running on ws://localhost:6790")
#         async with websockets.serve(self.handler, "localhost", 6790):
#             while True:
#                 # self.network_monitor.network_bpf.perf_buffer_poll(timeout=100)
#                 # self.user_monitor.user_bpf.perf_buffer_poll(timeout=100)
#                 # self.priv_monitor.priv_bpf.perf_buffer_poll(timeout=100)
#                 # self.process_monitor.process_bpf.perf_buffer_poll(timeout=100)
#                 await asyncio.sleep(0.1)

# async def start_websocket_server():
#     """Initialize monitors and start the WebSocket server."""
#     from src.cpu_monitor.cpu_monitor import init_cpu_monitor
#     from src.network_monitor.network_monitor import init_network_monitor
#     from src.user_monitor.user_monitor import init_user_monitor
#     from src.priv_monitor.priv_monitor import init_priv_monitor
#     from src.process_monitor.process_monitor import init_process_monitor
#     from src.cpu_line_monitor.cpu_line_monitor import init_cpu_line_monitor
#     from config.settings import GO_APP_PID
#     import psutil

#     cpu_monitor = init_cpu_monitor()
#     network_monitor = init_network_monitor()
#     user_monitor = init_user_monitor()
#     priv_monitor = init_priv_monitor()
#     process_monitor = init_process_monitor()
#     cpu_line_monitor = None
#     try:
#         if GO_APP_PID > 0 and psutil.pid_exists(GO_APP_PID):
#             cpu_line_monitor = init_cpu_line_monitor(GO_APP_PID)
#             print(f"CPU line monitoring started for PID {GO_APP_PID}")
#         else:
#             print("No valid Go application PID in settings.py or PID not running")
#     except Exception as e:
#         print(f"Error initializing CPU line monitor: {e}")

#     server = WebSocketServer(cpu_monitor, network_monitor, user_monitor, priv_monitor, process_monitor, cpu_line_monitor)
#     await server.run()


import asyncio
import websockets
import json
import logging
import psutil
import time
from src.notifications.email import send_email_alert

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Added new logic to send cpu alarm emails after 30 mins. 

last_email_sent_time = 0
EMAIL_SEND_INTERVAL = 30 * 60  # 30 minutes in seconds

def send_email_alert_limited(data, alert_type):
    """Send email alerts only if 30 minutes have passed since the last email."""
    global last_email_sent_time
    current_time = time.time()
    if current_time - last_email_sent_time > EMAIL_SEND_INTERVAL:
        send_email_alert(data, alert_type)
        last_email_sent_time = current_time
        logger.info(f"Email alert sent for {alert_type}")
    else:
        logger.debug(f"Email alert suppressed for {alert_type} (sent recently)")

class WebSocketServer:
    def __init__(self, cpu_monitor, network_monitor, user_monitor, priv_monitor, process_monitor, cpu_line_monitor):
        self.connected_clients = set()
        self.cpu_monitor = cpu_monitor
        self.network_monitor = network_monitor
        self.user_monitor = user_monitor
        self.priv_monitor = priv_monitor
        self.process_monitor = process_monitor
        self.cpu_line_monitor = cpu_line_monitor
        logger.debug(f"WebSocketServer initialized with cpu_line_monitor: {cpu_line_monitor}")

    async def handler(self, websocket):
        """Handle WebSocket client connections."""
        print(f"✅ Client connected: {websocket.remote_address}")
        self.connected_clients.add(websocket)
        try:
            while True:
                self.cpu_monitor.collect_data()
                # self.network_monitor.collect_data()
                # self.priv_monitor.collect_data()
                # self.user_monitor.collect_data()
                # self.priv_monitor.collect_data()
                if self.cpu_line_monitor:
                    if not psutil.pid_exists(self.cpu_line_monitor.pid):
                        logger.error(f"PID {self.cpu_line_monitor.pid} no longer exists")
                        self.cpu_line_monitor = None
                    else:
                        self.cpu_line_monitor.collect_data()
                        logger.debug(f"cpu_line_monitor data: {self.cpu_line_monitor.line_usage_data}")
                else:
                    logger.warning("cpu_line_monitor is None, skipping data collection")
                data = {
                    "cpuUtilization": self.cpu_monitor.cpu_data,
                    "cpuAlarms": self.cpu_monitor.cpu_alarms,
                    "networkPackets": self.network_monitor.collect_data(),
                    "userActivity": self.user_monitor.collect_data(),
                    "privilegedEvents": self.priv_monitor.collect_data(),
                    "processEvents": self.process_monitor.collect_data(),
                    "cpuLineUsage": self.cpu_line_monitor.line_usage_data if self.cpu_line_monitor else {"total_cpu_time": 0.0, "lines": []}
                }
                
                # logger.debug(f"Sending cpuLineUsage data: {data['cpuLineUsage']}")
                
                # Send Alerts: 
                if data["cpuAlarms"]:
                    send_email_alert_limited(data["cpuAlarms"], "CPU")
                
                current_user_activity = data["userActivity"]
                suspicious_user_activities = [event for event in current_user_activity if event.get("suspicious")]
                if suspicious_user_activities:
                    send_email_alert(suspicious_user_activities, "User Activity")                
                if data["privilegedEvents"]:
                    send_email_alert(data["privilegedEvents"], "Privileged Process")

                # Send data
                await websocket.send(json.dumps(data))
                await asyncio.sleep(1)
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
                self.process_monitor.process_bpf.perf_buffer_poll(timeout=100)
                await asyncio.sleep(0.1)

async def start_websocket_server():
    """Initialize monitors and start the WebSocket server."""
    from src.cpu_monitor.cpu_monitor import init_cpu_monitor
    from src.network_monitor.network_monitor import init_network_monitor
    from src.user_monitor.user_monitor import init_user_monitor
    from src.priv_monitor.priv_monitor import init_priv_monitor
    from src.process_monitor.process_monitor import init_process_monitor
    from src.cpu_line_monitor.cpu_line_monitor import init_cpu_line_monitor
    from config.settings import GO_APP_PID

    logger.info(f"Starting WebSocket server with GO_APP_PID: {GO_APP_PID}")
    if not psutil.pid_exists(GO_APP_PID):
        logger.error(f"PID {GO_APP_PID} does not exist")
    
    await asyncio.sleep(2)  # Wait for Go app to start
    logger.info("Waited 2s for Go application to initialize")

    cpu_monitor = init_cpu_monitor()
    network_monitor = init_network_monitor()
    user_monitor = init_user_monitor()
    priv_monitor = init_priv_monitor()
    process_monitor = init_process_monitor()
    cpu_line_monitor = None
    try:
        if GO_APP_PID > 0 and psutil.pid_exists(GO_APP_PID):
            cpu_line_monitor = init_cpu_line_monitor(GO_APP_PID)
            print(f"CPU line monitoring started for PID {GO_APP_PID}")
        else:
            logger.error("No valid Go application PID in settings.py or PID not running")
    except Exception as e:
        logger.error(f"Error initializing CPU line monitor: {e}")

    server = WebSocketServer(cpu_monitor, network_monitor, user_monitor, priv_monitor, process_monitor, cpu_line_monitor)
    await server.run()