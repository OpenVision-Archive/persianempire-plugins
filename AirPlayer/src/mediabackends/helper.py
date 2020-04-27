# -*- coding: utf-8 -*-
from twisted.python import failure
from twisted.internet import reactor, defer
import Queue
from threading import currentThread

def doBlockingCallFromMainThread(f, *a, **kw):
    queue = Queue.Queue()

    def _callFromThread():
        result = defer.maybeDeferred(f, *a, **kw)
        result.addBoth(queue.put)

    reactor.callFromThread(_callFromThread)
    result = None
    while True:
        try:
            result = queue.get(True, 30)
        except Queue.Empty as qe:
            if True:
                raise ValueError('Reactor no longer active, aborting.')
        else:
            break

    if isinstance(result, failure.Failure):
        result.raiseException()
    return result


def blockingCallFromMainThread(f, *a, **kw):
    if currentThread().getName() == 'MainThread':
        callMethod = lambda f, *a, **kw: f(*a, **kw)
    else:
        callMethod = doBlockingCallFromMainThread
    return callMethod(f, *a, **kw)


def callOnMainThread(func, *args, **kwargs):
    if currentThread().getName() == 'MainThread':
        reactor.callLater(0, func, *args, **kwargs)
    else:
        reactor.callFromThread(func, *args, **kwargs)
