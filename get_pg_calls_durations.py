#!/usr/bin/python

# Recording postgres function calls duration
# Copyright (c) 2022 Bertrand Drouvot

from __future__ import print_function
from bcc import BPF, USDT
from time import sleep, strftime
import argparse
import signal

EBPF_SRC = "c_src/get_pg_calls_durations.c"

def positive_int(val):
    try:
        ival = int(val)
    except ValueError:
        raise argparse.ArgumentTypeError("must be an integer")

    if ival < 0:
        raise argparse.ArgumentTypeError("must be positive")
    return ival

examples = """example:
    /get_pg_calls_durations.py -x /home/postgres/pgdirect/pg_installed/bin/postgres -i 3 -f RelationGetBufferForTuple
"""

parser = argparse.ArgumentParser(
    description="Recording postgres function calls duration",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=examples)

parser.add_argument("-x", "--binary", metavar="BINARY", dest="binary", required = True,
    help="path to postgres binary")

parser.add_argument("-f", "--func", metavar="function", dest="func", required = True,
    help="postgres function to trace")

parser.add_argument("-p", "--pid", metavar="PID", dest="pid",
    help="trace this PID only", type=positive_int)

parser.add_argument("-i", "--interval", default=99999999,
    help="summary interval, seconds")

args = parser.parse_args()

with open(EBPF_SRC) as fileobj:
     bpf_txt = fileobj.read()

func = args.func

# setup pid filter
thread_filter = '1'
if args.pid is not None:
    thread_filter = 'pid == %d' % args.pid

bpf_txt = bpf_txt.replace('THREAD_FILTER', thread_filter)

binary = args.binary

b=BPF(text=bpf_txt)

libpath = BPF.find_exe(binary)
if not libpath:
    bail("can't resolve library %s" % library)
library = libpath

b.attach_uprobe(name=library, sym_re=func,
    fn_name="trace_enter",
    pid = -1)

b.attach_uretprobe(name=library, sym_re=func,
    fn_name="trace_exit",
    pid = -1)

matched = b.num_open_uprobes()

if matched == 0:
    print("error: 0 functions traced. Exiting.", file=stderr)
    exit(1)

# signal handler
def signal_ignore(signal, frame):
    print()

# output
exiting = 0 if args.interval else 1
dist = b.get_table("dist")

while (1):
    try:
        sleep(int(args.interval))
    except KeyboardInterrupt:
        exiting = 1
        # as cleanup can take many seconds, trap Ctrl-C:
        signal.signal(signal.SIGINT, signal_ignore)

    print()
    print ("%-8s: %s calls duration\n" % (strftime("%H:%M:%S"), func))
    #print("%-8s\n" % strftime("%H:%M:%S"), end="")

    dist.print_log2_hist("usecs")
    dist.clear()

    if exiting:
        print("Detaching...")
        exit()
