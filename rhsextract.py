#!/usr/bin/env python
__author__ = 'paul'

# Purpose:
# Provide a command line tool to extract the max observed value given a specific time window
#

import argparse
import sys
import datetime

import rhsusage.tasks.config as cfg
from rhsusage.tasks.utils import dates_OK
from rhsusage.tasks.rrdtools import RRDdatabase

def rrd_info(rrd_db):

    print "\nEarliest Observation : %s" % rrd_db.rrd_boundary('first').strftime('%Y/%m/%d')
    print "Latest Observation   : %s\n" % rrd_db.rrd_boundary('last').strftime('%Y/%m/%d')


def rrd_extract(args, rrd_db):

    op_mode = {}
    op_mode['gluster'] = {'dedicated': 'nodes', 'shared': 'raw_used'}
    op_mode['ceph'] = {'dedicated': 'raw', 'shared': 'raw_used'}

    if args.lastndays:
        args.start_date = (datetime.datetime.today() - datetime.timedelta(days=int(args.lastndays))).strftime('%Y/%m/%d')
        args.end_date = datetime.datetime.today().strftime('%Y/%m/%d')

    # validate the start and end dates against each other and the rrd file
    if not dates_OK(args, rrd_db):
        sys.exit(12)

    # At this point the date range is usable with the rrd,
    # so go get the max value
    print 'everything looks ok for the query'
    peaks = rrd_db.get_max_values(start_date=args.start_date, end_date=args.end_date)
    peak_value = op_mode[cfg.storage_type][cfg.run_mode]
    print peaks[peak_value]

def main(args):

    rrd_db = RRDdatabase()
    if not rrd_db.db_usable:
        print "database provided is not usable"
        sys.exit(16)

    if args.info:
        rrd_info(rrd_db)
    else:
        rrd_extract(args, rrd_db)



if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", dest="debug", action="store_true",
                        default=False, help="run in debug mode")
    parser.add_argument("-s", "--start", dest="start_date", help="start date for the extract (yyyy/mm/dd)")
    parser.add_argument("-e", "--end", dest="end_date", help="end date for the extract(yyyy/mm/dd)")
    parser.add_argument("-l", "--last", dest="lastndays", help="go back this number of days from today")
    parser.add_argument("-i", "--info", dest="info", action="store_true",
                        default=False, help="show the first and last observation dates from the rrd file")
    args = parser.parse_args()

    # first make sure we have the required parameters for the rrdtool.fetch process to work with
    if args.info:
        pass
    else:
        if not ((args.start_date and args.end_date) or args.lastndays):
            print "Invalid date combination. Provide a start (-s) AND end (-e), OR the last n days value (-l)"
            sys.exit(12)

    cfg.init(args)

    main(args)

