#include <uapi/linux/ptrace.h>


BPF_HASH(counts, u64);

int on_event(struct pt_regs *ctx) {
    u64 ip = PT_REGS_IP(ctx);
    counts.increment(ip);
    return 0;
}
