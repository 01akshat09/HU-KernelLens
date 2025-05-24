# from bcc import BPF
# from ctypes import Structure, c_uint, c_char
# import re
# import time

# SUSPICIOUS_PATTERNS = [
#     r"/root", r"/etc", r"/boot", r"/proc", r"/sys",
#     r"rm\s+-rf\s+/", r"chmod\s+777", r"chown\s+root", r"/etc/passwd",
#     r"ncat", r"nc", r"tcpdump", r"curl", r"wget", r"python.*http\.server"
# ]

# class ExecData(Structure):
#     _fields_ = [
#         ("pid", c_uint),
#         ("uid", c_uint),
#         ("comm", c_char * 16),
#         ("argv", (c_char * 64) * 5)
#     ]

# class UserMonitor:
#     def __init__(self):
#         self.user_bpf = None
#         self.user_activity_events = []

#     def init_bpf(self):
#         """Initialize the BPF program for user activity monitoring."""
#         with open("src/user_monitor/user_bpf.c", "r") as f:
#             bpf_text = f.read()
#         self.user_bpf = BPF(text=bpf_text)
#         self.user_bpf["events"].open_perf_buffer(self.user_activity_event_handler)

#     def user_activity_event_handler(self, cpu, data, size):
#         """Handle user activity events from BPF."""
#         event = ExecData.from_buffer_copy(data)
#         args = []
#         for arg in event.argv:
#             arg_str = bytes(arg).decode(errors="ignore").rstrip("\x00")
#             if arg_str:
#                 args.append(arg_str)
#         arg_line = " ".join(args)
#         comm_str = event.comm.decode(errors="ignore").strip()
#         self.user_activity_events.append({
#             "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
#             "pid": event.pid,
#             "uid": event.uid,
#             "comm": comm_str,
#             "args": arg_line,
#             "suspicious": any(re.search(pattern, arg_line) for pattern in SUSPICIOUS_PATTERNS)
#         })

#     def collect_data(self):
#         """Collect and return user activity events, then clear the buffer."""
#         current_events = list(self.user_activity_events)
#         self.user_activity_events.clear()
#         return current_events

# def init_user_monitor():
#     """Initialize and return the user activity monitor."""
#     monitor = UserMonitor()
#     monitor.init_bpf()
#     return monitor


# from bcc import BPF
# from ctypes import Structure, c_uint, c_char
# import re
# import time
# import logging

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# SUSPICIOUS_PATTERNS = [
#     r"/root", r"/etc", r"/boot", r"/proc", r"/sys",
#     r"rm\s+-rf\s+/", r"chmod\s+777", r"chown\s+root", r"/etc/passwd",
#     r"ncat", r"nc", r"tcpdump", r"curl", r"wget", r"python.*http\.server"
# ]

# class ExecData(Structure):
#     _fields_ = [
#         ("pid", c_uint),
#         ("uid", c_uint),
#         ("comm", c_char * 16),
#         ("argv", (c_char * 64) * 5)
#     ]

# class UserMonitor:
#     def __init__(self):
#         self.user_bpf = None
#         self.user_activity_events = []

#     def init_bpf(self):
#         try:
#             with open("src/user_monitor/user_bpf.c", "r") as f:
#                 bpf_text = f.read()
#             self.user_bpf = BPF(text=bpf_text, cflags=["-Wno-macro-redefined"])
#             self.user_bpf["events"].open_perf_buffer(self.user_activity_event_handler)
#             logger.info("User Activity BPF program initialized successfully")
#         except FileNotFoundError:
#             logger.error("Could not find user_bpf.c at src/user_monitor/user_bpf.c")
#             raise
#         except Exception as e:
#             logger.error(f"Failed to initialize User Activity BPF program: {e}")
#             raise

#     def user_activity_event_handler(self, cpu, data, size):
#         """Handle user activity events from BPF."""
#         try:
#             event = ExecData.from_buffer_copy(data)
#             args = []
#             for arg in event.argv:
#                 arg_str = bytes(arg).decode(errors="ignore").rstrip("\x00")
#                 if arg_str:
#                     args.append(arg_str)
#             arg_line = " ".join(args)
#             comm_str = event.comm.decode(errors="ignore").strip()
#             self.user_activity_events.append({
#                 "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
#                 "pid": event.pid,
#                 "uid": event.uid,
#                 "comm": comm_str,
#                 "args": arg_line,
#                 "suspicious": any(re.search(pattern, arg_line) for pattern in SUSPICIOUS_PATTERNS)
#             })
#         except Exception as e:
#             logger.error(f"Error handling user activity event: {e}")

#     def collect_data(self):
#         """Collect and return user activity events, then clear the buffer."""
#         if self.user_bpf is None:
#             logger.error("Cannot collect user activity data: BPF program not initialized")
#             return []
#         current_events = list(self.user_activity_events)
#         self.user_activity_events.clear()
#         return current_events

# def init_user_monitor():
#     """Initialize and return the user activity monitor."""
#     monitor = UserMonitor()
#     monitor.init_bpf()
#     return monitor




# from bcc import BPF
# from ctypes import Structure, c_uint, c_char
# import re
# import time
# import logging

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# SUSPICIOUS_PATTERNS = [
#     r"/root", r"/etc", r"/boot", r"/proc", r"/sys",
#     r"rm\s+-rf\s+/", r"chmod\s+777", r"chown\s+root", r"/etc/passwd",
#     r"ncat", r"nc", r"tcpdump", r"curl", r"wget", r"python.*http\.server"
# ]

# class ExecData(Structure):
#     _fields_ = [
#         ("pid", c_uint),
#         ("uid", c_uint),
#         ("comm", c_char * 16),
#         ("argv", (c_char * 64) * 5)
#     ]

# class UserMonitor:
#     def __init__(self):
#         self.user_bpf = None
#         self.user_activity_events = []

#     def init_bpf(self):
#         """Initialize the BPF program for user activity monitoring."""
#         try:
#             with open("src/user_monitor/user_bpf.c", "r") as f:
#                 bpf_text = f.read()
#             self.user_bpf = BPF(text=bpf_text, cflags=["-Wno-macro-redefined"])
#             self.user_bpf["events"].open_perf_buffer(self.user_activity_event_handler)
#             logger.info("User Activity BPF program initialized successfully")
#         except FileNotFoundError:
#             logger.error("Could not find user_bpf.c at src/user_monitor/user_bpf.c")
#             raise
#         except Exception as e:
#             logger.error(f"Failed to initialize User Activity BPF program: {e}")
#             raise

#     def user_activity_event_handler(self, cpu, data, size):
#         """Handle user activity events from BPF."""
#         try:
#             event = ExecData.from_buffer_copy(data)
#             args = []
#             for arg in event.argv:
#                 try:
#                     # Ensure arg is a valid byte string before decoding
#                     if isinstance(arg, (bytes, bytearray)):
#                         arg_str = arg.decode('utf-8', errors='ignore').rstrip('\x00')
#                     else:
#                         logger.debug(f"Skipping invalid argv element: {arg}")
#                         arg_str = ''
#                     if arg_str:
#                         args.append(arg_str)
#                 except Exception as e:
#                     logger.warning(f"Skipping invalid argv element due to error: {e}")
#                     continue
#             arg_line = " ".join(args)
#             comm_str = event.comm.decode('utf-8', errors='ignore').strip()
#             self.user_activity_events.append({
#                 "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
#                 "pid": event.pid,
#                 "uid": event.uid,
#                 "comm": comm_str,
#                 "args": arg_line,
#                 "suspicious": any(re.search(pattern, arg_line) for pattern in SUSPICIOUS_PATTERNS)
#             })
#         except Exception as e:
#             logger.error(f"Error handling user activity event: {e}")

#     def collect_data(self):
#         """Collect and return user activity events, then clear the buffer."""
#         if self.user_bpf is None:
#             logger.error("Cannot collect user activity data: BPF program not initialized")
#             return []
#         current_events = list(self.user_activity_events)
#         self.user_activity_events.clear()
#         return current_events

# def init_user_monitor():
#     """Initialize and return the user activity monitor."""
#     monitor = UserMonitor()
#     monitor.init_bpf()
#     return monitor


from bcc import BPF
from ctypes import Structure, c_uint, c_char, sizeof, cast, POINTER # Ensure cast and POINTER are imported
import re
import time
import logging
import traceback

# ... (logging configuration, SUSPICIOUS_PATTERNS, constants like TASK_COMM_LEN, etc. remain the same) ...

# Constants for the ExecData structure.
# These MUST match the definitions in your BPF C code (e.g., user_bpf.c or user_ebpf.c).
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
    # ... (__init__, init_bpf, _decode_c_char_array remain the same as in the previous good version) ...

    def __init__(self):
        self.user_bpf = None
        self.user_activity_events = []
        # Ensure logger is set up if not globally
        self.SUSPICIOUS_PATTERNS = [r"/root", r"/etc", r"/boot", r"/proc", r"/sys",r"rm\s+-rf\s+/", r"chmod\s+777", r"chown\s+root", r"/etc/passwd",r"ncat", r"nc", r"tcpdump", r"curl", r"wget", r"python.*http\.server"]
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers: # Avoid duplicate handlers if run multiple times
            logging.basicConfig(level=logging.INFO)


    def init_bpf(self):
        """Initialize the BPF program for user activity monitoring."""
        bpf_file_path = "src/user_monitor/user_bpf.c" # Or user_ebpf.c
        try:
            with open(bpf_file_path, "r") as f:
                bpf_text = f.read()
            
            # Optional: Replace placeholders if your C code uses them
            # bpf_text = bpf_text.replace("##MAX_ARGS##", str(MAX_EXEC_ARGS))
            # ...

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
            # Using a local logger or global logger instance
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

            # --- Đây là thay đổi quan trọng ---
            # 'data' from the BPF callback is a c_void_p (effectively an integer memory address).
            # Cast this pointer to a pointer of our ExecData structure type.
            event_ptr = cast(data, POINTER(ExecData))
            # Dereference the pointer to get the actual structure instance.
            # This maps the ExecData Python structure onto the raw memory.
            event = event_ptr.contents
            # --- Kết thúc thay đổi quan trọng ---
            
            args = []
            for i in range(MAX_EXEC_ARGS):
                arg_c_array = event.argv[i] # This is a c_char_Array_ARG_LENGTH
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
            self.logger.error(traceback.format_exc()) # Log full traceback

    def collect_data(self):
        """Collect and return user activity events, then clear the buffer."""
        if self.user_bpf is None:
            self.logger.error("Cannot collect user activity data: BPF program not initialized")
            return []
        current_events = list(self.user_activity_events)
        self.user_activity_events.clear()
        return current_events

# ... (init_user_monitor and __main__ block can remain the same) ...

def init_user_monitor():
    """Initialize and return the user activity monitor."""
    monitor = UserMonitor()
    monitor.init_bpf()
    return monitor

if __name__ == '__main__':
    logger = logging.getLogger(__name__) # Ensure logger is accessible
    logger.info("Starting User Monitor example...")
    monitor = None
    try:
        monitor = init_user_monitor()
        logger.info("User Monitor initialized. Monitoring events for 20 seconds...")
        
        end_time = time.time() + 20
        while time.time() < end_time:
            time.sleep(1)
            # For open_perf_buffer, events are processed in a background thread.
            # Polling is not strictly necessary here for event processing itself,
            # but perf_buffer_poll() can be called to ensure events are flushed/processed
            # if there are concerns about the callback thread's activity or for specific BCC versions/setups.
            # Usually, just sleeping is fine as the callback thread does the work.
            # If you *do* call it, ensure it doesn't interfere with the callback.
            # For now, we'll rely on the callback thread.
            # if monitor.user_bpf:
            #    monitor.user_bpf.perf_buffer_poll() # Optional: explicitly poll

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
        # BCC's BPF objects generally clean up their resources when they go out of scope
        # or when the Python process exits. Explicit cleanup is usually not required
        # unless you are managing many BPF objects dynamically and need to free resources early.
        if monitor and monitor.user_bpf:
            # monitor.user_bpf.cleanup() # Only if such a method exists and is necessary
            pass
        logger.info("Exiting User Monitor example.")