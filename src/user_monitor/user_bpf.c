// #include <uapi/linux/ptrace.h>
// #include <linux/sched.h>

// #define MAX_ARGS 5
// #define ARG_LEN  64

// struct data_t {
// u32 pid;
// u32 uid;
// char comm[TASK_COMM_LEN];
// char argv[MAX_ARGS][ARG_LEN];
// };

// BPF_PERF_OUTPUT(events);

// int tracepoint__syscalls__sys_enter_execve(struct tracepoint__syscalls__sys_enter_execve *ctx) {
// struct data_t data = {};
// const char **argv = (const char **)(ctx->argv);

// data.pid = bpf_get_current_pid_tgid() >> 32;
// data.uid = bpf_get_current_uid_gid() & 0xFFFFFFFF;
// bpf_get_current_comm(&data.comm, sizeof(data.comm));

// #pragma unroll
// for (int i = 0; i < MAX_ARGS; i++) {
// const char *argp = NULL;
// if (bpf_probe_read_user(&argp, sizeof(argp), &argv[i]) != 0)
// break;
// if (!argp)
// break;
// if (bpf_probe_read_user_str(&data.argv[i], sizeof(data.argv[i]), argp) <= 0)
// break;
// }

// events.perf_submit(ctx, &data, sizeof(data));
// return 0;
// }


// #include <uapi/linux/ptrace.h>
// #include <linux/sched.h>
// #include <linux/string.h>

// #define MAX_ARGV 5
// #define MAX_ARG_LEN 64

// struct exec_data_t {
// u32 pid;
// u32 uid;
// char comm[16];
// char argv[MAX_ARGV][MAX_ARG_LEN];
// };

// BPF_PERF_OUTPUT(events);

// int kprobe__sys_execve(struct pt_regs *ctx, const char __user *filename,
// const char __user *const __user *argv,
// const char __user *const __user *envp) {
// struct exec_data_t data = {};
// struct task_struct *task = (struct task_struct *)bpf_get_current_task();

// data.pid = bpf_get_current_pid_tgid() >> 32;
// data.uid = bpf_get_current_uid_gid() & 0xffffffff;
// bpf_get_current_comm(&data.comm, sizeof(data.comm));

// // Copy up to MAX_ARGV arguments
// for (int i = 0; i < MAX_ARGV; i++) {
// const char __user *arg;
// if (bpf_probe_read_user(&arg, sizeof(arg), &argv[i])) {
// break; // Failed to read argv pointer
// }
// if (!arg) {
// break; // Null pointer, end of argv
// }
// if (bpf_probe_read_user_str(&data.argv[i], MAX_ARG_LEN, arg) < 0) {
// data.argv[i][0] = '\0'; // Ensure null-terminated empty string
// }
// }

// events.perf_submit(ctx, &data, sizeof(data));
// return 0;
// }



#include <uapi/linux/ptrace.h>
#include <linux/sched.h>
#include <linux/string.h>

#define MAX_ARGV 5
#define MAX_ARG_LEN 64

struct exec_data_t {
u32 pid;
u32 uid;
char comm[16];
char argv[MAX_ARGV][MAX_ARG_LEN];
};

BPF_PERF_OUTPUT(events);

int kprobe__sys_execve(struct pt_regs *ctx, const char __user *filename,
const char __user *const __user *argv,
const char __user *const __user *envp) {
struct exec_data_t data = {};
struct task_struct *task = (struct task_struct *)bpf_get_current_task();

data.pid = bpf_get_current_pid_tgid() >> 32;
data.uid = bpf_get_current_uid_gid() & 0xffffffff;
bpf_get_current_comm(&data.comm, sizeof(data.comm));

// Initialize argv to empty strings
for (int i = 0; i < MAX_ARGV; i++) {
data.argv[i][0] = '\0';
}

// Copy up to MAX_ARGV arguments
for (int i = 0; i < MAX_ARGV; i++) {
const char __user *arg;
if (bpf_probe_read_user(&arg, sizeof(arg), &argv[i])) {
break; // Failed to read argv pointer
}
if (!arg) {
break; // Null pointer, end of argv
}
if (bpf_probe_read_user_str(&data.argv[i], MAX_ARG_LEN, arg) < 0) {
data.argv[i][0] = '\0'; // Ensure null-terminated empty string
}
// Debug: Log first few bytes of each argument
char debug_buf[8];
bpf_probe_read(debug_buf, sizeof(debug_buf), data.argv[i]);
bpf_trace_printk("argv[%d]: %8s\n", i, debug_buf);
}

events.perf_submit(ctx, &data, sizeof(data));
return 0;
}