Introduction
============

eBPF toolkit to be used with PostgreSQL.  
Intend is not to be used in production but for study only.

It currently contains:

 * ``get_pg_calls_durations.py``: python script to get functions calls duration (histogram)
 * ``c_src/get_pg_calls_durations.c``: the c file associated to ``get_pg_calls_durations.py``

Example
========
- For one single PID, display histograms for the counts and timing of FileRead() calls, refresh at a 2 seconds interval, and don't zero across updates (showing final update only in the example output here):
```
pg-14.4 rw root@db1=# explain (analyze,verbose,buffers) select count(mydata) from test where mynumber1<10000000;
                                                                      QUERY PLAN
-------------------------------------------------------------------------------------------------------------------------------------------------------
 Aggregate  (cost=371666.17..371666.18 rows=1 width=8) (actual time=5756.050..5756.057 rows=1 loops=1)
   Output: count(mydata)
   Buffers: shared read=110660
   I/O Timings: read=3545.630
   ->  Index Scan using test_mynumber1 on public.test  (cost=0.57..348024.22 rows=9456780 width=18) (actual time=1.335..5033.194 rows=9999999 loops=1)
         Output: mydata, mynumber1, mynumber2
         Index Cond: (test.mynumber1 < 10000000)
         Buffers: shared read=110660
         I/O Timings: read=3545.630
 Query Identifier: -7984637647228499791
 Planning:
   Buffers: shared hit=59 read=23
   I/O Timings: read=7.484
 Planning Time: 63.294 ms
 Execution Time: 5773.535 ms
(15 rows)
Time: 6116.163 ms (00:06.116)

[root@ip-172-31-36-129 pg_ebpf]# ./get_pg_calls_durations.py -n -i 2 -f FileRead -p 11829 -x /usr/pgsql-14/bin/postgres
...
03:29:02: FileRead calls duration

     usecs_count         : count     distribution
         0 -> 1          : 0        |                                        |
         2 -> 3          : 0        |                                        |
         4 -> 7          : 100821   |****************************************|
         8 -> 15         : 2309     |                                        |
        16 -> 31         : 3768     |*                                       |
        32 -> 63         : 115      |                                        |
        64 -> 127        : 193      |                                        |
       128 -> 255        : 470      |                                        |
       256 -> 511        : 1350     |                                        |
       512 -> 1023       : 734      |                                        |
      1024 -> 2047       : 918      |                                        |
      2048 -> 4095       : 43       |                                        |
      4096 -> 8191       : 1        |                                        |
total: 110722
     usecs_time          : count     distribution
         0 -> 1          : 0        |                                        |
         2 -> 3          : 0        |                                        |
         4 -> 7          : 687903   |*********************                   |
         8 -> 15         : 23484    |                                        |
        16 -> 31         : 81331    |**                                      |
        32 -> 63         : 5206     |                                        |
        64 -> 127        : 18772    |                                        |
       128 -> 255        : 90812    |**                                      |
       256 -> 511        : 514217   |***************                         |
       512 -> 1023       : 533095   |****************                        |
      1024 -> 2047       : 1294741  |****************************************|
      2048 -> 4095       : 106673   |***                                     |
      4096 -> 8191       : 4598     |                                        |
total: 3360832
Detaching...
```

For more information, see the help:

```
# ./get_pg_calls_durations.py -h
usage: get_pg_calls_durations.py [-h] -x BINARY -f function [-p PID]
                                 [-i INTERVAL] [-z] [-n]

Recording postgres function call counts and timing

optional arguments:
  -h, --help            show this help message and exit
  -x BINARY, --binary BINARY
                        path to postgres binary
  -f function, --func function
                        postgres function to trace
  -p PID, --pid PID     trace this PID only
  -i INTERVAL, --interval INTERVAL
                        summary interval, seconds
  -z, --zero            zero history across display updates (default)
  -n, --no-zero         do not zero history across display updates

example:
    /get_pg_calls_durations.py -x /home/postgres/pgdirect/pg_installed/bin/postgres -i 3 -f RelationGetBufferForTuple
```
