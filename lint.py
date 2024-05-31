"""
# Joseph Kessler
# 2024 Jan 27
# lint.py
################################################################################
# Joe Kessler's Python code style tools
"""

################################################################################
############################## Prepend Docstrings ##############################
################################################################################

# https://peps.python.org/pep-0257/#handling-docstring-indentation
from inspect import cleandoc
def trim(func):
    """Trims multiline docstring indentation."""
    func.__doc__ = cleandoc(func.__doc__)
    return func

# https://stackoverflow.com/questions/5929107/decorators-with-parameters
# doesn't work with idle :(
# maybe it does?  it was complaining before, but its ok now?? strange.
def docstring(doc):
    """Decorator factory that assigns a docstring to a function."""
    def assign_docstring(func):
        func.__doc__ = cleandoc(doc)
        return trim(func)
    return assign_docstring

################################################################################
######################## Generate Python Comment Blocks ########################
################################################################################

@docstring("""
# Formats a paragraph to a given width.
# 
# Arguments:
# para: str -- paragraph to be formatted.  Newlines deleted.
#
# Keyword arguments:
# width: str(default: 78) -- block width
# tab: str(default: '    ') -- initial tab comment for long strings.
""")
def format_comment_paragraph(para, width=78, tab=' '*4):
    words = filter(None, para.replace('\n',' ').split(' '))
    words = [line.strip() for line in words]
    para = ' '.join(words)
    
    if len(para) <= width:
        return para

    class Pgraph:
        def __init__(self):
            self.para = ''
            self.line = tab
        def __iadd__(self, line):
            if len(self.para) == 0:
                self.para = self.line
            else:
                self.para = '\n'.join([self.para, line])
            self.line = ''
            return self 
        def append_word(self, word):
            line = self.line + word
            if len(line) < width:
                line += ' '
                self.line = line
            elif len(line) == width:
                self += line
            else: # line too long.
                # Check if word will fit on next line
                if len(word) <= width:
                    self += self.line
                    self.append_word(word)
                else: # word alone wont fit. Slice it up!
                    self += line[:width-1]+'-'
                    self.append_word(line[width-1:])

    pg = Pgraph()
                
    for word in words:
        pg.append_word(word)
    pg.para = '\n'.join([pg.para, pg.line])
    return pg.para

@docstring("""
# Formats a paragraph as a comment to a given width.
# 
# Arguments:
# para: str -- paragraph to be formatted.  Newlines deleted.
#
# Keyword arguments:
# width: int(default: 80) -- block width
# prefix: str(default: '# ') -- comment prefix
# suffix str(default: '') -- comment suffix.  If missing, does not include any right padding.
# tab str(default: '    ') -- initial tab comment for long strings.
""")
def generate_comment_paragraph(para, width=80, prefix='# ', suffix='', tab=' '*4):
    para = para.strip()
    pad = width - len(prefix+suffix)
    para = format_comment_paragraph(para, width=pad, tab=tab)
    if suffix == '':
        para = '\n'.join([prefix + line for line in para.split('\n')])
    else:
        para = '\n'.join([prefix + line.ljust(pad) + suffix for line in para.split('\n')])
    print(para)
    #return para

@docstring("""
########################################
######## Generate Comment Block ########
########################################
#
# Arguments:
# name: string -- string to be formatted
#
# Keyword arguments:
# width: int(default: 80) -- block width
# char: str(default: '#') -- block fill character
""")
def generate_comment_block(name, width=80, char='#'):
    s = char*width
    name = " %s "%name
    lpad = (width-len(name))//2
    rpad = width-len(name)-lpad
    name = char*lpad + name + char*rpad
    s = '\n'.join([s, name, s])
    print(s)
    #return s

if __name__ == "__main__":
    print(__doc__)

    print(help(generate_comment_paragraph))
    # https://hipsum.co/?paras=5&type=hipster-centric&start-with-lorem=1
    para = """
I'm baby portland
actually typewriter stumptown pitchfork enamel pin truffaut yuccie umami synth kitsch blog. Microdosing tumeric
master cleanse cronut portland cred meh dreamcatcher copper mug. Bodega boys celiac kale chips green juice DIY. XOXO farm-to-table
chicharrones ascot vibecession trust fund. Pop-up hexagon retro jean shorts, tumeric synth cloud bread jawn succulents. Microdosing la croix
gluten-free, deep v twee photo booth distillery glossier four dollar toast fam kitsch sus asymmetrical vice.
    """
    print("generate_comment_paragraph('disestablishmentarianism', width=10)")
    generate_comment_paragraph('disestablishmentarianism', width=10)
    print()

    print("para =", para)
    print("generate_comment_paragraph(para, width=80)")
    generate_comment_paragraph(para, width=80)
    print()
    
    print(help(generate_comment_block))
    generate_comment_block('hello!')

