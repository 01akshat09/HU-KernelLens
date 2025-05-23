#include <uapi/linux/ptrace.h>
BPF_HASH(start, u32);
BPF_HASH(cpu_time, u32, u64);

TRACEPOINT_PROBE(sched, sched_switch) {
u32 pid = bpf_get_current_pid_tgid();
u64 ts = bpf_ktime_get_ns();

u32 prev_pid = args->prev_pid;
u64 *tsp = start.lookup(&prev_pid);
if (tsp) {
u64 delta = ts - *tsp;
u64 *time = cpu_time.lookup(&prev_pid);
if (time) {
*time += delta;
} else {
cpu_time.update(&prev_pid, &delta);
}
start.delete(&prev_pid);
}

start.update(&pid, &ts);
return 0;
}