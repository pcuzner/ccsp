__author__ = 'paul'

import threading
import time

from rhsusage.tasks import config as cfg
from rhsusage.collectors.ceph import CephCollector
from rhsusage.collectors.gluster import GlusterCollector


class Collector(threading.Thread):

    def __init__(self, rrd_db, storage_type):
        # self.rrd_db = rrd_db
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.shutdown = False

        if storage_type == 'ceph':
            self.collector = CephCollector(rrd_db)
        elif storage_type == 'gluster':
            self.collector = GlusterCollector(rrd_db)

        # self.run_collector = getattr(self, Collector.workers[storage_type])

    def run(self):
        cfg.syslog.debug("- Collector running with %d second interval" % cfg.interval_secs)
        cfg.log.debug("Collector running with %d second interval" % cfg.interval_secs)
        while not self.shutdown:
            time.sleep(cfg.interval_secs)
            self.collector.update()
