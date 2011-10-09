import sys
import time
import traceback

import dds

recv = ['send', 'recv'].index(sys.argv[1])

d = dds.DDS()
l = dds.Library('../build/DDSMessages/libddsmessages2.so')
t = d.get_topic('newtopic2', l.DepthMessage)

if recv:
    while True:
        time.sleep(.01)
        try:
            msg = t.recv()
        except dds.Error, e:
            if e.message == 'no data':
                continue
            raise
        print "Received:", msg
else:
    x = 1.
    while True:
        x += 1.245
        msg = dict(timestamp=int(x*100), depth=x, humidity=x+2, thermistertemp=x+3, humiditytemp=x+4)
        print "Sending:", msg
        t.send(msg)
        time.sleep(1)
