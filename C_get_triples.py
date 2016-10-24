import networkx as nx
import pickle
from sys import argv
import html
import igraph
from matplotlib import pyplot as plt
import numpy as np
import matplotlib as mpl
from lingpy import *

# try to read the file
try:
    G = pickle.load(open('bin/infomap.bin','rb'))
except Exception:
    print(Exception)
    G = nx.read_yaml('yaml/infomap.yaml')
    with open('bin/infomap.bin', 'wb') as f:
        pickle.dump(G, f)


def get_infomap(graph):

    g = igraph.Graph()
    for node, data in graph.nodes(data=True):
        g.add_vertex(name=node, **data)
    for nodeA, nodeB, data in graph.edges(data=True):
        g.add_edge(nodeA, nodeB, **data)

    C = g.community_infomap(edge_weights='occurrence', vertex_weights='occurrence')

    for community,name in zip(C.membership, g.vs['name']):
        graph.node[name]['sginfomap'] = community

def sort_triples(triple):

    sAB = sorted([triple[0], triple[2]])
    return sAB[0],triple[1], sAB[1]

def write_gml(graph, path):
    
    with open(path, 'w') as f:
        f.write('\n'.join([html.unescape(x) for x in
            nx.generate_gml(graph)]))
    print("wrote data to file")

if 'degree' in argv:
    N = nx.Graph()
    E = {}
    for node, data in G.nodes(data=True):
        rime = data['rime']
        if rime:
            if rime not in N and rime:
                N.add_node(rime, foc=data['occurrence'], occ=1)
            elif rime:
                N.node[rime]['foc'] += data['occurrence']
                N.node[rime]['occ'] += 1

    for nA, nB, data in G.edges(data=True):
        rA, rB = G.node[nA]['rime'], G.node[nB]['rime']
        if rA and rB:
            try:
                E[rA, rB] += 1
                E[rB, rA] += 1
            except KeyError:
                E[rA, rB] = 1
                E[rB, rA] = 1
        if rA and rB:
            try:
                N.edge[rA][rB]['fweight'] += data['occurrence']
                N.edge[rA][rB]['weight'] += 1
            except KeyError:
                N.add_edge(rA, rB, fweight=data['occurrence'], weight=1)

    write_gml(N, 'networks/rimes.gml')

    deg = nx.degree(N, weight='weight')
    with open('stats/rime_degree.tsv', 'w') as f:
        f.write('Rime\tDegree\n')
        for n,w in sorted(deg.items(), key=lambda x: x[1], reverse=True):
            f.write(n+'\t'+str(w)+'\n')

    with open('stats/edges_rimes.tsv', 'w') as f:
        f.write('RimeA\tRimeB\tOccurrence\n')
        for (a,b),c in sorted(E.items(), key=lambda x: x[1], reverse=True):
            f.write(a+'\t'+b+'\t'+str(c)+'\n')
    
if 'triples' in argv:
    triples = []
    visited = []
    # make subgraph consisting only of nrj-cases
    for nA,dA in G.nodes(data=True):
        print(nA)
        rA = dA['rime']
        mA = dA['mch']
        if rA:
            for nB,dB in G.edge[nA].items():
                rB = G.node[nB]['rime']
                mB = G.node[nB]['mch']
                for nC,dC in G.edge[nB].items():
                    tnodes = tuple(sorted([nA, nB, nC]))
                    if nC != nA and nA not in G.edge[nC] and tnodes not in visited:
                        rC = G.node[nC]['rime']
                        if rA and rB and rC and rA != rB and rB != rC and rA != rC:
                            mC = G.node[nC]['mch']
                            triple = sort_triples([rA, rB, rC])
                            triples += [triple]
                            visited += [tnodes]
    
    triple_sets = sorted(set(triples), key=lambda x: triples.count(x), reverse=True)
    with open('triples.tsv', 'w') as f:
        for triple in triple_sets:
            f.write('{0}\t{1}\t{2}\t{3}\n'.format(triple[0], triple[1], triple[2],
                triples.count(triple)))

if 'subgraph' in argv:
    
    colors = ['red','green','blue', 'lightgray']
    nodes = []
    for node, data in G.nodes(data=True):
        rime = data['rime']
        mch = data['mch']
        if rime and rime[-1] in 'rnj':
            data['extracolor'] = colors['rnj'.index(rime[-1])]
            if data['certainty'] == '?':
                data['extracolor'] = 'gray'

            tmp = mch.replace('X','').replace('H', '')
            if tmp[-1] == 'j':
                data['mchcolor'] = 'red'
            elif tmp[-1] == 'n':
                data['mchcolor'] = 'blue'
            else:
                data['mchcolor'] = 'green'

            nodes += [node]

    S = G.subgraph(nodes)
    for i in range(1,5):
        for nA, nB, data in S.edges(data=True):
            if data['occurrence'] < i:
                S.remove_edge(nA ,nB)
            
            # compare aspects of connection
            rA, rB = G.node[nA]['rime'], G.node[nB]['rime']
            mA, mB = G.node[nA]['mchcolor'], G.node[nB]['mchcolor']

            if rA == rB:
                data['sharedrime'] = 'darkgray'
            else:
                data['sharedrime'] = 'lightgray'
            if mA == mB:
                data['sharedmch'] = 'darkgray'
            else:
                data['sharedmch'] = 'lightgray'
        
        print('calculating infomap')
        get_infomap(S)

        write_gml(S, 'networks/rnj-'+str(i)+'.gml')
    
    # get 'shijing' for finding occurrences of characters
    shijing = Wordlist('O_shijing.tsv', col='shijing', row='stanza')
    etd = shijing.get_etymdict(ref='rhymeid')
    for vowel in ['a','e','i','o','u','ə']:
        nodes = [n for n,d in G.nodes(data=True) if d['rime'] and d['rime'][0] == vowel and
                d['rime'][-1] in 'rnj']
        S = G.subgraph(nodes)
        get_infomap(S)
        write_gml(S, 'gml/subgraph-'+vowel+'rnj.gml')
        print("Wrote {0} subgraph to file.".format(vowel))

        # write the occurrence data to file
        with open('stats/vowel-'+vowel+'rnj.md', 'w') as f:
            imp = -1
            for node,data in sorted(S.nodes(data=True), key=lambda x:
                    x[1]['infomap']):

                ifp = data['infomap']
                mch = data['mch']
                och = data['reading'].replace(' ','')
                rime = data['rime']

                if ifp != imp:
                    imp = ifp
                    f.write('# Infomap Cluster {0}\n\n'.format(imp))

                f.write('## Character [{0}](http://dighl.github.io/shijing/?char={0}) (MCH: {1}, OCH: &#42;{2})\n'.format(
                    node, mch, och))
                neighbors = S.edge[node]
                neighbors_in = [n for n in neighbors if S.node[n]['infomap'] ==
                        ifp]
                neighbors_out = [n for n in neighbors if n not in neighbors_in]
                
                if neighbors_in:
                    f.write('**Community-Internal Edges ({0} in Total)**\n'.format(len(neighbors_in)))
                    for nB in neighbors_in:
                        try:
                            occ = S.edge[node][nB]['occurrence']
                        except:
                            occ = 0
                        f.write('* [{0}](http://dighl.github.io/shijing/?char={0}) (MCH: {1}, OCH: &#42;{2}, Frequency: {3})\n'.format(
                            nB, S.node[nB]['mch'],
                            S.node[nB]['reading'].replace(' ',''),
                            occ))
                    f.write('\n')
                
                if neighbors_out:
                    f.write('**Community-External Edges ({0} in Total)**\n'.format(len(neighbors_out)))
                    for nB in neighbors_out:
                        try:
                            occ = S.edge[node][nB]['occurrence']
                        except:
                            occ = 0

                        f.write('* [{0}](http://dighl.github.io/shijing/?char={0}) (MCH: {1}, OCH: &#42;{2}, Frequency: {3})\n'.format(
                            nB, S.node[nB]['mch'],
                            S.node[nB]['reading'].replace(' ',''),
                            occ))
                    f.write('\n')


if 'heatmap' in argv:
    
    #mpl.rc('text', usetex=True)
    mpl.rc('font', family='FreeSerif')
    plt.switch_backend('pgf')
    mpl.rcParams['text.latex.unicode'] = True
    #mpl.rcParams['pgf.preamble'] = [r'\usepackage{fontspec}\setmainfont{Free Serif}']

    # stores the scores for all pairs
    D = {}
    rimes = []
    R = {}
    for nA,nB,data in G.edges(data=True):

        rA = G.node[nA]['rime']
        rB = G.node[nB]['rime']
        if rA and rB:
            rimes += [rA,rB]
            try:
                D[rA,rB] += 1
                D[rB,rA] += 1
            except KeyError:
                D[rA,rB] = 1
                D[rB,rA] = 1

            try:
                R[rA] += 1
            except KeyError:
                R[rA] = 1
            try:
                R[rB] += 1
            except KeyError:
                R[rB] = 1

    # make the amtrix
    rime_set = sorted(set(rimes))

    # filter the rime-set 
    rime_set = [r for r in rime_set if r[-1]]
    matrix = [[0 for x in rime_set] for j in rime_set]

    # get the sum of all occurrences
    totals = sum([R[r] for r in rime_set])
    
    with open('stats/heatmap.tsv', 'w') as f:
        for i,rA in enumerate(rime_set):
            for j,rB in enumerate(rime_set):
                ocA = R[rA]
                ocB = R[rB]

                if (rA,rB) in D:
                    ocAB = D[rA,rB]
                else:
                    ocAB = 0
                
                # we calculate jaccard
                score = ocAB / (ocA + ocB - ocAB)
                
                matrix[i][j] = score
                f.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5:.2f}\n'.format(
                    rA, rB, ocA, ocB, ocAB, score))

    # make the figure
    figure = plt.figure()
    im = plt.matshow(matrix, aspect='auto', origin='lower', 
            interpolation='nearest', cmap=mpl.cm.jet)
    plt.xticks(
            range(len(rime_set)),
            rime_set,
            size=6,
            rotation=45
            )
    plt.yticks(
            range(len(rime_set)),
            rime_set,
            size=6,
            )
    plt.imshow(matrix, cmap=mpl.cm.jet, visible=False)
    c = plt.colorbar(im)
    plt.savefig('graphics/heatmap.pdf')


    

