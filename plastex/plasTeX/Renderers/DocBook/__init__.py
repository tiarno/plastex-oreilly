#!/usr/bin/env python
import re
from plasTeX.Renderers.PageTemplate import Renderer as _Renderer

class DocBook(_Renderer):
    """ Renderer for DocBook documents """
    fileExtension = '.xml'
    imageTypes = ['.png','.jpg','.jpeg','.gif']
    vectorImageTypes = ['.svg']

Renderer = DocBook
