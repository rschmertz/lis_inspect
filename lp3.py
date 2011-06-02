#!/usr/bin/env python

#God, I hope this makes it simpler

import sys, re, types

vmode = True #verbose

class nodeobject():
    def __init__(self, parent, type, attrs):
        self.parent = parent
        self.node_type = type
        self.attrs = attrs
        self.children = {}
        self.isListMember = False
        self.name = 'name not defined for ' + self.__class__.__name__

    def parasitize(self, parent):
        pass

    def dostuff(self):
        if vmode:
            print 'dostuff not defined for', self.__class__.__name__
        
    def addchild(self, new_child):
        name = new_child.node_type
        if not self.children.has_key(name):
            if new_child.isListMember:
                self.children[name] = [new_child]
            else:
                self.children[name] = new_child
        else:
            # This is a type that can have multiple entries
            # in the parent object
            if type(self.children[name]) != types.ListType:
                el = self.children[name]
                self.children[name] = [el]
            self.children[name].append(new_child)
        new_child.parasitize(self)

    def getchild(self, tag):
        return self.children.get(tag)

class listmemberobject(nodeobject):
    '''
       This type of object always occurs in a list.

       Some items (e.g., TLM_STATE_CONTEXT) may exist singly or
       multiply.  Rather than have such a child exist as a direct
       member if it is a singleton, but as a member of a list if it is
       one of many, it is btter to decare it as a member of a list
       from the beginning, to simplify searches.
    '''
    def __init__(self, parent, type, attrs):
        nodeobject.__init__(self, parent, type, attrs)
        self.isListMember = True
        

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

class dbobject(nodeobject):
    '''
    This is the object for the whole parsed database
    '''
    def __init__(self, parent, attrs):
        nodeobject.__init__(self, parent, 'The DB', attrs)
        self.pointdir = {}

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
                   ('GLOBAL_LONG_VALUE', None, None)])

cmd_def =   (  'CMD_DEFINITION', command,
               [(  'DATAWORD_ARG', listmemberobject,
                   [(  'VALUE_RANGE', None, None)]),
                ('PRIVILEGE_GROUP', None, None)])

everything = [point_def, cmd_def]

class gt_node:
    def __init__(self,tag,parent):
        self.parent = parent
        self.tag = tag
        self.kids = {}
        self.klass = None

    def add_child(self, tag, child):
        self.kids[tag] = child

    def add_class(self, klass):
        self.klass = klass or nodeobject
    def get_child(self, tag):
        return self.kids.get(tag, None)

class grammar_tree:
    def __init__(self, model):
        self.top_node = gt_node('TOP', None)
        self.tag_lookup = set(['top'])
        #self.tag_lookup = {}
        self.curr = self.top_node
        #add something about the current actual data node here, so that we can
        #move up the db tree as wee move up the grammar tree

        self.load_graph(model, self.curr)

    def add_child(self, parent, child_tag, the_class):
        if type(parent) == types.StringType:
            print 'looked up parent', parent
        else:
            parent_node = parent
        child = gt_node(child_tag, parent_node)
        #print type(parent_node)
        parent_node.add_child(child_tag, child)
        self.tag_lookup.add(child_tag)
        child.add_class(the_class)
        return child

    def walk_tree(self):
        def helper(node, count):
            print '  ' * count, node.tag
            for kid in node.kids.keys():
                helper(node.kids[kid], count + 1)
        helper(self.kids['TOP'], 0)

    def load_graph(self, graph, node):
        if not graph:
            return
        for tuple in graph:
            nu_node = self.add_child(node, tuple[0], tuple[1])
            self.load_graph(tuple[2], nu_node)
            
def tokenize(s):
    '''
    tokenizes a string in an EPOCH DB.  Assumptions:

    - string is of the form <key value key value ...>
    - key is a simple string of non-whitespace characters
    - value may be as above or a quote-delimited string
      poss. containing whitespace
    '''
    split1 = re.split(' *" *', s)
    #split1 = s.split('"')
    result = []
    #print 'length of split string is', len(split1)
    for t in range(len(split1)):
        if t % 2 == 0:
            result.extend(split1[t].split())
        else:
            #result.append('"' + split1[t] + '"')
            result.append(split1[t])
    return result

contchar = ';;'
contcharlen = len(contchar)

def line_get(thefile):
    '''
    Scan for lines with valid syntax(???).  Comment lines are ignored.  Sets
    of lines w/ continuations are joined into one.  If starting tag is
    not known, throw away new joined line and check for next.
    '''
    ll = [] # line list -- join at the end
    readmore = 1 # Flag -- yuck
    while readmore:
        #print 'in readmore loop'
        l = thefile.readline()
        if not l:
            return '',{}
        l = l.strip()
            #print 'just read:', l
        if l and l[0] == '#':
            l = '' # Treat comments as empty lines
        if not l:
            if not ll: # Got nothin'
                continue
            readmore = 0 # Continuation didn't pan out
        if len(l) >1 and l[-contcharlen:] == contchar:
            l = l[:-contcharlen]
        else:
            readmore = 0
        ll.append(l)
    rv = ' '.join(ll)
    if not rv:
        print 'returning nada'
        return '',{}
    toklist = tokenize(rv)
    #print 'returning element type', toklist[0]
    return toklist[0][1:-1], load_attrs(toklist[1:])

def load_attrs(tl):
    d = {}
    while len(tl) > 1:
        # Load the dictionary
        d[tl[0]] = tl[1]
        # dispense with the first key-value pair
        tl = tl[2:]
    return d

class parser():
    def __init__(k, filename):
        k.infile = open(filename)
        k.gt = grammar_tree(everything)

        k.db = dbobject(None, {})
        k.db.g_node = k.gt.top_node
        k.curr = k.db
        k.tag, k.attrs = line_get(k.infile)
        if not k.tag:
            print "file contains no tags"
            sys.exit(1)

    def showstuff(self):
        for p in self.db.children['TLM_POINT']:
            print '->', p.attrs['TLM_MNEMONIC']
            l = p.children['TLM_LOCATION']
            if type(l) != types.ListType:
                l = [l]
            for x in l:
                print '---->', x.attrs['START_BIT']

    def do_crap2(self):
        last_g_name = None
        while (self.tag):
            g = self.get_item()
            if g == None:
                print 'NO item returned!!!'
            last_g_name = g.attrs.get('VAR_NAME', last_g_name)
        self.showstuff()
        #print 'last global name is', last_g_name
        

    def locate_tag(self, tag):
        '''
           Determines whether and where a tag is found; does not change
           state of parser.
        '''
        gt = self.gt
        if tag not in gt.tag_lookup:
            return None
        temp = self.curr
        while temp and not temp.g_node.get_child(tag):
            #kids.has_key(tag):
            #print 'searaching for', tag, 'in', temp.g_node.tag
            temp = temp.parent
        return temp

    def get_item(self):
        '''
           Gets a complete item, e.g., a tlm_point or a global
        '''
        # Warning: assuming parser is at the sort-of-top level
        node = self.curr
        if node != self.db:
            print "get_tiem did not start out at top_node"
            #sys.exit(1)
            return None
        else:
            if vmode:
                print 'started out at top node'
            pass
        
        item_found = None
        while True:
            while True:
                if not self.tag:
                    # end of file
                    return item_found
                tempnode = self.locate_tag(self.tag)
                if tempnode:
                    break
                self.tag, self.attrs = line_get(self.infile)
            self.curr = tempnode
            if (self.curr == self.db) and item_found:
                return item_found
            child_g_node = tempnode.g_node.get_child(self.tag)
            x = child_g_node.klass(self.curr, self.tag, self.attrs)
            self.curr.addchild(x)
            x.dostuff()
            x.g_node = child_g_node
            self.curr = x
            if not item_found:
                item_found = x
            self.tag, self.attrs = line_get(self.infile)

def create_find_item(DBp, tagname):
    class index_holder:
        def __init__(self):
            self.curr_index = 0
    a = index_holder()
    def find_next_item(test):
        l = DBp.db.children.get(tagname)
        for item in ((l and l[a.curr_index:]) or []):
            a.curr_index = a.curr_index + 1
            if test(item):
                print 'Match found:', item.name
                return item
        item = DBp.get_item()
        while item:
            a.curr_index = a.curr_index + 1
            if item.node_type == tagname and test(item):
                print 'Match found:', item.name
                return item
            item = DBp.get_item()

        print 'No matches found'
        return None
    def find_first_item(test):
        a.curr_index = 0
        return find_next_item(test)
    return find_first_item, find_next_item

def location_lambda(location_bit):
    lbit = location_bit # less typing
    def find_loc(p):
        for loc in (p.getchild('TLM_LOCATION') or []):
            #start_it = int(loc.attrs['START_BIT'])
            #print 'start bit is', start_bit
            if loc.start_bit <= lbit and lbit < (loc.start_bit
                                             + loc.num_bits):
                print p.name, 'start bit:', loc.start_bit, ', num bits:', loc.num_bits,
                print 'for', loc.attrs['MODE_NAME'], 'value', loc.attrs.get('MODE_VALUE')
                
                return True
        return False
    return find_loc

xml_map = {
    'TLM_POINT':'point',
    'TLM_LOCATION':'location'
}

def xml_node_out(node, indent, out):
    indent = indent + 1
    tagname = xml_map.get(node.node_type, node.node_type.lower())
    line = ('    ' * indent) + '<' + tagname + ' '
    alist = ' '.join(['%s="%s"' % (j.lower(), node.attrs[j])
                      for j in sorted(node.attrs.keys())])
    line = line + alist + '>\n'
    out.write(line)
    for kidkey in sorted(node.children.keys()):
        kid = node.children[kidkey]
        if type(kid) != types.ListType:
            kidlist = [kid]
        else:
            kidlist = kid
        for k in kidlist:
            xml_node_out(k, indent, out)

def xml_out(DBp):
    out = open('nu.xml', 'w')
    out.write('<xml>\n')
    l = DBp.db.children.get('TLM_POINT')
    for item in l:
        xml_node_out(item, 0, out)
    item = DBp.get_item()
    while item:
        item = DBp.get_item()

    out.write('</xml>\n')

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print 'Need a file to parse as 1st arg'
        sys.exit()
    #DBp = dbparser(sys.argv[1])
    #load_db(DBp)
    fdsdfdsf = 9
    #everything = [point_def]
    DBp = parser(sys.argv[1])
    find_point, find_next_point = create_find_item(DBp, 'TLM_POINT')
    find_cmd, find_next_cmd = create_find_item(DBp, 'CMD_DEFINITION')

    #DBp.do_crap2()
    find_point(lambda p: len(p.children.get('TLM_LIMITS_SET') or []) > 1)
    find_point(lambda p: p.children.get('TLM_STATE_CONTEXT'))
    find_point(location_lambda(115))
    find_next_point(location_lambda(115))
    find_next_point(lambda p: len(p.children.get('TLM_EUS') or []) > 1)
    xml_out(DBp)
#    find_next_point(lambda p: p.children.get('TLM_STATE_CONTEXT'))
#    find_point(lambda p: p.children.get('TLM_STATE_CONTEXT'))
