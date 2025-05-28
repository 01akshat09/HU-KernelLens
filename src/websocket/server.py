import asyncio
import websockets
import json
from src.notifications.email import send_email_alert
from src.notifications.teams import send_teams_alert

##############################

# from influxdb_client import InfluxDBClient, Point, WritePrecision
# from influxdb_client.client.write_api import SYNCHRONOUS
# from config.settings import INFLUXDB_URL, INFLUXDB_TOKEN, INFLUXDB_ORG, INFLUXDB_BUCKET

# # Configure logging
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

# # InfluxDB client setup
# influx_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
# write_api = influx_client.write_api(write_options=SYNCHRONOUS)
# query_api = influx_client.query_api()

##############################

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
    def __init__(self, cpu_monitor, network_monitor, user_monitor, priv_monitor, process_monitor):
        self.connected_clients = set()
        self.cpu_monitor = cpu_monitor
        self.network_monitor = network_monitor
        self.user_monitor = user_monitor
        self.priv_monitor = priv_monitor
        self.process_monitor = process_monitor

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
                data = {
                    "cpuUtilization": self.cpu_monitor.cpu_data,
                    "cpuAlarms": self.cpu_monitor.cpu_alarms,
                    "networkPackets": self.network_monitor.collect_data(),
                    "userActivity": self.user_monitor.collect_data(),
                    "privilegedEvents": self.priv_monitor.collect_data(),
                    "processEvents": self.process_monitor.collect_data(),
                    "cpuLineUsage": self.cpu_line_monitor.line_usage_data if self.cpu_line_monitor else {
                        "timestamp": "",
                        "total_cpu_time": 0.0,
                        "total_cpu_usage": 0.0,
                        "lines": []
                    }
                }
                
                # Send Alerts with improved filtering: 
                if data["cpuAlarms"]:
                    logger.debug(f"Raw CPU alarms: {data['cpuAlarms']}")
                    send_email_alert_limited(data["cpuAlarms"], "CPU")
                    await send_teams_alert(data["cpuAlarms"], "CPU")
                
                current_user_activity = data["userActivity"]
                logger.debug(f"Raw user activity: {current_user_activity}")
                suspicious_user_activities = [
                    event for event in current_user_activity 
                    if str(event.get("suspicious")).lower() == "true"  # Convert to string and compare
                ]
                
                if suspicious_user_activities:
                    logger.info(f"Filtered suspicious activities: {suspicious_user_activities}")
                    send_email_alert(suspicious_user_activities, "User Activity")
                    await send_teams_alert(suspicious_user_activities, "User Activity")
                
                if data["privilegedEvents"]:
                    # Filter privileged events for non-root users and execve from /tmp
                    privileged_alerts = [
                        event for event in data["privilegedEvents"]
                        if (event.get("uid", 0) != 0) or  # non-root users
                           (event.get("syscall") == "execve" and  # execve syscall
                            str(event.get("filename", "")).startswith("/tmp/"))  # from /tmp
                    ]
                    if privileged_alerts:
                        logger.info(f"Filtered privileged events: {privileged_alerts}")
                        send_email_alert(privileged_alerts, "Privileged Process")
                        await send_teams_alert(privileged_alerts, "Privileged Process")

                # Send data

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
                self.process_monitor.process_bpf.perf_buffer_poll(timeout=100)
                await asyncio.sleep(0.1)

async def start_websocket_server():
    """Initialize monitors and start the WebSocket server."""
    from src.cpu_monitor.cpu_monitor import init_cpu_monitor
    from src.network_monitor.network_monitor import init_network_monitor
    from src.user_monitor.user_monitor import init_user_monitor
    from src.priv_monitor.priv_monitor import init_priv_monitor
    from src.process_monitor.process_monitor import init_process_monitor

    cpu_monitor = init_cpu_monitor()
    network_monitor = init_network_monitor()
    user_monitor = init_user_monitor()
    priv_monitor = init_priv_monitor()
    process_monitor = init_process_monitor()

    server = WebSocketServer(cpu_monitor, network_monitor, user_monitor, priv_monitor, process_monitor)
    await server.run()

