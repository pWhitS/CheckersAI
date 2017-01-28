from threading import Thread
from time import time


## Define 'INFINITY' and 'NEG_INFINITY'
try:
    INFINITY = float("infinity")
    NEG_INFINITY = float("-infinity")
except ValueError:                 # Windows doesn't support 'float("infinity")'.
    INFINITY = float(1e3000)       # However, '1e3000' will overflow and return
    NEG_INFINITY = float(-1e3000)  # the magic float Infinity value anyway.

class ContinuousThread(Thread):
    """
    A thread that runs a function continuously,
    with an incrementing 'depth' kwarg, until
    a specified timeout has been exceeded
    """

    def __init__(self, timeout=5, target=None, group=None, name=None, args=(), kwargs={}):
        """
        Store the various values that we use from the constructor args,
        then let the superclass's constructor do its thing
        """
        self._timeout = timeout
        self._target = target
        self._args = args
        self._kwargs = kwargs
        Thread.__init__(self, args=args, kwargs=kwargs, group=group, target=target, name=name)


    def run(self):
        """ Run until the specified time limit has been exceeded """
        depth = 1

        timeout = self._timeout**(1/2.0)  # Times grow exponentially, and we don't want to
                                          # start a new depth search when we won't have
                                          # enough time to finish it
        print("Exp Timeout:", timeout)

        end_time = time() + timeout
        
        while time() < end_time:
            self._kwargs['depth'] = depth
            self._most_recent_val = self._target(*self._args, **self._kwargs)
            depth += 1


    def get_most_recent_val(self):
        """ Return the most-recent return value of the thread function """
        return self._most_recent_val
        
    
def progressive_deepener(board, search_fn, eval_fn, get_next_moves_fn, timeout=5):
    """
    Run the specified search function "search_fn" to increasing depths
    until "time" has expired; then return the most recent available return value
    """
    eval_t = ContinuousThread(timeout=timeout, target=search_fn, kwargs={ 'board': board,
                                                                          'eval_fn': eval_fn,
                                                                          'get_next_moves_fn': get_next_moves_fn})

    eval_t.setDaemon(True)
    eval_t.start()
    
    eval_t.join(timeout)

    # Note that the thread may not actually be done eating CPU cycles yet;
    # Python doesn't allow threads to be killed meaningfully...
    return eval_t.get_most_recent_val()


class memoize(object):
    """
    'Memoize' decorator.

    Caches a function's return values,
    so that it needn't compute output for the same input twice.

    Use as follows:
    @memoize
    def my_fn(stuff):
        # Do stuff
    """
    def __init__(self, fn):
        self.fn = fn
        self.memocache = {}

    def __call__(self, *args, **kwargs):
        memokey = ( args, tuple( sorted(kwargs.items()) ) )
        if memokey in self.memocache:
            return self.memocache[memokey]
        else:
            val = self.fn(*args, **kwargs)
            self.memocache[memokey] = val
            return val






