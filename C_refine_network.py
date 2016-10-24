from lingpy import *
import networkx as nx
import igraph
from sys import argv
from lingpy.thirdparty import linkcomm

# preprocessing, load data, and modify the rimes
wl = Wordlist('O_shijing.tsv', col='shijing', row='stanza')

# define colors for vowels
colors = {
    'ə' : ['black', 'red'],
    'a' : ['white', 'green'],
    'u' : ['white', 'blue'],
    'e' : ['white', 'gray'],
    'i' : ['black', 'yellow'],
    'o' : ['black', 'cyan']
    }

D = {}
for k in wl:
    
    yunbu = wl[k,'ocbsyun']
    yunbu = yunbu.replace('A','a')
    yunbu = yunbu.replace('\u0325', '')
    yunbu = ''.join([x for x in yunbu if x not in '[]()ʔ'])
    
    yunbu2 = wl[k,'yun']
    if 'ʔ' in wl[k,'yun']:
        shang = yunbu + 'ʔ'
    else:
        shang = yunbu

    if '[' in yunbu2 or '(' in yunbu2:
        yunbu2 = '?'
    else:
        yunbu2 = '!' 

    D[k] = (yunbu,yunbu2, shang)

wl.add_entries('rime', D, lambda x: x[0])
wl.add_entries('certainty', D, lambda x: x[1])
wl.add_entries('shangsheng', D, lambda x: x[2])

# make the graph
_G = nx.Graph()
visited = []
excluded = 0

etd = wl.get_etymdict(ref='rhyme')

for row in wl.rows:
    print('[i] Analyzing stanza {0}...'.format(row))
    # get all stanzas
    idxs = wl.get_list(row=row, flat=True)
    
    # get the rime data
    rimes = [wl[idx, 'rime'] for idx in idxs]
    # get the words judged to be riming
    cogids = [wl[idx,'rhyme'] for idx in idxs]
    # get the readings
    readings = [wl[idx, 'ocbs'] for idx in idxs]
    # get the character
    chars = [wl[idx, 'character'] for idx in idxs]
    # get the sections
    sections = [wl[idx, 'raw_section'] for idx in idxs]
    # mch 
    mchs = [wl[idx, 'mchascii'] for idx in idxs]
    shangsheng = [wl[idx,'shangsheng'] for idx in idxs]

    # certainty
    certainties = [wl[idx, 'certainty'] for idx in idxs]
    
    # visited_tmp to trace multi-chars in one set
    visited_tmp = []

    # now start to populate the graph
    for i,(idxA, rimeA,cogidA,readingA,charA,secA, certA, sA) in enumerate(
            zip(idxs, rimes, cogids, readings, chars, sections, certainties,
                shangsheng)):
        for j,(idxB, rimeB,cogidB,readingB,charB, secB, certB, sB) in enumerate(
                zip(idxs, rimes, cogids, readings, chars, sections,
                    certainties, shangsheng)):
            if i < j:
                if charA not in _G:
                    _G.add_node(
                            charA,
                            rime = rimeA,
                            cogid = cogidA,
                            reading = readingA,
                            color = colors[rimeA[0]][1] if rimeA else '',
                            labelcolor = colors[rimeA[0]][0] if rimeA else '',
                            occurrence = len([k for k in wl if
                                wl[k,'character'] == charA]),
                            mch = mchs[i],
                            certainty = certA,
                            shangsheng=sA,
                            stanza = ','.join([wl[k,'stanza'] for k in wl if
                                wl[k,'character'] == charA]),
                            )
                
                if charB not in _G:
                    _G.add_node(
                            charB,
                            rime = rimeB,
                            cogid = cogidB,
                            reading = readingB,
                            color = colors[rimeB[0]][1] if rimeB else '',
                            labelcolor = colors[rimeB[0]][0] if rimeB else '',
                            occurrence = len([k for k in wl if
                                wl[k,'character'] == charB]),
                            stanza = ','.join([wl[k,'stanza'] for k in wl if
                                wl[k,'character'] == charB]),
                            mch = mchs[j],
                            certainty = certB,
                            shangsheng=sB
                            )
                
                # check for section identity
                if (secA, secB) not in visited and charA != charB and cogidA == \
                    cogidB and cogidA and (charA,charB) not in visited_tmp and \
                    (charB,charA) not in visited_tmp:
                    
                    visited += [(secA, secB)]
                    visited_tmp += [(charA, charB), (charB, charA)]
                    try:
                        _G.edge[charA][charB]['occurrence'] += 1
                        _G.edge[charA][charB]['stanza'] += [row]
                        _G.edge[charA][charB]['woccurrence'] += 1 / len(etd[cogidA][0])
                    except KeyError:
                        _G.add_edge(charA, charB, occurrence=1, 
                                stanza=[row],
                                woccurrence = 1 / len(etd[cogidA][0])
                                )
                else:
                    excluded += 1

# check for external and internal edges
N = nx.Graph()
for nA, nB, data in _G.edges(data=True):
    rA = _G.node[nA]['rime']
    rB = _G.node[nB]['rime']

    if rA and rB:

        if rA not in N:
            N.add_node(rA, occurrence=1, color = _G.node[nA]['color'],
                    lcolor=_G.node[nA]['labelcolor'])
        else:
            N.node[rA]['occurrence'] += 1
        if rB not in N:
            N.add_node(rB, occurrence=1, color =_G.node[nB]['color'],
                    lcolor=_G.node[nB]['labelcolor'])
        else:
            N.node[rB]['occurrence'] += 1

        # add edges, if rA not equal to rB
        if rA != rB:
            try:
                N.edge[rA][rB]['occurrence'] += 1
            except KeyError:
                N.add_edge(rA, rB, occurrence = 1)

for nA,nB,data in _G.edges(data=True):

    data['stanza'] = ','.join(data['stanza'])


# convert stuff to igraph
G = igraph.Graph()
for node,data in _G.nodes(data=True):
    G.add_vertex(name=node, **data)
for nodeA, nodeB, data in _G.edges(data=True):
    G.add_edge(nodeA, nodeB, **data)



# do the same for the N graph
_N = igraph.Graph()
for node,data in N.nodes(data=True):
    _N.add_vertex(name=node, **data)
for nodeA, nodeB, data in N.edges(data=True):
    if data['occurrence'] >= 10:
        _N.add_edge(nodeA, nodeB, **data)

nx.write_yaml(N, 'R_rime_graph.yaml') 


if 'communities' in argv:
    C = _N.community_infomap(
            edge_weights = 'occurrence',
            vertex_weights = 'occurrence'
            )
    for community,name in zip(C.membership, _N.vs['name']):
        N.node[name]['infomap'] = community

    print('[i] Calculated communities for rhyme groups')
    
    # check statistics, for example, get
    
    C = G.community_infomap(
            edge_weights = 'woccurrence',
            vertex_weights = 'occurrence'
            )
    for community,name in zip(C.membership, G.vs['name']):
        _G.node[name]['infomap'] = community

    print('[i] Calculated communities for rhyme words.')



from html import parser
nx.write_gml(N, 'R_rime_transitions.gml')
with open('R_rime_transitions.gml') as f:
    _t = f.read()
with open('R_rime_transitions.gml','w') as f:
    f.write(parser.unescape(_t))

nx.write_gml(_G, 'R_infomap.gml')
with open('R_infomap.gml') as f:
    _t = f.read()
with open('R_infomap.gml','w') as f:
    f.write(parser.unescape(_t))
nx.write_yaml(_G, 'R_infomap.yaml')



