import struct
import ctypes

_ddscore_lib = ctypes.CDLL('/home/forrest/RTI/ndds.4.5d/lib/x64Linux2.6gcc4.1.1/libnddscore.so', ctypes.RTLD_GLOBAL)
_ddsc_lib = ctypes.CDLL('/home/forrest/RTI/ndds.4.5d/lib/x64Linux2.6gcc4.1.1/libnddsc.so')

class Error(Exception):
    pass

def check_code(result, func, arguments):
    if result == 0:
        return
    raise Error(result)

def check_none(result, func, arguments):
    if result is None:
        raise Error()
    return result


class DDS_DomainParticipantFactory(ctypes.Structure):
    pass

_ddsc_lib.DDS_DomainParticipantFactory_get_instance.argtypes = []
_ddsc_lib.DDS_DomainParticipantFactory_get_instance.restype = ctypes.POINTER(DDS_DomainParticipantFactory)
_ddsc_lib.DDS_DomainParticipantFactory_create_participant.errcheck = check_none


class DDS_DomainParticipant(ctypes.Structure):
    pass

_ddsc_lib.DDS_DomainParticipantFactory_create_participant.argtypes = [ctypes.POINTER(DDS_DomainParticipantFactory), ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong]
_ddsc_lib.DDS_DomainParticipantFactory_create_participant.restype = ctypes.POINTER(DDS_DomainParticipant)
_ddsc_lib.DDS_DomainParticipantFactory_create_participant.errcheck = check_none


class DDS_Publisher(ctypes.Structure):
    pass

_ddsc_lib.DDS_DomainParticipant_create_publisher.argtypes = [ctypes.POINTER(DDS_DomainParticipant), ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong]
_ddsc_lib.DDS_DomainParticipant_create_publisher.restype = ctypes.POINTER(DDS_Publisher)
_ddsc_lib.DDS_DomainParticipant_create_publisher.errcheck = check_none


class DDS_Topic(ctypes.Structure):
    pass

_ddsc_lib.DDS_DomainParticipant_create_topic.argtypes = [ctypes.POINTER(DDS_DomainParticipant), ctypes.c_char_p, ctypes.c_char_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong]
_ddsc_lib.DDS_DomainParticipant_create_topic.restype = ctypes.POINTER(DDS_Topic)
_ddsc_lib.DDS_DomainParticipant_create_topic.errcheck = check_none

_ddsc_lib.DDS_DomainParticipant_delete_topic.argtypes = [ctypes.POINTER(DDS_DomainParticipant), ctypes.POINTER(DDS_Topic)]
_ddsc_lib.DDS_DomainParticipant_delete_topic.errcheck = check_code


class DDS_DataWriter(ctypes.Structure):
    pass

_ddsc_lib.DDS_Publisher_create_datawriter.argtypes = [ctypes.POINTER(DDS_Publisher), ctypes.POINTER(DDS_Topic), ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong]
_ddsc_lib.DDS_Publisher_create_datawriter.restype = ctypes.POINTER(DDS_DataWriter)
_ddsc_lib.DDS_Publisher_create_datawriter.errcheck = check_none

_ddsc_lib.DDS_Publisher_delete_datawriter.argtypes = [ctypes.POINTER(DDS_Publisher), ctypes.POINTER(DDS_DataWriter)]
_ddsc_lib.DDS_Publisher_delete_datawriter.errcheck = check_code
DDS_STATUS_MASK_NONE = ctypes.c_ulong(0)


class Topic(object):
    def __init__(self, library, topic_name, type_name):
        self._library = library
        self._topic_name = topic_name
        self._type_name = type_name
        del library, topic_name, type_name
        
        assert self._library._get_type_name(self._type_name) == self._type_name
        self._library._register_type(self._type_name, self._type_name)
        
        self._topic =  _ddsc_lib.DDS_DomainParticipant_create_topic(
            self._library._participant,
            self._topic_name,
            self._type_name,
            _ddsc_lib.DDS_TOPIC_QOS_DEFAULT,
            None,
            DDS_STATUS_MASK_NONE,
        )
        
        self._writer = _ddsc_lib.DDS_Publisher_create_datawriter(
            self._library._publisher,
            self._topic,
            _ddsc_lib.DDS_DATAWRITER_QOS_DEFAULT,
            None,
            DDS_STATUS_MASK_NONE,
        )
        
        self._writer2 = self._library._dw_narrow(self._type_name, self._writer)
    
    def send(self, msg):
        instance = self._library._create_data(self._type_name)
        x = ctypes.create_string_buffer(struct.pack("<16sII", "", 16, 0))
        self._library._dw_write(self._type_name, self._writer2, instance, x)
    
    def __del__(self, _ddsc_lib=_ddsc_lib):
        _ddsc_lib.DDS_Publisher_delete_datawriter(
            self._library._publisher,
            self._writer,
        )
        
        _ddsc_lib.DDS_DomainParticipant_delete_topic(
            self._library._participant,
            self._topic,
        )


class Library(object):
    def __init__(self, so_path):
        self._lib = ctypes.CDLL(so_path)
        
        self._participant = _ddsc_lib.DDS_DomainParticipantFactory_create_participant(
            _ddsc_lib.DDS_DomainParticipantFactory_get_instance(),
            0,
            _ddsc_lib.DDS_PARTICIPANT_QOS_DEFAULT,
            None,
            DDS_STATUS_MASK_NONE,
        )
        
        self._publisher = _ddsc_lib.DDS_DomainParticipant_create_publisher(
            self._participant,
            _ddsc_lib.DDS_PUBLISHER_QOS_DEFAULT,
            None,
            DDS_STATUS_MASK_NONE,
        )
        
        self._topics = {}
    
    def _get_type_name(self, name):
        f = getattr(self._lib, name + 'TypeSupport_get_type_name')
        f.argtypes = []
        f.restype = ctypes.c_char_p
        f.errcheck = check_none
        return f()
    
    def _register_type(self, name, type_name):
        f = getattr(self._lib, name + 'TypeSupport_register_type')
        f.argtypes = [ctypes.POINTER(DDS_DomainParticipant), ctypes.c_char_p]
        f.errcheck = check_code
        f(self._participant, type_name)
    
    def _dw_narrow(self, name, writer):
        f = getattr(self._lib, name + 'DataWriter_narrow')
        f.argtypes = [ctypes.POINTER(DDS_DataWriter)]
        f.restype = ctypes.c_void_p
        f.errcheck = check_none
        return f(writer)
    
    def _create_data(self, name):
        f = getattr(self._lib, name + 'TypeSupport_create_data')
        f.argtypes = []
        f.restype = ctypes.c_void_p
        f.errcheck = check_none
        return f()
    
    def _ts_print_data(self, name, d):
        f = getattr(self._lib, name + 'TypeSupport_print_data')
        f.argtypes = [ctypes.c_void_p]
        f(d)
    
    def _dw_write(self, name, writer, x, y):
        f = getattr(self._lib, name + 'DataWriter_write')
        f.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
        f.errcheck = check_code
        return f(writer, x, y)
    
    def get_topic(self, topic_name, type_name):
        # XXX
        return Topic(self, topic_name, type_name)
    
    def __del__(self):
        pass


x = Library('../build/DDSMessages/libddsmessages2.so')
t = x.get_topic('newtopic2', 'DepthMessage')
while True:
    t.send({})
