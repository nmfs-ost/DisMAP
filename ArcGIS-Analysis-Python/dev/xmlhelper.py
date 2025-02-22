# -*- coding: utf-8 -*-
# https://gis.stackexchange.com/questions/209324/editing-arcgis-metadata-elements-using-python
from xml.etree.ElementTree import ElementTree, Element, SubElement, Comment, tostring, parse, fromstring, fromstringlist
from xml.dom import minidom
from xml.sax.saxutils import escape, unescape
import os
import codecs

HTML = {
        '"': "&quot;",
        "'": "&apos;",
        ">": "&gt;",
        "<": "&lt;",
       }

HTML_UNESC = {v:k for k,v in HTML.items()}

class BaseXML(object):
    def __init__(self, xml_file):
        """base class for xml files"""
        self.document = xml_file
        if isinstance(xml_file, list):
            # we have a list of strings?
            self.tree = fromstringlist(xml_file)

        elif isinstance(xml_file, str) and not os.path.isfile(xml_file) and '<' in xml_file:
            # we have a string?
            self.tree = fromstring(xml_file)

        elif os.path.exists(xml_file):
            self.tree = parse(self.document)

        else:
            raise IOError('Invalid Input for XML file')

        self.directory = os.path.dirname(self.document)
        self.root = self.tree.getroot()
        self.parent_map = {}

        # make static copy
        self._backup = parse(self.document).getroot()

        # initialize parent map
        self.updateParentMap()

    @staticmethod
    def iterElm(root, tag_name=None, childrenOnly=True, **kwargs):
        """return generator for tree

        Optional:
            tag_name -- name of tag
            kwargs -- optional key word args to filter by tag attributes

        """
        for tag in root.iter(tag_name):
            if all([tag.get(k) == v for k,v in kwargs.items()]):
                if childrenOnly and tag != root:
                    yield tag

                elif not childrenOnly:
                    yield tag

    def elmHasTags(self, root, tag, **kwargs):
        """tests if there are valid tags

        tag_name -- name of tag to check for
        """
        gen = self.iterElm(root, tag, **kwargs)
        try:
            gen.next()
            return True

        except StopIteration:
            return False

    def findChild(self, parent, child_name, **kwargs):
        """find child anywhwere under parent element

        child_name -- name of tag
        kwargs -- keyword args to filter
        """
        for c in self.iterElm(parent, child_name, **kwargs):
            return c

    def findChildren(self, parent, child_name, **kwargs):
        """find all children anywhwere under parent element,
        returns a list of elements.

        child_name -- name of tag
        kwargs -- keyword args to filter
        """
        return [c for c in self.iterElm(parent, child_name, **kwargs)]

    def validateElm(self, elm, elm_name=None, **kwargs):
        """validates whether input is an Element name or Element object.  If it
        is an Element name, it will return the Element object with that name and
        any additional key word args

        Required:
            elm -- element name or Element object
            elm_name -- name of Element.tag, only used if elm is a string.

        Optional:
            kwargs -- keyword argument filters, required if elm is a string
        """
        if isinstance(elm, Element):
            return elm
        elif isinstance(elm, str):
            return self.getElm(elm_name, **kwargs)

    def updateParentMap(self):
        """updates the parent_map dictionary"""
        self.parent_map = {c:p for p in self.tree.iter() for c in p}

    def countParents(self, elm, parent_name, **kwargs):
        """Count the number of parents an element has of a certain name, does
        heiarchal search

        Required:
            elm -- child element for which to search parents
            parent_name -- name of parent tag

        Optional:
            kwargs -- keyword argument filters
        """
        count = 0
        parent = self.getParent(elm, parent_name, **kwargs)
        while parent != None:
            count += 1
            parent = self.getParent(parent, parent_name, **kwargs)
        return count

    def getParent(self, child, parent_name=None, **kwargs):
        """get parent element by tag name or first parent

        Required:
            child -- child element for which to find parent
            tag_name -- name of tag

        Optional:
            kwargs -- optional key word args to filter by tag attributes

        """
        parent = self.parent_map.get(child)
        if parent is None:
            return None
        if parent_name is None:
            return parent
        else:
            if parent.tag == parent_name and all([parent.get(k) == v for k,v in kwargs.items()]):
                return parent
            else:
                return self.getParent(parent, parent_name, **kwargs)

    def elmHasParentOfName(self, child, parent_name=None, **kwargs):
        """checks if a child element has a parent of an input name

        Required:
            child -- child element for which to find parent
            tag_name -- name of tag

        Optional:
            kwargs -- optional key word args to filter by tag attributes
        """
        return self.getParent(child, parent_name, **kwargs) is not None

    def getElm(self, tag_name, root=None, **kwargs):
        """get specific tag by name and kwargs filter

        Required:
            tag_name -- name of tag

        Optional:
            root -- root element to start with, defaults to the ElementTree
            kwargs -- optional key word args to filter by tag attributes
        """
        for tag in self.iterTags(tag_name, root=root, **kwargs):
            return tag

    def findChildrenWithKeys(self, elm, tag_name=None, keys=[]):
        """finds children of a parent Element of a specific tag and/or if that element has
        attributes matching the names found in input keys list

        Required:
            elm -- root element

        Optional: (should implement one or both of these)
            tag_name -- name of tags to search for
            keys -- list of attribute keys to check for
        """
        if isinstance(keys, str):
            keys = [keys]

        return [c for c in self.iterChildren(elm, tag_name) if c is not None and all(map(lambda k: k in c.keys(), keys))]

    @staticmethod
    def prettify(elem):
        """Return a pretty-printed XML string for the Element."""
        rough_string = tostring(elem, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        pretty =  reparsed.toprettyxml(indent="  ").split('\n')
        return '\n'.join([l for l in pretty if l.strip()])

    def iterTags(self, tag_name=None, root=None, **kwargs):
        """return generator for tree

        Optional:
            tag_name -- name of tag
            root -- optional root tag to start from, if None specified defaults
                to the ElementTree
            kwargs -- optional key word args to filter by tag attributes
        """
        if isinstance(root, Element):
            return self.iterElm(root, tag_name, **kwargs)
        else:
            return self.iterElm(self.tree, tag_name, **kwargs)

    @staticmethod
    def iterChildren(parent, tag=None, childrenOnly=True, **kwargs):
        """iterate all children of an element based on **kwargs filter

        Required:
            parent -- element for which to search children

        Optional:
            tag -- name of tag for filter
            childrenOnly -- return children only, if false, iterator will start
                at parent
            kwargs -- optional key word args to filter by tag attributes
        """
        for elm in parent.iter(tag):
            if all([elm.get(k) == v for k,v in kwargs.items()]):
                if childrenOnly and elm != parent:
                    yield elm

                elif not childrenOnly:
                    yield elm

    def hasTags(self, tag_name, root=None, **kwargs):
        """tests if there are valid tags

        tag_name -- name of tag to check for
        """
        gen = self.iterTags(tag_name, **kwargs)
        try:
            gen.next()
            return True

        except StopIteration:
            return False

    def addElm(self, tag_name, attrib={}, root=None, update_map=True):
        """add SubElement to site or existing element

        Required:
            tag_name -- name of new element

        Optional:
            attrib -- dictionary of attributes for new element
            root -- parent element for which to add element.  If none specified,
                element will be added to <Site> root.
            update_map -- option to update parent map, you may want to disable this
                when making many changes during an iterative process. Default is True.
        """
        if root is None:
            root = self.root
        sub = SubElement(root, tag_name, attrib)
        if update_map:
            self.updateParentMap()
        return sub

    def restore(self):
        """reverts all changes back to the state at which the Site.xml document was
        when this class was initialized
        """
        self.__init__(self.document)

    def save(self):
        """saves the changes"""
        with codecs.open(self.document, 'w', 'utf-8') as f:
            f.write(self.prettify(self.root))

    def __iter__(self):
        """create generator"""
        for elm in iter(self.tree.iter()):
            yield elm