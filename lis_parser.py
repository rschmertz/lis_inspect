
#God, I hope this makes it simpler

import sys, re, types

vmode = False #verbose

class nodeobject:
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
            print ('dostuff not defined for', self.__class__.__name__)

    def addchild(self, new_child):
        name = new_child.node_type
        if name not in self.children:
            if new_child.isListMember:
                self.children[name] = [new_child]
            else:
                self.children[name] = new_child
        else:
            # This is a type that can have multiple entries
            # in the parent object
            if not isinstance(self.children[name], list):
                el = self.children[name]
                self.children[name] = [el]
            self.children[name].append(new_child)
        new_child.parasitize(self)

    def getchild(self, tag):
        return self.children.get(tag)

    def getchildren(self, tag):
        return self.children.get(tag, [])

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


class _dbobject(nodeobject):
    '''
    This is the object for the whole parsed database
    '''
    def __init__(self, parent, attrs):
        nodeobject.__init__(self, parent, 'The DB', attrs)
        self.pointdir = {}

class _gt_node:
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

class _grammar_tree:
    def __init__(self, model):
        self.top_node = _gt_node('TOP', None)
        self.tag_lookup = set(['top'])
        #self.tag_lookup = {}
        self.curr = self.top_node
        #add something about the current actual data node here, so that we can
        #move up the db tree as we move up the grammar tree

        self.load_graph(model, self.curr)

    def add_child(self, parent, child_tag, the_class):
        if isinstance(parent, str):
            print ('looked up parent', parent)
        else:
            parent_node = parent
        child = _gt_node(child_tag, parent_node)
        #print type(parent_node)
        parent_node.add_child(child_tag, child)
        self.tag_lookup.add(child_tag)
        child.add_class(the_class)
        return child

    def walk_tree(self):
        def helper(node, count):
            print ('  ' * count, node.tag)
            for kid in node.kids.keys():
                helper(node.kids[kid], count + 1)
        helper(self.kids['TOP'], 0)

    def load_graph(self, graph, node):
        if not graph:
            return
        for tuple in graph:
            nu_node = self.add_child(node, tuple[0], tuple[1])
            self.load_graph(tuple[2], nu_node)

def _tokenize(s):
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

def _line_get(thefile):
    '''
    Scan for lines with valid syntax(???).  Comment lines are ignored.  Sets
    of lines w/ continuations are joined into one.
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
        print ('returning nada')
        return '',{}
    toklist = _tokenize(rv)
    #print 'returning element type', toklist[0]
    return toklist[0][1:-1], _load_attrs(toklist[1:])

def _load_attrs(tl):
    d = {}
    while len(tl) > 1:
        # Load the dictionary
        d[tl[0]] = tl[1]
        # dispense with the first key-value pair
        tl = tl[2:]
    return d

class parser:
    def __init__(k, grammar_def, filename):
        k.infile = open(filename)
        k.gt = _grammar_tree(grammar_def)

        k.db = _dbobject(None, {})
        k.db.g_node = k.gt.top_node
        k.curr = k.db
        k.tag, k.attrs = _line_get(k.infile)
        if not k.tag:
            print ("file contains no tags")
            sys.exit(1)

    def showstuff(self):
        for p in self.db.children['TLM_POINT']:
            print ('->', p.attrs['TLM_MNEMONIC'])
            l = p.children['TLM_LOCATION']
            if type(l) != types.ListType:
                l = [l]
            for x in l:
                print ('---->', x.attrs['START_BIT'])

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
           Gets a complete (i.e., top-level) item, e.g., a tlm_point or a global
        '''
        # Warning: assuming parser is at the sort-of-top level
        node = self.curr
        if node != self.db:
            print ("get_item did not start out at top_node")
            #sys.exit(1)
            return None
        else:
            if vmode:
                print ('started out at top node')
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
                self.tag, self.attrs = _line_get(self.infile)
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
            self.tag, self.attrs = _line_get(self.infile)

