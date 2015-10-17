from lingpy import *

wl = Wordlist('shijing.tsv', col='shijing', row='stanza')

# first make a link between a character in a section and its occurrence as
# rhyme word
chars = []
for k in wl:

    char = wl[k,'character']
    poem = wl[k,'number']
    stanza = wl[k,'stanza']
    section = wl[k,'section_number']
    ocbs = wl[k,'ocbs']
    pwy = wl[k,'pwy']
    mch = wl[k,'mchascii']
    pin = wl[k,'pinyin']
    gls = wl[k,'och_gloss']
    gsr = wl[k,'gsr']
    

    chars += [[k, char, pin, gls, mch, ocbs, pwy, gsr, poem, stanza, section]]

# now assemble poems under their id
poems = {}
for k in wl:
    
    poem = int(wl[k,'number'])
    name = wl[k,'title']
    block = wl[k,'block'] + '·'+wl[k,'chapter']
    rhyme = wl[k,'rhyme']
    arhyme = wl[k,'alternative_rhyme']
    section = wl[k,'raw_section']
    stanza = wl[k,'stanza']
    ocbs = wl[k,'ocbs']
    pwy = wl[k,'pwy']
    mch = wl[k,'mch']
    yun = wl[k,'ocbsyun']
    char = wl[k,'character']
    
    try:
        poems[poem]['sections'] += [[stanza, section, rhyme, arhyme, ocbs, pwy,
            mch, yun, char]]
    except KeyError:
        poems[poem] = { "name" : name, "block" : block }
        poems[poem]['sections'] = [[stanza, section, rhyme, arhyme, ocbs, pwy,
            mch, yun, char]]

import json
with open('js/shijing.js', 'w') as f:

    f.write('var POEMS = '+json.dumps(poems,indent=2)+';\n')
    f.write('var CHARS = '+json.dumps(chars,indent=2)+';\n')

