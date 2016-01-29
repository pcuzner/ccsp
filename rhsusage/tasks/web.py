__author__ = 'paul'

import SimpleHTTPServer
import BaseHTTPServer
import threading
import os
import math
import datetime

from rhsusage.tasks import config as cfg


class WebHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def translate_path(self, path):

        cfg.log.debug("web request for %s" % path)
        path = "%s%s" %(self.server.rootdir, path)
        cfg.log.debug("path translated to %s" % path)
        return path

    def log_message(self, format, *args):
        cfg.log.debug("%s", args)


class WebFrontEnd(threading.Thread):

    def __init__(self, webroot):
        threading.Thread.__init__(self)
        self.server = BaseHTTPServer.HTTPServer(('',cfg.web_server_port), WebHandler)
        self.server.rootdir = webroot
        self.setDaemon(True)
        self.shutdown = False
        update_mode_js(webroot)

    def run(self):
        cfg.log.info("Starting passive web interface")
        self.server.serve_forever()


def update_mode_js(web_root):
    # update the javascript so on page load the run time parameters
    # can be reflected in the web page
    with open(os.path.join(web_root, 'js/update_mode.js'), 'w') as js:
        js.write("// update_mode.js updated by rhsusage/tasks/web.py on %s\n" %
                 datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        js.write("function update_mode() {\n")
        js.write("document.getElementById('clusterType').innerHTML='" + cfg.storage_type.title() +"';\n")
        js.write("document.getElementById('accntMode').innerHTML='" + cfg.run_mode.title() +"';\n")
        js.write("}\n")
    cfg.log.debug("Updated update_mode.js with runtime settings")

def bold_text(text):
    return "<strong>" + text + "</strong>"

def update_details_js(web_root, max_values):

    # 1073741824 = 1GB expressed in bytes
    max_raw = math.ceil(max_values['raw'] / float(1024**3)) if max_values['raw'] > 1073741824 else 0
    max_raw_used = math.ceil(max_values['raw_used'] / float(1024**3)) if max_values['raw_used'] > 1073741824 else 0
    max_usable = math.ceil(max_values['usable'] / float(1024**3)) if max_values['usable'] > 1073741824 else 0
    max_used = math.ceil(max_values['used'] / float(1024**3)) if max_values['used'] > 1073741824 else 0

    # Define a nodes, usable and raw strings
    # check the cfg.run_mode
    # if set to shared, use set the max_usable string with <strong>
    # if dedicated for ceph emphasize the max_raw, for gluster emphasize max nodes
    max_nodes_str = str(max_values['nodes'])
    max_raw_str = str(int(max_raw))
    max_raw_used_str = str(int(max_raw_used))
    max_usable_str = str(int(max_usable))
    max_used_str = str(int(max_used))

    if cfg.run_mode == "dedicated":
        if cfg.storage_type == "gluster":
            max_nodes_str = bold_text(max_nodes_str)
        else:
            max_raw_str = bold_text(max_raw_str)
    else:
        max_raw_used_str = bold_text(max_raw_used_str)

    with open(os.path.join(web_root, 'js/update_details.js'), 'w') as js:
        js.write("// update_details.js updated by rhsusage/tasks/web.py on %s\n" %
                 datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        js.write("function update_details() {\n")
        js.write("document.getElementById('maxNodes').innerHTML='" + max_nodes_str + "';\n")
        js.write("document.getElementById('maxRaw').innerHTML='" + max_raw_str + " GB';\n")
        js.write("document.getElementById('maxRawUsed').innerHTML='" + max_raw_used_str + " GB';\n")
        js.write("document.getElementById('maxUsable').innerHTML='" + max_usable_str + " GB';\n")
        js.write("document.getElementById('maxUsed').innerHTML='" + max_used_str + " GB';\n")
        if cfg.storage_type == "ceph":
            js.write("document.getElementById('usable').style.display = 'none';\n")
        js.write("}\n")

    cfg.log.debug("Updated update_details.js with current maximums")
