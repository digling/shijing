import re
import json
from lingpy import *

meta = json.loads(open('meta.json').read())

data = open('shijing-rhymes.txt')

_ocbs = csv2dict('bsoc.csv', strip_lines=False, header=True)

def get_sagart(char):

    if char in _ocbs:
        pass
    elif sp.gbk2big5(char) in _ocbs:
        char = sp.gbk2big5(char)
    else:
        return ['','','','','','', '', '', '', '', '']

    yun = _ocbs[char][6]
    ini = _ocbs[char][4]
    suf = _ocbs[char][7]
    pre = _ocbs[char][3]
    med = _ocbs[char][5]
    gsr = _ocbs[char][8]
    mch = _ocbs[char][0]
    gls = _ocbs[char][-1]
    pin = _ocbs[char][1]

    if '[' in yun:
        nyun = ''.join([x for x in yun if x not in '[]'])
    else:
        nyun = yun

    gsr_class = ''.join([x for x in gsr if x.isdigit()])
    
    return [pre,ini,med,yun,suf,nyun,gsr,gsr_class,mch,gls,pin]


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
                if rhyme == 'x':
                    rhyme = ''
                if alt_rhyme == 'x':
                    alt_rhyme = ''
                rhyme_words += [(rhyme, alt_rhyme, char)]
                rhyme = ''
                alt_rhyme = ''
                alt = False
            else:
                pass
    if not rhyme_words:
        if line[-1] not in '兮之矣止也':
            rhyme_words = [('','',line[-1])]
        else:
            rhyme_words = [('','',line[-2])]
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

                for j,(a,b,c) in enumerate(rhyme_words):      
                    if a:
                        rhyme = str(number)+'.'+str(stanza)+'.'+a
                    else:
                        rhyme = ''
                    if b:
                        alt_rhyme = str(number)+'.'+str(stanza)+'.'+b
                    else:
                        alt_rhyme = ''

                    D[idx] = [
                            'shijing',
                            block, 
                            chapter,
                            number, 
                            title,str(number)+'.'+str(stanza), 
                            verse, 
                            i+1, 
                            j+1,
                            section,
                            raw_section, 
                            end_chars[i], 
                            comment,
                            rhyme, 
                            alt_rhyme, 
                            c
                            ]
                    idx += 1



D[0] = ['shijing', 'block', 'chapter', 'number', 'title',
        'stanza','verse','section_number','rhyme_number','section','raw_section','endchar',
        'note', 'rhyme', 'alternative_rhyme', 'character']

from lingpy import *
wl = Wordlist(D, row='stanza', col='shijing')
wl.renumber('rhyme')

from lingpyd.plugins.chinese import sinopy as sp
def get_och(char, what):
    
    out = []
    for k,tls in sp._cd.TLS[char].items():
        out += [tls[what]]

    return '/'.join(sorted(set(out)))


# now add the character readings for middle chinese
char2bax = {}
char2och = {}

for k in wl:
    
    char = wl[k,'character']
    if char:
        bax = sp.chars2baxter(char)
        if bax:
            char2bax[k] = ','.join(bax)
        else:
            char2bax[k] = ''
        
        try:
            ochbs = get_och(char, 'OCBS')
        except:
            ochbs = ''

        try:
            ochpw = get_och(char, 'OCH_PAN_WUYUN')
        except:
            ochpw = ''
        try:
            ochyb = get_och(char, 'YUNBU')
        except:
            ochyb = ''

        char2och[k] = [ochbs, ochpw, ochyb]

    else:
        char2bax[k] = ''
        char2och[k] = ['','','']

wl.add_entries('mch', char2bax, lambda x: x)
wl.add_entries('och', char2och, lambda x: x[0])
wl.add_entries('pwy', char2och, lambda x: x[1])
wl.add_entries('yunbu', char2och, lambda x: x[2])
wl.add_entries('sectionid', 'stanza,verse,section_number', lambda x,y:
        '{0}.{1}.{2}'.format(x[y[0]], x[y[1]], x[y[2]]))
D = {}
for k in wl:
    
    char = wl[k,'character']

    ocbs = get_sagart(char)
    
    D[k] = ocbs

for i,itm in enumerate(['preinitial', 'initial', 'medial', 'yun', 'suf',
    'ocbsyun','gsr','gsrclass','mchascii','och_gloss','pinyin']):
    wl.add_entries(itm, D, lambda x: x[i])
wl.add_entries('ocbs', 'preinitial,initial,medial,yun,suf', lambda x,y:
        ' '.join([x[z] for z in y]))



wl.output('tsv', filename='shijing', formatter='stanza')



# make the first graph
import networkx as nx
etd = wl.get_etymdict('rhymeid')
visited = []
G = nx.Graph()
for k in [key for key in etd if key > 0]:
    
    print("[i] Analyzing key {0}...".format(k))
    rhymes = []
    for line in etd[k]:
        rhymes += line
    
    visited2 = []
    for i,idxA in enumerate(rhymes):
        sectionA = wl[idxA,'section']
        ridA = wl[idxA,'rhymeid']
        mchA = wl[idxA,'mch']
        charA = wl[idxA, 'character']
        ochA = wl[idxA, 'och']
        ybA = wl[idxA, 'ocbsyun']
        gsrA = wl[idxA, 'gsrclass']

        for j,idxB in enumerate(rhymes):
            if i < j:
                sectionB = wl[idxB,'section']
                ridB = wl[idxB,'rhymeid']
                mchB = wl[idxB,'mch']
                charB = wl[idxB, 'character']
                ochB = wl[idxB, 'och']
                ybB = wl[idxB, 'ocbsyun']
                gsrB = wl[idxB, 'gsrclass']

                if sectionA == sectionB or sectionA+'/'+sectionB in visited or \
                        sectionB + '/' + sectionA in visited:
                            pass
                else:
                    visited += [sectionA+'/'+sectionB]
                    visited += [sectionB+'/'+sectionA]

                    if charA+'/'+charB not in visited2 and charB + '/'+charA \
                        not in visited2 and charA != charB:

                        visited2 += [charA+'/'+charB, charB+'/'+charA]

                        if charA not in G:
                            G.add_node(
                                    charA,
                                    mch = [mchA],
                                    rid = [ridA],
                                    yunbu = [ybA],
                                    och = [ochA],
                                    gsr = [gsrA],
                                    occ = 1
                                    )
                        else:
                            G.node[charA]['occ'] += 1
                            G.node[charA]['mch'] += [mchA]
                            G.node[charA]['rid'] += [ridA]
                            G.node[charA]['och'] += [ochA]
                            G.node[charA]['yunbu'] += [ybA]
                            G.node[charA]['gsr'] += [gsrA]

                        if charB not in G:
                            G.add_node(
                                    charB,
                                    mch = [mchB],
                                    rid = [ridB],
                                    yunbu = [ybB],
                                    och = [ochB],
                                    gsr = [gsrB],
                                    occ = 1
                                    )
                        else:
                            G.node[charB]['occ'] += 1
                            G.node[charB]['mch'] += [mchB]
                            G.node[charB]['rid'] += [ridB]
                            G.node[charB]['och'] += [ochB]
                            G.node[charB]['yunbu'] += [ybB]
                            G.node[charB]['gsr'] += [gsrB]

                        try:
                            G.edge[charA][charB]['weight'] += 1
                        except:
                            G.add_edge(
                                    charA,
                                    charB,
                                    weight = 1
                                    )

for node, data in G.nodes(data=True):
    data['mch'] = '/'.join(sorted(set(data['mch'])))
    data['rid'] = ','.join([str(x) for x in data['rid']])
    data['och'] = ','.join(sorted(set(data['och'])))
    data['yunbu'] = ','.join(sorted(set(data['yunbu'])))
    #data['pwy'] = ','.join(sorted(set(data['pwy'])))

for nA,nB,data in G.edges(data=True):

    data['nw'] = data['weight'] ** 2 / (G.node[nA]['occ'] + G.node[nB]['occ'] -
            data['weight'])

nx.write_gml(G, 'shijing.gml')

import html.parser

with open('shijing.gml') as f:
    shijing = f.read()
with open('shijing.gml', 'w') as f:
    f.write(html.parser.unescape(shijing))


# get chars which are unresolved
M = {}
for k in wl:
    

    ocbsyun = wl[k,'ocbsyun']
    rid = wl[k,'rhymeid']
    char = wl[k,'character']
    if rid != 0 and not ocbsyun:
        try:
            M[char] += [[wl[k,x] for x in ['stanza','section_number','mch',
            'pwy']]]
        except:
            M[char] = [[wl[k,x] for x in ['stanza', 'section_number','mch',
                'pwy']]]

with open('missing_data.tsv', 'w') as f:
    
    f.write('\t'.join([x.upper() for x in ['ID','character', 'stanza', 'section', 'mch', 'pwy']])+'\n')
    for i,k in enumerate(sorted(M)):

        for line in M[k]:
            f.write('\t'.join([str(x) for x in [i+1, k] + line])+'\n')
        
