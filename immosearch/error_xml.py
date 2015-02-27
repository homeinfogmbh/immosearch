# ./error_xml.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:5b85072a063471aea48a2605194b23c6855353b4
# Generated 2015-02-27 13:51:42.200125 by PyXB version 1.2.5-DEV using Python 3.4.2.final.0
# Namespace http://xml.homeinfo.de/schema/immosearch/1.0

from __future__ import unicode_literals
import pyxb
import pyxb.binding
import pyxb.binding.saxer
import io
import pyxb.utils.utility
import pyxb.utils.domutils
import sys
import pyxb.utils.six as _six

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:60c707e8-be7f-11e4-aba0-7427eaa9df7d')

# Version of PyXB used to generate the bindings
_PyXBVersion = '1.2.5-DEV'
# Generated bindings are not compatible across PyXB versions
if pyxb.__version__ != _PyXBVersion:
    raise pyxb.PyXBVersionError(_PyXBVersion)

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes

# NOTE: All namespace declarations are reserved within the binding
Namespace = pyxb.namespace.NamespaceForURI('http://xml.homeinfo.de/schema/immosearch/1.0', create_if_missing=True)
Namespace.configureCategories(['typeBinding', 'elementBinding'])

def CreateFromDocument (xml_text, default_namespace=None, location_base=None):
    """Parse the given XML and use the document element to create a
    Python instance.

    @param xml_text An XML document.  This should be data (Python 2
    str or Python 3 bytes), or a text (Python 2 unicode or Python 3
    str) in the L{pyxb._InputEncoding} encoding.

    @keyword default_namespace The L{pyxb.Namespace} instance to use as the
    default namespace where there is no default namespace in scope.
    If unspecified or C{None}, the namespace of the module containing
    this function will be used.

    @keyword location_base: An object to be recorded as the base of all
    L{pyxb.utils.utility.Location} instances associated with events and
    objects handled by the parser.  You might pass the URI from which
    the document was obtained.
    """

    if pyxb.XMLStyle_saxer != pyxb._XMLStyle:
        dom = pyxb.utils.domutils.StringToDOM(xml_text)
        return CreateFromDOM(dom.documentElement, default_namespace=default_namespace)
    if default_namespace is None:
        default_namespace = Namespace.fallbackNamespace()
    saxer = pyxb.binding.saxer.make_parser(fallback_namespace=default_namespace, location_base=location_base)
    handler = saxer.getContentHandler()
    xmld = xml_text
    if isinstance(xmld, _six.text_type):
        xmld = xmld.encode(pyxb._InputEncoding)
    saxer.parse(io.BytesIO(xmld))
    instance = handler.rootObject()
    return instance

def CreateFromDOM (node, default_namespace=None):
    """Create a Python instance from the given DOM node.
    The node tag must correspond to an element declaration in this module.

    @deprecated: Forcing use of DOM interface is unnecessary; use L{CreateFromDocument}."""
    if default_namespace is None:
        default_namespace = Namespace.fallbackNamespace()
    return pyxb.binding.basis.element.AnyCreateFromDOM(node, default_namespace)


# Complex type {http://xml.homeinfo.de/schema/immosearch/1.0}Error with content type EMPTY
class Error (pyxb.binding.basis.complexTypeDefinition):
    """
                A generic error
            """
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'Error')
    _XSDLocation = pyxb.utils.utility.Location('/home/rne/Dokumente/Programmierung/python/immosearch/doc/error_xml.xsd', 14, 4)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute code uses Python identifier code
    __code = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'code'), 'code', '__httpxml_homeinfo_deschemaimmosearch1_0_Error_code', pyxb.binding.datatypes.integer)
    __code._DeclarationLocation = pyxb.utils.utility.Location('/home/rne/Dokumente/Programmierung/python/immosearch/doc/error_xml.xsd', 20, 8)
    __code._UseLocation = pyxb.utils.utility.Location('/home/rne/Dokumente/Programmierung/python/immosearch/doc/error_xml.xsd', 20, 8)
    
    code = property(__code.value, __code.set, None, None)

    
    # Attribute msg uses Python identifier msg
    __msg = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'msg'), 'msg', '__httpxml_homeinfo_deschemaimmosearch1_0_Error_msg', pyxb.binding.datatypes.string)
    __msg._DeclarationLocation = pyxb.utils.utility.Location('/home/rne/Dokumente/Programmierung/python/immosearch/doc/error_xml.xsd', 21, 8)
    __msg._UseLocation = pyxb.utils.utility.Location('/home/rne/Dokumente/Programmierung/python/immosearch/doc/error_xml.xsd', 21, 8)
    
    msg = property(__msg.value, __msg.set, None, None)

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __code.name() : __code,
        __msg.name() : __msg
    })
Namespace.addCategoryObject('typeBinding', 'Error', Error)


error = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'error'), Error, location=pyxb.utils.utility.Location('/home/rne/Dokumente/Programmierung/python/immosearch/doc/error_xml.xsd', 11, 4))
Namespace.addCategoryObject('elementBinding', error.name().localName(), error)
