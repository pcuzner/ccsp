__author__ = 'paul'
import socket
from dateutil.parser import parse
import math


def str2bool(value):
    return value.lower() in ['y','yes','1']

def host_2_ip(hostname):
    try:
        return socket.gethostbyname(hostname)
    except:
        return hostname

def readable_bytes(bytes_in, scale, mode='bin'):

    valid_scale = ['KB', 'MB', 'GB', 'TB', 'PB',
                   'EB', 'ZB', 'YB']

    if scale.upper() not in valid_scale:
        return 0

    divisor_unit = 1024 if mode == 'bin' else 1000
    divisor = math.pow(divisor_unit, (valid_scale.index(scale) + 1))
    rounding = {'K': 0, 'M': 0, 'G': 0, 'T': 1, 'P': 2, 'Z': 2, 'Y': 2}
    precision = rounding[scale[0]]

    readable = bytes_in / divisor

    return '{0:.{1}f} {2}'.format(readable, precision, scale.upper())

def dates_OK(args, rrd_db):

    try:
        s_date = parse(args.start_date)
        e_date = parse(args.end_date)

    except ValueError:
        print 'Error: at least one of the date(s) provided is in an invalid format'
        return False

    # quick check that the date range is ok
    if e_date <= s_date:
        print 'Error: The combination of end date and start date is not valid. Are they reversed?'
        return False

    # now check that the date range is meaningful to the rrd dataset
    if (s_date > rrd_db.rrd_boundary('last') or
        e_date < rrd_db.rrd_boundary('first')):
        print 'Error: the date range provided is not available within the rrd file'
        return False

    # at this point the dates pass the initial 'sniff' test

    return True


