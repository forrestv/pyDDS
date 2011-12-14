from twisted.internet import main, reactor
from twisted.python import failure

import dds

class DDSTransport(object):
    def __init__(self, topic, protocol):
        self.topic = topic
        self.protocol = protocol
    
    def connect(self):
        self._cb_ref = self.topic.add_data_available_callback(self._data_available_callback)
        self.protocol.transport = self
        self.protocol.connectionMade()
    
    def send(self, msg):
        self.topic.send(msg)
    
    def _data_available_callback(self):
        reactor.callFromThread(self._data_available_callback2)
    
    def _data_available_callback2(self):
        while True:
            try:
                msg = self.topic.recv()
            except dds.Error, e:
                if e.message == 'no data':
                    break
                raise
            else:
                self.protocol.messageReceived(msg)
    
    def loseConnection(self):
        self.topic.remove_data_available_callback(self._cb_ref)
        self.protocol.connectionLost(failure.Failure(main.CONNECTION_DONE))

def connectDDS(topic, protocol):
    DDSTransport(topic, protocol).connect()
