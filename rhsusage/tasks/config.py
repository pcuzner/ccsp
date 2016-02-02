__author__ = 'paul'

import logging
import logging.handlers
import os
import sys
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
    global points_to_summarize
    global web_server
    global web_server_port
    global sample_interval
    global rrd_db
    global web_root
    global interactive
    global caller
    global web_enabled
    global days_to_keep

    # set defaults
    log_file = '/var/log/rhs-usage.log'
    log_level = 'debug'
    rrd_db = '/var/ccsp/rhs-usage.rrd'
    storage_type = 'gluster'
    run_mode = 'shared'

    # default to : 60 minute samples, that will be summarised every 4 hours retained for 180 days
    sample_interval = 60
    points_to_summarize = 4
    days_to_keep = 180

    web_server = 'y'
    web_server_port = 8080
    web_root = '/var/www/ccsp'

    defaults = ['log_file', 'log_level', 'rrd_db', 'storage_type', 'run_mode', 'web_server', 'web_server_port',
                'web_root', 'sample_interval', 'points_to_summarize', 'days_to_keep']

    # True = interactive shell, False = background service
    interactive = sys.stdout.isatty()
    caller = os.path.basename(sys.argv[0])

    log = logging.getLogger('rhs-usage-log')
    syslog = logging.getLogger('syslog')

    # setup syslog first so we can log immediately, for any startup or config errors
    syslog.setLevel(logging.DEBUG) if run_time_args.debug else syslog.setLevel(logging.INFO)
    syslog_format = logging.Formatter("%(message)s")

    if interactive:
        syslog_handler = logging.StreamHandler(sys.stdout)
    else:
        syslog_handler = logging.handlers.SysLogHandler(address='/dev/log')

    syslog_handler.setFormatter(syslog_format)
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

    web_enabled = web_server.upper() in ['Y', 'YES']

    # if the rrd file exists use the existing step setting not the supplied value from the
    # configuration file
    if os.path.exists(rrd_db):
        interval_secs = rrdtool.info(rrd_db)['step']
        syslog.debug('Data gathering interval set by existing rrd file to %d secs - config file ignored'
                    % interval_secs)
    else:
        interval_secs = sample_interval * 60

    # set up application logging
    log.setLevel(logging.DEBUG) if run_time_args.debug else log.setLevel(logging.getLevelName(log_level.upper()))

    if interactive:
        formatter = logging.Formatter("%(message)s")
        handler = logging.StreamHandler(sys.stdout)
    else:
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler = logging.FileHandler(log_file)

    handler.setFormatter(formatter)
    log.addHandler(handler)
