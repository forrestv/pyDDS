import ctypes
import os
import struct
import sys
import weakref

arch_str = 'x64Linux2.6gcc4.1.1' if sys.maxsize > 2**32 else 'i86Linux2.6gcc4.1.1'
_ddscore_lib = ctypes.CDLL(os.path.join(os.environ['NDDSHOME'], 'lib', arch_str, 'libnddscore.so'), ctypes.RTLD_GLOBAL)
_ddsc_lib = ctypes.CDLL(os.path.join(os.environ['NDDSHOME'], 'lib', arch_str, 'libnddsc.so'))

# Error checkers

class Error(Exception):
    pass

def check_code(result, func, arguments):
    if result != 0:
        raise Error({
            1: 'error',
            2: 'unsupported',
            3: 'bad parameter',
            4: 'precondition not met',
            5: 'out of resources',
            6: 'not enabled',
            7: 'immutable policy',
            8: 'inconsistant policy',
            9: 'already deleted',
            10: 'timeout',
            11: 'no data',
            12: 'illegal operation',
        }[result])

def check_null(result, func, arguments):
    if not result:
        raise Error()
    return result

def check_ex(result, func, arguments):
    if arguments[-1]._obj.value != 0:
        raise Error({
            1: '(user)',
            2: '(system)',
            3: 'bad param (system)',
            4: 'no memory (system)',
            5: 'bad typecode (system)',
            6: 'badkind (user)',
            7: 'bounds (user)',
            8: 'immutable typecode (system)',
            9: 'bad member name (user)',
            10: 'bad member id (user)',
        }[arguments[-1]._obj.value])
    return result

def check_true(result, func, arguments):
    if not result:
        raise Error()

# Function and structure accessors

def get(name, type):
    return ctypes.cast(getattr(_ddsc_lib, 'DDS_' + name), ctypes.POINTER(type)).contents

@apply
class DDSFunc(object):
    pass

@apply
class DDSType(object):
    def __getattr__(self, attr):
        contents = type(attr, (ctypes.Structure,), {})
        
        def g(self2, attr2):
            f = getattr(DDSFunc, attr + '_' + attr2)
            def m(*args):
                return f(self2, *args)
            setattr(self2, attr2, m)
            return m
        # make structs dynamically present bound methods
        contents.__getattr__ = g
        # take advantage of POINTERs being cached to make type pointers do the same
        ctypes.POINTER(contents).__getattr__ = g
        
        setattr(self, attr, contents)
        return contents

DDSType.Topic._fields_ = [
    ('_as_Entity', ctypes.c_void_p),
    ('_as_TopicDescription', ctypes.POINTER(DDSType.TopicDescription)),
]
ctypes.POINTER(DDSType.Topic).as_topicdescription = lambda self: self.contents._as_TopicDescription

DDSType.DynamicDataSeq._fields_ = DDSType.SampleInfoSeq._fields_ = [
    ('_owned', ctypes.c_bool),
    ('_contiguous_buffer', ctypes.c_void_p),
    ('_discontiguous_buffer', ctypes.c_void_p),
    ('_maximum', ctypes.c_ulong),
    ('_length', ctypes.c_ulong),
    ('_sequence_init', ctypes.c_long),
    ('_read_token1', ctypes.c_void_p),
    ('_read_token2', ctypes.c_void_p),
    ('_elementPointersAllocation', ctypes.c_bool),
]

DDSType.InstanceHandle_t._fields_ = [
    ('keyHash_value', ctypes.c_byte * 16),
    ('keyHash_length', ctypes.c_uint32),
    ('isValid', ctypes.c_int),
]
DDS_HANDLE_NIL = DDSType.InstanceHandle_t((ctypes.c_byte * 16)(*[0]*16), 16, False)

'''DDSType.SampleInfo._fields_ = [
    ('sample_state', DDS_SampleStateKind),
    ('view_state', DDS_ViewStateKind),
    ('instance_state', DDS_InstanceStateKind),
    ('source_timestamp', DDS_Time_t),
    ('instance_handle', DDSType.InstanceHandle_t),
    ('publication_handle', DDSType.InstanceHandle_t),
    ('disposed_generation_count', DDS_Long),
    ('no_writers_generation_count', DDS_Long),
    ('sample_rank', DDS_Long),
    ('generation_rank', DDS_Long),
    ('absolute_generation_rank', DDS_Long),
    ('valid_data', DDS_Boolean),
    ('reception_timestamp', DDS_Time_t),
    ('publication_sequence_number', DDS_SequenceNumber_t),
    ('reception_sequence_number', DDS_SequenceNumber_t),
    ('publication_virtual_guid', DDS_GUID_t),
    ('publication_virtual_sequence_number', DDS_SequenceNumber_t),
    ('original_publication_virtual_guid', DDS_GUID_t),
    ('original_publication_virtual_sequence_number', DDS_SequenceNumber_t),
]'''

# some types
enum = ctypes.c_int

DDS_Char = ctypes.c_char
DDS_Wchar = ctypes.c_wchar
DDS_Octet = ctypes.c_ubyte
DDS_Short = ctypes.c_int16
DDS_UnsignedShort = ctypes.c_uint16
DDS_Long = ctypes.c_int32
DDS_UnsignedLong = ctypes.c_uint32
DDS_LongLong = ctypes.c_int64
DDS_UnsignedLongLong = ctypes.c_uint64
DDS_Float = ctypes.c_float
DDS_Double = ctypes.c_double
DDS_LongDouble = ctypes.c_longdouble
DDS_Boolean = ctypes.c_bool
DDS_Enum = DDS_UnsignedLong

DDS_DynamicDataMemberId = DDS_Long
DDS_ReturnCode_t = enum
DDS_ExceptionCode_t = enum
def ex():
    return ctypes.byref(DDS_ExceptionCode_t())
DDS_DomainId_t = ctypes.c_int32
DDS_TCKind = enum

DDS_SampleStateMask = DDS_UnsignedLong
DDS_ViewStateMask = DDS_UnsignedLong
DDS_InstanceStateMask = DDS_UnsignedLong
DDS_StatusMask = DDS_UnsignedLong

DDS_DYNAMIC_DATA_MEMBER_ID_UNSPECIFIED = 0

class TCKind(object):
    NULL = 0
    SHORT = 1
    LONG = 2
    USHORT = 3
    ULONG = 4
    FLOAT = 5
    DOUBLE = 6
    BOOLEAN = 7 
    CHAR = 8
    OCTET = 9
    STRUCT = 10
    UNION = 11
    ENUM = 12
    STRING = 13
    SEQUENCE = 14
    ARRAY = 15
    ALIAS = 16
    LONGLONG = 17
    ULONGLONG = 18
    LONGDOUBLE = 19
    WCHAR = 20
    WSTRING = 21
    VALUE = 22
    SPARSE = 23
    RAW_BYTES = 0x7e
    RAW_BYTES_KEYED = 0x7f

# Function prototypes

_dyn_basic_types = {
    TCKind.LONG: ('long', DDS_Long, (-2**31, 2**31)),
    TCKind.ULONG: ('ulong', DDS_UnsignedLong, (0, 2**32)),
    TCKind.SHORT: ('short', DDS_Short, (-2**15, 2**15)),
    TCKind.USHORT: ('ushort', DDS_UnsignedShort, (0, 2**16)),
    TCKind.LONGLONG: ('longlong', DDS_LongLong, (-2**63, 2**63)),
    TCKind.ULONGLONG: ('ulonglong', DDS_UnsignedLongLong, (0, 2**64)),
    TCKind.FLOAT: ('float', DDS_Float, None),
    TCKind.DOUBLE: ('double', DDS_Double, None),
    TCKind.BOOLEAN: ('boolean', DDS_Boolean, None),
    TCKind.OCTET: ('octet', DDS_Octet, (0, 2**8)),
    TCKind.CHAR: ('char', DDS_Char, None),
    TCKind.WCHAR: ('wchar', DDS_Wchar, None),
}
def _define_func((p, errcheck, restype, argtypes)):
    f = getattr(_ddsc_lib, 'DDS_' + p)
    if errcheck is not None:
        f.errcheck = errcheck
    f.restype = restype
    f.argtypes = argtypes
    setattr(DDSFunc, p, f)
map(_define_func, [
    ('DomainParticipantFactory_get_instance', check_null, ctypes.POINTER(DDSType.DomainParticipantFactory), []),
    ('DomainParticipantFactory_create_participant', check_null, ctypes.POINTER(DDSType.DomainParticipant), [ctypes.POINTER(DDSType.DomainParticipantFactory), DDS_DomainId_t, ctypes.POINTER(DDSType.DomainParticipantQos), ctypes.POINTER(DDSType.DomainParticipantListener), DDS_StatusMask]),
    ('DomainParticipantFactory_delete_participant', check_code, DDS_ReturnCode_t, [ctypes.POINTER(DDSType.DomainParticipantFactory), ctypes.POINTER(DDSType.DomainParticipant)]),
    
    ('DomainParticipant_create_publisher', check_null, ctypes.POINTER(DDSType.Publisher), [ctypes.POINTER(DDSType.DomainParticipant), ctypes.POINTER(DDSType.PublisherQos), ctypes.POINTER(DDSType.PublisherListener), DDS_StatusMask]),
    ('DomainParticipant_delete_publisher', check_code, DDS_ReturnCode_t, [ctypes.POINTER(DDSType.DomainParticipant), ctypes.POINTER(DDSType.Publisher)]),
    ('DomainParticipant_create_subscriber', check_null, ctypes.POINTER(DDSType.Subscriber), [ctypes.POINTER(DDSType.DomainParticipant), ctypes.POINTER(DDSType.SubscriberQos), ctypes.POINTER(DDSType.SubscriberListener), DDS_StatusMask]),
    ('DomainParticipant_delete_subscriber', check_code, DDS_ReturnCode_t, [ctypes.POINTER(DDSType.DomainParticipant), ctypes.POINTER(DDSType.Subscriber)]),
    ('DomainParticipant_create_topic', check_null, ctypes.POINTER(DDSType.Topic), [ctypes.POINTER(DDSType.DomainParticipant), ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(DDSType.TopicQos), ctypes.POINTER(DDSType.TopicListener), DDS_StatusMask]),
    ('DomainParticipant_delete_topic', check_code, DDS_ReturnCode_t, [ctypes.POINTER(DDSType.DomainParticipant), ctypes.POINTER(DDSType.Topic)]),
    
    ('Publisher_create_datawriter', check_null, ctypes.POINTER(DDSType.DataWriter), [ctypes.POINTER(DDSType.Publisher), ctypes.POINTER(DDSType.Topic), ctypes.POINTER(DDSType.DataWriterQos), ctypes.POINTER(DDSType.DataWriterListener), DDS_StatusMask]),
    ('Publisher_delete_datawriter', check_code, DDS_ReturnCode_t, [ctypes.POINTER(DDSType.Publisher), ctypes.POINTER(DDSType.DataWriter)]),
    
    ('Subscriber_create_datareader', check_null, ctypes.POINTER(DDSType.DataReader), [ctypes.POINTER(DDSType.Subscriber), ctypes.POINTER(DDSType.TopicDescription), ctypes.POINTER(DDSType.DataReaderQos), ctypes.POINTER(DDSType.DataReaderListener), DDS_StatusMask]),
    ('Subscriber_delete_datareader', check_code, DDS_ReturnCode_t, [ctypes.POINTER(DDSType.Subscriber), ctypes.POINTER(DDSType.DataReader)]),
    
    ('DynamicDataTypeSupport_new', check_null, ctypes.POINTER(DDSType.DynamicDataTypeSupport), [ctypes.POINTER(DDSType.TypeCode), ctypes.POINTER(DDSType.DynamicDataTypeProperty_t)]),
    ('DynamicDataTypeSupport_delete', None, None, [ctypes.POINTER(DDSType.DynamicDataTypeSupport)]),
    ('DynamicDataTypeSupport_register_type', check_code, DDS_ReturnCode_t, [ctypes.POINTER(DDSType.DynamicDataTypeSupport), ctypes.POINTER(DDSType.DomainParticipant), ctypes.c_char_p]),
    ('DynamicDataTypeSupport_unregister_type', check_code, DDS_ReturnCode_t, [ctypes.POINTER(DDSType.DynamicDataTypeSupport), ctypes.POINTER(DDSType.DomainParticipant), ctypes.c_char_p]),
    ('DynamicDataTypeSupport_create_data', check_null, ctypes.POINTER(DDSType.DynamicData), [ctypes.POINTER(DDSType.DynamicDataTypeSupport)]),
    ('DynamicDataTypeSupport_delete_data', check_code, DDS_ReturnCode_t, [ctypes.POINTER(DDSType.DynamicDataTypeSupport), ctypes.POINTER(DDSType.DynamicData)]),
    ('DynamicDataTypeSupport_print_data', None, None, [ctypes.POINTER(DDSType.DynamicDataTypeSupport), ctypes.POINTER(DDSType.DynamicData)]),
    
    ('DynamicData_new', check_null, ctypes.POINTER(DDSType.DynamicData), [ctypes.POINTER(DDSType.TypeCode), ctypes.POINTER(DDSType.DynamicDataProperty_t)]),
] + [
    ('DynamicData_get_' + func_name, check_code, DDS_ReturnCode_t, [ctypes.POINTER(DDSType.DynamicData), ctypes.POINTER(data_type), ctypes.c_char_p, DDS_DynamicDataMemberId])
        for func_name, data_type, bounds in _dyn_basic_types.itervalues()
] + [
    ('DynamicData_set_' + func_name, check_code, DDS_ReturnCode_t, [ctypes.POINTER(DDSType.DynamicData), ctypes.c_char_p, DDS_DynamicDataMemberId, data_type])
        for func_name, data_type, bounds  in _dyn_basic_types.itervalues()
] + [
    ('DynamicData_get_string', check_code, DDS_ReturnCode_t, [ctypes.POINTER(DDSType.DynamicData), ctypes.POINTER(ctypes.c_char_p), ctypes.POINTER(DDS_UnsignedLong), ctypes.c_char_p, DDS_DynamicDataMemberId]),
    ('DynamicData_get_wstring', check_code, DDS_ReturnCode_t, [ctypes.POINTER(DDSType.DynamicData), ctypes.POINTER(ctypes.c_wchar_p), ctypes.POINTER(DDS_UnsignedLong), ctypes.c_char_p, DDS_DynamicDataMemberId]),
    ('DynamicData_set_string', check_code, DDS_ReturnCode_t, [ctypes.POINTER(DDSType.DynamicData), ctypes.c_char_p, DDS_DynamicDataMemberId, ctypes.c_char_p]),
    ('DynamicData_set_wstring', check_code, DDS_ReturnCode_t, [ctypes.POINTER(DDSType.DynamicData), ctypes.c_char_p, DDS_DynamicDataMemberId, ctypes.c_wchar_p]),    
    ('DynamicData_bind_complex_member', check_code, DDS_ReturnCode_t, [ctypes.POINTER(DDSType.DynamicData), ctypes.POINTER(DDSType.DynamicData), ctypes.c_char_p, DDS_DynamicDataMemberId]),
    ('DynamicData_unbind_complex_member', check_code, DDS_ReturnCode_t, [ctypes.POINTER(DDSType.DynamicData), ctypes.POINTER(DDSType.DynamicData)]),
    ('DynamicData_get_member_type', check_code, DDS_ReturnCode_t, [ctypes.POINTER(DDSType.DynamicData), ctypes.POINTER(ctypes.POINTER(DDSType.TypeCode)), ctypes.c_char_p, DDS_DynamicDataMemberId]),
    ('DynamicData_get_member_count', None, DDS_UnsignedLong, [ctypes.POINTER(DDSType.DynamicData)]),
    ('DynamicData_get_type', check_null, ctypes.POINTER(DDSType.TypeCode), [ctypes.POINTER(DDSType.DynamicData)]),
    ('DynamicData_get_type_kind', None, DDS_TCKind, [ctypes.POINTER(DDSType.DynamicData)]),
    ('DynamicData_delete', None, None, [ctypes.POINTER(DDSType.DynamicData)]),
    
    ('DynamicDataWriter_narrow', check_null, ctypes.POINTER(DDSType.DynamicDataWriter), [ctypes.POINTER(DDSType.DataWriter)]),
    ('DynamicDataWriter_write', check_code, DDS_ReturnCode_t, [ctypes.POINTER(DDSType.DynamicDataWriter), ctypes.POINTER(DDSType.DynamicData), ctypes.POINTER(DDSType.InstanceHandle_t)]),
    
    ('DynamicDataReader_narrow', check_null, ctypes.POINTER(DDSType.DynamicDataReader), [ctypes.POINTER(DDSType.DataReader)]),
    ('DynamicDataReader_take', check_code, DDS_ReturnCode_t, [ctypes.POINTER(DDSType.DynamicDataReader), ctypes.POINTER(DDSType.DynamicDataSeq), ctypes.POINTER(DDSType.SampleInfoSeq), DDS_Long, DDS_SampleStateMask, DDS_ViewStateMask, DDS_InstanceStateMask]),
    ('DynamicDataReader_return_loan', check_code, DDS_ReturnCode_t, [ctypes.POINTER(DDSType.DynamicDataReader), ctypes.POINTER(DDSType.DynamicDataSeq), ctypes.POINTER(DDSType.SampleInfoSeq)]),
    
    ('TypeCode_name', check_ex, ctypes.c_char_p, [ctypes.POINTER(DDSType.TypeCode), ctypes.POINTER(DDS_ExceptionCode_t)]),
    ('TypeCode_kind', check_ex, DDS_TCKind, [ctypes.POINTER(DDSType.TypeCode), ctypes.POINTER(DDS_ExceptionCode_t)]),
    ('TypeCode_member_count', check_ex, DDS_UnsignedLong, [ctypes.POINTER(DDSType.TypeCode), ctypes.POINTER(DDS_ExceptionCode_t)]),
    ('TypeCode_member_name', check_ex, ctypes.c_char_p, [ctypes.POINTER(DDSType.TypeCode), DDS_UnsignedLong, ctypes.POINTER(DDS_ExceptionCode_t)]),
    ('TypeCode_member_type', check_ex, ctypes.POINTER(DDSType.TypeCode), [ctypes.POINTER(DDSType.TypeCode), DDS_UnsignedLong, ctypes.POINTER(DDS_ExceptionCode_t)]),
    
    ('DynamicDataSeq_initialize', check_true, DDS_Boolean, [ctypes.POINTER(DDSType.DynamicDataSeq)]),
    ('DynamicDataSeq_get_length', None, DDS_Long, [ctypes.POINTER(DDSType.DynamicDataSeq)]),
    ('DynamicDataSeq_get_reference', check_null, ctypes.POINTER(DDSType.DynamicData), [ctypes.POINTER(DDSType.DynamicDataSeq), DDS_Long]),
    
    ('SampleInfoSeq_initialize', check_true, DDS_Boolean, [ctypes.POINTER(DDSType.SampleInfoSeq)]),
    ('SampleInfoSeq_get_length', None, DDS_Long, [ctypes.POINTER(DDSType.SampleInfoSeq)]),
    ('SampleInfoSeq_get_reference', check_null, ctypes.POINTER(DDSType.SampleInfo), [ctypes.POINTER(DDSType.SampleInfoSeq), DDS_Long]),
    
    ('String_free', None, None, [ctypes.c_char_p]),
    
    ('Wstring_free', None, None, [ctypes.c_wchar_p]),
])

def write_into_dd_member(obj, dd, member_name=None, member_id=DDS_DYNAMIC_DATA_MEMBER_ID_UNSPECIFIED):
    tc = ctypes.POINTER(DDSType.TypeCode)()
    dd.get_member_type(ctypes.byref(tc), member_name, member_id, ex())
    
    kind = tc.kind(ex())
    if kind in _dyn_basic_types:
        func_name, data_type, bounds = _dyn_basic_types[kind]
        if bounds is not None and not bounds[0] <= obj < bounds[1]:
            raise ValueError('%r not in range [%r, %r)' % (obj, bounds[0], bounds[1]))
        getattr(dd, 'set_' + func_name)(member_name, member_id, obj)
    elif kind == TCKind.STRUCT or kind == TCKind.SEQUENCE or kind == TCKind.ARRAY:
        inner = DDSFunc.DynamicData_new(None, get('DYNAMIC_DATA_PROPERTY_DEFAULT', DDSType.DynamicDataProperty_t))
        try:
            dd.bind_complex_member(inner, member_name, member_id)
            try:
                write_into_dd(obj, inner)
            finally:
                dd.unbind_complex_member(inner)
        finally:
            inner.delete()
    elif kind == TCKind.STRING:
        if '\0' in obj:
            raise ValueError('strings can not contain null characters')
        dd.set_string(member_name, member_id, obj)
    elif kind == TCKind.WSTRING:
        dd.set_wstring(member_name, member_id, obj)
    else:
        raise NotImplementedError(kind)

def write_into_dd(obj, dd):
    kind = dd.get_type_kind()
    if kind == TCKind.STRUCT:
        assert isinstance(obj, dict)
        tc = dd.get_type()
        for i in xrange(tc.member_count(ex())):
            name = tc.member_name(i, ex())
            write_into_dd_member(obj[name], dd, member_name=name)
    elif kind == TCKind.ARRAY or kind == TCKind.SEQUENCE:
        assert isinstance(obj, list)
        for i, x in enumerate(obj):
            write_into_dd_member(x, dd, member_id=i+1)
    else:
        raise NotImplementedError(kind)

def unpack_dd_member(dd, member_name=None, member_id=DDS_DYNAMIC_DATA_MEMBER_ID_UNSPECIFIED):
    tc = ctypes.POINTER(DDSType.TypeCode)()
    dd.get_member_type(ctypes.byref(tc), member_name, member_id, ex())
    
    kind = tc.kind(ex())
    if kind in _dyn_basic_types:
        func_name, data_type, bounds = _dyn_basic_types[kind]
        inner = data_type()
        getattr(dd, 'get_' + func_name)(ctypes.byref(inner), member_name, member_id)
        return inner.value
    elif kind == TCKind.STRUCT or kind == TCKind.SEQUENCE or kind == TCKind.ARRAY:
        inner = DDSFunc.DynamicData_new(None, get('DYNAMIC_DATA_PROPERTY_DEFAULT', DDSType.DynamicDataProperty_t))
        try:
            dd.bind_complex_member(inner, member_name, member_id)
            try:
                return unpack_dd(inner)
            finally:
                dd.unbind_complex_member(inner)
        finally:
            inner.delete()
    elif kind == TCKind.STRING:
        inner = ctypes.c_char_p(None)
        try:
            dd.get_string(ctypes.byref(inner), None, member_name, member_id)
            return inner.value
        finally:
            DDSFunc.String_free(inner)
    elif kind == TCKind.WSTRING:
        inner = ctypes.c_wchar_p(None)
        try:
            dd.get_wstring(ctypes.byref(inner), None, member_name, member_id)
            return inner.value
        finally:
            DDSFunc.Wstring_free(inner)
    else:
        raise NotImplementedError(kind)

def unpack_dd(dd):
    kind = dd.get_type_kind()
    if kind == TCKind.STRUCT:
        obj = {}
        tc = dd.get_type()
        for i in xrange(tc.member_count(ex())):
            name = tc.member_name(i, ex())
            obj[name] = unpack_dd_member(dd, member_name=name)
        return obj
    elif kind == TCKind.ARRAY or kind == TCKind.SEQUENCE:
        obj = []
        for i in xrange(dd.get_member_count()):
            obj.append(unpack_dd_member(dd, member_id=i+1))
        return obj
    else:
        raise NotImplementedError(kind)

class Topic(object):
    def __init__(self, dds, name, data_type):
        self._dds = dds
        self.name = name
        self.data_type = data_type
        del dds, name, data_type
        
        self._support = DDSFunc.DynamicDataTypeSupport_new(self.data_type._get_typecode(), get('DYNAMIC_DATA_TYPE_PROPERTY_DEFAULT', DDSType.DynamicDataTypeProperty_t))
        self._support.register_type(self._dds._participant, self.data_type.name)
        
        self._topic = self._dds._participant.create_topic(
            self.name,
            self.data_type.name,
            get('TOPIC_QOS_DEFAULT', DDSType.TopicQos),
            None,
            0,
        )
        
        self._writer = self._dds._publisher.create_datawriter(
            self._topic,
            get('DATAWRITER_QOS_DEFAULT', DDSType.DataWriterQos),
            None,
            0,
        )
        self._dyn_narrowed_writer = DDSFunc.DynamicDataWriter_narrow(self._writer)
        
        self._reader = self._dds._subscriber.create_datareader(
            self._topic.as_topicdescription(),
            get('DATAREADER_QOS_DEFAULT', DDSType.DataReaderQos),
            None,
            0,
        )
        self._dyn_narrowed_reader = DDSFunc.DynamicDataReader_narrow(self._reader)
    
    def send(self, msg):
        sample = self._support.create_data()
        
        try:
            write_into_dd(msg, sample)
            self._dyn_narrowed_writer.write(sample, DDS_HANDLE_NIL)
        finally:
            self._support.delete_data(sample)
    
    def recv(self):
        data_seq = DDSType.DynamicDataSeq()
        DDSFunc.DynamicDataSeq_initialize(data_seq)
        info_seq = DDSType.SampleInfoSeq()
        DDSFunc.SampleInfoSeq_initialize(info_seq)
        self._dyn_narrowed_reader.take(ctypes.byref(data_seq), ctypes.byref(info_seq), 1, get('ANY_SAMPLE_STATE', DDS_SampleStateMask), get('ANY_VIEW_STATE', DDS_ViewStateMask), get('ANY_INSTANCE_STATE', DDS_InstanceStateMask))
        try:
            info = info_seq.get_reference(0)
            return unpack_dd(data_seq.get_reference(0))
        finally:
            self._dyn_narrowed_reader.return_loan(ctypes.byref(data_seq), ctypes.byref(info_seq))
    
    def __del__(self):
        self._dds._publisher.delete_datawriter(self._writer)
        self._dds._subscriber.delete_datareader(self._reader)
        self._dds._participant.delete_topic(self._topic)
        self._support.unregister_type(self._dds._participant, self.data_type.name)
        self._support.delete()

class DDS(object):
    def __init__(self, domain_id=0):
        self._participant = DDSFunc.DomainParticipantFactory_get_instance().create_participant(
            domain_id,
            get('PARTICIPANT_QOS_DEFAULT', DDSType.DomainParticipantQos),
            None,
            0,
        )
        
        self._publisher = self._participant.create_publisher(
            get('PUBLISHER_QOS_DEFAULT', DDSType.PublisherQos),
            None,
            0,
        )
        
        self._subscriber = self._participant.create_subscriber(
            get('SUBSCRIBER_QOS_DEFAULT', DDSType.SubscriberQos),
            None,
            0,
        )
        self._open_topics = weakref.WeakValueDictionary()
    
    def get_topic(self, name, data_type):
        res = self._open_topics.get(name, None)
        if res is not None:
            if data_type != res.data_type:
                raise ValueError('get_topic called with a previous name but a different data_type')
            return res
        res = Topic(self, name, data_type)
        self._open_topics[name] = res
        return res
    
    def __del__(self):
        self._participant.delete_subscriber(self._subscriber)
        self._participant.delete_publisher(self._publisher)
        
        # very slow for some reason
        DDSFunc.DomainParticipantFactory_get_instance().delete_participant(self._participant)


class LibraryType(object):
    def __init__(self, lib, name):
        self._lib, self.name = lib, name
        del lib, name
        
        assert self._get_typecode().name(ex()) == self.name
    
    def _get_typecode(self):
        f = getattr(self._lib, self.name + '_get_typecode')
        f.argtypes = []
        f.restype = ctypes.POINTER(DDSType.TypeCode)
        f.errcheck = check_null
        return f()

class Library(object):
    def __init__(self, so_path):
        self._lib = ctypes.CDLL(so_path)
    
    def __getattr__(self, attr):
        res = LibraryType(self._lib, attr)
        setattr(self, attr, res)
        return res
