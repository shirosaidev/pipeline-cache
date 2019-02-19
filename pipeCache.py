#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""pipeCache.py - Pipeline cache module
Cache expensive json.load or common os calls like os.listdir over network mounts.
Cache is loaded/saved to disk on open/exit.

Author: shirosai <cpark16@gmail.com>

Copyright (C) Chris Park 2019
pipeline-cache is released under the Apache 2.0 license. See
LICENSE for the full license text.
"""

try:
    import cPickle as pickle
except ImportError:
    import pickle
from functools import wraps
import os
import sys
import time
import json
import tempfile
import logging
import atexit
import cProfile


PIPECACHE_VERSION = '0.1-b.2'
__version__ = PIPECACHE_VERSION

# disk cache paths
DISKCACHE_DIR = tempfile.gettempdir()
DISKCACHE_FILE = os.path.join(DISKCACHE_DIR, 'pipeCache_diskcache.pickle')

# settings
ttl=300
maxsize=100
pick_prot=-1
logtofile=True
loglevel=logging.DEBUG  # logging.INFO

# cache stats
hits = 0
misses = 0
fn_calls = {}


def logging_setup():
    """Set up logging."""
    logger = logging.getLogger(name='pipecache')
    logger.setLevel(loglevel)
    logformatter = logging.Formatter('%(asctime)s [%(levelname)s][%(name)s] %(message)s')
    ch = logging.StreamHandler()
    ch.setLevel(loglevel)
    ch.setFormatter(logformatter)
    logger.addHandler(ch)
    # prevent logging from bubbling up to maya's logger
    logger.propagate = False
    if logtofile:
        logfile = os.path.join(DISKCACHE_DIR, 'pipeCache.log')
        hdlr = logging.FileHandler(logfile)
        hdlr.setLevel(loglevel)
        hdlr.setFormatter(logformatter)
        logger.addHandler(hdlr)
    return logger

logger = logging_setup()


def write_cache_to_disk():
    """Write cache to disk at exit."""
    try:
        logger.info('writing cache to disk ' + DISKCACHE_FILE)
        with open(DISKCACHE_FILE, 'wb') as f:
            pickle.dump(cache, f)
    except IOError:
        logger.error('error writing cache to disk')


# check if we are using Maya and register callback (workaround for atexit not working)
# to save disk cache on exit
try:
    import maya.OpenMaya as om
    om.MSceneMessage.addCallback(om.MSceneMessage.kMayaExiting, write_cache_to_disk)
except ImportError:
    pass

atexit.register(write_cache_to_disk)


def load_disk_cache():
    """Load cache from disk."""
    try:
        logger.info('opening cache from disk ' + DISKCACHE_FILE)
        with open(DISKCACHE_FILE, 'rb') as f:
            cache = pickle.load(f)
    except IOError:
        logger.warning('no cache found on disk')
        cache = {}
    return cache

cache = load_disk_cache()


def profiled(fn):
    """cProfile decorator. Dumps cProfile stats to file named function name + .profile."""
    @wraps(fn)
    def profileit(*args, **kwargs):
        datafn = fn.__name__ + ".profile"
        prof = cProfile.Profile()
        res = prof.runcall(fn, *args, **kwargs)
        prof.dump_stats(datafn)
        logger.debug('wrote cProfile profile stats to %s' % datafn)
        return res
    return profileit


def timed(fn):
    """Timeit decorator."""
    @wraps(fn)
    def timeit(*args, **kwargs):
        t = time.time()
        res = fn(*args, **kwargs)
        t = time.time() - t
        strSecs = time.strftime("%M:%S.", time.localtime(t)) + ("%.3f" % t).split(".")[-1]
        fn_caller = sys._getframe().f_back.f_code.co_name
        logger.debug('function %s(%s, %s) - finished in %s seconds (caller: %s)' 
            % (fn.__name__, args, kwargs, strSecs, fn_caller))
        return res
    return timeit


def pCache(fn):
    """Memoization decorator. Caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned.
    Supports mutable args (list, dict, etc).
    """
    @wraps(fn)
    def cacher(*args, **kwargs):
        global hits
        global misses
        # add to cache stats number of times function is called
        if fn.__name__ in fn_calls:
            fn_calls[fn.__name__] += 1
        else:
            fn_calls[fn.__name__] = 1
        str = pickle.dumps(fn.__name__, pick_prot) + pickle.dumps(args, pick_prot) + pickle.dumps(kwargs, pick_prot)
        # check if cache is full, and remove first (oldest) item
        if cache_size() > maxsize:
            logger.debug('cache full, removing oldest..')
            oldest_key = None
            for k, v in cache.items():
                oldest_key = k if oldest_key < v[1] else oldest_key
            cache.pop(oldest_key)
        # check if item is not in cache or expired (older than ttl)
        if str not in cache or (str in cache and (time.time() - cache[str][1]) > ttl):
            logger.debug('cache miss %s %s %s' % (fn.__name__, args, kwargs))
            misses += 1
            res = fn(*args, **kwargs)
            cache[str] = [res, time.time()]
        else:  # item in cache
            logger.debug('cache hit %s %s %s' % (fn.__name__, args, kwargs))
            hits += 1
        return cache[str][0]
    return cacher


def reset_cache():
    """Remove all items from cache."""
    logger.info('resetting cache..')
    cache.clear()


def hit_rate():
    """Returns cache hit rate percent."""
    try:
        hitrate = hits / ((hits + misses) * 1.0)
    except ZeroDivisionError:
        return 0.0
    return hitrate


def cache_stats():
    """Returns dict with number of calls for each function."""
    return fn_calls


def cache_size():
    """Returns number of items in cache."""
    return len(cache)


@timed
@pCache
def listdir(path):
    return os.listdir(path)

@timed
@pCache
def stat(path):
    return os.stat(path)

@timed
@pCache
def lstat(path):
    return os.lstat(path)

@timed
@pCache
def isdir(path):
    return os.path.isdir(path)

@timed
@pCache
def isfile(path):
    return os.path.isfile(path)

@timed
@pCache
def loadjson(path):
    with open(path) as f:
        d = json.load(f)
    return d