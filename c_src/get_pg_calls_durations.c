#include <uapi/linux/ptrace.h>
#include <linux/sched.h>

BPF_HASH(start, u32);
BPF_HISTOGRAM(dist);

int trace_enter(struct pt_regs *ctx)
{
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    u64 ts = bpf_ktime_get_ns();

    if (!(THREAD_FILTER)) {
        return 0;
    }
    start.update(&pid, &ts);

    return 0;
}

int trace_exit(struct pt_regs *ctx)
{
    u64 *tsp, delta;
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    // calculate delta time
    if (!(THREAD_FILTER)) {
        return 0;
    }
    tsp = start.lookup(&pid);
    if (tsp == 0) {
        return 0;   // missed start
    }

    delta = bpf_ktime_get_ns() - *tsp;
    start.delete(&pid);
    delta /= 1000;
    dist.increment(bpf_log2l(delta));
      
   return 0;
}
