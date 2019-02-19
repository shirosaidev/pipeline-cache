# pipeline-cache Change Log

## [0.1-b.2] = 2019-02-18
### added
- time to live (ttl) of 300 seconds to cache items and max cache size of 100 items; when cache reaches maxsize, first item in is removed
- log to file setting; log gets written to pipeCache.log file in env temp directory
- profiled decorator for cProfile
- timed decorator for timing functions
### fixed
- logging in Maya

## [0.1-b.1] = 2019-02-14
### note
- first release