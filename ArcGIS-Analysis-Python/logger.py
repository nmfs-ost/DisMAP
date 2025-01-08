# -*- coding: utf-8 -*-
# https://community.esri.com/t5/python-questions/use-of-logging-module-in-python-toolbox/td-p/1248620
import os
import sys
import arcpy
import time
import glob

import logging
import logging.handlers


LOG_FILE = os.path.join(arcpy.env.scratchFolder, 'logs', 'fs', 'fs_log_%i.txt' % os.getpid())


# Log handler that forwards messages to ArcGIS
class ArcGisHandler(logging.Handler):
    try:
        #get_ipython()
        is_run_from_ipython = True
    except NameError:
        is_run_from_ipython = False

    is_run_from_cmd_line = sys.stdin is not None and sys.stdin.isatty()

    def emit(self, record):
        if not self.is_run_from_cmd_line and not self.is_run_from_ipython:
            arcpy.AddMessage(self.format(record))


# Set up logging
def get(log_name):
    # Compute the full path for this process and make sure the directory exists
    if not os.path.exists(os.path.dirname(LOG_FILE)):
        os.makedirs(os.path.dirname(LOG_FILE))

    # Clean up old log files
    if not os.path.exists(LOG_FILE):
        for file in glob.glob(os.path.join(arcpy.env.scratchFolder, 'logs', 'fs', 'fs_log_*.txt')):
            if time.time() - os.path.getmtime(file) > 2 * 60 * 60 * 24:
                try:
                    os.remove(file)
                except:
                    pass


    logger = logging.getLogger(log_name)
    logger.disabled = False
    logger.setLevel(logging.DEBUG)

    if len(logger.handlers) == 0:
        # File handler for detailed tracing
        try:
            formatter1 = logging.Formatter('%(asctime)s -  %(levelname)s - %(module)s - %(message)s')
            fh1 = logging.FileHandler(LOG_FILE)
            fh1.setFormatter(formatter1)
            fh1.setLevel(logging.DEBUG)
            logger.addHandler(fh1)
        except:
            pass
        # Standard out handler
        try:
            formatter2 = logging.Formatter('%(levelname)s - %(message)s')
            fh2 = logging.StreamHandler(sys.stdout)
            fh2.setFormatter(formatter2)
            fh2.setLevel(logging.INFO)
            logger.addHandler(fh2)
        except:
            pass
        # Custom handler to send messages to ArcGIS
        try:
            if sys.version_info.major > 2:
                formatter4 = logging.Formatter('%(asctime)s - %(message)s', '%H:%M:%S')
                fh4 = ArcGisHandler()
                fh4.setFormatter(formatter4)
                fh4.setLevel(logging.INFO)
                logger.addHandler(fh4)
        except:
            pass

    return logger