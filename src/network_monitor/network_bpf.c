#include <uapi/linux/ptrace.h>
#include <net/sock.h>
#include <net/inet_sock.h>
#include <bcc/proto.h>

struct data_t {
u32 pid;
u32 uid;
u32 saddr;
u32 daddr;
u16 sport;
u16 dport;
char task[TASK_COMM_LEN];
u8 event_type; // 0 = connect, 1 = accept
};

BPF_PERF_OUTPUT(events);

int trace_connect(struct pt_regs *ctx, struct sock *sk) {
struct data_t data = {};
u16 dport = 0, sport = 0;

data.pid = bpf_get_current_pid_tgid() >> 32;
data.uid = bpf_get_current_uid_gid();
bpf_probe_read_kernel(&dport, sizeof(dport), &sk->__sk_common.skc_dport);
bpf_probe_read_kernel(&sport, sizeof(sport), &sk->__sk_common.skc_num);
bpf_probe_read_kernel(&data.saddr, sizeof(data.saddr), &sk->__sk_common.skc_rcv_saddr);
bpf_probe_read_kernel(&data.daddr, sizeof(data.daddr), &sk->__sk_common.skc_daddr);

data.dport = ntohs(dport);
data.sport = sport;
data.event_type = 0;
bpf_get_current_comm(&data.task, sizeof(data.task));
events.perf_submit(ctx, &data, sizeof(data));
return 0;
}

int trace_accept_return(struct pt_regs *ctx) {
struct sock *sk = (struct sock *)PT_REGS_RC(ctx);
if (sk == NULL) return 0;

struct data_t data = {};
u16 dport = 0, sport = 0;

data.pid = bpf_get_current_pid_tgid() >> 32;
data.uid = bpf_get_current_uid_gid();

bpf_probe_read_kernel(&sport, sizeof(sport), &sk->__sk_common.skc_num);
bpf_probe_read_kernel(&dport, sizeof(dport), &sk->__sk_common.skc_dport);
bpf_probe_read_kernel(&data.saddr, sizeof(data.saddr), &sk->__sk_common.skc_rcv_saddr);
bpf_probe_read_kernel(&data.daddr, sizeof(data.daddr), &sk->__sk_common.skc_daddr);

data.sport = sport;
data.dport = ntohs(dport);
data.event_type = 1;
bpf_get_current_comm(&data.task, sizeof(data.task));
events.perf_submit(ctx, &data, sizeof(data));
return 0;
}