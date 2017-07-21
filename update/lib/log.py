#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os, string
import logging
import logging.config
import logging.handlers

# Color escape string
COLOR_RED = '\033[1;31m'
COLOR_GREEN = '\033[1;32m'
COLOR_YELLOW = '\033[1;33m'
COLOR_BLUE = '\033[1;34m'
COLOR_PURPLE = '\033[1;35m'
COLOR_CYAN = '\033[1;36m'
COLOR_GRAY = '\033[1;37m'
COLOR_WHITE = '\033[1;38m'
COLOR_RESET = '\033[1;0m'

# LOG_COLORS = {
#     'DEBUG': '%s',
#     'INFO': COLOR_GREEN + '%s' + COLOR_RESET,
#     'WARNING': COLOR_PURPLE + '%s' + COLOR_RESET,
#     'ERROR': COLOR_RED + '%s' + COLOR_RESET,
#     'CRITICAL': COLOR_RED + '%s' + COLOR_RESET,
#     'EXCEPTION': COLOR_PURPLE + '%s' + COLOR_RESET,
# }

LOG_COLORS = {
    'DEBUG': '%s',
    'INFO': '%s',
    'WARNING': '%s',
    'ERROR': '%s',
    'CRITICAL': '%s',
    'EXCEPTION': '%s',
}


class ColorFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None):
        logging.Formatter.__init__(self, fmt, datefmt)

    def format(self, record):
        level_name = record.levelname
        msg = logging.Formatter.format(self, record)

        return LOG_COLORS.get(level_name, '%s') % msg


def _create_formatters(cp):
    flist = cp.get("formatters", "keys")
    if not len(flist):
        return {}
    flist = string.split(flist, ",")
    flist = logging.config._strip_spaces(flist)
    formatters = {}
    for form in flist:
        sectname = "formatter_%s" % form
        opts = cp.options(sectname)
        if "format" in opts:
            fs = cp.get(sectname, "format", 1)
        else:
            fs = None
        if "datefmt" in opts:
            dfs = cp.get(sectname, "datefmt", 1)
        else:
            dfs = None
        c = ColorFormatter
        if "class" in opts:
            class_name = cp.get(sectname, "class")
            if class_name:
                c = logging.config._resolve(class_name)
        f = c(fs, dfs)
        formatters[form] = f
    return formatters

def _install_handlers(cp, formatters,mod_name):
    """Install and return handlers"""
    hlist = cp.get("handlers", "keys")
    if not len(hlist):
        return {}
    hlist = hlist.split(",")
    hlist = logging.config._strip_spaces(hlist)
    handlers = {}
    fixups = [] #for inter-handler references
    for hand in hlist:
        sectname = "handler_%s" % hand
        klass = cp.get(sectname, "class")
        opts = cp.options(sectname)
        if "formatter" in opts:
            fmt = cp.get(sectname, "formatter")
        else:
            fmt = ""
        try:
            klass = eval(klass, vars(logging))
        except (AttributeError, NameError):
            klass = logging.config._resolve(klass)
        if sectname == "handler_filehander":
            args = ('%s/log/%s.log' % (os.path.dirname(os.path.dirname(os.path.abspath(__file__))),mod_name), 'a')
        else:
            args = cp.get(sectname, "args")
            args = eval(args, vars(logging))
        h = klass(*args)
        if "level" in opts:
            level = cp.get(sectname, "level")
            h.setLevel(logging._levelNames[level])
        if len(fmt):
            h.setFormatter(formatters[fmt])
        if issubclass(klass, logging.handlers.MemoryHandler):
            if "target" in opts:
                target = cp.get(sectname,"target")
            else:
                target = ""
            if len(target): #the target handler may not be loaded yet, so keep for later...
                fixups.append((h, target))
        handlers[hand] = h
    #now all handlers are loaded, fixup inter-handler references...
    for h, t in fixups:
        h.setTarget(handlers[t])
    return handlers

def fileConfig(fname, mod_name,defaults=None, disable_existing_loggers=1):
    import ConfigParser

    cp = ConfigParser.ConfigParser(defaults)
    if hasattr(cp, 'readfp') and hasattr(fname, 'readline'):
        cp.readfp(fname)
    else:
        cp.read(fname)
    formatters = _create_formatters(cp)
    logging._acquireLock()
    try:
        logging._handlers.clear()
        del logging._handlerList[:]
        handlers = _install_handlers(cp, formatters,mod_name)
        logging.config._install_loggers(cp, handlers, disable_existing_loggers)
    finally:
        logging._releaseLock()





