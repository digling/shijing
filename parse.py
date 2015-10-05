import re
import json

meta = json.loads(open('meta.json').read())

data = open('shijing-rhymes.txt')

def parse_line(line):
    
    line = re.sub('<.>','', line)

    rhyme_words = []
    rhyme = ''
    alt_rhyme = ''
    alt = False
    for char in line:
        if char == '?':
            alt = True
        elif char in 'abcdefghijklmnopqrstuvwxyz' and not alt:
            rhyme = char
        elif char in 'abcdefghijklmnopqrstuvwxyz' and alt:
            alt_rhyme = char
            alt = False
        else:
            if rhyme:
                rhyme_words += [(rhyme, alt_rhyme, char)]
                rhyme = ''
                alt_rhyme = ''
                alt = False
            else:
                pass
    if not rhyme_words:
        rhyme_words = [('','','')]
    return rhyme_words

block = ''
chapter = ''
poem = False
empty_line = 0
stanza = 0
verse = 0
comment = ''

D = {}
idx = 1
for _line in data:

    line = _line.strip()

    if not line:
        empty_line += 1
    else:
        empty_line = 0

    if empty_line > 1:
        poem = False
        stanza = 0
        verse = 0
        comment = ''

    if poem and not line:
        stanza += 1
        verse = 0
        comment = ''

    # if the line is not empty, we have interesting information, and we try to
    # parse it
    if line:
        
        if line.startswith('?'):
            comment = line
        elif line in meta and not poem:
            block = line
        elif block and line in meta[block] and not poem:
            chapter = line
        elif not poem and line[0].isdigit():
            number = int(line[:line.index('.')])
            title = line[4:]
            print(number, title, block, chapter)
            poem = True
        elif poem:
            if not stanza:
                stanza = 1
                verse = 1
            else:
                verse += 1
            
            # now let's split stuff up
            sections = ['']
            end_chars = []
            for char in line:
                if char not in ('、。'):
                    sections[-1] += char
                else:
                    end_chars += [char]
                    sections += ['']

            # clean section parts for empty things
            sections = [s for s in sections if s]

            # start adding sections to database
            for i,section in enumerate(sections):
                print(section, end_chars)
                raw_section = ''.join([k for k in section if k not in 'abcdefghijklmn?xyz'])

                rhyme_words = parse_line(section)

                for a,b,c in rhyme_words:      
                    if a:
                        rhyme = str(number)+'.'+str(stanza)+'.'+a
                    else:
                        rhyme = ''
                    if b:
                        alt_rhyme = str(number)+'.'+str(stanza)+'.'+b
                    else:
                        alt_rhyme = ''

                    D[idx] = ['shijing',block, chapter,
                           number, title,str(number)+'.'+str(stanza), verse, i, section,
                            raw_section, end_chars[i], comment,
                            rhyme, alt_rhyme, c]
                    idx += 1



D[0] = ['shijing', 'block', 'chapter', 'number', 'title',
        'stanza','verse','section_number','section','raw_section','endchar',
        'note', 'rhyme', 'alternative_rhyme', 'character']

from lingpy import *
wl = Wordlist(D, row='stanza', col='shijing')
wl.renumber('rhyme')
wl.output('tsv', filename='shijing', formatter='stanza')
