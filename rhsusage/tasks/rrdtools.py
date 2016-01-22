__author__ = 'paul'

import os
import rrdtool
import platform
from operator import itemgetter


from rhsusage.tasks import config as cfg
from rhsusage.tasks.utils import str2bool
from rhsusage.tasks.web import update_details_js


class RRDdatabase(object):

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
                            'DS:raw_used:GAUGE:%s:U:U' % overdue_secs,
                            'DS:usable_capacity:GAUGE:%s:U:U' % overdue_secs,
                            'DS:used_capacity:GAUGE:%s:U:U' % overdue_secs,
                            'RRA:AVERAGE:0.5:4:256',
                            'RRA:MAX:0.5:4:256')

    def update(self, stats):
        # use a dict to update the rrd
        cfg.log.debug('updating rrd database with the following values;')

        # specific pre-processing for the data coming from a gstatus command
        if 'glfs_version' in stats:
            # Workaround - account for gstatus not providing a raw_used variable
            stats['raw_used'] = stats['used_capacity']
            # now we look at each volumes used capacity to derive the logical used capacity
            # (should be fix in gstatus really!)
            stats['used_capacity'] = 0
            for vol in stats['volume_summary']:
                stats['used_capacity'] += vol['used_capacity']


        cfg.log.debug("node_count = %s, nodes_active = %s, raw_capacity = %s, raw_used = %s,"
                      " usable_capacity = %s, used_capacity = %s"
                      % (stats['node_count'], stats['nodes_active'], stats['raw_capacity'],
                         stats['raw_used'], stats['usable_capacity'], stats['used_capacity']))

        rc = rrdtool.update(str(self.filename),
                            'N:%s:%s:%s:%s:%s:%s' % (stats['node_count'],
                                                  stats['nodes_active'],
                                                  stats['raw_capacity'],
                                                  stats['raw_used'],
                                                  stats['usable_capacity'],
                                                  stats['used_capacity']))
        self.ctr += 1
        if self.web_enabled and self.ctr == 2:
            self.create_graphs()
            max_values = self.get_max_values()
            update_details_js(cfg.web_root, max_values)
            self.ctr = 0

    def _ceph_options(self):
        return [
                'DEF:used=' + self.filename + ':used_capacity:MAX',
                'DEF:raw=' + self.filename + ':raw_capacity:MAX',
                'DEF:raw_used=' + self.filename + ':raw_used:MAX',
                'LINE2:used#0000ff:Logical Capacity Used',
                'LINE2:raw#cc0000:Physical Raw Capacity Installed',
                'LINE2:raw_used#f9931a:Physical Raw Capacity Used']


    def _gluster_options(self):
        return [
                'DEF:used=' + self.filename + ':used_capacity:MAX',
                'DEF:usable=' + self.filename + ':usable_capacity:MAX',
                'LINE2:used#0000ff:GB Used',
                'LINE2:usable#cc0000:GB Usable']

    def _create_capacity_graph(self):
        graph_filename = os.path.join(cfg.web_root,'images/usage_chart.png')
        cfg.log.debug("Created capacity graph - %s" % graph_filename)

        # setup references to specific function calls
        graph_detail = {}
        graph_detail['ceph'] = self._ceph_options
        graph_detail['gluster'] = self._ceph_options

        graph_options = [str(graph_filename), '--start', 'now-4h', '--step', '600', '--watermark', 'Red Hat Storage',
                         '--imgformat', 'PNG', '--disable-rrdtool-tag', '--width', '550', '--height', '350', '--title',
                         '%s Capacity Utilisation' % cfg.storage_type.title(), '--vertical-label', 'Disk Capacity',
                         '--lower-limit', '0', '--base', '1024', graph_detail[cfg.storage_type]()]

        # Later versions of rrdtool.graph support a null border. However, it's not listed in the __doc__ for
        # graph, so here I just check for the version of OS and add the additional options if supported
        # platform.dist() examples: ('redhat', '6.6', 'Santiago') or ('redhat', '7.1', 'Maipo')
        if platform.dist()[1].startswith('7'):
            graph_options.append('--border')
            graph_options.append('0')

        rc = rrdtool.graph(*graph_options)


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

        peak['nodes'] = int(self._find_max(maximums[2], 0))
        peak['raw'] = self._find_max(maximums[2], 2)
        peak['raw_used'] = self._find_max(maximums[2], 3)
        peak['usable'] = self._find_max(maximums[2], 4)
        peak['used'] = self._find_max(maximums[2], 5)
        return peak

