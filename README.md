# pipeline-cache
Python pipeline cache module

Cache expensive json.load or common os calls like os.listdir over network mounts. Cache is loaded/saved to disk on open/exit. Can also be used as an analysis/debugging tool with file logging to see which functions are making the same repetitive calls to os with same parameters.

Supported cached os calls are listdir, stat, lstat, isdir, isfile.

**Cache has a max size of 100 items and time to live (ttl) of 300 seconds for items. When cache reaches maxsize, first item in is removed.**

The `@timed` decorator can be used for logging how long it takes to run the function and calling function.

The `@profiled` decorator can be used create cProfile profile files for any wrapped functions. Use [runsnakerun](http://www.vrplumber.com/programming/runsnakerun/) or [snakevis](https://jiffyclub.github.io/snakeviz/) to open the .profile files. [kcachegrind](https://kcachegrind.github.io/html/Home.html) is also a really good profile ui tool and here is a good [how to](https://julien.danjou.info/guide-to-python-profiling-cprofile-concrete-case-carbonara/) for it.


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

# add timed decorator to your own methods to log time to run function and calling function
from pipeCache import timed

@timed
function do_stuff(*args, **kwargs):
  # slow code
  return value
  
# add profiled (cProfile) decorator to your own methods to create cPython .profile files
from pipeCache import profiled

@profiled
function do_stuff(*args, **kwargs):
  # slow code
  return value
```
