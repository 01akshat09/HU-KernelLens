from bcc import BPF
import psutil
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CPUMonitor:
    def __init__(self):
        self.cpu_bpf = None
        self.cpu_data = []
        self.cpu_alarms = []

    def init_bpf(self):
        """Initialize the BPF program for CPU monitoring."""
        try:
            with open("src/cpu_monitor/cpu_bpf.c", "r") as f:
                bpf_text = f.read()
            self.cpu_bpf = BPF(text=bpf_text)
            logger.info("CPU BPF program initialized successfully")
        except FileNotFoundError:
            logger.error("Could not find cpu_bpf.c at src/cpu_monitor/cpu_bpf.c")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize CPU BPF program: {e}")
            raise

    def collect_data(self):
        """Collect CPU usage data and check for alarms."""
        if self.cpu_bpf is None:
            logger.error("Cannot collect CPU data: BPF program not initialized")
            return

        self.cpu_data.clear()
        self.cpu_alarms.clear()
        now = time.strftime("%Y-%m-%d %H:%M:%S")

        try:
            for k, v in self.cpu_bpf["cpu_time"].items():
                pid = k.value
                cpu_time_ns = v.value
                cpu_time_sec = cpu_time_ns / 1e9

                try:
                    proc = psutil.Process(pid)
                    comm = proc.name()
                    self.cpu_data.append({
                        "timestamp": now,
                        "pid": pid,
                        "comm": comm,
                        "cpu_time": round(cpu_time_sec, 4)
                    })

                    if cpu_time_sec > 5000.0:
                        self.cpu_alarms.append({
                            "pid": pid,
                            "comm": comm,
                            "cpu": round(cpu_time_sec, 4),
                            "threshold": 1000.0,
                            "triggeredAt": now
                        })
                except psutil.NoSuchProcess:
                    continue
        except Exception as e:
            logger.error(f"Error collecting CPU data: {e}")

def init_cpu_monitor():
    """Initialize and return the CPU monitor."""
    monitor = CPUMonitor()
    monitor.init_bpf()
    return monitor