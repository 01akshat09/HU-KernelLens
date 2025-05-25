from bcc import BPF, PerfType, PerfSWConfig
import subprocess
import psutil
import time
import logging
import datetime
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class CPULineMonitor:
    def __init__(self, pid):
        self.pid = pid
        self.binary_path = f"/proc/{pid}/exe"
        self.bpf = None
        self.line_usage_data = {"timestamp": "", "total_cpu_time": 0.0, "total_cpu_usage": 0.0, "lines": []}

    def init_bpf(self):
        """Initialize the BPF program for CPU line usage monitoring."""
        try:
            bpf_text = """
#include <uapi/linux/ptrace.h>
BPF_HASH(counts, u64);

int on_event(struct pt_regs *ctx) {
    u64 ip = PT_REGS_IP(ctx);
    counts.increment(ip);
    return 0;
}
"""
            self.bpf = BPF(text=bpf_text)
            self.bpf.attach_perf_event(
                ev_type=PerfType.SOFTWARE,
                ev_config=PerfSWConfig.CPU_CLOCK,
                fn_name="on_event",
                pid=self.pid,
                sample_freq=999
            )
            logger.info(f"CPU line usage BPF program initialized for PID {self.pid}")
            logger.debug(f"Attached perf event to PID {self.pid} with sample_freq=999")
        except Exception as e:
            logger.error(f"Failed to initialize CPU line usage BPF program for PID {self.pid}: {e}")
            raise

    def get_total_cpu_time(self):
        """Get total CPU time for the monitored process."""
        try:
            p = psutil.Process(self.pid)
            cpu_times = p.cpu_times()
            total = round(cpu_times.user + cpu_times.system, 3)
            logger.debug(f"Got CPU time for PID {self.pid}: {total} seconds")
            return total
        except (psutil.NoSuchProcess, psutil.Error) as e:
            logger.warning(f"Could not get CPU time for PID {self.pid}: {e}")
            return 0.0

    def get_total_cpu_usage(self):
        """Get total CPU usage percentage for the monitored process."""
        try:
            p = psutil.Process(self.pid)
            cpu_usage = p.cpu_percent(interval=1)  # Get CPU usage percentage
            logger.debug(f"Got CPU usage for PID {self.pid}: {cpu_usage}%")
            return round(cpu_usage, 2)
        except (psutil.NoSuchProcess, psutil.Error) as e:
            logger.warning(f"Could not get CPU usage for PID {self.pid}: {e}")
            return 0.0

    def resolve_addr(self, ip):
        """Resolve instruction pointer to function and source location."""
        try:
            out = subprocess.check_output(
                ["addr2line", "-f", "-e", self.binary_path, hex(ip)],
                stderr=subprocess.DEVNULL
            ).decode().strip().split('\n')
            func_name = out[0] if len(out) > 0 else "??"
            location = out[1] if len(out) > 1 else "??:0"
            logger.debug(f"Resolved IP {hex(ip)} to {func_name} at {location}")
            return func_name.strip(), location.strip()
        except subprocess.CalledProcessError as e:
            logger.debug(f"Failed to resolve address {hex(ip)}: {e}")
            return "??", "??:0"
        except Exception as e:
            logger.warning(f"Error resolving address {hex(ip)}: {e}")
            return "??", "??:0"

    def collect_data(self):
        """Collect CPU line usage data with timestamp and total CPU usage."""
        if self.bpf is None:
            logger.error("Cannot collect CPU line usage data: BPF program not initialized")
            self.line_usage_data = {"timestamp": "", "total_cpu_time": 0.0, "total_cpu_usage": 0.0, "lines": []}
            return

        try:
            # Get current timestamp
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            total_cpu_time = self.get_total_cpu_time()
            total_cpu_usage = self.get_total_cpu_usage()

            counts = self.bpf.get_table("counts")
            ip_counts = defaultdict(int)
            for k, v in counts.items():
                ip_counts[k.value] += v.value
            self.bpf["counts"].clear()

            logger.debug(f"Captured {len(ip_counts)} IP counts for PID {self.pid}")

            if not ip_counts:
                logger.debug(f"No CPU activity captured for PID {self.pid}")
                self.line_usage_data = {

                    "total_cpu_time": total_cpu_time,
                    "total_cpu_usage": total_cpu_usage,
                    "lines": []
                }
                return

            resolved = defaultdict(lambda: {"samples": 0, "function": "", "location": ""})
            for ip, count in ip_counts.items():
                func, loc = self.resolve_addr(ip)
                key = f"{func}|{loc}"
                resolved[key]["samples"] += count
                resolved[key]["function"] = func
                resolved[key]["location"] = loc

            total_samples = sum(entry["samples"] for entry in resolved.values())
            lines = []
            for key, entry in sorted(resolved.items(), key=lambda x: x[1]["samples"], reverse=True):
                percent = (entry["samples"] / total_samples * 100) if total_samples else 0
                lines.append({
                    "function": entry["function"],
                    "location": entry["location"],
                    "samples": entry["samples"],
                    "percent": round(percent, 2)
                })

            self.line_usage_data = {
                "timestamp": timestamp,
                "total_cpu_time": total_cpu_time,
                "total_cpu_usage": total_cpu_usage,
                "lines": lines
            }
            logger.info(f"Collected CPU line usage data for PID {self.pid}: {len(lines)} lines")
        except Exception as e:
            logger.error(f"Error collecting CPU line usage data for PID {self.pid}: {e}")
            self.line_usage_data = {"timestamp": "", "total_cpu_time": 0.0, "total_cpu_usage": 0.0, "lines": []}

def init_cpu_line_monitor(pid):
    """Initialize and return the CPU line monitor."""
    try:
        monitor = CPULineMonitor(pid)
        monitor.init_bpf()
        logger.info(f"Initialized CPU line monitor for PID {pid}")
        return monitor
    except Exception as e:
        logger.error(f"Failed to initialize CPU line monitor for PID {pid}: {e}")
        raise