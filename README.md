Introduction
============

eBPF toolkit to be used with PostgreSQL.  
Intend is not to be used in production but for study only.

It currently contains:

 * ``get_pg_calls_durations.py``: python script to get functions calls duration (histogram)
 * ``c_src/get_pg_calls_durations.c``: the c file associated to ``get_pg_calls_durations.py``

Example
========
- Display the duration of RelationGetBufferForTuple() calls and display at a 3 seconds interval.
```
# ./get_pg_calls_durations.py -x /home/postgres/pgdirect/pg_installed/bin/postgres -i 3 -f RelationGetBufferForTuple

13:32:49: RelationGetBufferForTuple calls duration                                                                                                                                                                                                                           [9/1953]

     usecs               : count     distribution
         0 -> 1          : 0        |                                        |
         2 -> 3          : 0        |                                        |
         4 -> 7          : 346754   |****************************************|
         8 -> 15         : 869      |                                        |
        16 -> 31         : 2059     |                                        |
        32 -> 63         : 5        |                                        |
        64 -> 127        : 1        |                                        |
       128 -> 255        : 1        |                                        |
       256 -> 511        : 0        |                                        |
       512 -> 1023       : 1        |                                        |

13:32:52: RelationGetBufferForTuple calls duration

     usecs               : count     distribution
         0 -> 1          : 0        |                                        |
         2 -> 3          : 0        |                                        |
         4 -> 7          : 348035   |****************************************|
         8 -> 15         : 861      |                                        |
        16 -> 31         : 2091     |                                        |
        32 -> 63         : 8        |                                        |
        64 -> 127        : 1        |                                        |
```
It's also possible to filter on a pid, see the help:

```
# ./get_pg_calls_durations.py -h
usage: get_pg_calls_durations.py [-h] -x BINARY -f function [-p PID] [-i INTERVAL]

Recording postgres function calls duration

options:
  -h, --help            show this help message and exit
  -x BINARY, --binary BINARY
                        path to postgres binary
  -f function, --func function
                        postgres function to trace
  -p PID, --pid PID     trace this PID only
  -i INTERVAL, --interval INTERVAL
                        summary interval, seconds

example:
    /get_pg_calls_durations.py -x /home/postgres/pgdirect/pg_installed/bin/postgres -i 3 -f RelationGetBufferForTuple
```
