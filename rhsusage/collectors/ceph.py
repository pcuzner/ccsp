__author__ = 'paul'

from rhsusage.tasks import config as cfg


class CephCollector(object):

    def __init__(self, rrd_db):
        self.rrd_db = rrd_db
        pass

    def update(self):
        cfg.log.info('get ceph stats')
        cluster_stats = self.get_data()
        self.rrd_db.update(cluster_stats)

    def get_data(self):
        # use ceph df, then extract the raw/usable/used
        # Need to get a total node count for ceph? parse ceph.conf?
        pass

    # def _update_rrd(self):
    #     cfg.log.debug('updating rrd database')
    #     # rc = rrdtool.update(self.rrd_db, 'N:%s:%s' %(metric1, metric2));
    #     pass

    # def _refresh_graph(self):
    #     cfg.log.debug('refreshing rrd graph')