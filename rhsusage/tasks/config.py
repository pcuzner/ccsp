__author__ = 'paul'

import logging
import logging.handlers
import os
import rrdtool

from ConfigParser import SafeConfigParser


def init(run_time_args):
    parser = SafeConfigParser()
    parser.read('/etc/rhs-usage.conf')

    global log_file
    global log_level
    global storage_type
    global run_mode
    global log
    global syslog
    global interval_secs
    global web_server
    global web_server_port
    global sample_interval
    global rrd_db
    global web_root

    # set defaults
    log_file = '/var/log/rhs-usage.log'
    log_level = 'debug'
    rrd_db = '/var/ccsp/rhs-usage.rrd'
    storage_type = 'gluster'
    run_mode = 'shared'
    sample_interval = 240
    web_server = 'n'
    web_server_port = 8080
    web_root = '/var/www/ccsp'

    defaults = ['log_file', 'log_level', 'rrd_db', 'storage_type', 'run_mode', 'web_server', 'web_server_port',
                'web_root', 'sample_interval']

    log = logging.getLogger('rhs-usage-log')
    syslog = logging.getLogger('syslog')

    # setup syslog first so we can log immediately, for any startup or config errors
    syslog.setLevel(logging.DEBUG) if run_time_args.debug else syslog.setLevel(logging.INFO)
    syslog_handler = logging.handlers.SysLogHandler(address='/dev/log')
    syslog.addHandler(syslog_handler)

    # Process the config file, overriding any of the defaults with the value
    # from the .conf file
    for section_name in parser.sections():
        for var_name, var_value in parser.items(section_name):

            if var_value.isdigit():
                var_value = int(var_value)

            globals()[var_name] = var_value

            if var_name in defaults:
                defaults.remove(var_name)

    if defaults and run_time_args.debug:
        for default_var in defaults:
            syslog.debug("[DEBUG] Default value used for '%s' - %s " % (default_var, eval(default_var)))

    # if the rrd file exists use the existing step setting not the supplied value from the
    # configuration file
    if os.path.exists(rrd_db):
        interval_secs = rrdtool.info(rrd_db)['step']
        syslog.info('Data gathering interval set by existing rrd file to %d secs - config file ignored'
                    % interval_secs)
    else:
        interval_secs = sample_interval * 60

    # set up application logging
    log.setLevel(logging.DEBUG) if run_time_args.debug else log.setLevel(logging.getLevelName(log_level.upper()))
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)
    log.addHandler(handler)
