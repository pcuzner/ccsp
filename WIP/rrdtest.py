__author__ = 'paul'

import rrdtool
import math

# get list of tuples for the maximums
# can use --start <time> to grab only the observations in the last reporting period - default is now - 1d
# tuple element 0 is
#               1 tuple of field names
#               2 is list of tuples
maximums = rrdtool.fetch('/home/paul/Downloads/rhs-usage.rrd', 'MAX')

max_used = 0
ptr = maximums[1].index('used_capacity')

for reading in maximums[2]:
    if reading[ptr]:
        if reading[ptr] > max_used:
            max_used = reading[ptr]

# round to the nearest GB
print math.ceil(max_used / float(1024**3))


