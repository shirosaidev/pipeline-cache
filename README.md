# pipeline-cache
Python pipeline cache module

Cache expensive json.load or common os calls like os.listdir over network mounts.
Can also be used as an analysis tool with file logging to see which functions are making the same repetitive calls to os with same parameters.
Cache is loaded/saved to disk on open/exit.

Supported os calls are listdir, stat, lstat, isdir, isfile.

**Cache has a max size of 100 items and time to live (ttl) of 300 seconds for items. When cache reaches maxsize, first item in is removed.**


```python
import pipeCache
from pipeCache import listdir, loadjson

# cache directory listing
path = '/some/network/path'
listdir(path)  # cache miss
listdir(path)  # cache hit

# load and cache json file
file = '/some/network/file.json'
loadjson(file)

# empty the cache
pipeCache.reset_cache()

# get hit rate
pipeCache.hit_rate()

# get cache size (items)
pipeCache.cache_size()

# get cache stats (calls per function)
pipeCache.cache_stats()

# manually write cache to disk
pipeCache.write_cache_to_disk()

# add cache decorator to your own methods to cache the parameters and return value
from pipeCache import pCache

@pCache
function do_stuff(*args, **kwargs):
  # slow code
  return value
```
