import os, re
import plasTeX.Base as Base
from plasTeX.Packages import hyperref
from plasTeX.Packages.book import ProcessOptions as ProcessDocumentOptions
from plasTeX.Packages.graphics import DeclareGraphicsExtensions, graphicspath

def idgen():
    """ Generate a unique ID """
    i = 1
    while 1:
        yield 'a%.10d' % i
        i += 1

idgen = idgen()

def ProcessOptions(options,document):
    context = document.context
    ProcessDocumentOptions(options,document)
    context.newcounter('exercise', resetby='chapter',
                       format='${thechapter}.${exercise}')

class url(hyperref.url):
   pass

class clearemptydoublepage(Base.Command):pass

class Eqn(Base.Command):
    args = 'self'

class Anchor(Base.Command):
    args = 'label:str'
    def invoke(self, tex):
        Base.Command.invoke(self, tex)
        self.ownerDocument.context.label(self.attributes['label'], self)

class exercisename(Base.Command):pass
class frontmatter(Base.Command):pass
class indexname(Base.Command):pass
class chaptername(Base.Command):pass
class theexercise(Base.Command):pass
class thechapter(Base.Command):pass

class exercise(Base.Environment):
    counter = 'exercise'

class index(Base.Command):
    args = 'termstring'

    def setEntry(self, s, seetype=0):
    #    TYPE_NORMAL = 0
    #    TYPE_SEE = 1
    #    TYPE_SEEALSO = 2
        if type(s) != type(''):
            s = s.textContent
        if s.count('!'):
            priterm, secterm = s.split('!')
            if priterm.count('@'):
                prisort, primary = priterm.split('@')
            else:
                prisort, primary = None, priterm
            if secterm.count('@'):
                secsort, secondary = secterm.split('@')
            else:
                secsort, secondary = None, secterm
        elif s.count('@'):
            prisort, primary = s.split('@')
            secsort, secondary = None, None
        else:
            prisort, primary = None, s
            secsort, secondary = None, None

#        if secondary:
#            self.ownerDocument.userdata.setdefault('index', []).append(\
#                Base.IndexEntry([primary, secondary], self, [prisort, secsort], None, type=seetype))
#        else:
#            self.ownerDocument.userdata.setdefault('index', []).append(\
#                Base.IndexEntry([primary], self, [prisort], None, type=seetype))
        return prisort, primary, secsort, secondary

    def invoke(self, tex):
        Base.Command.invoke(self, tex)
        self.prisort=''
        self.primary=''
        self.secsort=''
        self.secondary=''
        self.ownerDocument.context.label(idgen.next(), self)
        p0,p1,s0,s1 = self.setEntry(self.attributes['termstring'])
        if p0:
            self.prisort = '%s' % p0
        if p1:
            self.primary = '%s' % p1
        if s0:
            self.secsort = '%s' % s0
        if s1:
            self.secondary = '%s' % s1

class scriptN(Base.Command):
       unicode = u'\U0001D4A9'

class uxbar(Base.Command): pass
class uybar(Base.Command): pass
class unhat(Base.Command): pass
class ule(Base.Command): pass
class minus(Base.Command): pass
class lowast(Base.Command): pass
class Erdos(Base.Command): pass
class newstyle(Base.Command):pass
class newtheoremstyle(Base.Command):pass
class theoremstyle(Base.Command):pass
class spacing(Base.Command):pass
class blankpage(Base.Command):pass
class htmlonly(Base.Command):pass
class latexonly(Base.Command):pass
class setlinkstext(Base.Command):pass
class imgsrc(Base.Command):pass

class includegraphics(Base.Command):
    blockType = False
    args = '* [ options:dict ] file:str'
    packageName = 'graphicx'

    def invoke(self, tex):
        res = Base.Command.invoke(self, tex)

        # TODO(downey): there is a bug somewhere that causes this 
        # attribute to be the string representation of a TexFragment object
        # sometimes.
        f = self.attributes['file']

        ext = self.ownerDocument.userdata.getPath(
                      'packages/%s/extensions' % self.packageName, 
                      ['.png','.jpg','.jpeg','.gif','.pdf','.ps','.eps'])
        paths = self.ownerDocument.userdata.getPath(
                        'packages/%s/paths' % self.packageName, ['.'])
        img = None

        # Check for file using graphicspath
        for p in paths:
            for e in ['']+ext:
                fname = os.path.join(p,f+e)
                if os.path.isfile(fname):
                    img = os.path.abspath(fname)
                    break
            if img is not None:
                break

        # Check for file using kpsewhich
        if img is None:
            for e in ['']+ext:
                try: 
                    img = os.path.abspath(tex.kpsewhich(f+e))
                    break
                except (OSError, IOError): 
                    pass 

        options = self.attributes['options']

        if options is not None:
            scale = options.get('scale')
#            if scale is not None:
#                scale = float(scale)
#
#                # TODO(downey): this does not work for PDFs.
#                # as a workaround, I am passing the scale parameter
#                # through as an attribute
#                if img and img.endswith('pdf'):
#                    try:
#                        from pyPdf import PdfFileWriter, PdfFileReader
#                        input = PdfFileReader(file(img),'rb')
#                        page = input.getPage(1)
#                        width,height = input.mediaBox.upperRight
#                        p.mediaBox.upperRight = (width*scale, height*scale)
#
#                        output = PdfFileWriter()
#                        output.addPage(page)
#                        with open(img,'wb') as f:
#                            output.write(f)
#                        self.style['width'] = '%spx' % (width * scale)
#                        self.style['height'] = '%spx' % (height * scale)
#                    except:
#                        self.attributes['scale'] = int(scale*100)
#                elif img:
#                    try:
#                        from PIL import Image
#                        w, h = Image.open(img).size
#                        self.style['width'] = '%spx' % (w * scale)
#                        self.style['height'] = '%spx' % (h * scale)
#                    except:
#                        self.attributes['scale'] = int(scale*100)
                
            height = options.get('height')
            if height is not None:
                self.style['height'] = height

            width = options.get('width')
            if width is not None:
                self.style['width'] = width
                
            def getdimension(s):
                m = re.match(r'^([\d\.]+)\s*([a-z]*)$', s)
                if m and '.' in m.group(1):
                    return float(m.group(1)), m.group(2)
                elif m:
                    return int(m.group(1)), m.group(2)

            keepaspectratio = options.get('keepaspectratio')
            if img is not None and keepaspectratio == 'true' and \
               height is not None and width is not None:
                from PIL import Image
                w, h = Image.open(img).size
                
                height, hunit = getdimension(height)
                width, wunit = getdimension(width)
                
                scalex = float(width) / w
                scaley = float(height) / h
                
                if scaley > scalex:
                    height = h * scalex
                else:
                    width = w * scaley
                    
                self.style['width'] = '%s%s' % (width, wunit)
                self.style['height'] = '%s%s' % (height, hunit)

        self.imageoverride = img

        return res

class DeclareGraphicsExtensions(DeclareGraphicsExtensions):
    packageName = 'graphicx'

class graphicspath(graphicspath):
    packageName = 'graphicx'
