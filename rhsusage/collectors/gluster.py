__author__ = 'paul'

import json

from rhsusage.tasks import config as cfg
from rhsusage.tasks.cli import ShellCommand


class GlusterCollector(object):

    def __init__(self, rrd_db):
        self.rrd_db = rrd_db
        pass

    def update(self):
        cfg.log.info('calling get_data method (gstatus)')
        cluster_stats = self.get_data()
        if cluster_stats:
            self.rrd_db.update(cluster_stats)


    def get_data(self):

        cmd = ShellCommand('gstatus -o json', timeout=10)
        cmd.run()
        cfg.log.debug("gstatus command returned %d" % cmd.rc)

        if cmd.rc == 0:
            # ignore the timestamp that is normally returned by the gstatus command
            return json.loads(cmd.stdout[0][27:])
        else:
            return None
