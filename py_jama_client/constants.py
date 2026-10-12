DEFAULT_ALLOWED_RESULTS_PER_PAGE = 50

# Seconds to wait before each retry of a request Jama throttled (HTTP 429): the
# backoff Jama recommends for its REST API rate limit of 10 calls/s per environment,
# https://support.jamasoftware.com/hc/en-us/articles/37036412486285
DEFAULT_RETRY_BACKOFF = (3.0, 5.0, 8.0, 13.0)
# Up to this many seconds of random jitter are added to each wait, so that
# concurrent callers do not retry in lockstep.
RETRY_JITTER = 1.0
