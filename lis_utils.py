
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
                print ('Match found:', item.name)
                return item
        item = DBp.get_item()
        while item:
            a.curr_index = a.curr_index + 1
            if item.node_type == tagname and test(item):
                print ('Match found:', item.name)
                return item
            item = DBp.get_item()

        print ('No matches found')
        return None
    def find_first_item(test):
        a.curr_index = 0
        return find_next_item(test)
    return find_first_item, find_next_item

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
    line = line + alist
    if node.children:
        line = line + '>\n'
        out.write(line)
        for kidkey in sorted(node.children.keys()):
            kid = node.children[kidkey]
            if not isinstance(kid, list):
                kidlist = [kid]
            else:
                kidlist = kid
            for k in kidlist:
                xml_node_out(k, indent, out)
        line = ('    ' * indent) + '</' + tagname + '>\n'
        out.write(line)
    else:
        line = line + ' />\n'
        out.write(line)

def xml_out(DBp):
    out = open('nu.xml', 'w')
    out.write('<xml>\n')

    # Load the whole file
    item = DBp.get_item()
    while item:
        item = DBp.get_item()

    # output the points
    kids = DBp.db.children
    for item_type in kids.keys():
        for item in kids[item_type]:
            xml_node_out(item, 0, out)

    out.write('</xml>\n')

