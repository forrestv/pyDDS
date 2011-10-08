import struct
import ctypes

_ddscore_lib = ctypes.CDLL('/home/forrest/RTI/ndds.4.5d/lib/x64Linux2.6gcc4.1.1/libnddscore.so', ctypes.RTLD_GLOBAL)
_ddsc_lib = ctypes.CDLL('/home/forrest/RTI/ndds.4.5d/lib/x64Linux2.6gcc4.1.1/libnddsc.so')

# Error checkers

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

def check_ex(result, func, arguments):
    if arguments[-1]._obj.value == 0:
        return result
    raise Error(arguments[-1]._obj)

# Function and structure accessors

@apply
class DDSFunc(object):
    def __getattr__(self, attr):
        contents = getattr(_ddsc_lib, "DDS_" + attr)
        setattr(self, attr, contents)
        return contents

@apply
class DDSType(object):
    def __getattr__(self, attr):
        def g(self2, attr2):
            f = getattr(DDSFunc, attr + '_' + attr2)
            def p(*args):
                return f(self2, *args)
            return p
        
        contents = type(attr, (ctypes.Structure,), {})
        
        # takes advantage of POINTERs being cached
        p = ctypes.POINTER(contents)
        p.__getattr__ = g
        
        setattr(self, attr, contents)
        return contents

# some types

DDS_ReturnCode_t = ctypes.c_int
DDS_ExceptionCode_t = ctypes.c_int
def ex():
    return ctypes.byref(DDS_ExceptionCode_t())

# Function prototypes

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
    
    (DDSFunc.DynamicData_new, check_none, ctypes.POINTER(DDSType.DynamicData), [ctypes.POINTER(DDSType.TypeCode), ctypes.c_void_p]),
    (DDSFunc.DynamicData_set_long, check_code, DDS_ReturnCode_t, [ctypes.POINTER(DDSType.DynamicData), ctypes.c_char_p, ctypes.c_long, ctypes.c_long]),
    (DDSFunc.DynamicData_set_double, check_code, DDS_ReturnCode_t, [ctypes.POINTER(DDSType.DynamicData), ctypes.c_char_p, ctypes.c_long, ctypes.c_double]),
    (DDSFunc.DynamicData_set_ulonglong, check_code, DDS_ReturnCode_t, [ctypes.POINTER(DDSType.DynamicData), ctypes.c_char_p, ctypes.c_long, ctypes.c_ulonglong]),
    (DDSFunc.DynamicData_bind_complex_member, check_code, DDS_ReturnCode_t, [ctypes.POINTER(DDSType.DynamicData), ctypes.POINTER(DDSType.DynamicData), ctypes.c_char_p, ctypes.c_long]),
    (DDSFunc.DynamicData_get_type, check_none, ctypes.POINTER(DDSType.TypeCode), [ctypes.POINTER(DDSType.DynamicData)]),
    (DDSFunc.DynamicData_get_type_kind, None, ctypes.c_ulong, [ctypes.POINTER(DDSType.DynamicData)]),
    
    (DDSFunc.DynamicDataWriter_narrow, check_none, ctypes.POINTER(DDSType.DynamicDataWriter), [ctypes.POINTER(DDSType.DataWriter)]),
    (DDSFunc.DynamicDataWriter_write, check_code, DDS_ReturnCode_t, [ctypes.POINTER(DDSType.DynamicDataWriter), ctypes.POINTER(DDSType.DynamicData), ctypes.c_void_p]),
    
    (DDSFunc.TypeCode_kind, check_ex, ctypes.c_ulong, [ctypes.POINTER(DDSType.TypeCode), ctypes.POINTER(DDS_ExceptionCode_t)]),
    (DDSFunc.TypeCode_member_count, check_ex, ctypes.c_ulong, [ctypes.POINTER(DDSType.TypeCode), ctypes.POINTER(DDS_ExceptionCode_t)]),
    (DDSFunc.TypeCode_member_name, check_ex, ctypes.c_char_p, [ctypes.POINTER(DDSType.TypeCode), ctypes.c_ulong, ctypes.POINTER(DDS_ExceptionCode_t)]),
    (DDSFunc.TypeCode_member_type, check_ex, ctypes.POINTER(DDSType.TypeCode), [ctypes.POINTER(DDSType.TypeCode), ctypes.c_ulong, ctypes.POINTER(DDS_ExceptionCode_t)]),
])

def parse_into_dd(obj, dd):
    kind = dd.get_type_kind()
    if kind == 10:
        assert isinstance(obj, dict)
        tc = dd.get_type()
        for i in xrange(tc.member_count(ex())):
            name = tc.member_name(i, ex())
            kind2 = tc.member_type(i, ex()).kind(ex())
            if kind2 == 6:
                dd.set_double(name, 0, obj[name])
            elif kind2 == 18:
                dd.set_ulonglong(name, 0, obj[name])
            elif kind2 == 10:
                raise NotImplementedError()
                res = DDSFunc.DynamicData_new(None, DDSFunc.DYNAMIC_DATA_PROPERTY_DEFAULT)
                dd.bind_complex_member(res, tc.member_name(i, ex()), 0)
                parse_into_dd(obj[tc.member_name(i, ex())], dd)
                # unbind
                # delete res
            else:
                raise NotImplementedError(kind2)
    else:
        raise NotImplementedError(kind)

class Topic(object):
    def __init__(self, dds, topic_name, data_type):
        self._dds = dds
        self._topic_name = topic_name
        self._data_type = data_type
        del dds, topic_name, data_type
        
        self._support = DDSFunc.DynamicDataTypeSupport_new(self._data_type._TypeSupport_get_typecode(), DDSFunc.DYNAMIC_DATA_TYPE_PROPERTY_DEFAULT)
        self._support.register_type(self._dds._participant, self._data_type._TypeSupport_get_type_name())
        
        self._topic = self._dds._participant.create_topic(
            self._topic_name,
            self._data_type._TypeSupport_get_type_name(),
            DDSFunc.TOPIC_QOS_DEFAULT,
            None,
            0,
        )
        
        self._writer = self._dds._publisher.create_datawriter(
            self._topic,
            DDSFunc.DATAWRITER_QOS_DEFAULT,
            None,
            0,
        )
        
        self._dyn_narrowed_writer = DDSFunc.DynamicDataWriter_narrow(self._writer)
    
    def send(self, msg):
        sample = self._support.create_data()
        
        parse_into_dd(msg, sample)
        self._dyn_narrowed_writer.write(sample, ctypes.create_string_buffer(struct.pack('<16sII', '', 16, 0))) # XXX ugly
        
        self._support.delete_data(sample)
    
    def recv(self):
        # XXX make actually receive something
        DDS_DynamicData_get_long(sample, ctypes.byref(theInteger), "myInteger", DDS_DYNAMIC_DATA_MEMBER_ID_UNSPECIFIED);
    
    def __del__(self):
        self._dds._publisher.delete_datawriter(self._writer)
        self._dds._participant.delete_topic(self._topic)
        self._support.unregister_type(self._dds._participant, self._data_type._TypeSupport_get_type_name())
        self._support.delete()

class DDS(object):
    def __init__(self, domain_id=0):
        self._participant = DDSFunc.DomainParticipantFactory_get_instance().create_participant(
            domain_id,
            DDSFunc.PARTICIPANT_QOS_DEFAULT,
            None,
            0,
        )
        
        self._publisher = self._participant.create_publisher(
            DDSFunc.PUBLISHER_QOS_DEFAULT,
            None,
            0,
        )
    
    def get_topic(self, topic_name, data_type):
        # XXX cache this to handle it being called multiple times
        return Topic(self, topic_name, data_type)
    
    def __del__(self):
        self._participant.delete_publisher(self._publisher)
        
        # very slow for some reason
        DDSFunc.DomainParticipantFactory_get_instance().delete_participant(self._participant)


class LibraryType(object):
    def __init__(self, lib, name):
        self._lib, self._name = lib, name
        del lib, name
        
        assert self._TypeSupport_get_type_name() == self._name
    
    def _TypeSupport_get_typecode(self):
        f = getattr(self._lib, self._name + '_get_typecode')
        f.argtypes = []
        f.restype = ctypes.POINTER(DDSType.TypeCode)
        f.errcheck = check_none
        return f()
    
    def _TypeSupport_get_type_name(self):
        f = getattr(self._lib, self._name + 'TypeSupport_get_type_name')
        f.argtypes = []
        f.restype = ctypes.c_char_p
        f.errcheck = check_none
        return f()

class Library(object):
    def __init__(self, so_path):
        self._lib = ctypes.CDLL(so_path)
    
    def __getattr__(self, attr):
        return LibraryType(self._lib, attr)

def main():
    import time
    
    d = DDS()
    l = Library('../build/DDSMessages/libddsmessages2.so')
    t = d.get_topic('newtopic2', l.DepthMessage)
    x = 1.
    while True:
        x += 1.245
        t.send(dict(timestamp=int(x*100), depth=x, humidity=x+2, thermistertemp=x+3, humiditytemp=x+4))
        time.sleep(1)

if __name__ == '__main__':
    main()
