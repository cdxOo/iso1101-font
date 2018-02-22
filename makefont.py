import sys
import fontforge
import psMat
from pprint import pprint
from xml.dom import minidom # for svg parsing
import inspect

def copy_glyphs_in_place(src, dst, glyphs):

    if type(glyphs) is tuple:
        src.selection.select(('ranges', None), glyphs[0], glyphs[1])
        dst.selection.select(('ranges', None), glyphs[0], glyphs[1])
    else:
        src.selection.select(glyphs)
        dst.selection.select(glyphs)

    src.copy()
    dst.paste()

    return


def import_glyph_from_eps (font, name, width):

    glyph = font.createChar(-1, name)
    glyph.importOutlines('glyphs/boxing/' + name + '.eps')
    glyph.width = width

    return

def import_symbol_from_svg (font, name, codepoint = None, width = None):

    path = 'glyphs/symbols/' + name + '.svg'
    glyph = font.createChar(-1, name)
    glyph.importOutlines(path)

    if width != None:
        glyph.width = width
    else:
        svg = minidom.parse(path);
        glyph.width = float(svg.documentElement.attributes['width'].value)
        width = glyph.width # store width for further use
        svg.unlink() # free memory

    if codepoint != None:
        uni = font.createMappedChar(codepoint)
        uni.addReference(name)
        uni.width = width


    return



latopath = './Lato2OFL/Lato-Regular.ttf'
stixpath = './STIXv2.0.0/STIX2Math.otf'

isopath = './iso1101font.ttf'

iso = fontforge.font()
lato = fontforge.open(latopath)
stix = fontforge.open(stixpath)

iso.ascent = lato.ascent
iso.descent = lato.descent
iso.em = lato.em
iso.encoding = 'UnicodeFull'

stix.em = 2000 # this will scale the font to that size
               # so we can copy the gyphs at the right size

#pprint(inspect.getmembers(stix))

lato_glyphs = [
    ('!', '~'),
    'uni0020', # space
]

for glyphrange in lato_glyphs:
    copy_glyphs_in_place(lato, iso, glyphrange)

symbols = {
    'angularity':       'uni2220', # angle 
    'circular_runout':  'uni2197', # north east arrow
    'circularity':      'uni25cb', # circularity
    'concentricity':    'uni25ce', # bullseye
    'diameter':         'uni2300', # diameter
    'flatness':         'uni23e5', # flatness
    'line_profile':     'uni2312', # arc
    'parallelism':      'uni2afd', # double solidous operator
    'perpendicularity': 'uni27c2', # perpendicularity
    'position':         'uni2316', # position
    'straightness':     'uni23e4', # straightness
    'surface_profile':  'uni2313', # segment
    'symmetry':         'uni232f', # symmetry
    'total_runout':     'uni21D7', # north east double arrow
    'cylindricity':     'uni232d', # cylindricity
}

for name, codepoint in symbols.items():
    import_symbol_from_svg(iso, name, codepoint)

#pen = iso['B'].glyphPen()
#pen.addComponent('uni203E')
#iso['A'].draw(pen)

#pen = None


# all teh currently existing glyphs
# that should have a boxed equivalent
iso.selection.all()
unboxed = list(iso.selection.byGlyphs);

eps_glyphs = {
    # 'Symmetry': 1000, # missing from stix for some reason
    # 'SimpleRun': 1000, # doesnt exist in unicode
    # 'FullRun': 1000, # doesnt exist in unicode

    'BoxL': 823,
    'BoxR': 823,
    'BoxLines': 1300
}

for name, width in eps_glyphs.items():
    import_glyph_from_eps(iso, name, width)

lineswidth = eps_glyphs['BoxLines']

for glyph in unboxed:
    original_name = glyph.glyphname
    boxed_name = glyph.glyphname + '.Boxed'

    iso.createChar(-1, boxed_name)
    boxed = iso[boxed_name]

    boxed.addReference('BoxLines', psMat.scale(glyph.width/lineswidth, 1))
    boxed.addReference(original_name)

    boxed.width = glyph.width
    #boxed.left_side_bearing = glyph.left_side_bearing
    #boxed.right_side_bearing = glyph.right_side_bearing

    #pprint(glyph.glyphname)
    #pprint(glyph.width)
    #pprint(boxed.width)
    #pprint(glyph.width/lineswidth)
    





#print(iso['A'].foreground)

#for glyph in iso.glyphs():
#    print(glyph)

iso.mergeFeature('ligatures.fea')
iso.mergeFeature('contextual-alternatives.fea')

iso.fontname = 'ISO1101Font'

iso.generate(isopath)

iso.close()
lato.close()
