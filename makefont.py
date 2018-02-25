import sys
import os

import fontforge
import psMat
from xml.dom import minidom # for svg parsing
import jinja2

from pprint import pprint
import inspect


class Literal:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

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

def import_glyph_from_svg (font, basedir, name, codepoint = None, width = None):

    path = basedir + name + '.svg'
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

def create_outlined_variant (font, glyph, lines_name, suffix):
    original_name = glyph.glyphname
    outlined_name = glyph.glyphname + suffix

    outlined = iso.createChar(-1, outlined_name)

    # FIXME: we actually need to center the outline after scaling
    # since the scaling seems to be not from the center
    # FIXME: mod lines are incorrectly set up for this
    outlined.addReference(
        lines_name,
        psMat.scale(glyph.width / font[lines_name].width, 1)
    )
    outlined.addReference(original_name)

    outlined.width = glyph.width # reset width
    return;


latopath = './Lato2OFL/Lato-Regular.ttf'
isopath = './build/iso1101-font.ttf'

iso = fontforge.font()
lato = fontforge.open(latopath)

iso.ascent = lato.ascent
iso.descent = lato.descent
iso.em = lato.em
iso.encoding = 'UnicodeFull'

# glyph map
gm = Literal(
    lato = [
        ('!', '~'),
        'uni0020', # space
    ],
    symbols = {
        'angularity':       'uni2220', # angle 
        'circularrunout':   'uni2197', # north east arrow
        'circularity':      'uni25cb', # circularity
        'concentricity':    'uni25ce', # bullseye
        'diameter':         'uni2300', # diameter
        # FIXME we might want to enlarge the flattness svg again and fiddle around with left(right bearing
        'flatness':         'uni23e5', # flatness
        'lineprofile':      'uni2312', # arc
        'parallelism':      'uni2afd', # double solidous operator
        'perpendicularity': 'uni27c2', # perpendicularity
        'position':         'uni2316', # position
        'straightness':     'uni23e4', # straightness
        'surfaceprofile':   'uni2313', # segment
        'symmetry':         'uni232f', # symmetry
        'totalrunout':      'uni21D7', # north east double arrow
        'cylindricity':     'uni232d', # cylindricity
    },

    # we need small caps to make the letters fit the modifier boxes properly
    # unfortunately they are scattered accross the unicode table
    small_caps = {
        'A': 'uni1D00',
        'B': 'uni0299',
        'C': 'uni1D04',
        'D': 'uni1D05',
        'E': 'uni1D07',
        'F': 'uniA730',
        'G': 'uni0262',
        'H': 'uni029C',
        'I': 'uni026A',
        'J': 'uni1D0A',
        'K': 'uni1D0B',
        'L': 'uni029F',
        'M': 'uni1D0D',
        'N': 'uni0274',
        'O': 'uni1D0F',
        'P': 'uni1D18',
        'Q': None, # missing from unicode
        'R': 'uni0280',
        'S': 'uniA731',
        'T': 'uni1D1B',
        'U': 'uni1D1C',
        'V': 'uni1D20',
        'W': 'uni1D21',
        'X': None, # missing from unicode
        'Y': 'uni028F', 
        'Z': 'uni1D22',
    },

    modifier_initializers = [
        'modifier_left',
    ],
    modifier_other = [
        'modifier_lines',
        'modifier_right',

        'modifier_circle',
    ],

    box_initializers = [
        'square_box_left',
        'hex_box_left',
        'roof_box_left',
        'circle_box_left',
    ],
    box_separators = [
        'box_seperator',
    ],
    box_other = [
        'box_lines',

        'square_box_right',
        'hex_box_right',
        'roof_box_right',
    ],

    suffixes = Literal(
        small_caps = '.sc',
        modcircled = '.modcircled',
        modinline = '.modinline',
        modleft = '.modleft',
        modright = '.modright',
        boxed = '.boxed',
    )
)

# store generated/imported glyph names
# will be used for feature file template


generated = Literal(
    basic = None,
    modinline = list(map(
        lambda n: n + gm.suffixes.small_caps + gm.suffixes.modinline,
        gm.small_caps.keys()
    )),
    modcircled = list(map(
        lambda n: n + gm.suffixes.small_caps + gm.suffixes.modcircled,
        gm.small_caps.keys()
    )),
    modleft = list(map(
        lambda n: n + gm.suffixes.small_caps + gm.suffixes.modleft,
        gm.small_caps.keys()
    )),
    modright = list(map(
        lambda n: n + gm.suffixes.small_caps + gm.suffixes.modright,
        gm.small_caps.keys()
    )),

    boxed = None,
    boxed_default = None,
    boxed_modifier_initializers = list(map(
        lambda n: n + gm.suffixes.boxed,
        gm.modifier_initializers
    )),
    boxed_modinline = list(map(
        lambda n: n + gm.suffixes.small_caps + gm.suffixes.modinline + gm.suffixes.boxed,
        gm.small_caps.keys()
    )),
    boxed_modcircled = list(map(
        lambda n: n + gm.suffixes.small_caps + gm.suffixes.modcircled + gm.suffixes.boxed,
        gm.small_caps.keys()
    )),
    boxed_modleft = list(map(
        lambda n: n + gm.suffixes.small_caps + gm.suffixes.modleft + gm.suffixes.boxed,
        gm.small_caps.keys()
    )),
    boxed_modright = list(map(
        lambda n: n + gm.suffixes.small_caps + gm.suffixes.modright + gm.suffixes.boxed,
        gm.small_caps.keys()
    )),
)

for glyphrange in gm.lato:
    copy_glyphs_in_place(lato, iso, glyphrange)

# add the symbol glyphs from svg files
for name, codepoint in gm.symbols.items():
    import_glyph_from_svg(iso, 'glyphs/symbols/', name, codepoint)


# after inserting the symbols we store the currently
# available glyphs for further use
iso.selection.all()
generated.basic = list(map(lambda n: n.glyphname, iso.selection.byGlyphs))

# import modfier outline glyphs
# and create variants that have additional box outlines
modifier_outlines = ( gm.modifier_initializers + gm.modifier_other )
for name in modifier_outlines:
    import_glyph_from_svg(iso, 'glyphs/boxing/', name)

for name, codepoint in gm.small_caps.items():
    sc_name = name + gm.suffixes.small_caps
    sc = iso.createChar(-1, sc_name)

    # latin Q and X have no small caps equivalent
    if codepoint != None:
        lato.selection.select(codepoint)
        iso.selection.select(sc_name)
        lato.copy()
        iso.paste()
    else:
        import_glyph_from_svg(iso, 'glyphs/small-caps/', name + '.sc')

    # make sure the letter is vertically centered within the modifier outlines
    sc.transform(psMat.translate(0, 210)) # we measured that

    circle_width = iso['modifier_circle'].width
    # create circled variant
    circled = iso.createChar(-1, name + gm.suffixes.small_caps + gm.suffixes.modcircled)
    circled.addReference(
        sc_name,
        psMat.translate((circle_width - sc.width) / 2, 0) 
    )
    circled.addReference('modifier_circle')
    circled.width = circle_width

    modifier_lines_width = iso['modifier_lines'].width
    # create left variant
    modifier_left_width = iso['modifier_left'].width
    left = iso.createChar(-1, name + gm.suffixes.small_caps + gm.suffixes.modleft)
    left.addReference('modifier_left')
    left.addReference(
        sc_name,
        psMat.translate(modifier_left_width - (sc.width / 2), 0)
    )
    left.addReference(
        'modifier_lines',
        psMat.compose(
            psMat.scale(sc.width / 2 / modifier_lines_width, 1),
            psMat.translate(modifier_left_width, 0)
        )
    )
    left.width = modifier_left_width + (sc.width / 2)
    # create right variant
    modifier_right_width = iso['modifier_right'].width
    right = iso.createChar(-1, name + gm.suffixes.small_caps + gm.suffixes.modright)
    right.addReference(
        'modifier_right',
        psMat.translate(sc.width / 2, 0)
    )
    right.addReference(sc_name)
    right.addReference(
        'modifier_lines',
        psMat.scale(sc.width / 2 / modifier_lines_width, 1),
    )
    right.width = modifier_left_width + (sc.width / 2)

    # create inline variant
    create_outlined_variant(iso, sc, 'modifier_lines', gm.suffixes.modinline)



# TODO: arrow assembly
arrow_segments = [
    'start', # default start with zero degre angle
    
    'mid_none',
    'mid_circle',
    'mid_bullseye',

    'start90_none',
    'start90_circle',
    'start90_bullseye',

    'end'
]

# import box outline glyphs from svg
box_outlines = ( gm.box_initializers + gm.box_separators + gm.box_other )
for name in box_outlines:
    import_glyph_from_svg(iso, 'glyphs/boxing/', name)


# create glyphs width box outlines
glyphs_that_need_boxing = (
    generated.basic
    + generated.modinline
    + generated.modcircled
    + generated.modleft
    + generated.modright
    + gm.modifier_initializers
    + gm.modifier_other
)
for name in glyphs_that_need_boxing:
    glyph = iso[name]
    create_outlined_variant(iso, glyph, 'box_lines', gm.suffixes.boxed)

generated.boxed = list(map(lambda n: n + gm.suffixes.boxed, glyphs_that_need_boxing))
    #boxed.left_side_bearing = glyph.left_side_bearing
    #boxed.right_side_bearing = glyph.right_side_bearing

    #pprint(glyph.glyphname)
    #pprint(glyph.width)
    #pprint(boxed.width)
    #pprint(glyph.width/lineswidth)
    





#print(iso['A'].foreground)

#for glyph in iso.glyphs():
#    print(glyph)

# prepare data for feature file generation
jinja_context = Literal(
    default_glyphs = generated.basic,

    modinline_glyphs = generated.modinline,
    modcircled_glyphs = generated.modcircled,
    modifier_initializers = gm.modifier_initializers,
    
    box_initializers = gm.box_initializers,
    box_separators = gm.box_separators,
    boxed_glyphs = generated.boxed,

    boxed_modifier_initializers = generated.boxed_modifier_initializers,
    boxed_modinline_glyphs = generated.boxed_modinline,

    moddable_glyphs = gm.small_caps.keys(),
    symbols = gm.symbols.keys(),

    suffixes = gm.suffixes,
)

pprint(jinja_context.__dict__)

rendered = jinja2.Environment(
    loader = jinja2.FileSystemLoader('./features'),
    trim_blocks = True,
    lstrip_blocks = True
).get_template('_main.fea.jinja').render(jinja_context.__dict__) # FIXME __dict__ wtf

with open('./build/iso1101-font.fea', 'w') as fh:
    fh.write(rendered)


#iso.mergeFeature('ligatures.fea')
#iso.mergeFeature('contextual-alternatives.fea')
iso.mergeFeature('build/iso1101-font.fea')

iso.fontname = 'ISO1101Font'

iso.selection.all()
iso.autoHint()
iso.generate(isopath)

iso.close()
lato.close()
