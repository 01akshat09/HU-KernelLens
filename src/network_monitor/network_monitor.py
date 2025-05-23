# from bcc import BPF
# import socket
# import time

# class NetworkMonitor:
#     def __init__(self):
#         self.network_bpf = None
#         self.network_events = []

#     def init_bpf(self):
#         """Initialize the BPF program for network monitoring."""
#         with open("src/network_monitor/network_bpf.c", "r") as f:
#             bpf_text = f.read()
#         self.network_bpf = BPF(text=bpf_text)
#         self.network_bpf.attach_kprobe(event="tcp_connect", fn_name="trace_connect")
#         self.network_bpf.attach_kretprobe(event="inet_csk_accept", fn_name="trace_accept_return")
#         self.network_bpf["events"].open_perf_buffer(self.handle_network_event)

#     def handle_network_event(self, cpu, data, size):
#         """Handle network events from BPF."""
#         event = self.network_bpf["events"].event(data)
#         event_dict = {
#             "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
#             "pid": event.pid,
#             "comm": event.task.decode('utf-8', 'replace'),
#             "event_type": "connect" if event.event_type == 0 else "accept",
#             "saddr": socket.inet_ntoa(event.saddr.to_bytes(4, byteorder='big')),
#             "daddr": socket.inet_ntoa(event.daddr.to_bytes(4, byteorder='big')),
#             "sport": event.sport,
#             "dport": event.dport,
#             "protocol": "TCP"
#         }
#         self.network_events.append(event_dict)

#     def collect_data(self):
#         """Collect and return network events, then clear the buffer."""
#         current_events = list(self.network_events)
#         self.network_events.clear()
#         return current_events

# def init_network_monitor():
#     """Initialize and return the network monitor."""
#     monitor = NetworkMonitor()
#     monitor.init_bpf()
#     return monitor




from bcc import BPF
import socket
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NetworkMonitor:
    def __init__(self):
        self.network_bpf = None
        self.network_events = []

    def init_bpf(self):
        """Initialize the BPF program for network monitoring."""
        try:
            with open("src/network_monitor/network_bpf.c", "r") as f:
                bpf_text = f.read()
            self.network_bpf = BPF(text=bpf_text)
            self.network_bpf.attach_kprobe(event="tcp_connect", fn_name="trace_connect")
            self.network_bpf.attach_kretprobe(event="inet_csk_accept", fn_name="trace_accept_return")
            self.network_bpf["events"].open_perf_buffer(self.handle_network_event)
            logger.info("Network BPF program initialized successfully")
        except FileNotFoundError:
            logger.error("Could not find network_bpf.c at src/network_monitor/network_bpf.c")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Network BPF program: {e}")
            raise

    def handle_network_event(self, cpu, data, size):
        """Handle network events from BPF."""
        try:
            event = self.network_bpf["events"].event(data)
            event_dict = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "pid": event.pid,
                "comm": event.task.decode('utf-8', 'replace'),
                "event_type": "connect" if event.event_type == 0 else "accept",
                "saddr": socket.inet_ntoa(event.saddr.to_bytes(4, byteorder='big')),
                "daddr": socket.inet_ntoa(event.daddr.to_bytes(4, byteorder='big')),
                "sport": event.sport,
                "dport": event.dport,
                "protocol": "TCP"
            }
            self.network_events.append(event_dict)
        except Exception as e:
            logger.error(f"Error handling network event: {e}")

    def collect_data(self):
        """Collect and return network events, then clear the buffer."""
        if self.network_bpf is None:
            logger.error("Cannot collect network data: BPF program not initialized")
            return []
        current_events = list(self.network_events)
        self.network_events.clear()
        return current_events

def init_network_monitor():
    """Initialize and return the network monitor."""
    monitor = NetworkMonitor()
    monitor.init_bpf()
    return monitor