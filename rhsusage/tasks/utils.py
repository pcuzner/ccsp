__author__ = 'paul'
import socket
from dateutil.parser import parse


def str2bool(value):
    return value.lower() in ['y','yes','1']

def host_2_ip(hostname):
    try:
        return socket.gethostbyname(hostname)
    except:
        return hostname

def dates_OK(args, rrd_db):

    try:
        s_date = parse(args.start_date)
        e_date = parse(args.end_date)

    except ValueError:
        print 'at least one of the date(s) provided is in an invalid format'
        return False

    # quick check that the date range is ok
    if e_date <= s_date:
        print 'The combination of end date and start date is not valid. Are they reversed?'
        return False

    # now check that the date range is meaningful to the rrd dataset
    if (s_date > rrd_db.rrd_boundary('last') or
        e_date < rrd_db.rrd_boundary('first')):
        print 'The date range provided is not available within the rrd file'
        return False

    # at this point the dates pass the initial 'sniff' test

    return True


