#include <uapi/linux/ptrace.h>
#include <linux/sched.h>

#define TASK_COMM_LEN 16

struct proc_data_t {
u32 pid;
u32 ppid;
char comm[TASK_COMM_LEN];
};

BPF_PERF_OUTPUT(proc_events);

TRACEPOINT_PROBE(sched, sched_process_fork) {
struct proc_data_t data = {};

data.pid = args->child_pid;
data.ppid = args->parent_pid;
bpf_get_current_comm(&data.comm, sizeof(data.comm));

proc_events.perf_submit(args, &data, sizeof(data));
return 0;
}