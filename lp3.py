#!/usr/bin/env python

#God, I hope this makes it simpler

import sys, re, types

class nodeobject():
    def __init__(self, parent, attrs):
        self.parent = parent
        self.attrs = attrs
        self.children = {}

    def parasitize(self, parent):
        pass

    def dostuff(self):
        print 'dostuff not defined for', self.__class__.__name__
        
    def addchild(self, name, new_child):
        if not self.children.has_key(name):
            self.children[name] = new_child
        else:
            # This is a type that can have multiple entries
            # in the parent object
            if type(self.children[name]) != types.ListType:
                el = self.children[name]
                self.children[name] = [el]
            self.children[name].append(new_child)
        new_child.parasitize(self)

        

class point(nodeobject):
    def __init__(self, parent, attrs):
        nodeobject.__init__(self, parent, attrs)

    def dostuff(self):
        print 'point name is', self.attrs['TLM_MNEMONIC']

    def parasitize(self, parent):
        try:
            parent.pointlist.append(self)
        except AttributeError:
            parent.pointlist = []
            parent.pointlist.append(self)
        
#     def addchild(name, obj):
#         nodeobject.addchild(self, name, obj)
#         if obj.__class__.__name__ == 'point':
#             pointlist.append(obj)


class dbobject(nodeobject):
    def __init__(self, parent, attrs):
        nodeobject.__init__(self, parent, attrs)
        self.pointdir = {}

point_def = (  'TLM_POINT', point,
               [(  'TLM_VALUE', None, None),
                (  'TLM_STATE_CONTEXT', None,
                   [(  'TLM_STATE', None, None)]),
                (  'TLM_LOCATION', None, None)])

global_def = (  'GLOBAL_VAR', None,
                [(  'GLOBAL_LONG_VALUE', None, None)])

everything = [point_def, global_def]

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
        

class grammar_tree:
    def __init__(self):
        top_node = gt_node('TOP', None)
        self.tag_lookup = {'TOP':top_node}
        #self.tag_lookup = {}
        self.curr = top_node
        #add something about the current actual data node here, so that we can
        #move up the db tree as wee move up the grammar tree

    def add_child(self, parent, child_tag, the_class):
        if type(parent) == types.StringType:
            parent_node = self.tag_lookup[parent]
            print 'looked up parent', parent
        else:
            print 'parent is alreay a node type'
            parent_node = parent
        child = gt_node(child_tag, parent_node)
        print type(parent_node)
        parent_node.add_child(child_tag, child)
        print 'we eon\'t see this'
        self.tag_lookup[child_tag] = child
        child.add_class(the_class)
        return child

    def walk_tree(self):
        def helper(node, count):
            print '  ' * count, node.tag
            for kid in node.kids.keys():
                helper(node.kids[kid], count + 1)
        helper(self.kids['TOP'], 0)

    def handle_tag(self, tag):
        temp = self.curr
        count = 0
        while temp and not temp.kids.has_key(tag):
            print 'searaching for', tag, 'in', temp.tag
            temp = temp.parent
            count = count + 1
        if temp:
            print tag, 'is a valid tag'
            self.curr = temp.kids[tag]
            return self.curr.klass, count
        else:
            return None, 0

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
    tag = ll[0].split()[0][1:-1] # Got that? ;-)
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
        k.gt = grammar_tree()
        if False:
            gt = k.gt
            l1 = gt.add_child('TOP','TLM_POINT', None)
            l2 =    gt.add_child(l1, 'TLM_VALUE', None)
            l2 =    gt.add_child(l1, 'TLM_STATE_CONTEXT', None)
            l3 =       gt.add_child(l2, 'TLM_STATE', None)
            l2 =    gt.add_child(l1, 'TLM_LOCATION', None)
            l1 = gt.add_child('TOP', 'GLOBAL_VAR', None)
            l2 =    gt.add_child(l1, 'GLOBAL_LONG_VALUE', None)
        else:
            k.load_graph(everything, k.gt.curr)

        k.db = dbobject(None, {})
        k.curr = k.db
        k.tag, k.attrs = line_get(k.infile)

    def load_graph(self, graph, node):
        if not graph:
            return
        for tuple in graph:
            nu_node = self.gt.add_child(node, tuple[0], tuple[1])
            self.load_graph(tuple[2], nu_node)
            
    def do_crap(self):
        while (self.tag):
            cl, uplevels = self.gt.handle_tag(self.tag)
            if cl:
                while uplevels:
                    self.curr = self.curr.parent
                    uplevels = uplevels - 1
                x = cl(self.curr, self.attrs)
                self.curr.addchild(self.tag, x)
                x.dostuff()
                self.curr = x
            self.tag, self.attrs = line_get(self.infile)
        for p in self.db.pointlist:
            print '->', p.attrs['TLM_MNEMONIC']
            l = p.children['TLM_LOCATION']
            if type(l) != types.ListType:
                l = [l]
            for x in l:
                print '---->', x.attrs['START_BIT']

    def get_item(self):
        # Warning: assuming parser is at the sort-of-top level
        node = self.gt.curr
        ''' starts off at 'top', but ever after, it will complete at
        one level below.
        '''
        #new_node = self.gt.

p = parser(sys.argv[1])
p.do_crap()
