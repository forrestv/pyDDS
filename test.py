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
topics.append((d.get_topic('t6', l.IMUMessage), lambda: dict(timestamp=int(1e9*time.time()), flags=random.randrange(2**16), temp=random.random(), supply=random.random(), acceleration=[random.gauss(0, 1) for i in xrange(3)], angular_rate=[random.gauss(0, 1) for i in xrange(3)], mag_field=[random.gauss(0, 1) for i in xrange(3)])))
topics.append((d.get_topic('t7', l.PDStatusMessage), lambda: dict(timestamp=int(1e9*time.time()), state=random.randrange(-2**15, 2**15), estop=random.choice([True, False]), current=[random.random() for i in xrange(8)], tickcount=random.randrange(2**32), flags=random.randrange(2**32), current16=random.gauss(10, 1), voltage16=random.gauss(16, 1), current32=random.gauss(5, .5), voltage32=random.gauss(32, 2))))
topics.append((d.get_topic('t8', l.FinderMessageList), lambda: dict(messages2d=[dict(objectid=random.randrange(2**30), u=random.randrange(2**30), v=random.randrange(2**30), scale=random.gauss(0, 1), angle=random.gauss(1, 1)) for i in xrange(random.randrange(10))], messages3d=[dict(objectid=random.randrange(2**30), x=random.gauss(0, 1), y=random.gauss(0, 1), z=random.gauss(0, 1), ang1=random.gauss(0, 1), ang2=random.gauss(0, 1), ang3=random.gauss(0, 1)) for i in xrange(random.randrange(10))], cameraid=random.randrange(10))))
topics.append((d.get_topic('t8', l.FinderMessageList), lambda: dict(messages2d=[dict(objectid=random.randrange(2**30), u=random.randrange(2**30), v=random.randrange(2**30), scale=random.gauss(0, 1), angle=random.gauss(1, 1)) for i in xrange(random.randrange(10))], messages3d=[dict(objectid=random.randrange(2**30), x=random.gauss(0, 1), y=random.gauss(0, 1), z=random.gauss(0, 1), ang1=random.gauss(0, 1), ang2=random.gauss(0, 1), ang3=random.gauss(0, 1)) for i in xrange(random.randrange(10))], cameraid=random.randrange(10))))

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
        print "Received %r on %s" % (msg, t.name)
else:
    while True:
        t, mf = random.choice(topics)
        msg = mf()
        print "Sending %r on %s" % (msg, t.name)
        t.send(msg)
        time.sleep(.1)
