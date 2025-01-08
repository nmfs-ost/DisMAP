# -*- coding: utf-8 -*-
# https://joelmccune.com/arcpy-python-logger/
__title__ = 'arcpy-logging'
__version__ = '1.0.0'
__author__ = 'Joel McCune (https://github.com/knu2xs)'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2022 by Joel McCune (https://github.com/knu2xs)'

import importlib
import logging
from pathlib import Path
from typing import Union, Optional

__all__ = ['get_logger']

if importlib.util.find_spec("arcpy") is None:
    has_arcpy = False
else:
    has_arcpy = True
    import arcpy
    __all__ = __all__ + ['ArcpyHandler']

if importlib.util.find_spec("pandas") is None:
    has_pandas = False
else:
    has_pandas = True
    import pandas as pd
    __all__ = __all__ + ['log_pandas_df']


class ArcpyHandler(logging.Handler):
    """
    Logging message handler capable of routing logging through ArcPy ``AddMessage``, ``AddWarning`` and ``AddError``
    methods.
    """

    # since everything goes through ArcPy methods, we do not need a message line terminator
    terminator = ''

    def __init__(self, level: Union[int, str] = 10):

        # throw logical error if arcpy not available
        if not has_arcpy:
            raise EnvironmentError('The ArcPy handler requires an environment with ArcPy, a Python environment with '
                                   'ArcGIS Pro or ArcGIS Enterprise.')

        # call the parent to cover rest of any potential setup
        super().__init__(level=level)

    def emit(self, record: logging.LogRecord) -> None:
        """
        Args:
            record: Record containing all information needed to emit a new logging event.
        .. note::
            This method should not be called directly, but rather enables the ``Logger`` methods to
            be able to use this handler correctly.
        """
        # run through the formatter to honor logging formatter settings
        msg = self.format(record)

        # route anything NOTSET (0), DEBUG (10) or INFO (20) through AddMessage
        if record.levelno <= 20:
            arcpy.AddMessage(msg)

        # route all WARN (30) messages through AddWarning
        elif record.levelno == 30:
            arcpy.AddWarning(msg)

        # everything else; ERROR (40), FATAL (50) and CRITICAL (50), route through AddError
        else:
            arcpy.AddError(msg)


# setup logging
def get_logger(
               logger_name: Optional[str] = 'arcpy-logger',
               log_level: Optional[Union[str, int]] = 'INFO',
               logfile_pth: Union[Path, str] = None, propagate: bool = False
              ) -> logging.Logger:
    """
    Get Python :class:`Logger<logging.Logger>` configured to provide stream, file or, if available, ArcPy output.
    The way the method is set up, logging will be routed through ArcPy messaging using :class:`ArcpyHandler` if
    ArcPy is available. If ArcPy is *not* available, messages will be sent to the console using a
    :class:`StreamHandler<logging.StreamHandler>`. Next, if the ``logfile_path`` is provided, log messages will also
    be written to the provided path to a logfile using a :class:`FileHandler<logging.FileHandler>`.
    Valid ``log_level`` inputs include:
    * ``DEBUG`` - Detailed information, typically of interest only when diagnosing problems.
    * ``INFO`` - Confirmation that things are working as expected.
    * ``WARNING`` or ``WARN`` -  An indication that something unexpected happened, or indicative of some problem in the
      near future (e.g. ‘disk space low’). The software is still working as expected.
    * ``ERROR`` - Due to a more serious problem, the software has not been able to perform some function.
    * ``CRITICAL`` - A serious error, indicating that the program itself may be unable to continue running.
    Args:
        logger_name: Name for logger. Default is 'arcpy-logger'.
        log_level: Logging level to use. Default is `'INFO'`.
        logfile_pth: Where to save the logfile.log if file output is desired.
        propagate: Whether to propagate message up to any parent loggers. Defaults to ``False`` to avoid repeated
          messages to ArcPy.
    """
    # ensure valid logging level
    log_str_lst = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'WARN', 'FATAL']
    log_int_lst = [0, 10, 20, 30, 40, 50]

    if not isinstance(log_level, (str, int)):
        raise ValueError('You must define a specific logging level for log_level as a string or integer.')
    elif isinstance(log_level, str) and log_level not in log_str_lst:
        raise ValueError(f'The log_level must be one of {log_str_lst}. You provided "{log_level}".')
    elif isinstance(log_level, int) and log_level not in log_int_lst:
        raise ValueError(f'If providing an integer for log_level, it must be one of the following, {log_int_lst}.')

    # get a logger object instance
    logger = logging.getLogger(logger_name)

    # set propagation
    logger.propagate = propagate

    # set logging level
    if isinstance(log_level, str):
        log_level = getattr(logging, log_level)
    logger.setLevel(log_level)

    # configure formatting
    log_frmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # if in an environment with ArcPy, add handler to bubble logging up to ArcGIS through ArcPy
    if has_arcpy:
        ah = ArcpyHandler()
        ah.setFormatter(log_frmt)
        logger.addHandler(ah)

    # create handler to console if arcpy is not providing status
    else:
        ch = logging.StreamHandler()
        ch.setFormatter(log_frmt)
        logger.addHandler(ch)

    # if a path for the logfile is provided, log results to the file
    if logfile_pth is not None:

        # ensure the full path exists
        if not logfile_pth.parent.exists():
            logfile_pth.parent.mkdir(parents=True)

        # create and add the file handler
        fh = logging.FileHandler(str(logfile_pth))
        fh.setFormatter(log_frmt)
        logger.addHandler(fh)

    # keep logging from bubbling up - keep messages just in these handlers
    logger.propagate = False

    return logger