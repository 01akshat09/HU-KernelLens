from bcc import BPF
from ctypes import Structure, c_uint, c_char, sizeof, cast, POINTER 
import re
import time
import logging
import traceback

TASK_COMM_LEN = 16
MAX_EXEC_ARGS = 5
ARG_LENGTH = 64

class ExecData(Structure):
    _fields_ = [
        ("pid", c_uint),
        ("uid", c_uint),
        ("comm", c_char * TASK_COMM_LEN),
        ("argv", (c_char * ARG_LENGTH) * MAX_EXEC_ARGS)
    ]

class UserMonitor:

    def __init__(self):
        self.user_bpf = None
        self.user_activity_events = []
        self.SUSPICIOUS_PATTERNS = [r"/root", r"/etc", r"/boot", r"/proc", r"/sys",r"rm\s+-rf\s+/", r"chmod\s+777", r"chown\s+root", r"/etc/passwd",r"ncat", r"nc", r"tcpdump", r"curl", r"wget", r"python.*http\.server"]
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers: 
            logging.basicConfig(level=logging.INFO)


    def init_bpf(self):
        """Initialize the BPF program for user activity monitoring."""
        bpf_file_path = "src/user_monitor/user_bpf.c" 
        try:
            with open(bpf_file_path, "r") as f:
                bpf_text = f.read()
            
            self.user_bpf = BPF(text=bpf_text, cflags=["-Wno-macro-redefined"])
            self.user_bpf["events"].open_perf_buffer(self.user_activity_event_handler)
            self.logger.info(f"User Activity BPF program initialized successfully from {bpf_file_path}")
        except FileNotFoundError:
            self.logger.error(
                f"Could not find BPF C code at {bpf_file_path}. "
                "Ensure the path and filename are correct."
            )
            raise
        except Exception as e:
            self.logger.error(f"Failed to initialize User Activity BPF program: {e}")
            self.logger.error(traceback.format_exc())
            raise

    @staticmethod
    def _decode_c_char_array(c_char_arr, max_len):
        try:
            # raw_bytes = c_char_arr.value
            raw_bytes = bytes(c_char_arr)
            try:
                nul_index = raw_bytes.index(b'\x00')
                decodable_bytes = raw_bytes[:nul_index]
            except ValueError:
                decodable_bytes = raw_bytes[:max_len]
            return decodable_bytes.decode('utf-8', errors='replace')
        except Exception as e:
            logging.getLogger(__name__).warning(f"Error decoding c_char_array: {e}. Raw start: {getattr(c_char_arr, 'value', b'')[:10]}...")
            return ""

    def user_activity_event_handler(self, cpu, data, size):
        """Handle user activity events from BPF."""
        try:
            expected_size = sizeof(ExecData)
            if size < expected_size:
                self.logger.warning(
                    f"Received data size {size} is less than expected {expected_size} for ExecData. Skipping event."
                )
                self.logger.debug(f"Data type: {type(data)}, Data value (if int): {data if isinstance(data, int) else 'not an int'}")
                return

            
            event_ptr = cast(data, POINTER(ExecData))
            
            event = event_ptr.contents
            
            args = []
            for i in range(MAX_EXEC_ARGS):
                arg_c_array = event.argv[i] 
                arg_str = self._decode_c_char_array(arg_c_array, ARG_LENGTH)
                if arg_str:
                    args.append(arg_str)
            
            arg_line = " ".join(args)

            comm_str = self._decode_c_char_array(event.comm, TASK_COMM_LEN).strip()

            self.user_activity_events.append({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "pid": event.pid,
                "uid": event.uid,
                "comm": comm_str,
                "args": arg_line,
                "suspicious": any(re.search(pattern, arg_line, re.IGNORECASE) for pattern in self.SUSPICIOUS_PATTERNS)
            })
        except Exception as e:
            self.logger.error(f"Error handling user activity event: {e}")
            self.logger.error(traceback.format_exc()) 

    def collect_data(self):
        """Collect and return user activity events, then clear the buffer."""
        if self.user_bpf is None:
            self.logger.error("Cannot collect user activity data: BPF program not initialized")
            return []
        current_events = list(self.user_activity_events)
        self.user_activity_events.clear()
        return current_events


def init_user_monitor():
    """Initialize and return the user activity monitor."""
    monitor = UserMonitor()
    monitor.init_bpf()
    return monitor

if __name__ == '__main__':
    logger = logging.getLogger(__name__) 
    logger.info("Starting User Monitor example...")
    monitor = None
    try:
        monitor = init_user_monitor()
        logger.info("User Monitor initialized. Monitoring events for 20 seconds...")
        
        end_time = time.time() + 20
        while time.time() < end_time:
            time.sleep(1)
            collected_events = monitor.collect_data()
            if collected_events:
                logger.info(f"Collected {len(collected_events)} events in the last period:")
                for event_data in collected_events:
                    logger.info(f"  PID: {event_data['pid']}, UID: {event_data['uid']}, Comm: {event_data['comm']}, Args: {event_data['args']}, Suspicious: {event_data['suspicious']}")
        
        logger.info("Example monitoring finished.")

    except KeyboardInterrupt:
        logger.info("Monitoring interrupted by user.")
    except Exception as main_e:
        logger.error(f"An error occurred in the User Monitor example: {main_e}")
        logger.error(traceback.format_exc())
    finally:
        if monitor and monitor.user_bpf:
            pass
        logger.info("Exiting User Monitor example.")