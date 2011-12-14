from twisted.internet import reactor

import dds
import twistedds

class TestProtocol(object):
    def connectionMade(self):
        print 'connection made!'
    
    def messageReceived(self, msg):
        print 'message received:', msg
    
    def connectionLost(self, reason):
        print 'connection lost! reason:', reason

twistedds.connectDDS(dds.DDS().get_topic('t2', dds.Library('./libddsmessages_c.so').HydrophoneMessage), TestProtocol())

reactor.run()
