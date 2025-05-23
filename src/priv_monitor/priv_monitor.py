from bcc import BPF
from datetime import datetime

class PrivMonitor:
    def __init__(self):
        self.priv_bpf = None
        self.privileged_events = []
        self.syscall_map = {
            105: "setuid",
            117: "setresuid",
            59: "execve",
            257: "openat",
            1: "write",
        }

    def init_bpf(self):
        """Initialize the BPF program for privileged process monitoring."""
        with open("src/priv_monitor/priv_bpf.c", "r") as f:
            bpf_text = f.read()
        self.priv_bpf = BPF(text=bpf_text)
        self.priv_bpf.attach_tracepoint("raw_syscalls:sys_enter", "tracepoint__raw_syscalls__sys_enter")
        self.priv_bpf["events"].open_perf_buffer(self.handle_priv_event)

    def handle_priv_event(self, cpu, data, size):
        """Handle privileged process events from BPF."""
        event = self.priv_bpf["events"].event(data)
        syscall = self.syscall_map.get(event.syscall_id, f"unknown ({event.syscall_id})")
        filename = event.filename.decode('utf-8', 'replace').strip('\x00')
        insight = ""

        if event.syscall_id in [105, 117]:
            insight = "Privilege escalation attempt to UID 0"
        elif event.syscall_id == 59:
            insight = "⚠️ Execve from /tmp — Possible malicious execution" if filename.startswith("/tmp") else "Privileged process executed a program"
        elif event.syscall_id == 257:
            insight = "Privileged process opened a file"
        elif event.syscall_id == 1:
            insight = "Privileged process wrote to a file"

        payload = {
            "time": datetime.utcnow().isoformat() + "Z",
            "pid": event.pid,
            "uid": event.uid,
            "comm": event.comm.decode('utf-8', 'replace'),
            "syscall": syscall,
            "filename": filename,
            "args": [event.arg1, event.arg2, event.arg3],
            "insight": insight
        }
        self.privileged_events.append(payload)

    def collect_data(self):
        """Collect and return privileged events, then clear the buffer."""
        current_events = list(self.privileged_events)
        self.privileged_events.clear()
        return current_events

def init_priv_monitor():
    """Initialize and return the privileged process monitor."""
    monitor = PrivMonitor()
    monitor.init_bpf()
    return monitor