#!/usr/bin/python

__author__ = 'paul'

# rpm dependencies
# + python-configparser - used to parse the .conf file in config.py
# + rrdtool-python

import argparse
import threading
import signal
import sys
import os

from rhsusage.tasks import config as cfg

#
from rhsusage.tasks.rrdtools import RRDdatabase
from rhsusage.tasks.web import WebFrontEnd
from rhsusage.tasks.data_collectors import Collector


def pre_reqs_ok(cluster_type):

    pre_req = {"gluster": "_gluster_checks",
               "ceph": "_ceph_checks"}

    this_module = sys.modules[__name__]
    check_pre_reqs = getattr(this_module, pre_req[cluster_type], None)
    return check_pre_reqs()


def _gluster_checks():
    try:
        __import__('imp').find_module('gstatus')
        return True
    except ImportError:
        cfg.syslog.error("rhs-usage needs the gstatus rpm installed.")
        return False


def _ceph_checks():
    conf_available = os.path.exists('/etc/ceph/ceph.conf')
    if not conf_available:
        cfg.syslog.error("rhs-usage is set to monitor ceph, but a local ceph.conf is not available")
    return conf_available


def shutdown(signal, frame):
    cfg.log.info("Shutting down all threads")
    cfg.syslog.info("Shutting down all threads")
    for thread in threading.enumerate():
        thread.shutdown = True

    sys.exit(0)


def start_data_collection():

    rrd_db = RRDdatabase(cfg.web_server, cfg.interval_secs)
    if not rrd_db.db_usable:
        cfg.syslog.error("RRD database provided (%s) is not usable by rrd" % cfg.rrd_db)
        sys.exit(12)

    thread_list = []
    get_capacity_data = Collector(rrd_db, cfg.storage_type)

    cfg.syslog.info("Starting data collector")
    get_capacity_data.start()
    thread_list.append(get_capacity_data)

    if cfg.web_server in ['y', 'Y', 'Yes', 'YES']:
        cfg.syslog.info("Starting passive web interface")
        web_server = WebFrontEnd(cfg.web_root)
        web_server.start()
        thread_list.append(web_server)

    # threading.join starves the signal handler when you don't use
    # a timeout - consequently, the loop here uses a time out to make
    # sure we catch the stop request from upstart or systemd
    # ref: http://stackoverflow.com/questions/631441/interruptible-thread-join-in-python
    while threading.activeCount > 0:
        for thread in thread_list:
            thread.join(1)


if __name__ == "__main__":

    # set up signal handles to catch sigterm to provide a graceful shutdown
    signal.signal(signal.SIGTERM, shutdown)
    signal.siginterrupt(signal.SIGTERM, False)

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", dest="debug", action="store_true", default=False, help="run in debug mode")
    args = parser.parse_args()

    cfg.init(args)

    # Before we start make sure we satisfy any pre-req checks
    if not pre_reqs_ok(cfg.storage_type):
        cfg.syslog.error('Pre-requisites for rhs-usage are not available ... Aborting')
        sys.exit(16)

    start_data_collection()
