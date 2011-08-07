from datetime import timedelta, datetime
from itertools import cycle
import os

pidfile = 'cron.pid'
logfile = 'demo.log'
name = 'cron daemon'

# example generators for rescheduling tasks
# currently there isn't any like real cron format
# I might steal what celery periodic tasks does
def every(*args, **kwargs):
    delta = timedelta(*args, **kwargs)
    while 1:
        yield delta

def cycle_every(interval_list):
    for i in cycle(interval_list):
        yield timedelta(seconds=i)

def every_fib():
    a,b = 1,0
    while True:
        a, b = (a + b), a
        yield timedelta(seconds=b)

def service():
    """Required service function"""
    # It's important to know you MUST make any imports that
    # use gevent to happen INSIDE this function
    from gevent_tools.service import Service

    class CronService(Service):

        def do_start(self):
            self.spawn(self.run)

        def schedule(self, timer, func, *args, **kwargs):
            def job():
                self.spawn(func, *args, **kwargs)
                try:
                    time = timer.next()
                    self.spawn_later(time.total_seconds(), job)
                except StopIteration:
                    pass
            job()

        def run(self):
            print 'wutup'

    # lame example methods for croning
    def message(string):
        print(string)

    def poke_website(url, data=None):
        import urllib2
        print(urllib2.urlopen(url, data).read())

    cs = CronService()
    cs.schedule(every(seconds=10), message, "Every 10 seconds")
    cs.schedule(every(seconds=30), poke_website, url="http://google.com", data="q=gevent")
    cs.schedule(cycle_every((1,2,1,0.3)), message, "Testing cycle")
    cs.schedule(every_fib(), message, "fib")
    return cs
