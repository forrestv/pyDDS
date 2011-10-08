import struct
import ctypes

_ddscore_lib = ctypes.CDLL('/home/forrest/RTI/ndds.4.5d/lib/x64Linux2.6gcc4.1.1/libnddscore.so', ctypes.RTLD_GLOBAL)
_ddsc_lib = ctypes.CDLL('/home/forrest/RTI/ndds.4.5d/lib/x64Linux2.6gcc4.1.1/libnddsc.so')

class Error(Exception):
    pass

def check_code(result, func, arguments, Error=Error):
    if result == 0:
        return
    raise Error(result)

def check_none(result, func, arguments, Error=Error):
    if result is None:
        raise Error()
    return result

@apply
class DDSFunc(object):
    def __getattr__(self, attr):
        contents = getattr(_ddsc_lib, "DDS_" + attr)
        setattr(self, attr, contents)
        return contents

@apply
class DDSType(object):
    def __getattr__(self, attr):
        contents = type(attr, (ctypes.Structure,), {})
        setattr(self, attr, contents)
        return contents

DDS_ReturnCode_t = ctypes.c_int

map(lambda (p, errcheck, restype, argtypes): (setattr(p, "errcheck", errcheck) if errcheck is not None else None, setattr(p, "restype", restype), setattr(p, "argtypes", argtypes)), [
    (DDSFunc.DomainParticipantFactory_get_instance, check_none, ctypes.POINTER(DDSType.DomainParticipantFactory), []),
    (DDSFunc.DomainParticipantFactory_create_participant, check_none, ctypes.POINTER(DDSType.DomainParticipant), [ctypes.POINTER(DDSType.DomainParticipantFactory), ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong]),
    (DDSFunc.DomainParticipantFactory_delete_participant, check_code, DDS_ReturnCode_t, [ctypes.POINTER(DDSType.DomainParticipantFactory), ctypes.POINTER(DDSType.DomainParticipant)]),
    (DDSFunc.DomainParticipant_create_publisher, check_none, ctypes.POINTER(DDSType.Publisher), [ctypes.POINTER(DDSType.DomainParticipant), ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong]),
    (DDSFunc.DomainParticipant_delete_publisher, check_code, DDS_ReturnCode_t, [ctypes.POINTER(DDSType.DomainParticipant), ctypes.POINTER(DDSType.Publisher)]),
    (DDSFunc.DomainParticipant_create_topic, check_none, ctypes.POINTER(DDSType.Topic), [ctypes.POINTER(DDSType.DomainParticipant), ctypes.c_char_p, ctypes.c_char_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong]),
    (DDSFunc.DomainParticipant_delete_topic, check_code, DDS_ReturnCode_t, [ctypes.POINTER(DDSType.DomainParticipant), ctypes.POINTER(DDSType.Topic)]),
    (DDSFunc.Publisher_create_datawriter, check_none, ctypes.POINTER(DDSType.DataWriter), [ctypes.POINTER(DDSType.Publisher), ctypes.POINTER(DDSType.Topic), ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong]),
    (DDSFunc.Publisher_delete_datawriter, check_code, DDS_ReturnCode_t, [ctypes.POINTER(DDSType.Publisher), ctypes.POINTER(DDSType.DataWriter)]),
    (DDSFunc.DynamicDataTypeSupport_new, check_none, ctypes.POINTER(DDSType.DynamicDataTypeSupport), [ctypes.POINTER(DDSType.TypeCode), ctypes.c_void_p]),
    (DDSFunc.DynamicDataTypeSupport_register_type, check_code, DDS_ReturnCode_t, [ctypes.POINTER(DDSType.DynamicDataTypeSupport), ctypes.POINTER(DDSType.DomainParticipant), ctypes.c_char_p]),
    (DDSFunc.DynamicDataTypeSupport_unregister_type, check_code, DDS_ReturnCode_t, [ctypes.POINTER(DDSType.DynamicDataTypeSupport), ctypes.POINTER(DDSType.DomainParticipant), ctypes.c_char_p]),
    (DDSFunc.DynamicDataTypeSupport_create_data, check_none, ctypes.POINTER(DDSType.DynamicData), [ctypes.POINTER(DDSType.DynamicDataTypeSupport)]),
    (DDSFunc.DynamicDataTypeSupport_delete, None, None, [ctypes.POINTER(DDSType.DynamicDataTypeSupport)]),
    (DDSFunc.DynamicData_set_long, check_code, DDS_ReturnCode_t, [ctypes.POINTER(DDSType.DynamicData), ctypes.c_char_p, ctypes.c_long, ctypes.c_long]),
    (DDSFunc.DynamicData_set_double, check_code, DDS_ReturnCode_t, [ctypes.POINTER(DDSType.DynamicData), ctypes.c_char_p, ctypes.c_long, ctypes.c_double]),
    (DDSFunc.DynamicDataWriter_narrow, check_none, ctypes.POINTER(DDSType.DynamicDataWriter), [ctypes.POINTER(DDSType.DataWriter)]),
    (DDSFunc.DynamicDataWriter_write, check_code, DDS_ReturnCode_t, [ctypes.POINTER(DDSType.DynamicDataWriter), ctypes.POINTER(DDSType.DynamicData), ctypes.c_void_p]),
])

class Topic(object):
    def __init__(self, dds, topic_name, data_type):
        self._dds = dds
        self._topic_name = topic_name
        self._data_type = data_type
        del dds, topic_name, data_type
        
        self._support = _ddsc_lib.DDS_DynamicDataTypeSupport_new(self._data_type._TypeSupport_get_typecode(), _ddsc_lib.DDS_DYNAMIC_DATA_TYPE_PROPERTY_DEFAULT)
        _ddsc_lib.DDS_DynamicDataTypeSupport_register_type(self._support, self._dds._participant, self._data_type._TypeSupport_get_type_name())
        
        self._topic =  _ddsc_lib.DDS_DomainParticipant_create_topic(
            self._dds._participant,
            self._topic_name,
            self._data_type._TypeSupport_get_type_name(),
            _ddsc_lib.DDS_TOPIC_QOS_DEFAULT,
            None,
            0,
        )
        
        self._writer = _ddsc_lib.DDS_Publisher_create_datawriter(
            self._dds._publisher,
            self._topic,
            _ddsc_lib.DDS_DATAWRITER_QOS_DEFAULT,
            None,
            0,
        )
        
        self._dyn_narrowed_writer = _ddsc_lib.DDS_DynamicDataWriter_narrow(self._writer)
    
    def send(self, msg):
        sample = _ddsc_lib.DDS_DynamicDataTypeSupport_create_data(self._support) #sample = _ddsc_lib.DDS_DynamicData_new(tc, _ddsc_lib.DDS_DYNAMIC_DATA_PROPERTY_DEFAULT)
        
        for k, v in msg.iteritems():
            if isinstance(v, int):
                _ddsc_lib.DDS_DynamicData_set_long(sample, k, 0, v)
            elif isinstance(v, float):
                _ddsc_lib.DDS_DynamicData_set_double(sample, k, 0, v)
            else:
                raise TypeError((k, v))
        
        _ddsc_lib.DDS_DynamicDataWriter_write(self._dyn_narrowed_writer, sample, ctypes.create_string_buffer(struct.pack('<16sII', '', 16, 0)))
        _ddsc_lib.DDS_DynamicDataTypeSupport_delete_data(self._support, sample)
    
    def recv(self):
        DDS_DynamicData_get_long(sample, ctypes.byref(theInteger), "myInteger", DDS_DYNAMIC_DATA_MEMBER_ID_UNSPECIFIED);
    
    def __del__(self, _ddsc_lib=_ddsc_lib):
        _ddsc_lib.DDS_Publisher_delete_datawriter(
            self._dds._publisher,
            self._writer,
        )
        
        _ddsc_lib.DDS_DomainParticipant_delete_topic(
            self._dds._participant,
            self._topic,
        )
        
        _ddsc_lib.DDS_DynamicDataTypeSupport_unregister_type(self._support, self._dds._participant, self._data_type._TypeSupport_get_type_name())
        
        _ddsc_lib.DDS_DynamicDataTypeSupport_delete(self._support)

class DDS(object):
    def __init__(self, domain_id=0):
        self._participant = _ddsc_lib.DDS_DomainParticipantFactory_create_participant(
            _ddsc_lib.DDS_DomainParticipantFactory_get_instance(),
            domain_id,
            _ddsc_lib.DDS_PARTICIPANT_QOS_DEFAULT,
            None,
            0,
        )
        
        self._publisher = _ddsc_lib.DDS_DomainParticipant_create_publisher(
            self._participant,
            _ddsc_lib.DDS_PUBLISHER_QOS_DEFAULT,
            None,
            0,
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
        f.restype = ctypes.POINTER(DDSType.TypeCode)
        f.errcheck = check_none
        return f()
    
    def _TypeSupport_get_type_name(self, ctypes=ctypes, check_none=check_none):
        f = getattr(self._lib, self._name + 'TypeSupport_get_type_name')
        f.argtypes = []
        f.restype = ctypes.c_char_p
        f.errcheck = check_none
        return f()
    
    def _TypeSupport_register_type(self, participant, type_name):
        f = getattr(self._lib, self._name + 'TypeSupport_register_type')
        f.argtypes = [ctypes.POINTER(DDSType.DomainParticipant), ctypes.c_char_p]
        f.errcheck = check_code
        f(participant, type_name)
    
    def _DataWriter_narrow(self, writer):
        f = getattr(self._lib, self._name + 'DataWriter_narrow')
        f.argtypes = [ctypes.POINTER(DDSType.DataWriter)]
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
        t.send(dict(depth=x, humidity=x+2, thermistertemp=x+3, humiditytemp=x+4))
        time.sleep(1)
