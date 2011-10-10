import sys
import time
import traceback
import random

import dds

recv = ['send', 'recv'].index(sys.argv[1])

d = dds.DDS()
l = dds.Library('../build/DDSMessages/libddsmessages2.so')

topics = []
topics.append((d.get_topic('t1', l.State), lambda: dict(workername=str(random.randrange(2**10)), state=random.randrange(-2**31, 2**31), health=random.random())))
topics.append((d.get_topic('t2', l.HydrophoneMessage), lambda: dict(timestamp=int(1e9*time.time()), declination=random.random(), heading=random.random(), distance=random.random(), frequency=random.random(), valid=random.choice([True, False]))))
topics.append((d.get_topic('t3', l.PDWrenchMessage), lambda: dict(linear=[random.gauss(0, 1) for i in xrange(3)], moment=[random.gauss(0, 1) for i in xrange(3)])))
topics.append((d.get_topic('t4', l.VisionSetIDsMessage), lambda: dict(visionids=[random.randrange(1000) for i in xrange(random.randrange(10))], cameraid=random.randrange(10))))
topics.append((d.get_topic('t5', l.ChatMessage), lambda: dict(username=str(random.randrange(2**10)), message=str(random.randrange(2**10)))))

if recv:
    while True:
        time.sleep(.01)
        t, mf = random.choice(topics)
        try:
            msg = t.recv()
        except dds.Error, e:
            if e.message == 'no data':
                continue
            raise
        print "Received %r on %s" % (msg, t._topic_name)
else:
    while True:
        t, mf = random.choice(topics)
        msg = mf()
        print "Sending %r on %s" % (msg, t._topic_name)
        t.send(msg)
        time.sleep(.5)
