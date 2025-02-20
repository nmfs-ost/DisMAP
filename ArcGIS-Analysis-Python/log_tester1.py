# -*- coding: utf-8 -*-
import logging
import logging.handlers

import arcpy

class ArcPyLogHandler(logging.handlers.RotatingFileHandler):
    """
    Custom logging class that bounces messages to the arcpy tool window as well
    as reflecting back to the file.
    """

    def emit(self, record):
        """
        Write the log message
        """
        try:
            msg = record.msg.format(record.args)
        except:
            msg = record.msg

        if record.levelno >= logging.ERROR:
            arcpy.AddError(msg)
        elif record.levelno >= logging.WARNING:
            arcpy.AddWarning(msg)
        elif record.levelno >= logging.INFO:
            arcpy.AddMessage(msg)

        super(ArcPyLogHandler, self).emit(record)

def main():

    logger = logging.getLogger("LoggerName")
    logger.handlers = []
    handler = ArcPyLogHandler(
                                "output_log.log",
                                maxBytes=1024 * 1024 * 2, #2MB log files
                                backupCount=10
                              )
    logger.addHandler(handler)
    formatter = logging.Formatter("%(levelname)-8s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    #logger.setLevel(logging.DEBUG)

    logger.debug("A debug message")
    logger.info("An info message")
    logger.warning("A warning message")
    logger.error("An error message")
    logger.critical("A critical error message")

    try:
        1 / 0
    except Exception as e:
        logger.exception(e)


if __name__ == '__main__':
    main()

##    errorLog = r'd:\log.txt'
##    filePath = errorLog
##    try:
##        with open(errorLog,'a') as errorMsg:
##            errorMsg.write("%s,%s\n" % (errorLog,filePath))
##    except RuntimeError:
##        print("Unable to log")
##        print RuntimeError.message