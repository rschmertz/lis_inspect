#!/usr/bin/env python

import sys
from epoch_defs import *
from lis_utils import *

def location_lambda(location_bit):
    lbit = location_bit # less typing
    def find_loc(p):
        for loc in (p.getchild('TLM_LOCATION') or []):
            #start_it = int(loc.attrs['START_BIT'])
            #print 'start bit is', start_bit
            if loc.start_bit <= lbit and lbit < (loc.start_bit
                                             + loc.num_bits):
                print (p.name, 'start bit:', loc.start_bit, ', num bits:', loc.num_bits,)
                mode_name = loc.attrs.get('MODE_NAME')
                mode_value = loc.attrs.get('MODE_VALUE')
                if mode_name and mode_value:
                    print ('for', mode_name, 'value', mode_value)
                else:
                    print ('\nno mode for point?')
                return True
        return False
    return find_loc

class epoch_parser(parser):
    def __init__(self, filename):
        parser.__init__(self, everything, filename)

def interact(filename):
    DBp = epoch_parser(sys.argv[1])
    find_point, find_next_point = create_find_item(DBp, 'TLM_POINT')
    find_cmd, find_next_cmd = create_find_item(DBp, 'CMD_DEFINITION')
    import code
    ibanner = '''
       Do queries here.  Create functions to use as predicates to
       find_point, find_next_command, etc.

       Examples: 

          find_point(lambda p: len(p.getchildren('TLM_LIMITS_SET')) > 1)

          find_next_point(location_lambda(115))

          
'''
    code.interact(banner=ibanner, local=dict(globals(), **locals()))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Need a file to parse as 1st arg')
        sys.exit()
    #DBp = dbparser(sys.argv[1])
    #load_db(DBp)
    fdsdfdsf = 9
    #everything = [point_def]
    DBp = epoch_parser(sys.argv[1])
    find_point, find_next_point = create_find_item(DBp, 'TLM_POINT')
    find_cmd, find_next_cmd = create_find_item(DBp, 'CMD_DEFINITION')
    find_evt, find_next_evt = create_find_item(DBp, 'SYSTEM_EVENT')

    find_point(lambda p: len(p.children.get('TLM_LIMITS_SET') or []) > 1)
    find_point(lambda p: p.children.get('TLM_STATE_CONTEXT'))
    find_point(location_lambda(115))
    find_next_point(location_lambda(115))
    find_next_point(lambda p: len(p.children.get('TLM_EUS') or []) > 1)
    find_cmd(lambda c: c.children.get('PRIVILEGE_GROUP'))
    try:
        e = DBp.db.numlist[201]
        print ('Event #201 is', e.name)
    except IndexError:
        print ('Evt 201 out of range')
    xml_out(DBp)
#    find_next_point(lambda p: p.children.get('TLM_STATE_CONTEXT'))
#    find_point(lambda p: p.children.get('TLM_STATE_CONTEXT'))
  
