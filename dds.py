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

_ddsc_lib.DDS_DomainParticipantFactory_delete_participant.argtypes = [ctypes.POINTER(DDS_DomainParticipantFactory), ctypes.POINTER(DDS_DomainParticipant)]
_ddsc_lib.DDS_DomainParticipant_delete_publisher.errcheck = check_code

class DDS_Publisher(ctypes.Structure):
    pass

_ddsc_lib.DDS_DomainParticipant_create_publisher.argtypes = [ctypes.POINTER(DDS_DomainParticipant), ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong]
_ddsc_lib.DDS_DomainParticipant_create_publisher.restype = ctypes.POINTER(DDS_Publisher)
_ddsc_lib.DDS_DomainParticipant_create_publisher.errcheck = check_none

_ddsc_lib.DDS_DomainParticipant_delete_publisher.argtypes = [ctypes.POINTER(DDS_DomainParticipant), ctypes.POINTER(DDS_Publisher)]
_ddsc_lib.DDS_DomainParticipant_delete_publisher.errcheck = check_code

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


class DDS_TypeCode(ctypes.Structure):
    pass

class DDS_DynamicDataTypeSupport(ctypes.Structure):
    pass

class DDS_DynamicData(ctypes.Structure):
    pass

_ddsc_lib.DDS_DynamicDataTypeSupport_new.argtypes = [ctypes.POINTER(DDS_TypeCode), ctypes.c_void_p]
_ddsc_lib.DDS_DynamicDataTypeSupport_new.restype = ctypes.POINTER(DDS_DynamicDataTypeSupport)
_ddsc_lib.DDS_DynamicDataTypeSupport_new.errcheck = check_none

_ddsc_lib.DDS_DynamicDataTypeSupport_create_data.argtypes = [ctypes.POINTER(DDS_DynamicDataTypeSupport)]
_ddsc_lib.DDS_DynamicDataTypeSupport_create_data.restype = ctypes.POINTER(DDS_DynamicData)
_ddsc_lib.DDS_DynamicDataTypeSupport_create_data.errcheck = check_none

_ddsc_lib.DDS_DynamicData_set_long.argtypes = [ctypes.POINTER(DDS_DynamicData), ctypes.c_char_p, ctypes.c_long, ctypes.c_long]
_ddsc_lib.DDS_DynamicData_set_long.errcheck = check_code

_ddsc_lib.DDS_DynamicData_set_double.argtypes = [ctypes.POINTER(DDS_DynamicData), ctypes.c_char_p, ctypes.c_long, ctypes.c_double]
_ddsc_lib.DDS_DynamicData_set_double.errcheck = check_code

_ddsc_lib.DDS_DynamicDataWriter_narrow.argtypes = [ctypes.POINTER(DDS_DataWriter)]
_ddsc_lib.DDS_DynamicDataWriter_narrow.restype = ctypes.c_void_p
_ddsc_lib.DDS_DynamicDataWriter_narrow.errcheck = check_none

DDS_STATUS_MASK_NONE = ctypes.c_ulong(0)


class Topic(object):
    def __init__(self, dds, topic_name, data_type):
        self._dds = dds
        self._topic_name = topic_name
        self._data_type = data_type
        del dds, topic_name, data_type
        
        self._data_type._TypeSupport_register_type(self._dds._participant, self._data_type._TypeSupport_get_type_name())
        
        self._topic =  _ddsc_lib.DDS_DomainParticipant_create_topic(
            self._dds._participant,
            self._topic_name,
            self._data_type._TypeSupport_get_type_name(),
            _ddsc_lib.DDS_TOPIC_QOS_DEFAULT,
            None,
            DDS_STATUS_MASK_NONE,
        )
        
        self._writer = _ddsc_lib.DDS_Publisher_create_datawriter(
            self._dds._publisher,
            self._topic,
            _ddsc_lib.DDS_DATAWRITER_QOS_DEFAULT,
            None,
            DDS_STATUS_MASK_NONE,
        )
        
        #self._narrowed_writer = self._data_type._DataWriter_narrow(self._writer)
        self._dyn_narrowed_writer = _ddsc_lib.DDS_DynamicDataWriter_narrow(self._writer)
    
    def send(self, msg):
        support = _ddsc_lib.DDS_DynamicDataTypeSupport_new(self._data_type._TypeSupport_get_typecode(), _ddsc_lib.DDS_DYNAMIC_DATA_TYPE_PROPERTY_DEFAULT)
        sample = _ddsc_lib.DDS_DynamicDataTypeSupport_create_data(support) #sample = _ddsc_lib.DDS_DynamicData_new(tc, _ddsc_lib.DDS_DYNAMIC_DATA_PROPERTY_DEFAULT)
        #_ddsc_lib.DDS_DynamicData_set_long(sample, "depth", 0, 5)
        print msg
        _ddsc_lib.DDS_DynamicData_set_double(sample, "depth", 0, msg['depth'])
        #DDS_Long theInteger = 0;
        #DDS_DynamicData_get_long(sample, &theInteger, "myInteger", DDS_DYNAMIC_DATA_MEMBER_ID_UNSPECIFIED); 
        print "fdasfas"
        _ddsc.DDS_DynamicDataWriter_write(self._dyn_narrowed_writer, sample, ctypes.create_string_buffer(struct.pack('<16sII', '', 16, 0)))
        
        _ddsc_lib.DDS_DynamicDataTypeSupport_delete_data(support, sample) # _ddsc_lib.DDS_DynamicData_delete(d)
    
    def __del__(self, _ddsc_lib=_ddsc_lib):
        _ddsc_lib.DDS_Publisher_delete_datawriter(
            self._dds._publisher,
            self._writer,
        )
        
        _ddsc_lib.DDS_DomainParticipant_delete_topic(
            self._dds._participant,
            self._topic,
        )

class DDS(object):
    def __init__(self, domain_id=0):
        self._participant = _ddsc_lib.DDS_DomainParticipantFactory_create_participant(
            _ddsc_lib.DDS_DomainParticipantFactory_get_instance(),
            domain_id,
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
    
    def get_topic(self, topic_name, data_type):
        # XXX
        return Topic(self, topic_name, data_type)
    
    def __del__(self, _ddsc_lib=_ddsc_lib):
        _ddsc_lib.DDS_DomainParticipant_delete_publisher(
            self._participant,
            self._publisher,
        )
        
        # very slow for some reason
        _ddsc_lib.DDS_DomainParticipantFactory_delete_participant(
            _ddsc_lib.DDS_DomainParticipantFactory_get_instance(),
            self._participant,
        )


class LibraryType(object):
    def __init__(self, lib, name):
        self._lib, self._name = lib, name
        del lib, name
    
    def _TypeSupport_get_typecode(self):
        f = getattr(self._lib, self._name + '_get_typecode')
        f.argtypes = []
        f.restype = ctypes.POINTER(DDS_TypeCode)
        f.errcheck = check_none
        return f()
    
    def _TypeSupport_get_type_name(self):
        f = getattr(self._lib, self._name + 'TypeSupport_get_type_name')
        f.argtypes = []
        f.restype = ctypes.c_char_p
        f.errcheck = check_none
        return f()
    
    def _TypeSupport_register_type(self, participant, type_name):
        f = getattr(self._lib, self._name + 'TypeSupport_register_type')
        f.argtypes = [ctypes.POINTER(DDS_DomainParticipant), ctypes.c_char_p]
        f.errcheck = check_code
        f(participant, type_name)
    
    def _DataWriter_narrow(self, writer):
        f = getattr(self._lib, self._name + 'DataWriter_narrow')
        f.argtypes = [ctypes.POINTER(DDS_DataWriter)]
        f.restype = ctypes.c_void_p
        f.errcheck = check_none
        return f(writer)
    
    def _TypeSupport_create_data(self):
        f = getattr(self._lib, self._name + 'TypeSupport_create_data')
        f.argtypes = []
        f.restype = ctypes.c_void_p
        f.errcheck = check_none
        return f()
    
    def _TypeSupport_print_data(self, d):
        f = getattr(self._lib, self._name + 'TypeSupport_print_data')
        f.argtypes = [ctypes.c_void_p]
        f(d)
    
    def _DataWriter_write(self, writer, x, y):
        f = getattr(self._lib, self._name + 'DataWriter_write')
        f.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
        f.errcheck = check_code
        return f(writer, x, y)

class Library(object):
    def __init__(self, so_path):
        self._lib = ctypes.CDLL(so_path)
    
    def __getattr__(self, attr):
        return LibraryType(self._lib, attr)

if __name__ == '__main__':
    import time
    
    d = DDS()
    l = Library('../build/DDSMessages/libddsmessages2.so')
    t = d.get_topic('newtopic2', l.DepthMessage)
    x = 1.
    while True:
        x += 1.245
        t.send({'depth': x})
        time.sleep(1)
