import feedparser
import time
import re
from requestbin import config

bin_ttl = config.BIN_TTL
storage_backend = config.STORAGE_BACKEND

storage_module, storage_class = storage_backend.rsplit('.', 1)

try:
    klass = getattr(__import__(storage_module, fromlist=[storage_class]), storage_class)
except ImportError, e:
    raise ImportError("Unable to load storage backend '{}': {}".format(storage_backend, e))

db = klass(bin_ttl)

def create_bin(private=False):
    return db.create_bin(private)

def create_request(bin, request):
    return db.create_request(bin, request)

def lookup_bin(name):
    name=re.split(r"[/.]", name)[0]
    print "[db.py] I got a name: " + name
    # name = name.split("requestbin_")[1]
    # print "splitted: " + name
    try:
        return db.lookup_bin(name)
    except Exception:
        print "[db.py] db.lookup_bin(" + name + ") failed"

def count_bins():
    return db.count_bins()

def count_requests():
    return db.count_requests()

def avg_req_size():
    return db.avg_req_size()

def get_all_keys():
    try: 
        return db.get_all_keys()
    except TypeError:
        print "[db.py] redis.py get_all keys error"
        raise KeyError("db.py get_all keys error")
