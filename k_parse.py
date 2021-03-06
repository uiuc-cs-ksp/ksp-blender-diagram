from __future__ import print_function
import xml.dom as DOM

import re

LINE_EOF = -1
LINE_BLANK = 0
LINE_ATTRIBUTE = 1
LINE_OPEN_BRAK = 2
LINE_CLOSE_BRAK = 3
LINE_ELEMENT_TYPE = 4

re_blank = re.compile("^\\s*$")
re_attribute = re.compile("^\\s*([\\S]+)\\s*=\\s*(.*?)\\s*$")
re_open_brak = re.compile("^\\s*(\\{)\\s*$")
re_close_brak = re.compile("^\\s*(\\})\\s*$")
re_element_type = re.compile("^\\s*([a-zA-Z_/0-9]+)\\s*$")

from collections import OrderedDict

type_re_map = OrderedDict(
[
    (LINE_BLANK,re_blank),
    (LINE_ATTRIBUTE,re_attribute),
    (LINE_OPEN_BRAK,re_open_brak),
    (LINE_CLOSE_BRAK,re_close_brak),
    (LINE_ELEMENT_TYPE,re_element_type)
])

from collections import defaultdict
multiple_allowed = defaultdict(set)
multiple_allowed["Tech"] = set(["part"])
multiple_allowed["PART"] = set(["link","attN","sym"])
multiple_allowed["CONTRACT"] = set(["body"])
multiple_allowed["sizeCurve"] = set(["key"])


#link is for parts that the current part is parent of.
#attN is for parts that are somehow attached to the current part, could be parent or child.
#srfN is for the child to describe its surface attachment to a parent, with a description of the kind of attachment

#sym is for parts that are members of the same symmetry group as this part.

def next_token_iterator(filelike):
    for line in filelike:
        for TOK, an_re in type_re_map.iteritems():
            foo = an_re.match(line)
            if foo is not None:
                yield TOK, foo
        #
    #
    yield LINE_EOF,(None,)



KSP_XML_BASE = "http://squad.com/ksp_ship"

#namespace, doctype
ksp_doctype_lookup = {
    "CRAFT": (KSP_XML_BASE, None),
    "GAME": (KSP_XML_BASE, None),
    None: (KSP_XML_BASE,None)
}

def new_ksp_document(dom_imp, root_node):
    namespace, doctype = ksp_doctype_lookup.get(root_node,ksp_doctype_lookup.get(None))
    return dom_imp.createDocument(namespace,root_node,doctype)


#https://stackoverflow.com/questions/662624/preserve-order-of-attributes-when-modifying-with-minidom
def parse_ksp_ship(filelike,implied_node="CRAFT"):


    parse_stack = list()

    di = DOM.getDOMImplementation()
    document = new_ksp_document(di,implied_node)
    parse_stack.append(document.documentElement)

    my_iter = next_token_iterator(filelike)
    line_no = 0
    for t_type,match in my_iter:
        line_no += 1
        if t_type == LINE_ATTRIBUTE:
            name,value = match.groups()
            if name in multiple_allowed[parse_stack[-1].tagName]:
                an_element = document.createElement(name)
                a_text_node = document.createTextNode(value)
                an_element.appendChild(a_text_node)
                parse_stack[-1].appendChild(an_element)
            else:
                assert len(parse_stack) > 0, " no stack on line {}, {}".format(line_no,document.toprettyxml())
                assert not parse_stack[-1].hasAttribute(name), "name {} repeated line {}, context {}: ".format(name,line_no,parse_stack[-1].tagName)
                parse_stack[-1].setAttribute(name,value)
        elif t_type == LINE_ELEMENT_TYPE:
            shouldbeopen,_ = my_iter.next()
            assert shouldbeopen == LINE_OPEN_BRAK
            line_no += 1
            if line_no == 2:#NIX the implied element
                document = new_ksp_document(di,match.groups()[0])
                parse_stack = list()
                parse_stack.append(document.documentElement)
            else:
                an_element = document.createElement(match.groups()[0])
                parse_stack[-1].appendChild(an_element)
                parse_stack.append(an_element)
            #
        elif t_type == LINE_CLOSE_BRAK:
            #TODO: put a space or emtpy text node in if the element is childless.
            parse_stack.pop()

    return document

#
# Hotpatching solution from https://stackoverflow.com/a/8429008
#
import xml.dom.minidom as minidom
from collections import OrderedDict
class _MinidomHooker(object):
    def __enter__(self):
        minidom.NamedNodeMap.keys_orig = minidom.NamedNodeMap.keys
        minidom.NamedNodeMap.keys = self._NamedNodeMap_keys_hook

        minidom.Element.init_orig = minidom.Element.__init__
        minidom.Element.__init__ = self._NamedNodeMap_eleminit
        return self

    def __exit__(self, *args):
        minidom.NamedNodeMap.keys = minidom.NamedNodeMap.keys_orig
        del minidom.NamedNodeMap.keys_orig

        minidom.Element.__init__ = minidom.Element.init_orig
        del minidom.Element.init_orig

    @staticmethod
    def _NamedNodeMap_keys_hook(node_map):
        class OrderPreservingList(list):
            def sort(self):
                pass
        return OrderPreservingList(node_map.keys_orig())

    @staticmethod
    def _NamedNodeMap_eleminit(not_self, *args,**kargs):
        minidom.Element.init_orig(not_self,*args,**kargs)
        not_self._attrs = OrderedDict()
        not_self._attrsNS = OrderedDict()



if __name__ == "__main__":
    import sys
    import argparse
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("infile")
    arg_parser.add_argument("outfile",default=None,nargs="?")
    args = arg_parser.parse_args()

    def open_or_stdout(filename_or_None):
        if filename_or_None == None:
            return sys.stdout
        else:
            return open(filename_or_None,"w")

    with open_or_stdout(args.outfile) as outfile:
        with open(args.infile) as infile:

            with _MinidomHooker():
                dom_doc = parse_ksp_ship(infile)
                outfile.write(dom_doc.toprettyxml())
