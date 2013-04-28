from lis_parser import *

class point(listmemberobject):
    def __init__(self, parent, type, attrs):
        listmemberobject.__init__(self, parent, type, attrs)
        self.name = self.attrs['TLM_MNEMONIC']

    def dostuff(self):
        if vmode:
            print 'point name is', self.name
        pass

    def parasitize(self, parent):
        try:
            #print 'Adding me to parent type ', parent.__class__.__name__
            parent.pointlist.append(self)
        except AttributeError:
            parent.pointlist = []
            parent.pointlist.append(self)

class command(listmemberobject):
    def __init__(self, parent, type, attrs):
        listmemberobject.__init__(self, parent, type, attrs)
        self.name = self.attrs['CMD_MNEMONIC']

    def dostuff(self):
        if vmode:
            print 'command mnemonic is', self.name
        pass

    def parasitize(self, parent):
        return # do I need to do something?
        try:
            #print 'Adding me to parent type ', parent.__class__.__name__
            parent.pointlist.append(self)
        except AttributeError:
            parent.pointlist = []
            parent.pointlist.append(self)

class location(listmemberobject):
    def __init__(self, parent, type, attrs):
        listmemberobject.__init__(self, parent, type, attrs)
        self.start_bit = int(self.attrs['START_BIT'])
        self.num_bits = int(self.attrs['NUM_BITS'])
        
#     def addchild(name, obj):
#         nodeobject.addchild(self, name, obj)
#         if obj.__class__.__name__ == 'point':
#             pointlist.append(obj)

class globalvar(listmemberobject):
    def __init__(self, parent, type, attrs):
        listmemberobject.__init__(self, parent, type, attrs)
        self.name = self.attrs['VAR_NAME']

class global_value(nodeobject):
    def x__init__(self, parent, type, attrs):
        nodeobject.__init__(self, parent, type, attrs)

    def parasitize(self, parent):
        if hasattr(parent, 'value_member'):
            raise 'Global has multiple default value definitions'
        parent.value_member = self

class event(listmemberobject):
    numlist = [] # class-wide list
    def __init__(self, parent, type, attrs):
        listmemberobject.__init__(self, parent, type, attrs)
        self.name = self.attrs['EVENT_NAME']
        num = int(self.attrs['EVENT_NUMBER'])
        self.num = num
        try:
            self.numlist[num] = self
        except IndexError:
            self.numlist.extend([None] * (num - len(self.numlist) + 2))
            self.numlist[num] = self
    @classmethod
    def printlist(self):
        for i in self.numlist:
            if i:
                print i.num, ': ', i.name

point_def = (  'TLM_POINT', point,
               [(  'TLM_VALUE', None, None),
                (  'TLM_STATE_CONTEXT', listmemberobject,
                   [(  'TLM_STATE', None, None)]),
                (  'TLM_LIMITS_SET', listmemberobject, None),
                (  'TLM_EUS', listmemberobject, None),
                (  'TLM_CAL_PAIRS_SET', listmemberobject, None),
                (  'TLM_LOCATION', location, None)])

global_def = (  'GLOBAL_VAR', globalvar,
                [  ('VAR_STATE', None, None),
                   ('VAR_LIMIT', None, None),
                   ('GLOBAL_LONG_VALUE', global_value, None),
                   ('GLOBAL_STRING_VALUE', global_value, None),
                   ('GLOBAL_DOUBLE_VALUE', global_value, None),
                   ('GLOBAL_TIMEVAL_VALUE', global_value, None),
                   ])

cmd_def =   (  'CMD_DEFINITION', command,
               [(  'DATAWORD_ARG', listmemberobject,
                   [(  'VALUE_RANGE', None, None)]),
                ('PRIVILEGE_GROUP', None, None)])

evt_def =   (  'SYSTEM_EVENT', event, None)

everything = [point_def, global_def, cmd_def, evt_def]

