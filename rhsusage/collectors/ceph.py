__author__ = 'paul'

import json

from rhsusage.tasks import config as cfg
from rhsusage.tasks.cli import ShellCommand
from rhsusage.tasks.utils import host_2_ip

class CephCollector(object):

    def __init__(self, rrd_db):
        self.rrd_db = rrd_db
        pass

    def update(self):
        cfg.log.info('getting ceph stats using various ceph commands')
        cluster_stats = self.get_data()
        self.rrd_db.update(cluster_stats)

    def get_data(self):
        # use ceph commands to get the data we need - or could
        # opt to parse ceph.conf with the configparser module?
        ceph_data = {}
        ceph_data['usable_capacity'] = 0
        ceph_data['nodes_active'] = 0
        ceph_data['raw_capacity'] = 0
        ceph_data['raw_used'] = 0
        ceph_data['used_capacity'] = 0
        ceph_nodes = set()

        # use ceph -s to get information about the monitors
        cmd = ShellCommand('ceph -s -f json')
        cmd.run()
        cfg.log.debug("ceph -s command completed rc=%d" % cmd.rc)
        if cmd.rc == 0:

            js = json.loads(cmd.stdout[1])

            # extract the mon information from the ceph output
            for mon in js['monmap']['mons']:
                # node info will look like this - 192.168.122.111:6789/0
                # and we only want the IP address
                ceph_nodes.add(mon['addr'].split(':')[0])

            # add the osd nodes to the ceph_nodes list
            cmd = ShellCommand('ceph osd tree -f json')
            cmd.run()
            cfg.log.debug("ceph osd tree command completed rc=%d" % cmd.rc)
            if cmd.rc == 0:
                js = json.loads(cmd.stdout[1])
                for osd_element in js['nodes']:
                    if osd_element['type'] == 'host':
                        hostname = osd_element['name']
                        if not hostname[0].isdigit():
                            hostname = host_2_ip(hostname)
                        ceph_nodes.add(hostname)

            ceph_data['node_count'] = len(ceph_nodes)

            cmd = ShellCommand('ceph df -f json')
            cmd.run()
            cfg.log.debug("ceph df command completed rc=%d" % cmd.rc)
            if cmd.rc == 0:
                js = json.loads(cmd.stdout[1])
                ceph_data['raw_capacity'] = js['stats']['total_bytes']
                ceph_data['raw_used'] = js['stats']['total_used_bytes']

                # calculate the used bytes, which is the logical view of space
                # space consumption (i.e. as viewed from the client)
                for pool in js['pools']:
                    ceph_data['used_capacity'] += pool['stats']['bytes_used']

        return ceph_data
