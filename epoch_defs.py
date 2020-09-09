'''
EPOCH .lis file parser implementation
'''

from lis_parser import parser, nodeobject, listmemberobject

vmode = False

'''
   First define class types where desired
'''

class point(listmemberobject):
    def __init__(self, parent, type, attrs):
        listmemberobject.__init__(self, parent, type, attrs)
        self.name = self.attrs['TLM_MNEMONIC']

    def dostuff(self):
        if vmode:
            print ('point name is', self.name)
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
            print('command mnemonic is', self.name)
        pass

    def parasitize(self, parent):
        try:
            #print 'Adding me to parent type ', parent.__class__.__name__
            parent.commandlist.append(self)
        except AttributeError:
            parent.commandlist = []
            parent.commandlist.append(self)

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
            raise Exception('Global has multiple default value definitions')
        parent.value_member = self

class event(listmemberobject):
    def __init__(self, parent, type, attrs):
        listmemberobject.__init__(self, parent, type, attrs)
        self.name = self.attrs['EVENT_NAME']
        num = int(self.attrs['EVENT_NUMBER'])
        self.num = num

    def parasitize(self, parent):
        try:
            #print 'Adding me to parent type ', parent.__class__.__name__
            parent.eventlist.append(self)
        except AttributeError:
            parent.eventlist = []
            parent.eventlist.append(self)

        try:
            parent.numlist[self.num] = self
        except AttributeError:
            parent.numlist = [None] * (self.num + 2)
            parent.numlist[self.num] = self
        except IndexError:
            parent.numlist.extend([None] * (self.num - len(parent.numlist) + 2))
            parent.numlist[self.num] = self

    def dostuff(self):
        pass

'''
   Now that all the desired class types have been defined, describe the node
   hierarchy for all "items" of interest.  The hierarchy description need not
   be complete in order for the parser to work correctly.
'''

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

