#include <uapi/linux/ptrace.h>
#include <linux/sched.h>

struct data_t {
u32 pid;
u32 uid;
u64 syscall_id;
u64 arg1;
u64 arg2;
u64 arg3;
char comm[16];
char filename[256];
};

BPF_HASH(privileged_pids, u32, u8);
BPF_PERF_OUTPUT(events);

TRACEPOINT_PROBE(raw_syscalls, sys_enter) {
struct data_t data = {};
u32 pid = bpf_get_current_pid_tgid() >> 32;
data.pid = pid;
data.uid = bpf_get_current_uid_gid();
data.syscall_id = args->id;
data.arg1 = args->args[0];
data.arg2 = args->args[1];
data.arg3 = args->args[2];
bpf_get_current_comm(&data.comm, sizeof(data.comm));

if (args->id == 105 && args->args[0] == 0) {
u8 mark = 1;
privileged_pids.update(&pid, &mark);
__builtin_memcpy(&data.filename, "setuid(0)", 10);
events.perf_submit(args, &data, sizeof(data));
return 0;
}

if (args->id == 117 && args->args[2] == 0) {
u8 mark = 1;
privileged_pids.update(&pid, &mark);
__builtin_memcpy(&data.filename, "setresuid(..., ..., 0)", 24);
events.perf_submit(args, &data, sizeof(data));
return 0;
}

u8 *marked = privileged_pids.lookup(&pid);

if (!marked) {
struct task_struct *task = (struct task_struct *)bpf_get_current_task();
u32 ppid = 0;
bpf_probe_read_kernel(&ppid, sizeof(ppid), &task->real_parent->tgid);
u8 *parent_marked = privileged_pids.lookup(&ppid);
if (parent_marked) {
u8 mark = 1;
privileged_pids.update(&pid, &mark);
marked = &mark;
}
}

if (marked) {
if (args->id == 59) {
bpf_probe_read_user_str(&data.filename, sizeof(data.filename), (void *)args->args[0]);
events.perf_submit(args, &data, sizeof(data));
} else if (args->id == 257) {
bpf_probe_read_user_str(&data.filename, sizeof(data.filename), (void *)args->args[1]);
events.perf_submit(args, &data, sizeof(data));
} else if (args->id == 1) {
__builtin_memcpy(&data.filename, "-", 2);
events.perf_submit(args, &data, sizeof(data));
}
}

return 0;
}