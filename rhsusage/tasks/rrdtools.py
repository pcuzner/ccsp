__author__ = 'paul'

import os
import rrdtool
from operator import itemgetter


from rhsusage.tasks import config as cfg
from rhsusage.tasks.utils import str2bool
from rhsusage.tasks.web import update_details_js

class RRDdatabase(object):

    # db_type = {'ceph': '_create_ceph_rrd',
    #            'gluster': '_create_gluster_rrd'}

    # data_source = ['node_count', 'nodes_active', 'raw_capacity', 'usable_capacity', 'used_capacity']
    # gluster_data_sources = []

    def __init__(self, web_server, interval_secs):
        cfg.log.debug("Using rrd filename of '%s'" % cfg.rrd_db)
        self.fields = ['node_count', 'nodes_active', 'raw_capacity', 'usable_capacity', 'used_capacity']
        self.filename = cfg.rrd_db
        self.db_usable = True
        self.ctr = 0
        self.interval_secs = interval_secs
        self.web_enabled = str2bool(web_server)

        if os.path.exists(cfg.rrd_db):
            try:
                info = rrdtool.info(cfg.rrd_db)
            except:
                self.db_usable = False
                pass
        else:
            cfg.syslog.debug("[DEBUG] Requested RRD file ('%s') does not exist, creating it" % cfg.rrd_db)
            self.create_rrd_db()

    def create_rrd_db(self):
        cfg.log.debug("Creating generic rrd database %s" % self.filename)

        overdue_secs = self.interval_secs + 10

        rc = rrdtool.create(str(self.filename),
                            '--step', str(cfg.interval_secs),
                            '--start', '0',
                            'DS:node_count:GAUGE:%s:U:U' % overdue_secs,
                            'DS:nodes_active:GAUGE:%s:U:U' % overdue_secs,
                            'DS:raw_capacity:GAUGE:%s:U:U' % overdue_secs,
                            'DS:usable_capacity:GAUGE:%s:U:U' % overdue_secs,
                            'DS:used_capacity:GAUGE:%s:U:U' % overdue_secs,
                            'RRA:AVERAGE:0.5:4:256',
                            'RRA:MAX:0.5:4:256')

    def update(self, stats):
        # use a dict to update the rrd
        cfg.log.debug('updating rrd database with the following values;')
        cfg.log.debug('node_count = %s, nodes_active = %s, raw_capacity = %s, usable_capacity = %s, used_capacity = %s'
                      % (stats['node_count'], stats['nodes_active'], stats['raw_capacity'],
                         stats['usable_capacity'], stats['used_capacity']))

        rc = rrdtool.update(str(self.filename),
                            'N:%s:%s:%s:%s:%s' % (stats['node_count'],
                                                  stats['nodes_active'],
                                                  stats['raw_capacity'],
                                                  stats['usable_capacity'],
                                                  stats['used_capacity']))
        self.ctr += 1
        if self.web_enabled and self.ctr == 2:
            self.create_graphs()
            max_values = self.get_max_values()
            update_details_js(cfg.web_root, max_values)
            self.ctr = 0

    def _create_capacity_graph(self):
        graph_filename = os.path.join(cfg.web_root,'images/usage_chart.png')
        cfg.log.debug("Created capacity graph - %s" % graph_filename)

        rrdtool.graph(str(graph_filename),'--start','now-4h','--step','600',
                      '--border','0','--watermark','Red Hat Storage','--imgformat','PNG','--disable-rrdtool-tag',
                      '--width','550','--height','350','--title','Capacity Utilisation',
                      '--vertical-label','Disk Capacity',
                      '--lower-limit','0',
                      '--base','1024',
                      'DEF:used=' + self.filename +':used_capacity:AVERAGE',
                      'DEF:usable=' + self.filename +':usable_capacity:MAX',
                      'LINE2:used#0000ff:GB Used',
                      'LINE2:usable#cc0000:GB Usable')

    def create_graphs(self):
        cfg.log.debug('creating rrd graph(s)')
        self._create_capacity_graph()

    def _find_max(self,data_series, ptr):

        m = max(data_series,key=itemgetter(4))[ptr]

        # its possible for early iterations to encounter a None value, so if we see that
        # we return 0
        return m if m else 0

    def get_max_values(self):

        maximums = rrdtool.fetch(str(self.filename), 'MAX')

        peak = {}

        peak['nodes'] = self._find_max(maximums[2], 0)
        peak['raw'] = self._find_max(maximums[2], 2)
        peak['usable'] = self._find_max(maximums[2], 3)
        peak['used'] = self._find_max(maximums[2], 4)
        return peak


