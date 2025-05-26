from bcc import BPF
from ctypes import Structure, c_uint, c_char
import os
import signal
import logging
from datetime import datetime
from ctypes import cast, POINTER

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ProcData(Structure):
    _fields_ = [
        ("pid", c_uint),
        ("ppid", c_uint),
        ("comm", c_char * 16)
    ]

class ProcessMonitor:
    def __init__(self):
        self.process_bpf = None
        self.process_events = []

    def init_bpf(self):
        """Initialize the BPF program for process monitoring."""
        try:
            with open("src/process_monitor/process_bpf.c", "r") as f:
                bpf_text = f.read()
            self.process_bpf = BPF(text=bpf_text, cflags=["-Wno-macro-redefined"])
            self.process_bpf["proc_events"].open_perf_buffer(self.process_event_handler)

            logger.info("Process Monitor BPF program initialized successfully")
        except FileNotFoundError:
            logger.error("Could not find process_bpf.c at src/process_monitor/process_bpf.c")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Process Monitor BPF program: {e}")
            raise

    def get_state(self, pid):
        """Get process state from /proc/[pid]/status."""
        try:
            with open(f"/proc/{pid}/status", "r") as f:
                for line in f:
                    if line.startswith("State:"):
                        return line.split()[1]
        except:
            return None

    def generate_process_insight(self, pid, ppid):
        """Classify process as zombie, orphan, short-lived, or normal."""
        proc_path = f"/proc/{pid}"
        state = self.get_state(pid)

        if not os.path.exists(proc_path):
            return (
                "Short-lived or ghost process",
                "Process exited before inspection",
                "Process likely ran and exited very quickly."
            )
        if state == "Z":
            return (
                "Zombie process",
                "Process is dead but not cleaned up",
                "Zombie processes are completed programs whose parent hasn’t read their exit status."
            )
        if ppid == 1:
            return (
                "Orphan process",
                "Parent process exited",
                "The parent died, so the process was re-parented to init/systemd (PID 1)."
            )
        return (
            "Normal process",
            "Typical fork/exec event",
            "Standard process creation event with no abnormal traits."
        )

    def process_event_handler(self, cpu, data, size):
        """Handle process creation events from BPF."""
        try:
            # event = ProcData.from_buffer_copy(data)
            event = cast(data, POINTER(ProcData)).contents
            pid = event.pid
            ppid = event.ppid
            comm = event.comm.decode('utf-8', errors='ignore').strip()
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            activity, reason, desc = self.generate_process_insight(pid, ppid)
            action = "Process appears safe"
            if activity in ["Zombie process", "Orphan process", "Short-lived or ghost process"]:
                try:
                    os.kill(pid, signal.SIGKILL)
                    action = f"Killed suspicious process (PID {pid})"
                    logger.info(f"Killed {activity} (PID {pid})")
                except ProcessLookupError:
                    action = "Process already exited before kill"
                except PermissionError:
                    action = f"Insufficient permissions to kill PID {pid}"
                except Exception as e:
                    action = f"Failed to kill PID {pid} ({e})"
            else:
                # logger.debug(f"Safe process detected: PID {pid}, Comm {comm}")
                pass

            self.process_events.append({
                "timestamp": ts,
                "pid": pid,
                "ppid": ppid,
                "comm": comm,
                "activity": activity,
                "reason": reason,
                "description": desc,
                "action": action
            })
            # logger.debug(f"Appended process event: {self.process_events[-1]}")
        except Exception as e:
            logger.error(f"Error handling process event: {e}")

    def collect_data(self):
        """Collect and return process events, then clear the buffer."""
        if self.process_bpf is None:
            logger.error("Cannot collect process data: BPF program not initialized")
            return []
        current_events = list(self.process_events)
        self.process_events.clear()
        # logger.debug(f"Collected {len(current_events)} process events")
        return current_events

def init_process_monitor():
    """Initialize and return the process monitor."""
    monitor = ProcessMonitor()
    monitor.init_bpf()
    return monitor